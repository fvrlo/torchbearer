from __future__ import annotations

import struct
import zlib
from abc import ABC, abstractmethod

from collections.abc import Generator
from inspect import getmembers, ismethod, isfunction
from pathlib import Path
from typing import Any, BinaryIO, Callable, final, Literal, Optional, Protocol

from lz4 import block, frame
from io import BytesIO
from itertools import batched

from loguru import logger

__all__ = [
	"byter",
	"Stream",
	"EndianLiteral",
	"CloseStrCache",
	"OutOfBoundsException",
	"find_start_of_nts_array",
	"StreamObject",
	"StreamFields",
	"ByteStreamField"
]

from mulch import Dictable

type EndianLiteral = Literal['little', 'big']

def byter(value: int) -> str:
	tm = 0
	while value > 1024:
		tm += 1
		value /= 1024
	return f"{round(value, 2)} {['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'][tm]}"




class _StreamTempConfig:
	type TTuple[T] = tuple[T, Optional[T]]
	
	prnt: Stream
	ppos: int
	ofst: Optional[int]
	odir: Optional[int]
	endi: TTuple[EndianLiteral]
	sign: TTuple[bool]
	size: TTuple[int]
	blen: TTuple[int]
	
	def __init__(self, /, prnt: Stream, *,
	             ofst:  Optional[int]             = None,
	             odir:  Optional[int]             = None,
	             endi:  Optional[EndianLiteral]   = None,
	             sign:  Optional[bool]            = None,
	             size:  Optional[int]             = None,
	             blen:  Optional[int]             = None,
	             ):
		self.prnt = prnt
		self.ppos = prnt.tell()
		self.ofst = ofst
		self.odir = odir
		self.endi = (self.prnt.endi, endi)
		self.sign = (self.prnt.sign, sign)
		self.size = (self.prnt.size, size)
		self.blen = (self.prnt.blen, blen)
	
	def __enter__(self):
		endi = self.endi[1]
		sign = self.sign[1]
		size = self.size[1]
		blen = self.blen[1]
		if endi is not None:
			self.prnt.endi = endi
		if size is not None:
			self.prnt.size = size
		if sign is not None:
			self.prnt.sign = sign
		if blen is not None:
			self.prnt.blen = blen
		if self.ofst is not None:
			self.prnt.seek(self.ofst, self.odir if self.odir is not None else 0)
		return self
	
	def __exit__(self, *args) -> None:
		if self.endi[1] is not None:
			self.prnt.endi = self.endi[0]
		if self.size[1] is not None:
			self.prnt.size = self.size[0]
		if self.sign[1] is not None:
			self.prnt.sign = self.sign[0]
		if self.blen[1] is not None:
			self.prnt.blen = self.blen[0]
		if self.ofst is not None:
			self.prnt.seek(self.ppos)
	
class _DebugNamespace:
	@staticmethod
	def parse(data: int, *, decode: bool = True):
		piece = data.to_bytes()
		if piece == b'\x00':
			return '__'
		elif decode and (0x21 <= int.from_bytes(piece) <= 0x7e):
			return f'{piece.decode("utf-8", "strict")} '
		else:
			return piece.hex()
	
	@classmethod
	def yielder_str(cls, data: bytes | bytearray, *, chunksize: int = 4, decode: bool = True) -> Generator[tuple[str, ...]]:
		for chunk in batched(data, chunksize):
			yield tuple(cls.parse(x, decode=decode) for x in chunk)
	
	@classmethod
	def print(cls, data: bytes | bytearray, *, chunksize: int = 4, decode: bool = True) -> str:
		return ' | '.join(' '.join(piece_tup) for piece_tup in cls.yielder_str(data, chunksize=chunksize, decode=decode))

	@classmethod
	def print_straight(cls, data: bytes | bytearray) -> str:
		return ' '.join(cls.parse(x) for x in data)


class OutOfBoundsException(Exception):
	pass


