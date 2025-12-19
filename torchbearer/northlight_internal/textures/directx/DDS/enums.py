from __future__ import annotations
from enum import IntEnum

__all__ = [
	'DDS_HEADER_DXT10_miscFlags2'
]

class DDS_HEADER_DXT10_miscFlags2(IntEnum):
	"""Contains additional metadata (formerly was reserved)."""
	DDS_ALPHA_MODE_UNKNOWN          = 0
	"""Any alpha channel content is unknown. This is the value for legacy files, which typically is assumed to be 'straight' alpha."""
	
	DDS_ALPHA_MODE_STRAIGHT         = 1
	"""Any alpha channel content is presumed to use straight alpha."""
	
	DDS_ALPHA_MODE_PREMULTIPLIED    = 2
	"""Any alpha channel content is using premultiplied alpha. The only legacy file formats that indicate this information are 'DX2' and 'DX4'."""
	
	DDS_ALPHA_MODE_OPAQUE           = 3
	"""Any alpha channel content is all set to fully opaque."""
	
	DDS_ALPHA_MODE_CUSTOM           = 4
	"""Any alpha channel content is being used as a 4th channel and is not intended to represent transparency (straight or premultiplied)."""
	