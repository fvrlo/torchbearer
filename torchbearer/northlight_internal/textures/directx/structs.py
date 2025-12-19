from __future__ import annotations
import ctypes
import math
from enum import IntEnum
from functools import cached_property
from typing import Literal


from mulch import Stream
from . import D3D10
from . import DDS
from . import DXGI

__all__ = [
	"DDS_HEADER",
	"DDS_HEADER_DXT10",
	"DDS_PIXELFORMAT",
	"DDS_FILEHEAD",
]

class DDSTextureType(IntEnum):
	Texture2D                       = 0
	TextureCube                     = 1
	Texture2DArray                  = 2
	TextureCubeArray                = 3

class DX10_Bitmasks:
	RGBA = (0xff000000, 0x00ff0000, 0x0000ff00, 0x000000ff)
	RBGA = (0xff000000, 0x0000ff00, 0x00ff0000, 0x000000ff)
	GRBA = (0x00ff0000, 0xff000000, 0x0000ff00, 0x000000ff)
	BGRA = (0x0000ff00, 0x00ff0000, 0xff000000, 0x000000ff)
	RGB  = (0xff000000, 0x00ff0000, 0x0000ff00, 0x00000000)
	RBG  = (0xff000000, 0x0000ff00, 0x00ff0000, 0x00000000)
	GRB  = (0x00ff0000, 0xff000000, 0x0000ff00, 0x00000000)
	BGR  = (0x0000ff00, 0x00ff0000, 0xff000000, 0x00000000)