def find_start_of_nts_array(real_namecount: int, data: bytes) -> int:
	with Stream(data[::-1]) as neg_stream:
		with Stream(data) as fwd_stream:
			# the first (last in neg_stream) word should have a LE integer in front describing the size of the null terminated string array (nameSize)
			# nameSize should be equal to the position of the first (last in neg_stream) word's first letter in our inverse stream
			while True:
				negpos = neg_stream.tell()
				nameSize = int.from_bytes(neg_stream.peek(4), byteorder='big') # BE is just reverse LE, 5Head
				if negpos == nameSize:
					logger.info(f"Found possible namesize value of {negpos}...")
					# begin test by going to the negative index negpos
					fwd_stream.seek(-negpos, 2)
					fwd_namecount = 0
					while fwd_stream.tell() < len(data):
						# get a null term string, add to the counter, repeat until we reach the end of the stream
						str(fwd_stream)
						fwd_namecount += 1
					if fwd_namecount == real_namecount:
						logger.info(f"Found successful namesize value of {negpos}")
						return negpos
					else:
						# failiure.
						# could be a collision error, so let's just keep iterating and ignore it.
						logger.error(f"Didn't work at {negpos}...")
				neg_stream.seek(1, 1)


class StreamObject[ExtraType]:
	__so_init__: bool
	__so_pos0__: int
	
	@final
	@classmethod
	def __so_fields__(cls) -> list[ByteStreamField]:
		"""StreamObject get descriptors"""
		return [v for v in cls.__dict__.values() if isinstance(v, ByteStreamField)]
	
	def __init__(self, stream: Stream, /, *, extra: ExtraType = None):
		self.__so_init__ = False
		self.__so_pos0__ = stream.tell()
		somdesc = self.__so_fields__()
		
		if len(stream) == 0 and len(somdesc) != 0:
			logger.error(f"{self.__class__.__name__} errored when initializing: zero-length stream")
			raise ValueError
		
		for member_object in somdesc:
			try:
				member_object.setter(stream=stream, obj=self, extra=extra)
			except ValueError as e:
				logger.error(f"Error setting {member_object.__bsf_orig__} on {type(self).__name__}")
				raise e
		
		set_attrs = [x for x in self.__dict__.keys() if '_bsf_' in x]
		assert len(set_attrs) == len(somdesc), (len(set_attrs), len(somdesc), self.__dict__.keys())
		self.__so_init__ = True
	
	def dict(self):
		gen = {k: getattr(self, k) for k in [name for name, x in getmembers(self.__class__) if not (ismethod(x) or isfunction(x) or name.startswith('_') or name.endswith('_'))]}
		return {k: v.dict() if isinstance(v, Dictable) else v for k, v in gen.items()}









class ByteStreamField[returnType, extraType](ABC):
	__bsf_orig__: str
	__bsf_name__: str
	
	def __set_name__(self, obj: StreamObject, name: str):
		self.__bsf_orig__ = name
		self.__bsf_name__ = f'_bsf_{name}'

	def __get__(self, obj: StreamObject, objtype: type[StreamObject]) -> returnType:
		try:
			return getattr(obj, self.__bsf_name__)
		except AttributeError as e:
			logger.error(f"StreamField error: tried getting {self.__bsf_orig__} but this object/caller hasn't set one yet!")
			logger.error(f"Is the object even a StreamObject?: {isinstance(obj, StreamObject)}")
			logger.error(f"Real type: {obj} ({type(obj)}, caller says {objtype})")
			logger.error(f"Initialized?: {obj.__so_init__}")
			logger.error(f"__get__ caller type: {objtype.__name__}")
			logger.error(f"stream fields: {[x for x in dir(obj) if '_bsf_' in x]}")
			raise e
	
	def setter(self, *, stream: Stream, obj: StreamObject, extra: extraType):
		try:
			value = self.caller(stream, obj, extra)
			setattr(obj, self.__bsf_name__, value)
			assert value == getattr(obj, self.__bsf_name__)
		except OutOfBoundsException as e:
			logger.error(f"{obj.__class__.__name__} errored when initializing field {self.__bsf_name__}")
			logger.error(f"start: {obj.__so_pos0__}, current pos: {stream.tell()}")
			logger.error(f"{Stream.debug.print(stream.peekskip(-(stream.tell() - obj.__so_pos0__), stream.tell() - obj.__so_pos0__), decode=False)}")
			raise e
		except AssertionError as e:
			logger.error(f"{obj.__class__.__name__} errored when initializing field {self.__bsf_name__}")
			logger.error(f"field was set but getattr retrieved something else")
			raise e
		
	@abstractmethod
	def caller(self, stream: Stream, obj: StreamObject, extra: extraType) -> returnType:
		...



