from __future__ import annotations

import inspect
import tomllib
from pathlib import Path

from typing import Callable


class FieldTOML[T]:
	fieldtype: type[T]
	
	def __init__(self, fieldtype: type[T], /, *, to_str: Callable[[T], str]):
		self.fieldtype = fieldtype
		self.to_str = to_str
	
	def __set_name__(self, obj: ConfigTOML, name: str):
		self.name = f'_tomlfield_{name}'
	
	def __get__(self, obj: ConfigTOML, objtype: type = None) -> T:
		return self.from_str(getattr(obj, self.name))
	
	def __set__(self, obj: ConfigTOML, value):
		setattr(obj, self.name, value)
		obj.save()
	
	def from_str(self, value: str) -> T:
		if self.fieldtype != str:
			return self.fieldtype(value)
		else:
			return value


def field[T](fieldtype: type[T] = str, /, *, to_str: Callable[[T], str] = lambda x: f"\"{x}\"") -> FieldTOML[T]:
	return FieldTOML(fieldtype, to_str=to_str)


class ConfigTOML:
	tomlpath: Path
	
	@classmethod
	def __fields__(cls) -> dict[str, FieldTOML]:
		return {k: v for k, v in inspect.getmembers(cls) if isinstance(v, FieldTOML)}
	
	@classmethod
	def writetoml(cls, path: Path, /, **kwargs) -> Path:
		path.write_text('\n'.join([f"{name} = {_field.to_str(kwargs[name])}" for name, _field in cls.__fields__().items()]))
		return path
	
	def __init__(self, tomlpath: Path, /):
		self.tomlpath = tomlpath
		self.load()
	
	def save(self):
		self.writetoml(self.tomlpath, **{name: getattr(self, name) for name in self.__fields__().keys()})
	
	def load(self):
		if self.tomlpath.suffix != '.toml':
			raise ValueError(f'Only .toml files are supported, got {self.tomlpath.suffix}')
		elif not self.tomlpath.exists():
			raise FileNotFoundError(self.tomlpath)
		valid_fields = self.__fields__()
		for k, v in tomllib.loads(self.tomlpath.read_text()).items():
			if k in valid_fields.keys():
				setattr(self, valid_fields[k].name, valid_fields[k].from_str(v))
