from __future__ import annotations
from enum import IntFlag

__all__ = [
	"D3D10_RESOURCE_MISC_FLAG"
]

class D3D10_RESOURCE_MISC_FLAG(IntFlag):
	"""Identifies other, less common options for resources."""
	GENERATE_MIPS = 0x00000001
	"""Enables an application to call ID3D10Device::GenerateMips on a texture resource."""
	
	SHARED = 0x00000002
	"""Enables the sharing of resource data between two or more Direct3D devices."""
	
	TEXTURECUBE = 0x00000004
	"""Enables an application to create a cube texture from a Texture2DArray that contains 6 textures."""
	
	SHARED_KEYEDMUTEX = 0x00000010
	"""Enables the resource created to be synchronized using the IDXGIKeyedMutex::AcquireSync and ReleaseSync APIs."""
	
	GDI_COMPATIBLE = 0x00000020
	"""Enables a surface to be used for GDI interoperability."""

