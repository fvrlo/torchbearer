from __future__ import annotations
from enum import IntEnum
from functools import cached_property
import ctypes
import math
from typing import Generator, Literal

from mulch import Stream
from .directx import DDS
from .directx.structs import DDS_HEADER, DDS_PIXELFORMAT, DDS_HEADER_DXT10

class TextureType(IntEnum):
	Texture2D = 0
	Texture3D = 1
	TextureCube = 2


def closest_to_multiple(number: int, multiple: int):
	return multiple * math.ceil(number / multiple)


def getformat(form_int):
	match form_int:
		case 0:
			return 'RGBA8'
		case 1:
			return 'DXT1'
		case 3:
			return 'DXT5'
		case 4:
			return 'RGBA8'
		case 5:
			return 'DXT1'
		case 6:
			return 'RGBA16F'
		case 7:
			return 'DXT5'
		case 8:
			return 'RGBA8'
		case 9:
			return 'DXT5'
		case 10:
			return 'RGBA16F'
		case _:
			return f"Unknown({form_int})"



def mmgen(w: int, h: int, mipmaps: int, is_cube: bool, fmt: str):
	size: int = 0
	for x in range(mipmaps):
		match fmt:
			case 'DXT1':
				size = max(8, (closest_to_multiple(w, 4) // 4) * (closest_to_multiple(h, 4) // 4) * 8)
			case 'DXT5': # BC3
				size = max(16, (closest_to_multiple(w, 4) // 4) * (closest_to_multiple(h, 4) // 4) * 16)
			case '1Bpp': # 1 byte per pixel
				size = w * h * 1
			case '2Bpp': # 2 bytes per pixel
				size = w * h * 2
			case '3Bpp': # 3 bytes per pixel
				size = w * h * 3
			case '4Bpp': # 4 bytes per pixel
				size = w * h * 4
			case _:
				size = -1
		size *= 6 if is_cube else 1
		yield size, w, h
		w = max(w // 2, 1)
		h = max(h // 2, 1)


def guess_form(w: int, h: int, mipmap_count: int, size: int, iscube: bool):
	sizes = {z: sum(x[0] for x in mmgen(w, h, mipmap_count, iscube, z)) for z in ["1Bpp", "2Bpp", "3Bpp", "4Bpp", "DXT1", "DXT5"]}
	guess_prob = dict()
	possible = list()
	for k, v in sizes.items():
		if size == v:
			possible.append(k)
			continue
		guess_prob[k] = size - v
	
	if len(possible) == 0:
		min_val = min([abs(x) for x in guess_prob.values()])
		for k, v in guess_prob.items():
			if v == abs(min_val):
				return f'fail, but closest is {k} ({v} difference)'
		return f'fail'
	else:
		return ' or '.join(possible) + (" (cube)" if iscube else "")



def getimgsize(form, w, h, d) -> int:
	match form:
		case 'R8':
			return w*h*d
		case 'RG8':
			return w*h*d*2
		case 'RGB8':
			return w*h*d*3
		case 'R32F' | 'RG16' | 'RGBA8':
			return w*h*d*4
		case 'RGBA16F':
			return w*h*d*8
		case 'DXT1':
			return max(8, ((w + 3) // 4) * ((h + 3) // 4) * 8)
		case 'DXT5':
			return max(16, ((w + 3) // 4) * ((h + 3) // 4) * 16)
		case _:
			return 0

class NorthlightTexHeader(ctypes.LittleEndianStructure):
	_fields_ = [
		('textype', ctypes.c_uint32),
		('texfmt', ctypes.c_uint32),
		('width', ctypes.c_uint32),
		('height', ctypes.c_uint32),
		('depth', ctypes.c_uint32),
		('mipmap', ctypes.c_uint32),
		('filter', ctypes.c_uint32),
		('unknown', ctypes.c_uint32),
	]
	textype: int
	texfmt: int
	width: int
	height: int
	depth: int
	mipmap: int
	filter: int
	unknown: int
	
	def __repr__(self):
		return f"<instance of NorthlightTexHeader(textype={self.textype}, texfmt={self.texfmt}, dimensions={self.dimensions}, depth={self.depth}, mipmap={self.mipmap}, filter={self.filter}, unknown={self.unknown})"
	
	@property
	def dimensions(self) -> str:
		return f"{self.width}x{self.height}"
	
	def dict(self):
		return {
			"textype": self.textype,
			"texfmt": self.texfmt,
			"width": self.width,
			"height": self.height,
			"depth": self.depth,
			"mipmap": self.mipmap,
			"texflt": self.filter,
			"unknown": self.unknown,
		}
	
	@cached_property
	def type(self) -> TextureType:
		return TextureType(value=self.textype)
	
	@cached_property
	def texture_format(self):
		return getformat(self.texfmt)
	
	def to_dds_header(self) -> DDS_HEADER:
		imgsize = getimgsize(self.texfmt, self.width, self.height, self.depth)
		flags = DDS.DDSD.CAPS | DDS.DDSD.HEIGHT | DDS.DDSD.WIDTH | DDS.DDSD.PIXELFORMAT
		caps1 = DDS.DDSCAPS.TEXTURE
		caps2 = DDS.DDSCAPS2(value=0)
		
		if self.header.textype == 2:
			caps2 |= DDS.DDSCAPS2.CUBEMAP_ALL()
		
		if self.mipmap > 1:
			flags |= DDS.DDSD.MIPMAPCOUNT
			caps1 |= DDS.DDSCAPS.MIPMAP | DDS.DDSCAPS.COMPLEX
		elif self.depth > 1 or self.textype != 0:
			caps1 |= DDS.DDSCAPS.COMPLEX
		
		if "DXT" in self.texture_format:
			flags |= DDS.DDSD.LINEARSIZE
			pxfmt = DDS_PIXELFORMAT.from_fields(fourcc=self.texture_format)
		else:
			pxfmt = DDS_PIXELFORMAT.from_fields(DDPF.RGB.value)  # type: ignore
		
		return DDS_HEADER.from_fields(flags, pxfmt, self.mipmap, imgsize, self.height, self.width, self.depth, caps1, caps2)
	
	def to_dds_dx10_custom(self, dx10_format: int) -> bytes:
		caps1 = DDS.DDSCAPS.TEXTURE
		caps2 = DDS.DDSCAPS2(value=0)
		
		if self.textype == 2:
			caps2 |= DDS.DDSCAPS2.CUBEMAP_ALL()
		
		if self.mipmap > 1:
			caps1 |= DDS.DDSCAPS.MIPMAP | DDS.DDSCAPS.COMPLEX
		
		cnst = bytearray()
		if 27 <= dx10_format <= 32:
			modus = 'rgba'
		elif dx10_format == 87:
			modus = 'bgra'
		else:
			modus = None
		cnst += DDS_HEADER.generic_dx10(self.height, self.width, self.depth, self.mipmap, caps1, caps2, modus)
		cnst += DDS_HEADER_DXT10.from_fields(dxgiFormat=dx10_format, resourceDimension=3, arraySize=6 if self.textype == 2 else 1, miscFlag=0, miscFlags2=0)
		return cnst
	
	def mipmap_specs(self, sizemode: Literal['bytes', 'pixels'] = 'bytes', /, *, min_size: int = 0) -> Generator[tuple[int, int, int, int, int]]:
		size = 0
		w = self.width
		h = self.height
		d = self.depth
		for iteration in range(self.mipmap):
			match sizemode:
				case 'bytes':
					size = getimgsize(self.texture_format, w, h, d) * (6 if self.textype == 2 else 1)
				case 'pixels':
					size = max(min_size, w * h * (6 if self.textype == 2 else 1))
				case _:
					raise ValueError(sizemode)
			yield iteration, size, w, h, d
			w = max(w // 2, 1)
			h = max(h // 2, 1)
			d = max(d // 2, 1)
	
	def mipmap_specs_bytes(self) -> Generator[tuple[int, int, int, int, int]]:
		yield from self.mipmap_specs('bytes')
	
	def mipmap_specs_pixels(self, min_size: int = 0) -> Generator[tuple[int, int, int, int, int]]:
		yield from self.mipmap_specs('pixels', min_size=min_size)
	
	@cached_property
	def mipmap_dict_bytes(self):
		return {x[0]: {'imageSize': x[1], 'width': x[2], 'height': x[3], 'depth': x[4]} for x in self.mipmap_specs_bytes()}
	

class NorthlightTex:
	header: NorthlightTexHeader
	texData: bytes
	
	def __init__(self, stream: Stream, size: int):
		self.header = NorthlightTexHeader.from_buffer_copy(stream[32])
		self.texData = stream[size-32]
	
	@property
	def data(self):
		rtrn = bytearray()
		rtrn += bytes(self.header)
		rtrn += self.texData
		return bytes(rtrn)
	
	def list(self):
		return [self.textype, self.header.texfmt, self.width, self.height, self.depth, self.mipmap, self.filter, self.unknown, self.bytelen]
	
	@property
	def width(self) -> int:
		return self.header.width
	
	@property
	def height(self) -> int:
		return self.header.height
	
	@property
	def depth(self) -> int:
		return self.header.depth
	
	@property
	def mipmap(self) -> int:
		return self.header.mipmap
	
	@property
	def filter(self) -> int:
		return self.header.filter
	
	@property
	def unknown(self) -> int:
		return self.header.unknown
	
	@property
	def textype(self):
		return self.header.textype
	
	@property
	def texfmt(self):
		return self.header.texfmt

	@property
	def type(self) -> TextureType:
		return self.header.type
	
	@cached_property
	def bytelen(self) -> int:
		return len(self.texData)
	
	def dict(self):
		return {
			"header": self.header.dict(),
			"bytelen": self.bytelen,
		}
	
	def to_dds(self):
		return b"DDS " + bytes(self.header.to_dds_header()) + self.texData
	
	def to_dds_dx10_custom(self, dx10_format: int):
		cnst = bytearray()
		cnst += b"DDS "
		cnst += self.header.to_dds_dx10_custom(dx10_format)
		cnst += self.texData
		return cnst