class CallProto[cType: Stream, rType](Protocol):
	def __call__(self, x: cType) -> rType:
		...


class StreamFields:
	class peek(ByteStreamField[None, None]):
		"""A field meant for peeking in a stream, logging what it finds, and returning nothing else. Useful for debugging StreamObject parsing."""
		
		def __init__(self, size: int, /):
			self.size = size
		
		def caller(self, stream, obj, extra):
			logger.info(f"peek (starting at {stream.tell()}): {Stream.debug.print(stream.peek(self.size), decode=False)}")
	
	class peekskip(ByteStreamField[None, None]):
		"""A field meant for skipping a distance, peeking in a stream, logging what it finds, and returning nothing else. Useful for debugging StreamObject parsing."""
		
		def __init__(self, skip: int, size: int, /):
			self.skip = skip
			self.size = size
		
		def caller(self, stream, obj, extra):
			logger.info(f"peek: {Stream.debug.print(stream.peekskip(self.skip, self.size), decode=False)}")
	
	class bytes(ByteStreamField[bytes, None]):
		def __init__(self, size: int, /):
			self.size = size
		
		def caller(self, stream, obj, extra):
			return stream[self.size]
	
	class crc(ByteStreamField[str, None]):
		def caller(self, stream, obj, extra):
			return stream[4].hex().upper()
	
	class int(ByteStreamField[int, None]):
		def __init__(self, size: int | None = None, /, sign: bool | None = None, endi: EndianLiteral | None = None):
			self.size = size
			self.sign = sign
			self.endi = endi
		
		def caller(self, stream, obj, extra):
			size = stream.size if self.size is None else self.size
			sign = stream.sign if self.sign is None else self.sign
			endi = stream.endi if self.endi is None else self.endi
			data = stream[size]
			if data is None:
				logger.error([self.size, stream.tell(), len(stream)])
				raise ValueError(self.size)
			return int.from_bytes(data, byteorder=endi, signed=sign) # type: ignore
	
	class sint(ByteStreamField[int, None]):
		def __init__(self, size: int | None = None, /, endi: EndianLiteral | None = None):
			self.size = size
			self.endi = endi
		
		def caller(self, stream, obj, extra):
			size = stream.size if self.size is None else self.size
			endi = stream.endi if self.endi is None else self.endi
			data = stream[size]
			if data is None:
				logger.error([self.size, stream.tell(), len(stream)])
				raise ValueError(self.size)
			return int.from_bytes(data, byteorder=endi, signed=True)  # type: ignore
	
	class uint(ByteStreamField[int, None]):
		def __init__(self, size: int | None = None, /, endi: EndianLiteral | None = None):
			self.size = size
			self.endi = endi
		
		def caller(self, stream, obj, extra):
			size = stream.size if self.size is None else self.size
			endi = stream.endi if self.endi is None else self.endi
			data = stream[size]
			if data is None:
				logger.error([self.size, stream.tell(), len(stream)])
				raise ValueError(self.size)
			return int.from_bytes(data, byteorder=endi, signed=False)  # type: ignore
	
	class float(ByteStreamField[float, None]):
		size: Literal[2, 4, 8]
		
		def __init__(self, size: Literal[2, 4, 8] = 4):
			self.size = size
		
		def caller(self, stream, obj, extra):
			match self.size:
				case 2: return stream.f2
				case 4: return stream.f4
				case 8: return stream.f8

	class bool(ByteStreamField[bool, None]):
		def caller(self, stream, obj, extra):
			return bool(stream)

	class str(ByteStreamField[str, None]):
		size: int | None
		
		def __init__(self, size: int | None = None):
			self.size = size
		
		def caller(self, stream, obj, extra):
			if self.size is None:
				return str(stream)
			elif self.size == -1:
				return stream.string(int(stream))
			else:
				return stream.string(self.size)

	class nts(ByteStreamField[str, None]):
		"""Null terminated string"""
		def caller(self, stream, obj, extra):
			return str(stream)
	
	class istr(ByteStreamField[str, None]):
		"""String prepended with length field"""
		def caller(self, stream, obj, extra):
			return stream.string(int(stream))

	class checkstr(ByteStreamField[str, None]):
		valu: str
		size: int | None
		
		def __init__(self, real_value: str, size: int | None = None):
			self.valu = real_value
			self.size = size
		
		def caller(self, stream, obj, extra):
			if self.size is None:
				x = str(stream)
			elif self.size == -1:
				x = stream.string(int(stream))
			else:
				x = stream.string(self.size)
			assert x == self.valu
			return x

	class call[returnType](ByteStreamField[returnType, None]):
		action: CallProto[Stream, returnType]
		
		def __init__(self, action: CallProto):
			self.action = action
		
		def caller(self, stream, obj, extra) -> returnType:
			return self.action(stream)

	class callextra[returnType, extraType](ByteStreamField[returnType, extraType]):
		action: Callable[[extraType], returnType]
		
		def __init__(self, action: Callable[[extraType], returnType]):
			self.action = action
		
		def caller(self, stream, obj, extra) -> returnType:
			return self.action(extra)

	class callself[returnType, selfType: StreamObject](ByteStreamField[returnType, None]):
		action: Callable[[selfType], returnType]
		
		def __init__(self, action: Callable[[selfType], returnType]):
			self.action = action
		
		def caller(self, stream, obj, extra) -> returnType:
			return self.action(obj)

	class callstreamself[returnType](ByteStreamField[returnType, None]):
		action: Callable[[Stream, StreamObject], returnType]
		
		def __init__(self, action: Callable[[Stream, StreamObject], returnType]):
			self.action = action
		
		def caller(self, stream, obj, extra) -> returnType:
			return self.action(stream, obj)

	class callstreamselfplus[returnType, extraType](ByteStreamField[returnType, extraType]):
		action: Callable[[Stream, StreamObject, extraType], returnType]
		
		def __init__(self, action: Callable[[Stream, StreamObject, extraType], returnType]):
			self.action = action
		
		def caller(self, stream, obj, extra) -> returnType:
			return self.action(stream, obj, extra)

	class callplus[returnType, extraType](ByteStreamField[returnType, extraType]):
		action: Callable[[Stream, extraType], returnType]
		
		def __init__(self, action: Callable[[Stream, extraType], returnType]):
			self.action = action
		
		def caller(self, stream, obj, extra: extraType | None) -> returnType:
			return self.action(stream, extra)

	class iter[returnType](ByteStreamField[returnType, None]):
		action: Callable[[Stream], returnType]
		length: int | None
		
		def __init__(self, action: Callable[[Stream], returnType], length: int | None = None):
			self.action = action
			self.length = length
		
		def caller(self, stream, obj, extra) -> list[returnType]:
			if self.length is None:
				length = stream.integer(4, signed=False, endi='little')
			else:
				length = self.length
			return [self.action(stream) for _ in range(length)]
		
	class subitem[subType: StreamObject](ByteStreamField[subType, None]):
		sso: type[subType]
		
		def __init__(self, sso: type[subType]):
			self.sso = sso

		def caller(self, stream, obj, extra) -> subType:
			return self.sso(stream)



