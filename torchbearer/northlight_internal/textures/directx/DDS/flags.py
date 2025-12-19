from __future__ import annotations
from enum import IntFlag

__all__ = [
	"DDSD",
	"DDSCAPS",
	"DDSCAPS2",
	"DDSCAPS3",
	"DDPF"
]


class DDSD(IntFlag):
	"""Flags to indicate which members contain valid data."""
	CAPS = 0x00000001
	"""ddsCaps field is valid."""
	
	HEIGHT = 0x00000002
	"""dwHeight field is valid."""
	
	WIDTH = 0x00000004
	"""lPitch is valid."""
	
	PITCH = 0x00000008
	"""lPitch is valid."""
	
	BACKBUFFERCOUNT = 0x00000020
	"""dwBackBufferCount is valid."""
	
	ZBUFFERBITDEPTH = 0x00000040
	"""dwZBufferBitDepth is valid."""
	
	ALPHABITDEPTH = 0x00000080
	"""dwAlphaBitDepth is valid."""
	
	LPSURFACE = 0x00000800
	"""lpSurface is valid."""
	
	PIXELFORMAT = 0x00001000
	"""ddpfPixelFormat is valid."""
	
	CKDESTOVERLAY = 0x00002000
	"""ddckCKDestOverlay is valid."""
	
	CKDESTBLT = 0x00004000
	"""ddckCKDestBlt is valid."""
	
	CKSRCOVERLAY = 0x00008000
	"""ddckCKSrcOverlay is valid."""
	
	CKSRCBLT = 0x00010000
	"""ddckCKSrcBlt is valid."""
	
	MIPMAPCOUNT = 0x00020000
	"""dwMipMapCount is valid."""
	
	REFRESHRATE = 0x00040000
	"""dwRefreshRate is valid"""
	
	LINEARSIZE = 0x00080000
	"""dwLinearSize is valid"""
	
	TEXTURESTAGE = 0x00100000
	"""dwTextureStage is valid"""
	
	FVF = 0x00200000
	"""dwFVF is valid"""
	
	SRCVBHANDLE = 0x00400000
	"""dwSrcVBHandle is valid"""
	
	DEPTH = 0x00800000
	"""dwDepth is valid"""
	
	ALL = 0x00fff9ee
	"""All input fields are valid."""


class DDSCAPS(IntFlag):
	"""Specifies the complexity of the surfaces stored."""
	RESERVED1 = 0x00000001
	"""This bit is reserved. It should not be specified."""
	
	ALPHA = 0x00000002
	"""Indicates that this surface contains alpha-only information. (To determine if a surface is RGBA/YUVA, the pixel format must be interrogated.)"""
	
	BACKBUFFER = 0x00000004
	"""Indicates that this surface is a backbuffer."""
	
	COMPLEX = 0x00000008
	"""Indicates a complex surface structure is being described."""
	
	FLIP = 0x00000010
	"""Indicates that this surface is a part of a surface flipping structure."""
	
	FRONTBUFFER = 0x00000020
	"""Indicates that this surface is THE front buffer of a surface flipping structure."""
	
	OFFSCREENPLAIN = 0x00000040
	"""Indicates that this surface is any offscreen surface that is not an overlay, texture, zbuffer, front buffer, back buffer, or alpha surface."""
	
	OVERLAY = 0x00000080
	"""Indicates that this surface is an overlay."""
	
	PALETTE = 0x00000100
	"""Indicates that unique DirectDrawPalette objects can be created and attached to this surface."""
	
	PRIMARYSURFACE = 0x00000200
	"""Indicates that this surface is the primary surface."""
	
	RESERVED3 = 0x00000400
	"""This flag used to be DDSCAPS_PRIMARYSURFACELEFT, which is now obsolete."""
	
	SYSTEMMEMORY = 0x00000800
	"""Indicates that this surface memory was allocated in system memory"""
	
	TEXTURE = 0x00001000
	"""Indicates that this surface can be used as a 3D texture."""
	
	DEVICE3D = 0x00002000
	"""Indicates that a surface may be a destination for 3D rendering."""
	
	VIDEOMEMORY = 0x00004000
	"""Indicates that this surface exists in video memory."""
	
	VISIBLE = 0x00008000
	"""Indicates that changes made to this surface are immediately visible."""
	
	WRITEONLY = 0x00010000
	"""Indicates that only writes are permitted to the surface."""
	
	ZBUFFER = 0x00020000
	"""Indicates that this surface is a z buffer."""
	
	OWNDC = 0x00040000
	"""Indicates surface will have a DC associated long term."""
	
	LIVEVIDEO = 0x00080000
	"""Indicates surface should be able to receive live video."""
	
	HWCODEC = 0x00100000
	"""Indicates surface should be able to have a stream decompressed to it by the hardware."""
	
	MODEX = 0x00200000
	"""Surface is a ModeX surface."""
	
	MIPMAP = 0x00400000
	"""Indicates surface is one level of a mip-map."""
	
	RESERVED2 = 0x00800000
	"""This bit is reserved. It should not be specified."""
	
	ALLOCONLOAD = 0x04000000
	"""Indicates that memory for the surface is not allocated until the surface is loaded (via the Direct3D texture Load() function)."""
	
	VIDEOPORT = 0x08000000
	"""Indicates that the surface will recieve data from a video port."""
	
	LOCALVIDMEM = 0x10000000
	"""Indicates that a video memory surface is resident in true, local video memory rather than non-local video memory."""
	
	NONLOCALVIDMEM = 0x20000000
	"""Indicates that a video memory surface is resident in non-local video memory rather than true, local video memory."""
	
	STANDARDVGAMODE = 0x40000000
	"""Indicates that this surface is a standard VGA mode surface, and not a ModeX surface."""
	
	OPTIMIZED = 0x80000000
	"""Indicates that this surface will be an optimized surface."""


