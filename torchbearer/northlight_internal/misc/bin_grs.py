from pathlib import Path

from mulch import Stream


def bingrs2dict(bingrsfile: Path):
	with Stream(bingrsfile) as stream:
		version = int(stream)
		if version != 3:
			raise Exception("Invalid version")
		
		num_mesh = int(stream)
		num_vert = int(stream)
		num_indc = int(stream)
		
		# Uniforms
		num_uniforms = int(stream)
		for i in range(num_uniforms):
			name = stream.string(int(stream))
			
			uniform_type = int(stream)
			if uniform_type == 7:
				texture_name = stream.integer(stream)
			else:
				# Both Alan Wake and Alan Wakes American nightmare only have one color map sampler
				raise Exception("")
		
		# Meshes
		for i in range(num_mesh):
			object_name = f"grass_{i}"
			num_mesh_vertices = int(stream)
			num_mesh_indices = int(stream)
			
			for j in range(num_mesh_vertices):
				pos = dict(x=float(stream), y=float(stream), z=float(stream))
				unk1_1 = stream.unpack('b')[0]
				unk1_2 = stream.unpack('b')[0]
				unk1_3 = stream.unpack('b')[0]
				unk1_4 = stream.unpack('b')[0]
			
			for j in range(0, num_mesh_indices, 3):
				face = [1, 1, 1]
				face[0] += stream.integer(2)
				face[1] += stream.integer(2)
				face[2] += stream.integer(2)