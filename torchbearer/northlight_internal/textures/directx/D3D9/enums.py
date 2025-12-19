from __future__ import annotations
from enum import IntEnum

__all__ = [
	"D3DSAMPLERSTATETYPE",
	"D3DTEXTUREFILTERTYPE",
	"D3DRESOURCETYPE",
	"D3DTEXTUREADDRESS",
	"D3DFMT"
]

# https://github.com/apitrace/dxsdk/blob/master/Include/d3d9types.h


class D3DSAMPLERSTATETYPE(IntEnum):
	"""`D3DSAMPLERSTATETYPE <https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dsamplerstatetype>`__ (D3DSAMP) enumeration

	Sampler states define texture sampling operations such as texture addressing and texture filtering. Some sampler states set-up vertex processing, and some set-up pixel processing.
	"""
	
	ADDRESSU = 1
	"""Texture-address mode for the u coordinate. The default is D3DTADDRESS_WRAP. For more information, see `D3DTEXTUREADDRESS <https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dtextureaddress>`__."""
	
	ADDRESSV = 2
	"""Texture-address mode for the v coordinate. The default is D3DTADDRESS_WRAP. For more information, see `D3DTEXTUREADDRESS <https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dtextureaddress>`__."""
	
	ADDRESSW = 3
	"""Texture-address mode for the w coordinate. The default is D3DTADDRESS_WRAP. For more information, see `D3DTEXTUREADDRESS <https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dtextureaddress>`__."""
	
	BORDERCOLOR = 4
	"""Border color or type D3DCOLOR. The default color is 0x00000000."""
	
	MAGFILTER = 5
	"""Magnification filter of type D3DTEXTUREFILTERTYPE. The default value is D3DTEXF_POINT."""
	
	MINFILTER = 6
	"""Minification filter of type D3DTEXTUREFILTERTYPE. The default value is D3DTEXF_POINT."""
	
	MIPFILTER = 7
	"""Mipmap filter to use during minification. See D3DTEXTUREFILTERTYPE. The default value is D3DTEXF_NONE."""
	
	MIPMAPLODBIAS = 8
	"""Mipmap level-of-detail bias. The default value is zero."""
	
	MAXMIPLEVEL = 9
	"""level-of-detail index of largest map to use. Values range from 0 to (n - 1) where 0 is the largest. The default value is zero."""
	
	MAXANISOTROPY = 10
	"""DWORD maximum anisotropy. Values range from 1 to the value that is specified in the MaxAnisotropy member of the D3DCAPS9 structure. The default value is 1."""
	
	SRGBTEXTURE = 11
	"""Gamma correction value. The default value is 0, which means gamma is 1.0 and no correction is required. Otherwise, this value means that the sampler should assume gamma of 2.2 on the content and convert it to linear (gamma 1.0) before presenting it to the pixel shader."""
	
	ELEMENTINDEX = 12
	"""When a multielement texture is assigned to the sampler, this indicates which element index to use. The default value is 0."""
	
	DMAPOFFSET = 13
	"""Vertex offset in the presampled displacement map. This is a constant used by the tessellator, its default value is 0."""