class DDSCAPS2(IntFlag):
	"""Additional detail about the surfaces stored."""
	RESERVED4 = 0x00000002
	"""This bit is reserved"""
	
	HINTDYNAMIC = 0x00000004
	"""Indicates to the driver that this surface will be locked very frequently (for procedural textures, dynamic lightmaps, etc)."""
	
	HINTSTATIC = 0x00000008
	"""Indicates to the driver that this surface can be re-ordered/retiled on load."""
	
	TEXTUREMANAGE = 0x00000010
	"""Indicates that the client would like this texture surface to be managed by the DirectDraw/Direct3D runtime."""
	
	RESERVED1 = 0x00000020
	"""These bits are reserved for internal use"""
	
	RESERVED2 = 0x00000040
	"""These bits are reserved for internal use"""
	
	OPAQUE = 0x00000080
	"""Indicates to the driver that this surface will never be locked again."""
	
	HINTANTIALIASING = 0x00000100
	"""Applications should set this bit at CreateSurface time to indicate that they intend to use antialiasing."""
	
	CUBEMAP = 0x00000200
	"""This flag is used at CreateSurface time to indicate that this set of surfaces is a cubic environment map"""
	
	CUBEMAP_POSITIVEX = 0x00000400
	""""""
	
	CUBEMAP_NEGATIVEX = 0x00000800
	""""""
	
	CUBEMAP_POSITIVEY = 0x00001000
	""""""
	
	CUBEMAP_NEGATIVEY = 0x00002000
	""""""
	
	CUBEMAP_POSITIVEZ = 0x00004000
	""""""
	
	CUBEMAP_NEGATIVEZ = 0x00008000
	""""""
	
	MIPMAPSUBLEVEL = 0x00010000
	"""This flag is an additional flag which is present on mipmap sublevels from DX7 onwards."""
	
	D3DTEXTUREMANAGE = 0x00020000
	"""This flag indicates that the texture should be managed by D3D only"""
	
	DONOTPERSIST = 0x00040000
	"""This flag indicates that the managed surface can be safely lost"""
	
	STEREOSURFACELEFT = 0x00080000
	"""This flag indicates that this surface is part of a stereo flipping chain"""
	
	VOLUME = 0x00200000
	"""Indicates that the surface is a volume."""
	
	NOTUSERLOCKABLE = 0x00400000
	"""Indicates that the surface may be locked multiple times by the application."""
	
	POINTS = 0x00800000
	"""Indicates that the vertex buffer data can be used to render points and point sprites."""
	
	RTPATCHES = 0x01000000
	"""Indicates that the vertex buffer data can be used to render rt pactches."""
	
	NPATCHES = 0x02000000
	"""Indicates that the vertex buffer data can be used to render n patches."""
	
	RESERVED3 = 0x04000000
	"""This bit is reserved for internal use"""
	
	DISCARDBACKBUFFER = 0x10000000
	"""Indicates that the contents of the backbuffer do not have to be preserved the contents of the backbuffer after they are presented."""
	
	ENABLEALPHACHANNEL = 0x20000000
	"""Indicates that all surfaces in this creation chain should be given an alpha channel."""
	
	EXTENDEDFORMATPRIMARY = 0x40000000
	"""Indicates that all surfaces in this creation chain is extended primary surface format."""
	
	ADDITIONALPRIMARY = 0x80000000
	"""Indicates that all surfaces in this creation chain is additional primary surface."""
	
	@classmethod
	def CUBEMAP_ALL(cls):
		return cls.CUBEMAP | cls.CUBEMAP_POSITIVEX | cls.CUBEMAP_NEGATIVEX | cls.CUBEMAP_POSITIVEY | cls.CUBEMAP_NEGATIVEY | cls.CUBEMAP_POSITIVEZ | cls.CUBEMAP_NEGATIVEZ