class Stream:
	internal_io: BinaryIO
	len: int
	read_count: int
	
	endi: EndianLiteral
	sign: bool
	size: int
	
	debug = _DebugNamespace
	
	
	# Dunder Methods
	
	def __init__(self,
	             data: Path | bytes | bytearray | memoryview,
	             *,
	             comp: Literal['zlib', 'lz4', False] = False,
	             endi: EndianLiteral = 'little',
	             sign: bool = False,
	             size: int = 4,
	             blen: Optional[int] = None,
	             spos: Optional[int] = None
	             ):
		if isinstance(data, Path) and not comp:
			self.internal_io = data.open('rb', buffering=-1)
		else:
			if isinstance(data, Path):
				data = data.read_bytes()
			match comp:
				case 'zlib':
					self.internal_io = BytesIO(zlib.decompress(data))
				case 'lz4':
					self.internal_io = BytesIO(frame.decompress(data))
				case _:
					self.internal_io = BytesIO(data)
		
		# define stream bounds
		self.internal_io.seek(0, 2)
		self.len = self.tell()
		self.internal_io.seek(0)
		
		self.read_count = 0
		if spos is not None:
			self.internal_io.seek(spos, 0)
		self.endi = endi
		self.sign = sign
		self.size = size
		self.blen = blen if blen is not None else size
	
	def __len__(self):
		return self.len
	
	def __enter__(self):
		return self
	
	def __exit__(self, *args, **kwargs) -> None:
		self.internal_io.close()

	def __str__(self):
		return self.nts()
	
	def __int__(self):
		return self.integer()
	
	def __float__(self):
		return self.f4
	
	def __bool__(self):
		return self.integer(1) != 0
	
	def __bytes__(self):
		return self[self.blen]
	
	def __call__(
			self,
			ofst: int = None,
			odir: int = None,
			*,
			endi: EndianLiteral = None,
			sign: bool = None,
			size: int = None,
			blen: int = None
			) -> _StreamTempConfig:
		return _StreamTempConfig(self, ofst=ofst, odir=odir, endi=endi, sign=sign, size=size, blen=blen)
	
	def __getitem__(self, i: int | slice) -> bytes:
		if isinstance(i, slice):
			start, stop, step = i.indices(self.len)
			with _StreamTempConfig(self, ofst=start):
				return self.read(stop - start)
		else:
			return self.read(i)
	
	def nts(self, min_len: int = 1, /, encoding: str = "utf-8") -> str:
		"""Method for reading a null-terminated string (AKA CString)."""
		array = bytearray()
		yield_count = 0
		while True:
			letter = self.read(1)
			if letter != b'\x00':
				array += letter
			yield_count += 1
			if yield_count >= min_len:
				if letter == b'\x00':
					break
		return array.decode(encoding)
	
	def nts_at(self, pos: int, min_len: int = 1, /, encoding: str = "utf-8") -> str:
		self.seek(pos)
		return self.nts(min_len, encoding)
	
	def peek(self, length: int) -> bytes:
		data = self[length]
		self.seek(-length, 1)
		return data
	
	def peekprint(self, length: int) -> str:
		return _DebugNamespace.print(self.peek(length), decode=False)
	
	def peekskipprint(self, skip: int, length: int) -> str:
		return _DebugNamespace.print(self.peekskip(skip, length), decode=False)
	
	def peekskip(self, skip: int, length: int) -> bytes:
		self.seek(skip, 1)
		data = self[length]
		self.seek(-(length + skip), 1)
		return data
	
	# Reimplementations
	def seek(self, __offset: int, __whence: Literal[0, 1, 2, 'start', 'current', 'end', 's', 'c', 'e'] = 0) -> int:
		"""Change the stream `position`_ to the given byte offset, interpreted relative to the position indicated by whence, and return the new absolute position. Values for whence are:

	     - 0: absolute position (start of the stream); offset should be zero or positive
	     - 1: relative position (current stream position); offset may be negative
	     - 2: negative position (end of the stream); offset should be zero or negative
		
	    .. _position: https://docs.python.org/3.12/library/io.html#io.IOBase.seek
		"""
		match __whence:
			case 's' | 'start':
				__whence = 0
			case 'c' | 'current':
				__whence = 1
			case 'e' | 'end':
				__whence = 2
		if not isinstance(__whence, int):
			raise ValueError(__whence)
		return self.internal_io.seek(__offset, __whence)
	
	def readline(self, __limit: int = -1, /):
		return self.internal_io.readline(__limit)
	
	def readlines(self, __hint: int = -1, /):
		return self.internal_io.readlines(__hint)
	
	@property
	def pos(self) -> int:
		return self.tell()
	
	def tell(self) -> int:
		return self.internal_io.tell()
	
	@staticmethod
	def to_hexstr(data: bytes, /, *, endi: EndianLiteral = 'little') -> str:
		if endi == 'big':
			data = data[::-1]
		return '0x' + data.hex().upper()
	
	def hexstr(self, distance: int = 4, /, *, endi: EndianLiteral = 'little') -> str:
		return self.to_hexstr(self[distance], endi=endi)
	
	def skip(self, distance: int) -> bytes:
		return self[distance]
	
	def iter[iterType](self, caller: Callable[[Stream], iterType], length: int, /) -> list[iterType]:
		return [caller(self) for _ in range(length)]
	
	def remaining(self) -> int:
		return self.len - self.tell()
	
	def read(self, __n: int = -1, /) -> bytes:
		if self.len != 0:
			if __n > self.remaining():
				raise OutOfBoundsException(f"{__n} > {self.remaining()} (len: {self.len}, pos: {self.tell()})")
			self.read_count += __n if __n >= 1 else 0
			return self.internal_io.read(__n)
		else:
			return b''
		
	def read_at(self, pos: int, size: int, go_back: bool = False) -> bytes:
		if go_back:
			startpos = self.tell()
			self.seek(pos, 0)
			data = self.read(size)
			self.seek(startpos, 0)
			return data
		else:
			self.seek(pos, 0)
			return self.read(size)
	
	def read_lz4_block(self, cmp_size: int, dcp_size: int, is_compressed: bool, offset: int = -1) -> bytes:
		if offset != -1:
			self.seek(offset, 0)
		if is_compressed:
			dcp = block.decompress(self.read(cmp_size), uncompressed_size=dcp_size)
			if len(dcp) != dcp_size:
				logger.error(f'Size difference encountered: expected {dcp_size}, got {len(dcp)}')
			return dcp
		else:
			return self.read(dcp_size)
	
	def integer(self, length: int | None = None, /, signed: bool | None = None, endi: EndianLiteral | None = None) -> int:
		if length is None:
			length = self.size
		if signed is None:
			signed = self.sign
		if endi is None:
			endi = self.endi
		return int.from_bytes(self.read(length), byteorder=endi, signed=signed)
	
	def string(self, length: int, /, *, encoding ="utf-8") -> str:
		if length == 0:
			return ''
		elif length == -1:
			return self.read(self.integer()).decode(encoding)
		else:
			return self.read(length).decode(encoding)
	
	def unpack(self, __fmt: str) -> tuple[Any, ...]:
		return struct.unpack(__fmt, self.read(struct.calcsize(__fmt)))
	
	@staticmethod
	def pack(__fmt: str, *vals) -> bytes:
		return struct.pack(__fmt, *vals)
	
	@property
	def crc(self) -> str:
		return self[4][::-1].hex().upper()
	
	# <------   Integers    ------>
	@property
	def i1(self) -> int:
		return self.integer(1)
	
	@property
	def i2(self) -> int:
		return self.integer(2)
	
	@property
	def i3(self) -> int:
		return self.integer(3)
	
	@property
	def i4(self) -> int:
		return self.integer(4)
	
	@property
	def i5(self) -> int:
		return self.integer(5)
	
	@property
	def i6(self) -> int:
		return self.integer(6)
	
	@property
	def i7(self) -> int:
		return self.integer(7)
	
	@property
	def i8(self) -> int:
		return self.integer(8)
	
	
	# <------   Signed Integers    ------>
	@property
	def i_2s(self) -> int:
		return self.integer(2, signed=True)
	
	@property
	def i_3s(self) -> int:
		return self.integer(3, signed=True)
	
	@property
	def i_4s(self) -> int:
		return self.integer(4, signed=True)
	
	@property
	def i_8s(self) -> int:
		return self.integer(8, signed=True)
	
	
	# <------   Unsigned Integers    ------>
	@property
	def i_2u(self) -> int:
		return self.integer(2, signed=False)
	
	@property
	def i_3u(self) -> int:
		return self.integer(3, signed=False)
	
	@property
	def i_4u(self) -> int:
		return self.integer(4, signed=False)
	
	@property
	def i_8u(self) -> int:
		return self.integer(8, signed=False)
	
	
	# <------   Floats    ------>
	@property
	def f2(self) -> float:
		return struct.unpack('e', self[2])[0]
	
	@property
	def f4(self) -> float:
		return struct.unpack('f', self[4])[0]
	
	@property
	def f8(self) -> float:
		return struct.unpack('d',  self[8])[0]
	
	# <------   Booleans    ------>
	@property
	def boolean(self) -> bool:
		return self.i1 != 0


