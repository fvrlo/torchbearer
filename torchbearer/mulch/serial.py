from collections import defaultdict
from pathlib import PurePath
from typing import Any, Callable
from orjson import orjson
import yaml
import enum

from typing import Generator, Protocol, runtime_checkable

from collections.abc import Buffer, Iterable, Mapping

__all__ = [
	"dd",
	"jsondump",
	"yamldump",
	"Dictable"
]


def dd() -> defaultdict:
	return defaultdict(dd)


@runtime_checkable
class Dictable(Protocol):
	def dict(self) -> dict: ...

@runtime_checkable
class YamlStringable(Protocol):
	def yamlstr(self) -> str: ...

@runtime_checkable
class Dictable_ByMethod(Protocol):
	def dictgen(self) -> Generator[tuple[..., ...], None, None]: ...



def prepass(obj: Any) -> Any:
	"""Parse an object for either JSON or YAML dumping with the intent of making it human-readable."""
	
	# Safe individual returns
	if isinstance(obj, (str, int, float, bool, type(None))):
		return obj

	# Match specific types
	elif isinstance(obj, (bytes, bytearray)):
		return f"0x{obj.hex().upper()}"
	elif isinstance(obj, memoryview):
		if obj.nbytes <= 24:
			return f"<memoryview object: {prepass(bytes(obj))}>"
		else:
			return f"<memoryview object ({obj.format} with len {len(obj)})>"
	
	# Match generic types
	elif isinstance(obj, enum.Enum):
		if isinstance(obj, enum.Flag):
			return {'rep': f"{obj.value} (0x{obj.value.to_bytes(4).hex()})", 'values': {member.name: bool(obj & member) for member in type(obj) if bool(obj & member)}}
		elif isinstance(obj, enum.IntEnum):
			return f"<IntEnum {type(obj).__name__} value: {obj.name} ({obj.value}, (0x{obj.value.to_bytes(4, 'little').hex()}))>"
		else:
			return f"<Enum {type(obj).__name__} value: {obj.name} ({obj.value})>"
	elif isinstance(obj, PurePath):
		return str(obj).replace('\\', '/')
	
	# Match ABC types
	elif isinstance(obj, YamlStringable):
		return prepass(obj.yamlstr())
	elif isinstance(obj, Dictable):
		return prepass(obj.dict())
	elif isinstance(obj, Dictable_ByMethod):
		return prepass({k: v for k, v in obj.dictgen()})
	elif isinstance(obj, Buffer):
		return f"0x{bytes(obj).hex().upper()}"
	elif isinstance(obj, Mapping):
		return {prepass(k): prepass(v) for k, v in obj.items()}
	elif isinstance(obj, Iterable):
		return [prepass(v) for v in obj]
	elif isinstance(obj, Callable):
		return prepass(obj())
	else:
		return obj


def jsondump(__obj: Any):
	return orjson.dumps(prepass(__obj), option=orjson.OPT_INDENT_2 | orjson.OPT_NON_STR_KEYS | orjson.OPT_PASSTHROUGH_SUBCLASS).debugprint().replace('  ', '    ')

def yamldump(__obj: Any, indent: int = 2):
	return yaml.dump(prepass(__obj), default_flow_style=False, sort_keys=False, indent=indent, allow_unicode=True)