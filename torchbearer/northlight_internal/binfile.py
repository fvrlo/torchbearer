from __future__ import annotations

import zlib
from dataclasses import dataclass
from functools import cached_property
from typing import Any, ClassVar

from mulch import Stream, OutOfBoundsException, yamldump, find_start_of_nts_array
from .cid_base import Datastream, DSC, RMDL_DSC
from .obrs import ObjectBinaryReadStream_v1, UnknownObjectOBRS
from .types_general import RID
from .dpfile import BinFileDP
from .obrs_objects import *

from loguru import logger

# There might also be more meaning to an archive file depending on what DP files it holds, if any.
# Do all archive files contain cid/dp subfiles? Looks like yes
#
# possible subtypes:
#   - DP_INTERIOR
#   - DP_TASK
#   - DP_EPISODE
#   - DP_HDCELL
#   - DP_LDCELL
#   - DP_BYTECODEPARAMETERS
#   - DP_BYTECODE
#   - DP_PERSISTENTDEBUG
#   - DP_GLOBAL
#   - DP_RESOURCEDB
#   - DP_PERSISTENT
#
# A bin seems to be either a "File Archive" or a "resource batch"
# RMDL seems to be a file archive with various cid_{x}.bin files, which are containers of cid d34db33f objects
# do any DatastreamContainerv2 types require runtime info or a dp file?
# packmeta doesn't have one anyway but still




encountered = set()

def binfile(name: str, data: bytes) -> BinFileStringTable | BinFileStreamedResource | BinFileDP | BinFileCID | BinFileArchive | BinFileAltCID | RMDL_DSC | DSC:
	if name == 'string_table.bin':
		return BinFileStringTable(name, data)
	match data[:4]:
		case b'\x3F\xB3\x4D\xD3' | b'\xEF\xBE\xAD\xDE':
			return Datastream.beef_container(Stream(data))
		case b'\x0D\x00\xDF\xBA':
			return BinFileStreamedResource(name, data)  # or 'streamed' in name, but we should stick to internal checking methods
		case b'RMDL':
			return RMDL_DSC(Stream(data))
		case _:
			pass
	
	if 'dp_' in name:
		return BinFileDP(name, data)
	elif 'cid_' in name:
		if 'cid_solidbsp.bin' in name:
			return BinFileAltCID(name, data)
		if 'cid_terraindata.bin' in name:
			return BinFileAltCID(name, data)
		elif 'cid_aofield.bin' in name:
			return BinFileAltCID(name, data)
		elif 'cid_coverpoints.bin' in name:
			return BinFileAltCID(name, data)
		elif 'cid_solidbsp.bin' in name:
			return BinFileAltCID(name, data)
		elif 'cid_pathfindingmesh.bin' in name:
			return BinFileAltCID(name, data)
		elif 'cid_foliagedata.bin' in name:
			return BinFileAltCID(name, data)
		elif 'cid_roadmap.bin' in name:
			return BinFileAltCID(name, data)
		else:
			logname = f'{name} | {int.from_bytes(data[:4], 'little')} | {int.from_bytes(data[4:8], 'little')} | {int.from_bytes(data[12:16], 'little')}'
			if logname not in encountered:
				logger.info(logname)
				encountered.add(logname)
			return BinFileCID(name, data)
	else:
		return BinFileArchive(name, data)




def bin_explorer(data: bytes, name: str) -> str:
	file = binfile(name, data)
	out = yamldump(file.dict())
	
	if isinstance(file, BinFileArchive):
		out += f"Subfiles:\n"
		for filename in file.files.keys():
			out += f"    {filename}\n"
		out += "\n"
		for i, (filename, filedata) in enumerate(file.files.items(), start=1):
			out += f"Subfile {i}:\n"
			out += f"{bin_explorer(filedata, filename)}\n"
	return out







class BinFileAltCID:
	name: str
	data: bytes
	
	def __init__(self, name: str, data: bytes):
		self.name = name
		self.data = data
	
	def dict(self):
		return {'datalen': len(self.data)}


@dataclass
class UnknownMetadataOBRS:
	name: str
	data: bytes
	v1: int
	v2: int


