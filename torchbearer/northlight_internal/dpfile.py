from __future__ import annotations

from functools import cached_property
from typing import Callable, Literal
from enum import IntFlag

from loguru import logger

from torchbearer.mulch import Stream
from torchbearer.northlight_internal.types_general import GID




class DP_Offset:
	class OffsetFlags(IntFlag):
		unk1 = 1
		unk2 = 2
		unk3 = 4
		unk4 = 8
		unk5 = 16
		unk6 = 32
		unk7 = 64
		overlap = 128
		
		@property
		def names(self) -> str:
			return ' & '.join([str(x.name) for x in self]) if len(self) != 0 else 'No Flags'
		
	raw_offset: int
	bit_offset: int
	flags: OffsetFlags
	size: int | None
	
	def __init__(self, offset: int, size: int | None = None):
		self.raw_offset = offset
		self.bit_offset = offset >> 8  # stream.integer(3)
		self.flags = DP_Offset.OffsetFlags(offset & 0b11111111)  # OffsetFlags(stream.integer(1))
		self.size = size
	
	@cached_property
	def offset(self):
		return (self.bit_offset * 8) + (4 if DP_Offset.OffsetFlags.overlap in self.flags else 0)
	
	def dict(self):
		return {
			'raw offset': self.raw_offset,
			'bit offset': self.bit_offset,
			'size'      : self.size,
			'offset'    : self.offset,
			'flags'     : self.flags.names
		}

	def infodump(self):
		return f"offset {self.offset} (raw {self.raw_offset}, flags {self.flags.names})"


class BinFileDP:
	"""From OpenAWE: This class reads dp_ prefixed files which contains various data associated with elements from the cid files."""
	
	stream: Stream
	headerType: Literal['v1', 'v2', 'v3']
	counts: dict[str, int]
	dataSize: int
	unknown: bytes
	datastart: int
	offsets: dict[str, list[DP_Offset]]

	def __init__(self, name: str, data: bytes):
		self.name = name
		self.stream = Stream(data)
		peek_array = self.stream.peek(16)
		peekdata = [int.from_bytes(peek_array[(x*4):(x*4)+4], byteorder='little') for x in range(0, 4)]
		if 20 + peekdata[0] * 4 + peekdata[1] * 4 + peekdata[2] == self.stream.len:
			self.headerType = 'v1' # 20
			self.counts = dict(values=int(self.stream), string=int(self.stream))
			self.dataSize = int(self.stream)
			self.unknown = self.stream[8]
			self.stream.size = 4
		elif 28 + peekdata[0] * 4 + peekdata[1] * 4 + peekdata[2] * 4 + peekdata[3] == self.stream.len:
			self.headerType = 'v2' # 28
			self.counts = dict(values1=int(self.stream), values2=int(self.stream), string=int(self.stream))
			self.dataSize = int(self.stream)
			self.unknown = self.stream[12]
			self.stream.size = 4
		elif 40 + peekdata[0] * 8 + peekdata[1] * 8 + peekdata[2] * 8 + peekdata[3] == self.stream.len:
			self.headerType = 'v3' # unknown
			self.counts = dict(values1=int(self.stream), values2=int(self.stream), string=int(self.stream))
			self.dataSize = int(self.stream)
			self.unknown = self.stream[24]
			self.stream.size = 8
		else:
			print(Stream.debug.print(self.stream.peek(64)))
			print(peekdata, self.stream.len)
			raise NotImplementedError("Invalid dp file, could not determine header type")
		
		#logger.debug(f"DP File - {self.headerType}")
		if self.unknown != b'\0' * len(self.unknown):
			logger.info(f"Found a DP file with nonzero exta data after {self.headerType} header data: {self.unknown.hex()}")

		self.datastart = self.stream.len - self.dataSize
		self.offsets = {k: [DP_Offset(int(self.stream)) for _ in range(self.counts[k])] for k in self.counts.keys()}
	
		ordered_ofst_list = self.all_offsets()
		for i, x in enumerate(ordered_ofst_list):
			x.size = (ordered_ofst_list[i + 1].offset - x.offset) if x != ordered_ofst_list[-1] else abs(-self.dataSize + x.offset)

	def dict(self):
		return {
			'Name'       : self.name,
			'Header Type': self.headerType,
			'Size'       : self.dataSize,
			'Counts'     : self.counts,
			'Datastart'  : self.datastart,
		}
	
	def all_offsets(self) -> list[DP_Offset]:
		all_offset_list = list()
		for v in self.offsets.values():
			all_offset_list.extend(v)
		return sorted(all_offset_list, key=lambda z: z.offset)
	
	def go_to_offset(self, offset: DP_Offset):
		seekpoint = -self.dataSize + offset.offset
		assert abs(seekpoint) < len(self.stream), f"Offset too big! data {self.dataSize}, raw {offset.raw_offset}, rel_ofst {offset.offset}, seekpoing {seekpoint}, len {len(self.stream)}"
		self.stream.seek(seekpoint, 2)
	
	def is_offset_valid(self, offset: DP_Offset):
		for offset_key in self.offsets.keys():
			for x in self.offsets[offset_key]:
				if offset.offset == x.offset:
					return offset_key
		return False
	
	@staticmethod
	def errorlog(funcname: str, errorname: str, attempt_str: str, offset: DP_Offset):
		logger.error(f"{funcname} Error {errorname}: Attempted {funcname}({attempt_str}) at {offset.infodump()}")
	
	def getValue[actionType](self, offset: int, action: type[actionType] | Callable[[Stream], actionType]) -> actionType | None:
		offset = DP_Offset(offset)
		if offset.offset > self.dataSize:
			self.errorlog("getValue", f"OutOfBounds[0:{self.dataSize}]", action.__name__, offset)
			return None
		elif len(offset.flags) == 0:
			return ''
		elif action.__name__ != 'str' and (not self.is_offset_valid(offset)):
			self.errorlog("getValue", "InvalidOffset", action.__name__, offset)
			return None
		else:
			self.go_to_offset(offset)
			return action(self.stream)
	
	def getValueList[actionType](self, offset: int, count: int, action_name: str, action: type[actionType] | Callable[[Stream], actionType]) -> list[actionType] | None:
		offset = DP_Offset(offset)
		if not self.is_offset_valid(offset):
			self.errorlog("getValueList", "InvalidOffset", action_name, offset)
			return list()
		else:
			self.go_to_offset(offset)
			return [action(self.stream) for _ in range(count)]
	
	def get_list[vType](self, typearg: type[vType] | Callable[[Stream], vType], offset: int, count: int) -> list[vType]:
		return self.getValueList(offset=offset, count=count, action_name=str(typearg), action=lambda x: typearg(x))
	
	def getGIDS(self, offset: int, count: int) -> list[GID]:
		def DP_GID(stream: Stream):
			gid = GID(stream)
			stream.seek(8, 1)
			return gid
		return self.getValueList(offset=offset, count=count, action_name='GID', action=DP_GID)

	
	
