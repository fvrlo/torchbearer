from pathlib import Path

from torchbearer.mulch import Stream


def binhkx2dict(binhkxfile: Path):
	with Stream(binhkxfile) as stream:
		magic_id_1 = int(stream)
		magic_id_2 = int(stream)
		
		if magic_id_1 != 0x57e0e057 or magic_id_2 != 0x10c0c010:
			raise Exception("Invalid magic id")
		
		user_tag = int(stream)
		file_version = int(stream)
		unknown_skip = stream[4]  # Structure layout rules
		
		num_sections = int(stream)
		
		contents_section_index = int(stream)
		contents_section_offset = int(stream)
		class_name_section_index = int(stream)
		class_name_section_offset = int(stream)
		reserved = stream[16]  # Reserved
		flags = int(stream)
		pad = stream[4]  # Pad
		
		class_names = {}
		
		for i in range(num_sections):
			section_name = stream[19].decode("ascii").replace("\0", "")
			stream.seek(1, 1)
			
			section_node = {
				'type'                 : section_name,
				'absolute_data_start'  : int(stream),
				'local_fixups_offset'  : int(stream),
				'global_fixups_offset' : int(stream),
				'virtual_fixups_offset': int(stream),
				'exports_offset'       : int(stream),
				'imports_offset'       : int(stream),
				'end_offset'           : int(stream)
			}
			
			with stream(ofst=section_node['absolute_data_start']):
				if section_name == "__classnames__":
					while True:
						tag = int(stream)
						if tag == 0xFFFFFFFF:
							break
				elif section_name == "__types__":
					pass
				elif section_name == "__data__":
					pass