class DDS_PIXELFORMAT(ctypes.Structure):
	"""Surface pixel format."""
	_fields_ = [
		("dwSize", ctypes.c_uint32),
		("_dwFlags", ctypes.c_uint32),
		("_dwFourCC", ctypes.c_uint32),
		("dwRGBBitCount", ctypes.c_uint32),
		("dwRBitMask_int", ctypes.c_uint32),
		("dwGBitMask_int", ctypes.c_uint32),
		("dwBBitMask_int", ctypes.c_uint32),
		("dwABitMask_int", ctypes.c_uint32),
	]
	dwSize: int
	_dwFlags: int
	_dwFourCC: int
	dwRGBBitCount: int
	dwRBitMask_int: int
	dwGBitMask_int: int
	dwBBitMask_int: int
	dwABitMask_int: int
	
	# --- Property Methods
	
	@property
	def mask_rgba(self) -> tuple[int, int, int, int]:
		return self.dwRBitMask_int, self.dwGBitMask_int, self.dwBBitMask_int, self.dwABitMask_int
	
	@property
	def mask_rgb(self) -> tuple[int, int, int]:
		return self.dwRBitMask_int, self.dwGBitMask_int, self.dwBBitMask_int
	
	@property
	def mask_bgr(self) -> tuple[int, int, int]:
		return self.dwBBitMask_int, self.dwGBitMask_int, self.dwRBitMask_int
	
	# --- Cached Property Methods
	
	@cached_property
	def valid_RGBBitCount(self) -> bool:
		return True in [_field in self.dwFlags for _field in [DDS.DDPF.RGB, DDS.DDPF.LUMINANCE, DDS.DDPF.YUV]]
	
	@cached_property
	def dwFlags(self) -> DDS.DDPF:
		"""Values which indicate what type of data is in the surface."""
		return DDS.DDPF(value=self._dwFlags)
	
	@cached_property
	def dwFourCC(self) -> str:
		"""Four-character codes for specifying compressed or custom formats. A FourCC of DX10 indicates the prescense of the DDS_HEADER_DXT10 extended header, and the dxgiFormat member of that structure indicates the true format."""
		return self._dwFourCC.to_bytes(4, 'little').decode()
	
	@cached_property
	def dwRBitMask(self) -> bytes:
		"""Red (or luminance or Y) mask for reading color data. For instance, given the A8R8G8B8 format, the red mask would be 0x00ff0000."""
		return self.dwRBitMask_int.to_bytes(4, 'little')
	
	@cached_property
	def dwGBitMask(self) -> bytes:
		"""Green (or U) mask for reading color data. For instance, given the A8R8G8B8 format, the green mask would be 0x0000ff00."""
		return self.dwGBitMask_int.to_bytes(4, 'little')
	
	@cached_property
	def dwBBitMask(self) -> bytes:
		"""Blue (or V) mask for reading color data. For instance, given the A8R8G8B8 format, the blue mask would be 0x000000ff."""
		return self.dwBBitMask_int.to_bytes(4, 'little')
	
	@cached_property
	def dwABitMask(self) -> bytes:
		"""Alpha mask for reading alpha data. dwFlags must include DDPF_ALPHAPIXELS or DDPF_ALPHA. For instance, given the A8R8G8B8 format, the alpha mask would be 0xff000000."""
		return self.dwABitMask_int.to_bytes(4, 'little')
	
	# --- Class Methods
	
	@classmethod
	def generic_dx10(cls) -> "DDS_PIXELFORMAT":
		return cls.from_buffer_copy(cls.bytes_dx10())

	@staticmethod
	def bitmask_empty() -> bytes:
		cnst = bytearray()
		cnst += b'\x00\x00\x00\x00' # dwRGBBitCount
		cnst += b'\x00\x00\x00\x00' # dwRBitMask
		cnst += b'\x00\x00\x00\x00' # dwGBitMask
		cnst += b'\x00\x00\x00\x00' # dwBBitMask
		cnst += b'\x00\x00\x00\x00' # dwABitMask
		return bytes(cnst)
		
	@staticmethod
	def bitmask_rgb() -> bytes:
		cnst = bytearray()
		cnst += b'\x18\x00\x00\x00' # dwRGBBitCount
		cnst += b''.join(x.to_bytes(4, 'little') for x in DX10_Bitmasks.RGB)
		return bytes(cnst)
		
	@staticmethod
	def bitmask_rgba() -> bytes:
		cnst = bytearray()
		cnst += b'\x20\x00\x00\x00' # dwRGBBitCount
		cnst += b''.join(x.to_bytes(4, 'little') for x in DX10_Bitmasks.RGBA)
		return bytes(cnst)
		
	@staticmethod
	def bitmask_bgra() -> bytes:
		cnst = bytearray()
		cnst += b'\x20\x00\x00\x00' # dwRGBBitCount
		cnst += b''.join(x.to_bytes(4, 'little') for x in DX10_Bitmasks.BGRA)
		return bytes(cnst)
		
	@classmethod
	def bytes_dx10(cls) -> bytes:
		cnst = bytearray()
		cnst += b'\x20\x00\x00\x00' # dwSize
		cnst += b'\x04\x00\x00\x00' # dwFlags
		cnst += b'DX10'             # dwFourCC
		cnst += cls.bitmask_empty()
		return bytes(cnst)

	@classmethod
	def bytes_dx10_rgb(cls) -> bytes:
		cnst = bytearray()
		cnst += b'\x20\x00\x00\x00' # dwSize
		cnst += b'\x44\x00\x00\x00' # dwFlags
		cnst += b'DX10'             # dwFourCC
		cnst += cls.bitmask_rgb()
		return bytes(cnst)

	@classmethod
	def bytes_dx10_rgba(cls) -> bytes:
		cnst = bytearray()
		cnst += b'\x20\x00\x00\x00'  # dwSize
		cnst += b'\x45\x00\x00\x00'  # dwFlags
		cnst += b'DX10'              # dwFourCC
		cnst += cls.bitmask_rgba()
		return bytes(cnst)

	@classmethod
	def bytes_dx10_bgra(cls) -> bytes:
		cnst = bytearray()
		cnst += b'\x20\x00\x00\x00'  # dwSize
		cnst += b'\x45\x00\x00\x00'  # dwFlags
		cnst += b'DX10'              # dwFourCC
		cnst += cls.bitmask_bgra()
		return bytes(cnst)

	@classmethod
	def from_stream(cls, stream: Stream) -> "DDS_PIXELFORMAT":
		"""Create a PixelFormat from a stream, reading 32 bytes total."""
		newobj = cls.from_buffer_copy(stream[32])
		if newobj.dwSize != 32:
			raise ValueError(newobj.dwSize)
		return newobj

	@classmethod
	def from_fields(cls,
	                pfflag: int     = 0,
	                rgb_bc: int     = 0,
	                fourcc: bytes   = b'\x00\x00\x00\x00',
	                r_mask: bytes   = b'\x00\x00\x00\x00',
	                g_mask: bytes   = b'\x00\x00\x00\x00',
	                b_mask: bytes   = b'\x00\x00\x00\x00',
	                a_mask: bytes   = b'\x00\x00\x00\x00',
	                ) -> "DDS_PIXELFORMAT":
		"""Create a PixelFormat from the component fields."""
		if isinstance(fourcc, str):
			fourcc = fourcc.encode('ASCII')
		
		pfflag = DDS.DDPF(pfflag)
		if fourcc != b'\x00\x00\x00\x00' and DDS.DDPF.FOURCC not in pfflag:
			pfflag |= DDS.DDPF.FOURCC
		cnst = bytearray()
		cnst += b'\x20\x00\x00\x00'
		cnst += pfflag.to_bytes(4, 'little')
		cnst += fourcc
		cnst += rgb_bc.to_bytes(4, 'little')
		cnst += r_mask + g_mask + b_mask + a_mask
		return cls.from_buffer_copy(cnst)
	
	def dict(self):
		return {
			"dwSize": self.dwSize,
			"dwFlags": [x.name for x in self.dwFlags],
			"dwFourCC": self.dwFourCC,
			"dwRGBBitCount": self.dwRGBBitCount,
			"dwRBitMask": self.dwRBitMask,
			"dwGBitMask": self.dwGBitMask,
			"dwBBitMask": self.dwBBitMask,
			"dwABitMask": self.dwABitMask,
		}