class D3DTEXTUREFILTERTYPE(IntEnum):
	"""`D3DTEXTUREFILTERTYPE <https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dtexturefiltertype>`__ (D3DTEXF) enumeration

	Defines texture filtering modes for a texture stage.

	D3DTEXTUREFILTERTYPE is used by IDirect3DDevice9::SetSamplerState along with D3DSAMPLERSTATETYPE to define texture filtering modes for a texture stage.

	To check if a format supports texture filter types other than D3DTEXF_POINT (which is always supported), call IDirect3D9::CheckDeviceFormat with D3DUSAGE_QUERY_FILTER.

	Set a texture stage's magnification filter by calling IDirect3DDevice9::SetSamplerState with the D3DSAMP_MAGFILTER value as the second parameter and one member of this enumeration as the third parameter.

	Set a texture stage's minification filter by calling IDirect3DDevice9::SetSamplerState with the D3DSAMP_MINFILTER value as the second parameter and one member of this enumeration as the third parameter.

	Set the texture filter to use between-mipmap levels by calling IDirect3DDevice9::SetSamplerState with the D3DSAMP_MIPFILTER value as the second parameter and one member of this enumeration as the third parameter.

	Not all valid filtering modes for a device will apply to volume maps. In general, D3DTEXF_POINT and D3DTEXF_LINEAR magnification filters will be supported for volume maps. If D3DPTEXTURECAPS_MIPVOLUMEMAP is set, then the D3DTEXF_POINT mipmap filter and D3DTEXF_POINT and D3DTEXF_LINEAR minification filters will be supported for volume maps. The device may or may not support the D3DTEXF_LINEAR mipmap filter for volume maps. Devices that support anisotropic filtering for 2D maps do not necessarily support anisotropic filtering for volume maps. However, applications that enable anisotropic filtering will receive the best available filtering (probably linear) if anisotropic filtering is not supported.
	"""
	
	NONE = 0
	"""When used with D3DSAMP_MIPFILTER, disables mipmapping."""
	
	POINT = 1
	"""When used with D3DSAMP_ MAGFILTER or D3DSAMP_MINFILTER, specifies that point filtering is to be used as the texture magnification or minification filter respectively. When used with D3DSAMP_MIPFILTER, enables mipmapping and specifies that the rasterizer chooses the color from the texel of the nearest mip level."""
	
	LINEAR = 2
	"""When used with D3DSAMP_ MAGFILTER or D3DSAMP_MINFILTER, specifies that linear filtering is to be used as the texture magnification or minification filter respectively. When used with D3DSAMP_MIPFILTER, enables mipmapping and trilinear filtering; it specifies that the rasterizer interpolates between the two nearest mip levels."""
	
	ANISOTROPIC = 3
	"""When used with D3DSAMP_ MAGFILTER or D3DSAMP_MINFILTER, specifies that anisotropic texture filtering used as a texture magnification or minification filter respectively. Compensates for distortion caused by the difference in angle between the texture polygon and the plane of the screen. Use with D3DSAMP_MIPFILTER is undefined."""
	
	PYRAMIDALQUAD = 6
	"""A 4-sample tent filter used as a texture magnification or minification filter. Use with D3DSAMP_MIPFILTER is undefined."""
	
	GAUSSIANQUAD = 7
	"""A 4-sample Gaussian filter used as a texture magnification or minification filter. Use with D3DSAMP_MIPFILTER is undefined."""
	
	CONVOLUTIONMONO = 8
	"""Convolution filter for monochrome textures. See D3DFMT_A1."""


class D3DRESOURCETYPE(IntEnum):
	"""Defines resource types."""
	SURFACE = 1
	"""Surface resource."""
	
	VOLUME = 2
	"""Volume resource."""
	
	TEXTURE = 3
	"""Texture resource."""
	
	VOLUMETEXTURE = 4
	"""Volume texture resource."""
	
	CUBETEXTURE = 5
	"""Cube texture resource."""
	
	VERTEXBUFFER = 6
	"""Vertex buffer resource."""
	
	INDEXBUFFER = 7
	"""Index buffer resource."""


class D3DTEXTUREADDRESS(IntEnum):
	"""Defines constants that describe the supported texture-addressing modes."""
	WRAP = 1
	"""Tile the texture at every integer junction. For example, for u values between 0 and 3, the texture is repeated three times; no mirroring is performed."""
	
	MIRROR = 2
	"""Similar to D3DTADDRESS_WRAP, except that the texture is flipped at every integer junction. For u values between 0 and 1, for example, the texture is addressed normally; between 1 and 2, the texture is flipped (mirrored); between 2 and 3, the texture is normal again; and so on."""
	
	CLAMP = 3
	"""Texture coordinates outside the range [0.0, 1.0] are set to the texture color at 0.0 or 1.0, respectively."""
	
	BORDER = 4
	"""Texture coordinates outside the range [0.0, 1.0] are set to the border color."""
	
	MIRRORONCE = 5
	"""Similar to D3DTADDRESS_MIRROR and D3DTADDRESS_CLAMP. Takes the absolute value of the texture coordinate (thus, mirroring around 0), and then clamps to the maximum value. The most common usage is for volume textures, where support for the full D3DTADDRESS_MIRRORONCE texture-addressing mode is not necessary, but the data is symmetric around the one axis."""