class CloseStrCache:
	@classmethod
	def write(cls, path: Path, dicta: dict[int, str]):
		byets_len = bytearray()
		byets_str = bytearray()
		count = 0
		for i, item in dicta.items():
			byets_len += len(item).to_bytes(4, 'little')
			byets_str += item.encode()
			count += 1
		path.write_bytes(count.to_bytes(4, 'little') + byets_len + byets_str)
	
	@classmethod
	def read(cls, path: Path) -> dict[int, str]:
		with Stream(path) as stream:
			count = int(stream)
			newe = {i: stream[strlen[0]].decode() for i, strlen in enumerate(struct.iter_unpack('<I', stream[4 * count]))}
		return newe


class SimpleStringCache:
	path: Path
	
	def __init__(self, path: Path):
		self.path = path
	
	def write(self, strings: list[str]):
		with self.path.open('wb') as stream:
			stream.write(len(strings).to_bytes(4, 'little'))
			for string in strings:
				encoded = string.encode("utf-8")
				stream.write(len(encoded).to_bytes(4, 'little'))
				stream.write(encoded)
	
	def read(self) -> list[str]:
		with Stream(self.path) as stream:
			count = int(stream)
			strings = [stream.string(int(stream)) for _ in range(count)]
		return strings


class StringCache:
	str_hash: dict[str, str]
	str_hstr: dict[str, str]
	
	@classmethod
	def crchash(cls, *values: int | str) -> str:
		crcvalue = 0
		for x in values:
			if isinstance(x, int):
				x = x.to_bytes(8, byteorder='little')
			elif isinstance(x, str):
				x = x.encode('utf-8')
			crcvalue = zlib.crc32(x, crcvalue)
		return crcvalue.to_bytes(4, byteorder='little').hex()
	
	def __init__(self):
		self.str_hash = dict()
		self.str_hstr = dict()
	
	def get(self, path: Path, offset: int, size: int):
		return self.str_hstr[self.str_hash[self.crchash(str(path), offset, size)]]
	
	def add(self, crckey: str, path: Path, value: str):
		crcval = self.crchash(str(path), value)
		self.str_hstr[crcval] = value
		self.str_hash[crckey] = crcval
	
	def build(self, defs: dict[Path, list[tuple[int, int]]]):
		for path, osts in defs.items():
			with Stream(path) as stream:
				for (o, s) in osts:
					k = self.crchash(str(path), o, s)
					if k not in self.str_hash.keys():
						stream.seek(o, 0)
						self.add(k, path, stream.string(s) if s != 0 else stream.nts())