class DDS_HEADER(ctypes.Structure):
	_fields_ = [
		("_dwSize",                 ctypes.c_uint32),
		("_dwFlags",                ctypes.c_uint32),
		("_dwHeight",               ctypes.c_uint32),
		("_dwWidth",                ctypes.c_uint32),
		("_dwPitchOrLinearSize",    ctypes.c_uint32),
		("_dwDepth",                ctypes.c_uint32),
		("_dwMipMapCount",          ctypes.c_uint32),
		("_dwReserved1",            ctypes.c_uint32 * 11), # type: ignore
		("_ddspf",                  DDS_PIXELFORMAT),
		("_dwCaps",                 ctypes.c_uint32),
		("_dwCaps2",                ctypes.c_uint32),
		("_dwCaps3",                ctypes.c_uint32),
		("_dwCaps4",                ctypes.c_uint32),
		("_dwReserved2",            ctypes.c_uint32),
	]
	_dwSize: int
	_dwFlags: int
	_dwHeight: int
	_dwWidth: int
	_dwPitchOrLinearSize: int
	_dwDepth: int
	_dwMipMapCount: int
	_dwReserved1: ctypes.Array[int]
	_ddspf: DDS_PIXELFORMAT
	_dwCaps: int
	_dwCaps2: int
	_dwCaps3: int
	_dwCaps4: int
	_dwReserved2: int
	
	# --- Property Methods
	
	@property
	def dwSize(self) -> int:
		"""Size of structure. This member must be set to 124."""
		return self._dwSize
	
	@property
	def dwHeight(self) -> int:
		"""Surface height (in pixels)."""
		return self._dwHeight
	
	@property
	def dwWidth(self) -> int:
		"""Surface width (in pixels)."""
		return self._dwHeight
	
	@property
	def dwPitchOrLinearSize(self) -> int:
		"""The pitch or number of bytes per scan line in an uncompressed texture; the total number of bytes in the top level texture for a compressed texture."""
		return self._dwPitchOrLinearSize
	
	@property
	def dwDepth(self) -> int:
		"""Depth of a volume texture (in pixels), otherwise unused."""
		return self._dwDepth
	
	@property
	def dwMipMapCount(self) -> int:
		"""Number of mipmap levels, otherwise unused."""
		return self._dwMipMapCount
	
	@property
	def ddspf(self) -> DDS_PIXELFORMAT:
		"""The pixel format."""
		return self._ddspf
	
	@property
	def dwReserved1(self) -> ctypes.Array[int]:
		"""Unused."""
		return self._dwReserved1
	
	@property
	def dwReserved2(self) -> int:
		"""Unused."""
		return self._dwReserved2
	
	@property
	def dwCaps(self) -> DDS.DDSCAPS:
		"""Specifies the complexity of the surfaces stored."""
		return self.dwCaps1
	
	# --- Cached Property Methods
	
	@cached_property
	def dwFlags(self) -> DDS.DDSD:
		"""Values which indicate what type of data is in the surface."""
		return DDS.DDSD(value=self._dwFlags)

	@cached_property
	def dwCaps1(self) -> DDS.DDSCAPS:
		"""Specifies the complexity of the surfaces stored."""
		return DDS.DDSCAPS(value=self._dwCaps)

	@cached_property
	def dwCaps2(self) -> DDS.DDSCAPS2:
		"""Additional detail about the surfaces stored."""
		return DDS.DDSCAPS2(value=self._dwCaps2)

	@cached_property
	def dwCaps3(self) -> DDS.DDSCAPS3:
		"""Unused."""
		return DDS.DDSCAPS3(value=self._dwCaps3)

	@property
	def dwCaps4(self):
		"""Unused."""
		raise NotImplementedError
	
	# --- Class Methods
	
	@classmethod
	def generic_dx10(cls, h: int, w: int, d: int, mmc: int, caps1: int = 0, caps2: int = 0, rgb: Literal['rgb', 'rgba', 'bgra', None] = None) -> "DDS_HEADER":
		cnst = bytearray()
		cnst += b'\x7C\x00\x00\x00'
		cnst += (DDS.DDSD.CAPS | DDS.DDSD.HEIGHT | DDS.DDSD.WIDTH | DDS.DDSD.PIXELFORMAT | DDS.DDSD.MIPMAPCOUNT).to_bytes(4, 'little')
		cnst += h.to_bytes(4, 'little')
		cnst += w.to_bytes(4, 'little')
		cnst += b'\x00\x00\x00\x00'
		cnst += d.to_bytes(4, 'little')
		cnst += mmc.to_bytes(4, 'little')
		cnst += b''.join(b'\x00' for _ in range(44))
		match rgb:
			case 'rgb':
				cnst += DDS_PIXELFORMAT.bytes_dx10_rgb()
			case 'rgba':
				cnst += DDS_PIXELFORMAT.bytes_dx10_rgba()
			case 'bgra':
				cnst += DDS_PIXELFORMAT.bytes_dx10_bgra()
			case _:
				cnst += DDS_PIXELFORMAT.bytes_dx10()
		cnst += caps1.to_bytes(4, 'little')
		cnst += caps2.to_bytes(4, 'little')
		cnst += b''.join(b'\x00' for _ in range(12))
		return cls.from_buffer_copy(cnst)

	@classmethod
	def from_stream(cls, stream: Stream) -> "DDS_HEADER":
		"""Create a `Header` from a stream, reading 124 bytes total."""
		return cls.from_buffer_copy(stream[124])

	@classmethod
	def from_fields(cls, flags: int, ddspf: DDS_PIXELFORMAT, mipMapCount: int, pitchOrLinearSize: int, height: int, width: int, depth: int,
	                caps1: int = 0, caps2: int = 0, caps3: int = 0, caps4: int = 0) -> "DDS_HEADER":
		"""Create a `Header` from the component fields."""
		init_buffer = bytearray(b'\x7C\x00\x00\x00') + b''.join(x.to_bytes(4, 'little') for x in [flags, height, width, pitchOrLinearSize, depth, mipMapCount]) + (b'\x00' * 44)
		init_buffer += bytes(ddspf) + b''.join(x.to_bytes(4, 'little') for x in [caps1, caps2, caps3, caps4]) + (b'\x00' * 4)
		return cls.from_buffer_copy(init_buffer)
	
	def dict(self):
		return {
			"dwSize": self.dwSize,
			"dwFlags": self.dwFlags,
			"dwHeight": self.dwHeight,
			"dwWidth": self.dwWidth,
			"dwPitchOrLinearSize": self.dwPitchOrLinearSize,
			"dwDepth": self.dwDepth,
			"dwMipMapCount": self.dwMipMapCount,
			"ddspf": self.ddspf.dict(),
			"dwCaps": [x.name for x in self.dwCaps],
			"dwCaps2": [x.name for x in self.dwCaps2],
			"dwCaps3": [x.name for x in self.dwCaps3],
		}
	

