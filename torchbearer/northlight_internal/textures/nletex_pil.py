from __future__ import annotations

import ctypes
from PIL import Image, ImageFile

"""
BCx	 FourCC     Channels	Description		    Alpha Type		    Bytes / Bits per 4x4 (16) pixels (Block Size)
1	 DXT1	    RGBA		1b/Opaque		    Premultiplied	    8	   64		    two 16-bit RGB 5:6:5 color values and a 4×4 two-bit lookup table
2	 DXT2	    RGBA		Explicit Alpha	    Premultiplied	    16	  128		    64 bits of alpha channel data (4 bits for each pixel), 64 bits of color data like DXT1
2	 DXT3	    RGBA		Explicit Alpha	    Not Premultiplied   16	  128		    64 bits of alpha channel data (4 bits for each pixel), 64 bits of color data like DXT1
3	 DXT4	    RGBA		Interpolated Alpha  Premultiplied	    16	  128		    64 bits of alpha channel data (two 8-bit alpha values and a 4×4 3-bit lookup table), 64 bits of color data like DXT1
3	 DXT5	    RGBA		Interpolated Alpha  Not Premultiplied   16	  128		    64 bits of alpha channel data (two 8-bit alpha values and a 4×4 3-bit lookup table), 64 bits of color data like DXT1
4	 ATI1 	    X		    Interpolated Grey   n/a				    8	   64		    two 16-bit float values and a 4×4 two-bit lookup table
5	 ATI2 	    XY		    Interpolated 2Chnl  n/a				    16	  128		    64 bits of color data like BC4 for each channel

For block-compressed formats, compute the pitch as:
	pitch (bits) = max(1,((width+3)/4)) * block-size

For R8G8_B8G8, G8R8_G8B8, legacy UYVY-packed, and legacy YUY2-packed formats, compute the pitch as:
	pitch (bits) = ((width+1) >> 1) * 4

For other formats, compute the pitch as:
	pitch (bits) = (width * bits-per-pixel + 7) / 8


predictions:
#   Cube	BPP		    Form Guess	    OpenAWE	    AWTools
0:  N	   4		    B8G8R8A8		N/A		    RGBA8_LUT
1:  N	   0.5/0.75	BC1 (DXT1)	        DXT1		GRAYSCALE_4BIT (Potentially swizzled?)
2:  ~	   4		    B8G8R8A8		N/A		    N/A
3:  N	   1		    BC3 (DXT5)	    DXT5		N/A
4:  ~	   4		    B8G8R8A8		RGBA8 LUT   RGBA_CUBE_DXT1
5:  ~	   0.5/0.75	BC1 (DXT1)	        DXT1		RGBA_DXT1
6:  ~	   4		    B8G8R8A8		RGBA16F	    RGBA8
7:  N	   1		    BC3 (DXT5)	    DXT5		RGBA_DXT3
8:  N	   4		    B8G8R8A8		RGBA8	    N/A
9:  N	   1		    BC3 (DXT5)	    DXT5		RGBA_DXT5
10: ?	   ?		    ?			    RGBA16F	    N/A
11: Y	   4		    maybe B8G8R8A8  N/A		    RGBA8_CUBE



possible definition lists:
0:	    DXT1	DXT1    DXT1	 DXT1
1:	    DXT3	DXT3    DXT3	 DXT3t
2:	    DXT5	DXT5    DXT5	 DXT5u
3:	    DXT2	DXT2    DXT2	 DXT3
4:	    DXT4	DXT4    DXT4	 DXT1t
5:	    BC4U	ATI1    BC4U	 DXT2
6:	    BC4S	BC4U    BC4S	 DXT4t
7:	    BC5U	BC4S    BC5U	 DXT5t
8:	    BC5S	ATI2    BC5S	 DXT1
9:	    ATI1	BC5U    ATI1	 DXT3t
10:	    ATI2	BC5S    ATI2	 DXT5t
11:	    BC6H	RGBG    RGBG	 DXT1
12:	    BC7L	GRGB    GRGB
13:	    BC7	    YUY2    YUY2
14:	    RGBG
15:	    GRGB
16:	    YUY2
17:	    UYVY


possible parameters lists:
m_type
m_filter
m_iWidth
m_iHeight
m_iDepth
m_iMipmapCount
m_iMipOffset
m_bIsTiled
m_bIsVideoTexture2
m_desc
m_fHighDetailStreamDistance
m_bUseTextureLOD
m_bUseNewTextureLOD
"""