@dataclass
class BinnedDataEntry:
	name: str
	size: int
	ofst: int
	data: bytes
	
	def dict(self):
		return {'name': self.name, 'size': self.size, 'ofst': self.ofst}



class BinFileArchive:
	name: str
	icount: int
	entries: dict[int, BinnedDataEntry]
	
	def __init__(self, name: str, data: bytes):
		self.name = name
		self.entries = dict()
		with Stream(data, endi='little', size=4, sign=False, blen=4) as stream:
			self.icount = int(stream)
			table = [(stream.string(int(stream)), int(stream)) for _ in range(self.icount)]
			with Stream(zlib.decompress(stream.read(len(stream) - stream.tell()))) as data:
				for i, (file, size) in enumerate(table):
					self.entries[i] = BinnedDataEntry(file, size, data.tell(), data[size])
	
	@cached_property
	def sizesum(self) -> int:
		return sum(x.size for x in self.entries.values())
	
	@cached_property
	def names(self) -> list[str]:
		return [x.name for x in self.entries.values()]
	
	@property
	def files(self) -> dict[str, bytes]:
		return {x.name: x.data for x in self.entries.values()}
	
	def dict(self):
		return {
			'icount' : self.icount,
			'sizesum': self.sizesum,
			'entries': self.entries
		}
	
	def subitems(self):
		for i in self.entries.values():
			yield i.name, i.data


class StreamedResource:
	rid: RID
	offset: int
	fileinfometadata: Metadata.FileInfoMetadata_v1
	metadata: Any | None
	name: str | None
	
	def __init__(self, stream: Stream, v1: int, v2: int, filename: str, discovered_namesize: int):
		self.rid = RID(stream)
		self.offset = int(stream)
		self.fileinfometadata = Metadata.FileInfoMetadata_v1(stream)
		self.name = None
		match v1, v2:
			case 4, 32:     self.metadata = None                                       # cid_streamedfacefxactor.bin metadata?
			case 7, 32:     self.metadata = None                                       # cid_streamedcloth.bin/cid_streamedsound.bin metadata?
			case 10, 32:    self.metadata = None                                       # cid_streamedcollisionpackage.bin metadata?
			case 4, 36:     self.metadata = stream[4]                                  # cid_streamedfacefxanimset.bin
			case 5, 68:     self.metadata = Metadata.ParticleSystemMetadata_v1(stream) # cid_streamedparticlesystem.bin
			case 5, 100:    self.metadata = Metadata.FoliageMeshMetadata_v1(stream)    # cid_streamedfoliagemesh.bin
			case 10, 100:   self.metadata = Metadata.TextureMetadata_v1(stream)        # cid_streamedtexture.bin
			case 6, 160:    self.metadata = Metadata.HavokAnimationMetadata_v1(stream) # cid_streamedhavokanimation.bin
			case 7, 200:    self.metadata = Metadata.MeshMetadata_v1(stream)           # cid_streamedmesh.bin
			case _:         self.metadata = UnknownMetadataOBRS(filename, stream[discovered_namesize], v1, v2) if discovered_namesize != 0 else None