class DDS_HEADER_DXT10(ctypes.Structure):
	_fields_ = [
		("_dxgiFormat",         ctypes.c_uint32),
		("_resourceDimension",  ctypes.c_uint32),
		("_miscFlag",           ctypes.c_uint32),
		("_arraySize",          ctypes.c_uint32),
		("_miscFlags2",         ctypes.c_uint32),
	]
	_dxgiFormat: int
	_resourceDimension: int
	_miscFlag: int
	_arraySize: int
	_miscFlags2: int
	
	# --- Property Methods
	
	@property
	def arraySize(self) -> int:
		"""The number of elements in the array."""
		return self._arraySize
	
	# --- Cached Property Methods
	
	@cached_property
	def dxgiFormat(self) -> DXGI.DXGI_FORMAT:
		"""The surface pixel format enum."""
		return DXGI.DXGI_FORMAT(value=self._dxgiFormat)
	
	@cached_property
	def resourceDimension(self) -> D3D10.D3D10_RESOURCE_DIMENSION:
		"""Identifies the type of resource."""
		return D3D10.D3D10_RESOURCE_DIMENSION(value=self._resourceDimension)
	
	@cached_property
	def miscFlag(self) -> D3D10.D3D10_RESOURCE_MISC_FLAG:
		"""Identifies other, less common options for resources."""
		return D3D10.D3D10_RESOURCE_MISC_FLAG(value=self._miscFlag)
	
	@cached_property
	def miscFlags2(self) -> D3D10.D3D10_RESOURCE_miscFlags2:
		"""Contains additional metadata (formerly was reserved). The lower 3 bits indicate the alpha mode of the associated resource. The upper 29 bits are reserved and are typically 0."""
		return D3D10.D3D10_RESOURCE_miscFlags2(value=self._miscFlags2)
	
	# --- Class Methods
	
	@classmethod
	def from_stream(cls, stream: Stream) -> "DDS_HEADER_DXT10":
		"""Create a `Header_DXT10` from a stream, reading 20 bytes total."""
		return cls.from_buffer_copy(stream[20])

	@classmethod
	def from_fields(cls, dxgiFormat: int, resourceDimension: int, miscFlag: int, arraySize: int, miscFlags2: int) -> "DDS_HEADER_DXT10":
		"""Create a `Header_DXT10` from the component fields."""
		return cls.from_buffer_copy(b''.join(x.to_bytes(4, 'little') for x in [dxgiFormat, resourceDimension, miscFlag, arraySize, miscFlags2]))