__all__ = [
	'register'
]


class NorthlightTex_Header(ctypes.LittleEndianStructure):
	_fields_ = [
		('type', ctypes.c_uint32),
		('form', ctypes.c_uint32),
		('dimw', ctypes.c_uint32),
		('dimh', ctypes.c_uint32),
		('dimd', ctypes.c_uint32),
		('mmap', ctypes.c_uint32),
		('fltr', ctypes.c_uint32),
		('unkw', ctypes.c_uint32),
	]
	type: int   # 0: 2D, 1: 3D, 2: Cube
	form: int   # integer, 0-11
	dimw: int   # width
	dimh: int   # height
	dimd: int   # depth
	mmap: int   # mipmaps
	fltr: int   # filter, meaning unknown
	unkw: int   # unknown, always 0
	
	def __repr__(self):
		return f"<NorthlightTex_Header(type={self.type}, form={self.form}, dimw={self.dimw}, dimh={self.dimh}, dimd={self.dimd}, mmap={self.mmap}, fltr={self.fltr}, unkw={self.unkw})"
	
	def dict(self):
		return {
			"type": self.type,
			"form": self.form,
			"dimw": self.dimw,
			"dimh": self.dimh,
			"dimd": self.dimd,
			"mmap": self.mmap,
			"fltr": self.fltr,
			"unkw": self.unkw,
		}

class NorthlightTex_ImageFile(ImageFile.ImageFile):
	format = "nletex"
	format_description = "Northlight TEX file"
	
	def _open(self) -> None:
		header = NorthlightTex_Header.from_buffer_copy(self.fp.read(32))
		self._size = (header.dimw, header.dimh)
		self.info['TEX Header'] = header.dict()
		# not sure what the differences are yet, not alpha premultiplication
		
		match header.form:
			case 0 | 2 | 4 | 6 | 8: # not sure what the differences are yet, gamma maybe?
				self._mode = "RGBA"
				self.tile = [("nletex", (0, 0) + self.size, 32, (32, 'BGRA'))] # type: ignore
			case 1 | 5:
				self._mode = "RGBA"
				self.tile = [("bcn", (0, 0) + self.size, 32, (1, "BC1"))] # type: ignore
			case 3 | 7 | 9:
				self._mode = "RGBA"
				self.tile = [("bcn", (0, 0) + self.size, 32, (3, "BC3"))] # type: ignore
			case 11: # not sure yet exactly, definitely not RGBA8. All cubes and random names.
				self._mode = "RGBA"
				self.tile = [("nletex", (0, 0) + self.size, 32, (32, 'BGRA'))] # type: ignore
			case _:
				raise SyntaxError(f"Invalid form value: {header.form}")


class NorthlightTex_Decoder(ImageFile.PyDecoder):
	_pulls_fd = True
	
	def decode(self, buffer: bytes | Image.SupportsArrayInterface) -> tuple[int, int]:
		bitlength, mode = self.args
		bytelength = bitlength // 8
		assert self.fd is not None
		data = bytearray()
		while len(data) < self.state.xsize * self.state.ysize * bytelength:
			tuplet = self.fd.read(bytelength//4), self.fd.read(bytelength//4), self.fd.read(bytelength//4), self.fd.read(bytelength//4)
			data += tuplet[mode.index('R')]
			data += tuplet[mode.index('G')]
			data += tuplet[mode.index('B')]
			data += tuplet[mode.index('A')]
		self.set_as_raw(data)
		return -1, 0

def register():
	Image.register_open(NorthlightTex_ImageFile.format, NorthlightTex_ImageFile, lambda prefix: not (prefix.startswith(b"DDS") or prefix.startswith(b"KB2") or prefix.startswith(b"BNK")))
	Image.register_decoder("nletex", NorthlightTex_Decoder)
	Image.register_extension(NorthlightTex_ImageFile.format, ".tex")