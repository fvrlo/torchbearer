from __future__ import annotations

import math
from typing import overload

from pyglm.glm import vec2, vec3, mat3, normalize, distance

from mulch import Stream, ByteStreamField

__all__ = [
	"ObjectID",
	"RID",
	"GID",
	"BoundBox",
	"BoundSphere",
	"GLMFields"
]


class GLMFields:
	class vec2(ByteStreamField[str, None]):
		def caller(self, stream, obj, extra):
			return vec2(stream.f4, stream.f4)
	
	class vec3(ByteStreamField[str, None]):
		def caller(self, stream, obj, extra):
			return vec3(stream.f4, stream.f4, stream.f4)
	
	class mat3(ByteStreamField[str, None]):
		def caller(self, stream, obj, extra):
			return mat3(stream.f4, stream.f4, stream.f4, stream.f4, stream.f4, stream.f4, stream.f4, stream.f4, stream.f4)


class BoundBox:
	lo: vec3
	hi: vec3
	
	def __init__(self, stream: Stream | None):
		if stream is None:
			self.lo = vec3()
			self.hi = vec3()
		else:
			x1 = float(stream)
			y1 = float(stream)
			z1 = float(stream)
			x2 = float(stream)
			y2 = float(stream)
			z2 = float(stream)
			self.lo = vec3(x=min(x1, x2), y=min(y1, y2), z=min(z1, z2))
			self.hi = vec3(x=max(x1, x2), y=max(y1, y2), z=max(z1, z2))
	
	def isInside(self, p: vec3, margin: float = 0.00001) -> bool:
		chk_xmin = self.lo.x - margin <= p[0]
		chk_xmax = p[0] <= self.hi.x + margin
		chk_ymin = self.lo.y - margin <= p[1]
		chk_ymax = p[1] <= self.hi.y + margin
		chk_zmin = self.lo.z - margin <= p[2]
		chk_zmax = p[2] <= self.hi.z + margin
		return chk_xmin & chk_xmax & chk_ymin & chk_ymax & chk_zmin & chk_zmax


class BoundSphere:
	pos: vec3
	rad: float
	
	def __init__(self, stream: Stream):
		self.pos = vec3(stream.f4, stream.f4, stream.f4)
		self.rad = stream.f4
	
	@classmethod
	def from_values(cls, pos: vec3, rad: float):
		new = cls.__new__(cls)
		new.pos = pos
		new.rad = rad
		return new
	
	def intersect(self, other: BoundSphere) -> bool:
		return distance(self.pos, other.pos) < self.rad + other.rad
	
	def contains(self, other: vec3 | BoundSphere) -> bool:
		if isinstance(other, vec3):
			return distance(self.pos, other) <= self.rad
		else:
			return distance(self.pos, other.pos) + other.rad <= self.rad
	
	def __add__(self, other: BoundSphere) -> BoundSphere:
		if self.contains(other):
			return self
		elif other.contains(self):
			return other
		diff = other.pos - self.pos
		length = math.sqrt(
			sum([
				math.pow(other.pos.x - self.pos.x, 2),
				math.pow(other.pos.y - self.pos.y, 2),
				math.pow(other.pos.z - self.pos.z, 2),
			]))
		radius1 = self.rad
		radius2 = other.rad
		ddir = normalize(diff)
		vmin = min(-radius1, length - radius2)
		vmax = (max(radius1, length + radius2) - vmin) * 0.5
		return BoundSphere.from_values(self.pos + ddir * (vmax + vmin), vmax)


class RID:
	value: bytes
	
	def dict(self):
		return {'RID': str(self)}
	
	@classmethod
	def long(cls, value: Stream):
		return cls(value, 8)
	
	def __init__(self, value: Stream, _len: int = 4, /):
		self.value = value[_len]

	def __str__(self):
		return self.value[::-1].hex().upper()
	

class GID:
	type: int
	id: int
	
	@property
	def id_hex(self) -> str:
		return f'0x{self.id.to_bytes(4, 'big').hex().upper()}'
	
	def isNil(self) -> bool:
		return self == None
	
	def dict(self):
		return {'GID': {'Type': self.type, 'ID': self.id, 'ID Hex': self.id_hex}}
	
	def __init__(self, stream: Stream):
		self.type = stream.i_4u
		self.id = stream.integer(4, signed=False, endi='big')
	
	def __str__(self):
		return f'{self.type}:{self.id_hex}'
	
	def __eq__(self, other: GID | None) -> bool:
		return (self.type == 0 & self.id == 0) if other is None else (self.type, self.id) == (other.type, other.id)
	
	def __gt__(self, other: GID) -> bool:
		return (self.type, self.id) < (other.type, other.id)
	
	def __lt__(self, other: GID) -> bool:
		return (self.type, self.id) > (other.type, other.id)
	


class ObjectID:
	value: int
	type: int
	id: int
	
	def get_type(self):
		return self.value & 0x1FF
	
	def yamlstr(self):
		return str(self)
	
	@overload
	def __init__(self): ...
	
	@overload
	def __init__(self, value: int): ...
	
	@overload
	def __init__(self, value: Stream): ...
	
	@overload
	def __init__(self, value: int, obj_id: int): ...
	
	def __init__(self, value: int | Stream = 0, obj_id: int = None):
		if obj_id is None:
			self.value = value
		elif isinstance(value, Stream):
			self.value = value.i_4u
		elif isinstance(value, int):
			self.value = value | (obj_id << 9)
		self.type = self.value & 0x1FF
		self.id = self.value >> 9
	
	def __str__(self):
		return f'0x{self.value.to_bytes(4, 'little').hex().upper()}'
	
	def __bool__(self):
		return self.value != 0
	
	def __eq__(self, other: ObjectID):
		return self.value == other.value
	
	def __lt__(self, other: ObjectID):
		return self.value < other.value
	
	def __gt__(self, other: ObjectID):
		return self.value > other.value
