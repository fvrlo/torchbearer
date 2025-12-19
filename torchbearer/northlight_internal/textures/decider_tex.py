from __future__ import annotations

from torchbearer.northlight_internal.textures.nletex import NorthlightTex
from torchbearer.northlight_internal.textures.radtools_bink import BINK_Header
from torchbearer.northlight_internal.textures.directx.structs import DDS_FILEHEAD
from torchbearer.northlight_engine.northlight import Northlight

from mulch import Stream

def tex_handler(file: Northlight.File) -> DDS_FILEHEAD | NorthlightTex | BINK_Header | None:
	# the first chunk (if chunked) will always be size_decompressed == 148 if it's a real dds file. If it isn't, it's a bink video file in disguise
	# older tex files may also be a custom format DDS where the header is abbreviated
	match file.admin.reader.version:
		case 'v2.0':
			# either actual DDS or BINK file
			# games: AW2, FBR
			if file.chunks[0].size_decompressed == 148:
				return DDS_FILEHEAD.from_data(file.read_first_chunk())
			else:
				return BINK_Header(Stream(file.read_first_chunk()))
		case 'v1.8' | 'v1.9':
			# either actual DDS or BINK file
			# games: QBR, CTL
			with Stream(file.data) as f:
				magic = f.peek(3)
				if magic == b'DDS':
					return DDS_FILEHEAD.from_stream(f)
				else:
					return BINK_Header(Stream(file.read_first_chunk()))
		case 'v1.7' | 'v1.3' | 'v1.2':
			# custom Northlight TEX type
			# games: AW1, AWR, AWN
			with Stream(file.chunks[0].archive.path, spos=file.chunks[0].offset) as f:
				return NorthlightTex(f, file.chunks[0].size)