class DDS_DX10_FILE(ctypes.Structure):
	"""https://github.com/microsoft/DirectXTex/blob/main/DirectXTex/DDS.h"""
	_fields_ = [
		("header", DDS_HEADER),
		("header_dx10", DDS_HEADER_DXT10)
	]
	
	header: DDS_HEADER
	header_dx10: DDS_HEADER_DXT10




class DDS_FILEHEAD(ctypes.Structure):
	"""https://github.com/microsoft/DirectXTex/blob/main/DirectXTex/DDS.h"""
	
	class _FHU(ctypes.Union):
		_fields_ = [("header10", DDS_HEADER_DXT10), ("_empty", ctypes.c_byte * 20)]  # type: ignore
		header10: DDS_HEADER_DXT10
	_fields_ = [
		("_dwMagic",    ctypes.c_uint32),
	    ("_header", DDS_HEADER),
	    ("_header10u",  _FHU)
	]
	_dwMagic: int
	_header: DDS_HEADER
	_header10u: _FHU
	
	@property
	def header(self) -> DDS_HEADER:
		return self._header
	
	@cached_property
	def dwMagic(self) -> str:
		return self._dwMagic.to_bytes(4, 'little').decode()
	
	@cached_property
	def is_dx10(self) -> bool:
		return self.header.ddspf.dwFourCC == "DX10"
	
	@cached_property
	def header10(self) -> DDS_HEADER_DXT10 | None:
		return self._header10u.header10 if self.is_dx10 else None
	
	
	# --- Class Methods
	
	@classmethod
	def from_stream(cls, stream: Stream) -> "DDS_FILEHEAD":
		"""Create a `File_Header` from a stream, reading 128 or 148 bytes."""
		new = cls.from_buffer_copy(stream[148])
		if new.header10 is None:
			stream.seek(-20, 1)
		return new
	
	@classmethod
	def from_data(cls, byets: bytes) -> "DDS_FILEHEAD":
		return cls.from_buffer_copy(byets)
	
	# --- Static Methods
	
	@staticmethod
	def dds_quick_type_read(stream: Stream) -> str:
		pxfmt = stream.string(3)
		if pxfmt == 'DDS':
			stream.seek(128)
			pxfmt = DXGI.DXGI_FORMAT(value=int(stream)).name
		return pxfmt
	
	
	# TODO Legacy functions, reformat
	
	@cached_property
	def type(self) -> DDSTextureType:
		return DDSTextureType(value=(self.is_array << 1) + self.is_cube)
	
	@cached_property
	def surface_count(self) -> int:
		return max(1, self.header10.arraySize) * (6 if self.is_cube else 1)
	
	@cached_property
	def is_array(self) -> bool:
		return self.header10.arraySize > 1
	
	@cached_property
	def is_cube(self) -> bool:
		return bool(self.header.dwCaps2 & self.header.dwCaps2.CUBEMAP)
	
	def dict(self):
		return self.header.dict()
	
	def alleged_pitch(self):
		if self.header10 is not None:
			if "BC1" in self.header10.dxgiFormat.name or "BC4" in self.header10.dxgiFormat.name:
				return max(1.0, ((self.header.dwWidth + 3) / 4)) * 8
			elif "BC" in self.header10.dxgiFormat.name:
				return max(1.0, ((self.header.dwWidth + 3) / 4)) * 16
			elif self.header10.dxgiFormat in [
				DXGI.DXGI_FORMAT.R8G8_B8G8_UNORM,
				DXGI.DXGI_FORMAT.G8R8_G8B8_UNORM
			]:
				return ((self.header.dwWidth+1) >> 1) * 4
			else:
				return (self.header.dwWidth * self.bpp + 7 ) / 8
		elif self.header.ddspf.dwFourCC == 'DXT1':
			return max(1.0, ((self.header.dwWidth + 3) / 4)) * 8
		else:
			return (self.header.dwWidth * self.bpp + 7) / 8
		
				
	
	
	
	
	@property
	def internal_pitch(self):
		# https://learn.microsoft.com/en-us/windows/win32/direct3d9/width-vs--pitch
		comp_pitch = self.compute_pitch(self.header.dwWidth)
		return f"{self.header.dwPitchOrLinearSize == comp_pitch} ({self.header.dwPitchOrLinearSize} vs {comp_pitch})"
	
	@cached_property
	def bpp(self):
		bpp = self.header.dwPitchOrLinearSize // self.header.dwWidth
		if not self.header.dwFlags.PITCH in self.header.dwFlags:
			bpp = bpp // self.header.dwHeight
		return bpp
	
	@cached_property
	def get_cpp_bpe(self):
		"""https://github.com/microsoft/DXUT/blob/main/Core/DDSTextureLoader.cpp"""
		if self.format.bcmp:
			return self.format.bits * 2
		elif self.format.packed or self.format.planar:
			return self.format.bits // 8
		else:
			return 0
	
	# https://learn.microsoft.com/en-us/windows/win32/direct3d10/d3d10-graphics-programming-guide-resources-block-compression#bc5
	# https://learn.microsoft.com/en-us/windows/win32/direct3d11/overviews-direct3d-11-resources-textures-intro
	# https://learn.microsoft.com/en-us/windows/win32/api/d3d11/ns-d3d11-d3d11_texture2d_desc
	
	# https://github.com/matyalatte/Blender-DDS-Addon/blob/main/addons/blender_dds_addon/directx/dds.py#L423
	# https://github.com/python-pillow/Pillow/blob/58e48745cc7b6c6f7dd26a50fe68d1a82ea51562/src/PIL/DdsImagePlugin.py#L331
	
	# https://github.com/microsoft/DXUT/blob/main/Core/DDSTextureLoader.cpp
	
	def dds_tex_sizedict(self):
		"""https://learn.microsoft.com/en-us/windows/win32/direct3ddds/dds-file-layout-for-textures"""
		
		def sizecalc(width, height):
			if self.format.bcmp:
				width = max(1, (width + 3) // 4) * 4  # aligned
				height = max(1, (height + 3) // 4) * 4  # aligned
			return {'w': width, 'h': height, 'bits_per_pixel': self.format.bits, 's': (width * height * self.format.bits) // 8}
		
		sizedict = {}
		w = self.header.dwWidth
		h = self.header.dwHeight
		for x in range(self.header.dwMipMapCount):
			sizedict[x] = sizecalc(w, h)
			w = w // 2
			h = h // 2
		return sizedict
	
	def compute_pitch(self, width):
		if self.format.bcmp:
			return int(max(1, ((width + 3) / 4)) * self.get_cpp_bpe)
		elif self.format.packed:
			return ((width + 1) >> 1) * 4
		else:
			return int((width * self.format.bits + 7) / 8)
	
	# https://github.com/matyalatte/Blender-DDS-Addon/blob/main/addons/blender_dds_addon/directx/dds.py#L423
	def get_sizes(self):
		sizedict = {}
		m_offset = self.eoh
		s_offset = self.eoh
		for i in range(self.surface_count):
			width = self.header.dwWidth
			height = self.header.dwHeight
			s_size = self.header.dwPitchOrLinearSize * (1 if self.format.bcmp else height)
			
			for ii in range(self.header.dwMipMapCount):
				pitch = self.compute_pitch(width)
				if self.format.bcmp:
					m_size = math.ceil(width / 4) * math.ceil(height / 4) * self.get_cpp_bpe
					rowBytes = (width + 3) // 4 * self.get_cpp_bpe
					numRows = (height + 3) // 4
				
				else:
					m_size = width * height * self.get_cpp_bpe
					rowBytes = ((width * self.format.bits) + 7) // 8  # round up to nearest byte
					numRows = height
				
				sizedict[f"{i}:{ii}"] = {'wxh'     : f"{width}x{height}", 'pitch': pitch, 'm_offset': m_offset, 'm_size': m_size, 's_offset': s_offset, 's_size': s_size,
				                         'numBytes': rowBytes * numRows, 'rowBytes': rowBytes, 'numRows': numRows}
				
				m_offset += m_size
				s_offset += s_size
				width = width // 2
				height = height // 2
				s_size = max(s_size // 4, 8)
		return sizedict
	
	def CPP_GetSurfaceInfo(self, width: int, height: int) -> tuple[int, int, int]:
		"""https://github.com/microsoft/DXUT/blob/main/Core/DDSTextureLoader.cpp"""
		if self.format.bcmp:
			rowBytes = (max(1, (width + 3) // 4) if width > 0 else 0) * self.get_cpp_bpe
			numRows = max(1, (height + 3) // 4) if height > 0 else 0
			numBytes = rowBytes * numRows
		else:
			rowBytes = (width * self.format.bits + 7) >> 3  # round up to nearest byte
			numRows = height
			numBytes = rowBytes * numRows
		
		return numBytes, rowBytes, numRows
	
	
	