class D3DFMT(IntEnum):
	"""
	Defines the various types of surface formats. There are several types of formats:

	`Buffer Formats`
		Depth, stencil, vertex, and index buffers each have unique formats.

		All depth-stencil formats except **D16_LOCKABLE** indicate no particular bit ordering per pixel, and the driver is allowed to consume more than the indicated number of bits-per-depth channel (but not stencil channel).

	`DXTn Compressed Texture Formats`
		The runtime will not allow an application to create a surface using a DXTn format unless the surface dimensions are multiples of 4.
		This applies to offscreen-plain surfaces, render targets, 2D textures, cube textures, and volume textures.

	`Floating-Point Formats`
		These flags are used for floating-point surface formats. These 16-bits-per-channel formats are also known as s10e5 formats.

	`FOURCC Formats`
		Data in a FOURCC format is compressed data.

	`IEEE Formats`
		These flags are used for floating-point surface formats. These 32-bits-per-channel formats are also known as s23e8 formats.

	`Mixed Formats`
		Data in mixed formats can contain a combination of unsigned data and signed data.

	`Signed Formats`
		Data in a signed format can be both positive and negative. Signed formats use combinations of (U), (V), (W), and (Q) data.

	`Unsigned Formats`
		Data in an unsigned format must be positive. Unsigned formats use combinations of (R)ed, (G)reen, (B)lue, (A)lpha, (L)uminance, and (P)alette data. Palette data is also referred to as color indexed data because the data is used to index a color palette.

	`Other Formats`
		This flag is used for undefined formats.

	All formats are listed from left to right, most-significant bit to least-significant bit.
	For example, **ARGB** is ordered from the most-significant bit channel A (alpha), to the least-significant bit channel B (blue).
	When traversing surface data, the data is stored in memory from least-significant bit to most-significant bit, which means that the channel order in memory is from least-significant bit (blue) to most-significant bit (alpha).

	The default value for formats that contain undefined channels (**G16R16**, **A8**, and so on) is 1. The only exception is the A8 format, which is initialized to 000 for the three color channels.

	The order of the bits is from the most significant byte first, so **A8L8** indicates that the high byte of this 2-byte format is alpha.
	**D16** indicates a 16-bit integer value and an application-lockable surface.

	Pixel formats have been chosen to enable the expression of hardware-vendor-defined extension formats, as well as to include the well-established FOURCC method.
	The set of formats understood by the Direct3D runtime is defined by **D3DFORMAT**.

	Note that formats are supplied by independent hardware vendors (IHVs) and many **FOURCC** codes are not listed.
	The formats in this enumeration are unique in that they are sanctioned by the runtime, meaning that the reference rasterizer will operate on all these types.
	IHV-supplied formats will be supported by the individual IHVs on a card-by-card basis.
    """
	
	UNKNOWN = 0
	"""(Other Format) Surface format is unknown"""
	
	R8G8B8 = 20
	"""(Unsigned Format) 24-bit RGB pixel format with 8 bits per channel."""
	
	A8R8G8B8 = 21
	"""(Unsigned Format) 32-bit ARGB pixel format with alpha, using 8 bits per channel."""
	
	X8R8G8B8 = 22
	"""(Unsigned Format) 32-bit RGB pixel format, where 8 bits are reserved for each color."""
	
	R5G6B5 = 23
	"""(Unsigned Format) 16-bit RGB pixel format with 5 bits for red, 6 bits for green, and 5 bits for blue."""
	
	X1R5G5B5 = 24
	"""(Unsigned Format) 16-bit pixel format where 5 bits are reserved for each color."""
	
	A1R5G5B5 = 25
	"""(Unsigned Format) 16-bit pixel format where 5 bits are reserved for each color and 1 bit is reserved for alpha."""
	
	A4R4G4B4 = 26
	"""(Unsigned Format) 16-bit ARGB pixel format with 4 bits for each channel."""
	
	R3G3B2 = 27
	"""(Unsigned Format) 8-bit RGB texture format using 3 bits for red, 3 bits for green, and 2 bits for blue."""
	
	A8 = 28
	"""(Unsigned Format) 8-bit alpha only."""
	
	A8R3G3B2 = 29
	"""(Unsigned Format) 16-bit ARGB texture format using 8 bits for alpha, 3 bits each for red and green, and 2 bits for blue."""
	
	X4R4G4B4 = 30
	"""(Unsigned Format) 16-bit RGB pixel format using 4 bits for each color."""
	
	A2B10G10R10 = 31
	"""(Unsigned Format) 32-bit pixel format using 10 bits for each color and 2 bits for alpha."""
	
	A8B8G8R8 = 32
	"""(Unsigned Format) 32-bit ARGB pixel format with alpha, using 8 bits per channel."""
	
	X8B8G8R8 = 33
	"""(Unsigned Format) 32-bit RGB pixel format, where 8 bits are reserved for each color."""
	
	G16R16 = 34
	"""(Unsigned Format) 32-bit pixel format using 16 bits each for green and red."""
	
	A2R10G10B10 = 35
	"""(Unsigned Format) 32-bit pixel format using 10 bits each for red, green, and blue, and 2 bits for alpha."""
	
	A16B16G16R16 = 36
	"""(Unsigned Format) 64-bit pixel format using 16 bits for each component."""
	
	A8P8 = 40
	"""(Unsigned Format) 8-bit color indexed with 8 bits of alpha."""
	
	P8 = 41
	"""(Unsigned Format) 8-bit color indexed."""
	
	L8 = 50
	"""(Unsigned Format) 8-bit luminance only."""
	
	A8L8 = 51
	"""(Unsigned Format) 16-bit using 8 bits each for alpha and luminance."""
	
	A4L4 = 52
	"""(Unsigned Format) 8-bit using 4 bits each for alpha and luminance."""
	
	L16 = 81
	"""(Unsigned Format) 16-bit luminance only."""
	
	A1 = 118
	"""(Unsigned Format) 1-bit monochrome. This flag is available in Direct3D 9Ex only."""
	
	A2B10G10R10_XR_BIAS = 119
	"""(Unsigned Format) 2.8-biased fixed point. This flag is available in Direct3D 9Ex only."""
	
	BINARYBUFFER = 199
	"""(Unsigned Format) Binary format indicating that the data has no inherent type. This flag is available in Direct3D 9Ex only."""
	
	V8U8 = 60
	"""(Signed Format) 16-bit bump-map format using 8 bits each for u and v data."""
	
	Q8W8V8U8 = 63
	"""(Signed Format) 32-bit bump-map format using 8 bits for each channel."""
	
	V16U16 = 64
	"""(Signed Format) 32-bit bump-map format using 16 bits for each channel."""
	
	Q16W16V16U16 = 110
	"""(Signed Format) 64-bit bump-map format using 16 bits for each component."""
	
	CxV8U8 = 117
	"""(Signed Format) 16-bit normal compression format. The texture sampler computes the C channel from: ``C=sqrt(1-U²-V²)``."""
	
	L6V5U5 = 61
	"""(Mixed Format) 16-bit bump-map format with luminance using 6 bits for luminance, and 5 bits each for v and u."""
	
	X8L8V8U8 = 62
	"""(Mixed Format) 32-bit bump-map format with luminance using 8 bits for each channel."""
	
	A2W10V10U10 = 67
	"""(Mixed Format) 32-bit bump-map format using 2 bits for alpha and 10 bits each for w, v, and u."""
	
	R32F = 114
	"""(IEEE Format) 32-bit float format using 32 bits for the red channel."""
	
	G32R32F = 115
	"""(IEEE Format) 64-bit float format using 32 bits for the red channel and 32 bits for the green channel."""
	
	A32B32G32R32F = 116
	"""(IEEE Format) 128-bit float format using 32 bits for the each channel (alpha, blue, green, red)."""
	
	UYVY = int.from_bytes(b"UYVY", 'little')
	"""(FOURCC Format) UYVY format (PC98 compliance)"""
	
	YUY2 = int.from_bytes(b"YUY2", 'little')
	"""(FOURCC Format) YUY2 format (PC98 compliance)"""
	
	R8G8_B8G8 = int.from_bytes(b"RGBG", 'little')
	"""(FOURCC Format) A 16-bit packed RGB format analogous to UYVY (U0Y0, V0Y1, U2Y2, and so on).

	It requires a pixel pair in order to properly represent the color value.
	The first pixel in the pair contains 8 bits of green (in the low 8 bits) and 8 bits of red (in the high 8 bits).
	The second pixel contains 8 bits of green (in the low 8 bits) and 8 bits of blue (in the high 8 bits).
	Together, the two pixels share the red and blue components, while each has a unique green component (R0G0, B0G1, R2G2, and so on).
	The texture sampler does not normalize the colors when looking up into a pixel shader; they remain in the range of 0.0f to 255.0f.
	This is true for all programmable pixel shader models.
	For the fixed function pixel shader, the hardware should normalize to the 0.f to 1.f range and essentially treat it as the YUY2 texture.
	Hardware that exposes this format must have PixelShader1xMaxValue member of **D3DCAPS9** set to a value capable of handling that range.
	"""
	
	G8R8_G8B8 = int.from_bytes(b"GRGB", 'little')
	"""(FOURCC Format) A 16-bit packed RGB format analogous to YUY2 (Y0U0, Y1V0, Y2U2, and so on).

	It requires a pixel pair in order to properly represent the color value.
	The first pixel in the pair contains 8 bits of green (in the high 8 bits) and 8 bits of red (in the low 8 bits).
	The second pixel contains 8 bits of green (in the high 8 bits) and 8 bits of blue (in the low 8 bits).
	Together, the two pixels share the red and blue components, while each has a unique green component (G0R0, G1B0, G2R2, and so on).
	The texture sampler does not normalize the colors when looking up into a pixel shader; they remain in the range of 0.0f to 255.0f.
	This is true for all programmable pixel shader models.
	For the fixed function pixel shader, the hardware should normalize to the 0.f to 1.f range and essentially treat it as the YUY2 texture.
	Hardware that exposes this format must have the PixelShader1xMaxValue member of **D3DCAPS9** set to a value capable of handling that range.
	"""
	
	MULTI2_ARGB8 = int.from_bytes(b"MET1", 'little')
	"""(FOURCC Format) MultiElement texture (not compressed)"""
	
	D16_LOCKABLE = 70
	"""(Buffer Format) 16-bit z-buffer bit depth."""
	
	D32 = 71
	"""(Buffer Format) 32-bit z-buffer bit depth."""
	
	D15S1 = 73
	"""(Buffer Format) 16-bit z-buffer bit depth where 15 bits are reserved for the depth channel and 1 bit is reserved for the stencil channel."""
	
	D24S8 = 75
	"""(Buffer Format) 32-bit z-buffer bit depth using 24 bits for the depth channel and 8 bits for the stencil channel."""
	
	D24X8 = 77
	"""(Buffer Format) 32-bit z-buffer bit depth using 24 bits for the depth channel."""
	
	D24X4S4 = 79
	"""(Buffer Format) 32-bit z-buffer bit depth using 24 bits for the depth channel and 4 bits for the stencil channel."""
	
	D16 = 80
	"""(Buffer Format) 16-bit z-buffer bit depth."""
	
	D32F_LOCKABLE = 82
	"""(Buffer Format) A lockable format where the depth value is represented as a standard IEEE floating-point number."""
	
	D24FS8 = 83
	"""(Buffer Format) A non-lockable format that contains 24 bits of depth (in a 24-bit floating point format - 20e4) and 8 bits of stencil."""
	
	D32_LOCKABLE = 84
	"""(Buffer Format) A lockable 32-bit depth buffer. Differences between Direct3D 9 and Direct3D 9Ex: This flag is available in Direct3D 9Ex only."""
	
	S8_LOCKABLE = 85
	"""(Buffer Format) A lockable 8-bit stencil buffer. Differences between Direct3D 9 and Direct3D 9Ex: This flag is available in Direct3D 9Ex only."""
	
	VERTEXDATA = 100
	"""(Buffer Format) Describes a vertex buffer surface."""
	
	INDEX16 = 101
	"""(Buffer Format) 16-bit index buffer bit depth."""
	
	INDEX32 = 102
	"""(Buffer Format) 32-bit index buffer bit depth."""
	
	R16F = 111
	"""(Floating-Point Format) 16-bit float format using 16 bits for the red channel."""
	
	G16R16F = 112
	"""(Floating-Point Format) 32-bit float format using 16 bits for the red channel and 16 bits for the green channel."""
	
	A16B16G16R16F = 113
	"""(Floating-Point Format) 64-bit float format using 16 bits for the each channel (alpha, blue, green, red)."""
	
	DXT1 = int.from_bytes(b"DXT1", 'little')
	"""(DXTn) DXT1 compression texture format"""
	
	DXT2 = int.from_bytes(b"DXT2", 'little')
	"""(DXTn) DXT2 compression texture format"""
	
	DXT3 = int.from_bytes(b"DXT3", 'little')
	"""(DXTn) DXT3 compression texture format"""
	
	DXT4 = int.from_bytes(b"DXT4", 'little')
	"""(DXTn) DXT4 compression texture format"""
	
	DXT5 = int.from_bytes(b"DXT5", 'little')
	"""(DXTn) DXT5 compression texture format"""
	
	DX10 = int.from_bytes(b"DX10", 'little')
	"""(DXTn) DXTn compression texture format with a DX10 header that contains the DX10 format."""
	
	BC4S = int.from_bytes(b"BC4S", 'little')
	"""(DXTn) BC4 SNORM compression texture format"""
	
	BC4U = int.from_bytes(b"BC4U", 'little')
	"""(DXTn) BC4 UNORM compression texture format"""
	
	BC5S = int.from_bytes(b"BC5S", 'little')
	"""(DXTn) BC5 SNORM compression texture format"""
	
	BC5U = int.from_bytes(b"BC5U", 'little')
	"""(DXTn) BC5 UNORM compression texture format"""
	
	ATI1 = int.from_bytes(b"ATI1", 'little')
	"""(DXTn) BC4 compression texture format"""
	
	ATI2 = int.from_bytes(b"ATI2", 'little')
	"""(DXTn) BC5 compression texture format"""