from __future__ import annotations

from pyglm.glm import vec3

from torchbearer.mulch import Stream


class ATMFile:
	version: int
	v1: vec3
	v2: vec3
	v3: vec3
	unkValue: float
	stars: dict[int, vec3]
	atmosphericLUT: bytes
	
	def __init__(self, stream: Stream):
		self.version = int(stream)
		if self.version != 1:
			raise Exception(f'Invalid atmosphere file version. Expected 1, got {self.version}')
		else:
			self.v1 = vec3(x=stream.f4, y=stream.f4, z=stream.f4)
			self.v2 = vec3(x=stream.f4, y=stream.f4, z=stream.f4)
			self.v3 = vec3(x=stream.f4, y=stream.f4, z=stream.f4)
			self.unkValue = float(stream)
			self.stars = {i: vec3(x=stream.f4, y=stream.f4, z=stream.f4) for i in range(256)}
			self.atmosphericLUT = stream.read()