class DDSCAPS3(IntFlag):
	"""Further detail about the surfaces stored."""
	RESERVED1 = 0x00000100
	"""This bit is reserved for internal use"""
	
	RESERVED2 = 0x00000200
	"""This bit is reserved for internal use"""
	
	LIGHTWEIGHTMIPMAP = 0x00000400
	"""This indicates whether this surface has light-weight miplevels"""
	
	AUTOGENMIPMAP = 0x00000800
	"""This indicates that the mipsublevels for this surface are auto-generated"""
	
	DMAP = 0x00001000
	"""This indicates that the mipsublevels for this surface are auto-generated"""
	
	CREATESHAREDRESOURCE = 0x00002000
	"""This indicates that this surface is to be shared by processes"""
	
	READONLYRESOURCE = 0x00004000
	"""This indicates that this surface need to be initialized before being shared."""
	
	OPENSHAREDRESOURCE = 0x00008000
	"""This indicates that this surface is to share an existing video memory with another surface created with DDSCAPS3_CREATESHAREDRESOURCE"""


class DDPF(IntFlag):
	"""Values which indicate what type of data is in the surface."""
	ALPHAPIXELS = 0x00000001
	"""The surface has alpha channel information in the pixel format."""
	
	ALPHA = 0x00000002
	"""The pixel format contains alpha only information."""
	
	FOURCC = 0x00000004
	"""The FourCC code is valid."""
	
	PALETTEINDEXED4 = 0x00000008
	"""The surface is 4-bit color indexed."""
	
	PALETTEINDEXEDTO8 = 0x00000010
	"""The surface is indexed into a palette which stores indices into the destination surface's 8-bit palette."""
	
	PALETTEINDEXED8 = 0x00000020
	"""The surface is 8-bit color indexed."""
	
	RGB = 0x00000040
	"""The RGB data in the pixel format structure is valid."""
	
	COMPRESSED = 0x00000080
	"""The surface will accept pixel data in the format specified and compress it during the write."""
	
	RGBTOYUV = 0x00000100
	"""The surface will accept RGB data and translate it during the write to YUV data."""
	
	YUV = 0x00000200
	"""pixel format is YUV - YUV data in pixel format struct is valid."""
	
	ZBUFFER = 0x00000400
	"""pixel format is a z buffer only surface."""
	
	PALETTEINDEXED1 = 0x00000800
	"""The surface is 1-bit color indexed."""
	
	PALETTEINDEXED2 = 0x00001000
	"""The surface is 2-bit color indexed."""
	
	ZPIXELS = 0x00002000
	"""The surface contains Z information in the pixels"""
	
	STENCILBUFFER = 0x00004000
	"""The surface contains stencil information along with Z"""
	
	ALPHAPREMULT = 0x00008000
	"""Premultiplied alpha format -- the color components have been premultiplied by the alpha component."""
	
	LUMINANCE = 0x00020000
	"""Luminance data in the pixel format is valid."""
	
	BUMPLUMINANCE = 0x00040000
	"""Luminance data in the pixel format is valid."""
	
	BUMPDUDV = 0x00080000
	"""Bump map dUdV data in the pixel format is valid."""