class BinFileStreamedResource:
	name: str
	size: int
	version: int
	v1: int
	v2: int
	numResources: int
	
	objs: dict[int, StreamedResource]
	nameSize: int
	
	arms: int
	"""Average Resource Metadata Size"""
	
	datapairs: ClassVar[dict[str, int]] = dict()
	
	def dict(self):
		return {
			'name': self.name,
			'size': self.size,
			'version': self.version,
			'v1': self.v1,
			'v2': self.v2,
			'nameSize': self.nameSize,
			'numResources': self.numResources,
			'Average Resource Metadata Size': self.arms
		}
	
	def __init__(self, name: str, data: bytes):
		self.name = name
		self.size = len(data)
		self.objs = dict()
		
		with Stream(data) as stream:
			if int(stream) != 0xBADF000D:
				raise ValueError
			self.version = int(stream)
			if self.version != 1:
				raise NotImplementedError(f"Streamed resource file version {self.version} not yet supported")
			self.v1 = int(stream)
			self.v2 = int(stream)
			self.numResources = int(stream)
			
			start_resources = stream.tell()
			match (self.v1, self.v2):
				case (4, 32) | (4, 36) | (5, 100) | (6, 160) | (7, 200) | (7, 32) | (5, 68) | (10, 100) | (10, 32):
					pass
				case _:
					if f"{name}_{self.v1}_{self.v2}" in self.__class__.datapairs.keys():
						discovered_namesize = self.__class__.datapairs[f"{name}_{self.v1}_{self.v2}"]
					else:
						naemsize = ((((len(data) - find_start_of_nts_array(self.numResources, data)) - 4) - start_resources) / self.numResources) - 20
						if naemsize.is_integer():
							discovered_namesize = int(naemsize)
							logger.info(f"BFSR - New datapair size found ({name}, {self.v1}/{self.v2}): {discovered_namesize}")
							self.__class__.datapairs[f"{name}_{self.v1}_{self.v2}"] = discovered_namesize
						else:
							raise ValueError(f"BFSR - Datapair combo unknown ({name}, {self.v1}/{self.v2})")
			
			self.objs = {i: StreamedResource(stream, self.v1, self.v2, name, discovered_namesize) for i in range(self.numResources)}
			self.arms = (((stream.tell() - start_resources) / self.numResources) - 20) if self.numResources != 0 else 0
			self.nameSize = int(stream)
			for i in range(self.numResources):
				stream.seek(-self.nameSize + self.objs[i].offset, 2)
				self.objs[i].name = str(stream)










class BinFileCID:
	stream: Stream
	size: int
	name: str
	vrsn: int
	contentType: int
	numElements: int
	unko: bytes
	form: str
	
	def __init__(self, name: str, data: bytes):
		self.name = name
		self.stream = Stream(data)
		self.size = len(data)
		
		if self.size < 16:
			raise ValueError(self.size)
		
		self.vrsn = int(self.stream)
		self.contentType = int(self.stream)
		self.numElements = int(self.stream)
		self.unko = self.stream[4]
		if self.numElements != 0:
			match int(self.stream):
				case 0xDEADBEEF:
					self.form = 'kStructured'
				case 0xD34DB33F:
					self.form = 'kStructuredV2'
				case _:
					self.form = 'kSimple'
			self.stream.seek(-4, 1)
		else:
			self.form = 'kSimple'
		
	def yield_objects(self, objtype: str, dpfile: BinFileDP | None):
		if self.form == 'kSimple':
			try:
				obrs = ObjectBinaryReadStream_v1(self.stream, dpfile)
				for i in range(self.numElements):
					obj = obrs.object(objtype, self.vrsn)
					if isinstance(obj, str):
						if self.ees != 'Unsure':
							logger.debug(f'error on {objtype} #{i + 1}/{self.numElements} (pos: {self.stream.tell()}/{self.size}, ees: {self.ees})')
							obj = UnknownObjectOBRS(objtype, obrs.stream, self.ees, self.vrsn)
						else:
							logger.debug(f'error on {objtype} #{i + 1}/{self.numElements} (pos: {self.stream.tell()}/{self.size})')
							break
					yield obj
			except OutOfBoundsException as e:
				logger.debug(f'while yielding from {objtype}, an OutOfBounds exception occurred: {e}')
				return
		
	@cached_property
	def ees(self):
		ees = ((self.size - 16)/self.numElements) if self.numElements != 0 else 0
		return int(ees) if ees.is_integer() else 'Unsure'
	
	def dict(self):
		return {
			'Format': self.form,
			'Size': self.size,
			'Version': self.vrsn,
			'Content Type': self.contentType,
			'Elements': self.numElements,
			'Estimated Element Size': self.ees
		}


class BinFileStringTable:
	"""Adapted from AWTools's stringtable2xml.py, usually for data/locale/{language}/string_table.bin"""
	name: str
	pairs: list[tuple[str, str]]
	
	def __init__(self, name: str, data: bytes):
		self.name = name
		with Stream(data) as stream:
			self.pairs = [(stream[int(stream)].decode('utf-8'), stream[int(stream) * 2].decode('utf-16le')) for _ in range(int(stream))]
	# the value's length gets doubled because the value count is count of characters and the format is UTF-16, something about character widths goes here
	
	def dict(self):
		return {'name': self.name, 'count': len(self.pairs)}
