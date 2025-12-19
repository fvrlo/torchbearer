from __future__ import annotations
from enum import IntEnum

__all__ = [
	"D3D10_RESOURCE_DIMENSION",
	"D3D10_RESOURCE_miscFlags2"
]

class D3D10_RESOURCE_DIMENSION(IntEnum):
	"""Identifies the type of resource."""
	UNKNOWN                         = 0; """Resource is of unknown type."""
	BUFFER                          = 1; """Resource is a buffer."""
	TEXTURE1D                       = 2; """Resource is a 1D texture."""
	TEXTURE2D                       = 3; """Resource is a 2D texture."""
	TEXTURE3D                       = 4; """Resource is a 3D texture."""


class D3D10_RESOURCE_miscFlags2(IntEnum):
	"""Contains additional metadata (formerly was reserved). The lower 3 bits indicate the alpha mode of the associated resource. The upper 29 bits are reserved and are typically 0."""
	DDS_ALPHA_MODE_UNKNOWN = 0
	"""Alpha channel content is unknown. This is the value for legacy files, which typically is assumed to be 'straight' alpha."""
	
	DDS_ALPHA_MODE_STRAIGHT = 1
	"""Any alpha channel content is presumed to use straight alpha."""
	
	DDS_ALPHA_MODE_PREMULTIPLIED = 2
	"""Any alpha channel content is using premultiplied alpha. The only legacy file formats that indicate this information are 'DX2' and 'DX4'."""
	
	DDS_ALPHA_MODE_OPAQUE = 3
	"""Any alpha channel content is all set to fully opaque."""
	
	DDS_ALPHA_MODE_CUSTOM = 4
	"""Any alpha channel content is being used as a 4th channel and is not intended to represent transparency (straight or premultiplied)."""