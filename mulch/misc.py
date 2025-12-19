from __future__ import annotations

import os
import time
from collections import defaultdict
from pathlib import Path
from numbers import Number
from typing import Any, Generator, Sequence, SupportsInt, Literal
from math import floor, log10

from loguru import logger

__all__ = [
	'PassingException',
	'ValidationError',
	'Helper',
	'TimerLog',
	'PathPlus',
	'KDD',
	'VDD',
	'asciichart'
]

# ----------------------------------------------------------------------------------------------------------------------
# Custom Exceptions
# ----------------------------------------------------------------------------------------------------------------------

class PassingException(Exception):
	def __init__(self, func_name: str, message: str):
		self.func_name = func_name
		self.message = message
		super(PassingException, self).__init__(self.message)

	def __str__(self):
		return f'{self.func_name} passing, reason: {self.message}'



class ValidationError(Exception):
	pass




# ----------------------------------------------------------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------------------------------------------------------

class Helper:
	"""My own functools. Yes, they may be redundant/stupid/copies of standard lib functions, but I don't care. Computers aren't real. Go touch grass."""
	
	@classmethod
	def combine(cls, a: int, b: int):
		"""Make a float from whole number A and decimal value B"""
		if b == 0:
			return a
		return a + b * 10 ** -(floor(log10(b)) + 1)
	
	@classmethod
	def ceildiv(cls, a: int | float, b: int | float):
		return -(a // -b)
	
	@classmethod
	def merge[sK, sV, dK, dV](cls, src: dict[sK, sV], dst: dict[dK, dV]) -> dict[sK | dK, sV | dV]:
		"""A rudimentary dictionary merger."""
		for key, value in src.items():
			if isinstance(value, dict):
				Helper.merge(value, dst.setdefault(key, {}))
			else:
				dst[key] = value
		return dst

	@classmethod
	def chunks[T](cls, list_input: list[T], chunksize: int, /) -> Generator[list[T]]:
		"""Yield successive n-sized chunks from a list."""
		for i in range(0, len(list_input), chunksize):
			yield list_input[i:i + chunksize]
	
	@classmethod
	def flat(cls, nested: list | set) -> list:
		"""Un-nest lists of lists/sets into a single list."""
		return [cls.flat(item) if isinstance(item, list) or isinstance(item, set) else item for item in nested]
	
	@classmethod
	def avgseq(cls, sequence: Sequence[Number], /) -> float:
		"""Return the average value of a sequence of numbers."""
		return sum(sequence) / len(sequence)    # type: ignore

	@classmethod
	def avg(cls, *numbers: Number) -> float:
		"""Return the average value of a sequence of numbers."""
		return sum(numbers) / len(numbers)      # type: ignore

	@classmethod
	def occurences(cls, i: list) -> dict:
		"""Count occurences of each value that appears in a list."""
		return dict(sorted({value: i.count(value) for value in set(i)}.items()))

	@classmethod
	def makecsv(cls, items: list | set, sep: str = ',') -> str:
		"""Return a list of objects that can be turned into strings as a list in string form, formatted for CSV/TSV/etc."""
		return f'{sep}'.join(str(item) for item in items)

	@classmethod
	def digits(cls, n: SupportsInt) -> int:
		"""How many digits does this number have, not counting decimals?"""
		return len(str(int(n))) if n != 0 else 1

	@classmethod
	def multiremove(cls, string: str, remove: list[str]) -> str:
		"""Remove multiple things from a single string."""
		for x in remove:
			string = string.replace(x, '')
		return string

	@classmethod
	def rangefloat(cls, stop: int | float, start: int | float = 0, step: int | float = 1):
		constr = [start]
		itercount = 1
		while constr[-1] < stop:
			constr.append(start + step * itercount)
			itercount += 1
		constr.pop()
		return constr

# ----------------------------------------------------------------------------------------------------------------------
# Classes
# ----------------------------------------------------------------------------------------------------------------------


class TimerLog:
	depth = 0
	
	start:  float
	lvl:    Literal['trace', 'debug', 'info', 'success', 'warning', 'error', 'critical', 'exception']
	txt:    str
	extra:  dict
	
	def __init__(self, txt: str, lvl: Literal['trace', 'debug', 'info', 'success', 'warning', 'error', 'critical', 'exception'] = 'info', **extra):
		self.start = time.perf_counter()
		self.lvl = lvl
		self.txt = txt
		self.extra = extra
	
	def __enter__(self):
		TimerLog.depth += 1
		return self
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		TimerLog.depth -= 1
		duration = round(1000 * (time.perf_counter() - self.start), 2)
		
		if duration <= 800:
			vga_val = 214
		elif duration <= 1000:
			vga_val = 208
		elif duration <= 1500:
			vga_val = 202
		elif duration <= 2000:
			vga_val = 196
		else:
			vga_val = 40
		#   for x in range(self.logger.depth):
		#		rtrn += f"{Colors.rgb(128, 128, 255 - (x*64))}> "
		
		# if TimerLog.depth > 0:
		#	depthstr = f'{"##" * TimerLog.depth} '
		# else:
		#	depthstr = ''
		logger.opt(colors=True).log(self.lvl.upper(), f'{self.txt} finished (<fg {vga_val}>{duration}</> ms)'.format(**self.extra))





class PathPlus:
	@classmethod
	def open_in_explorer(cls, self: Path):
		os.startfile(self)

	@classmethod
	def clean_folder(cls, self: Path) -> None:
		"""
		Clear contents of a folder. Will only operate on the top level, ignoring recursion and folders themselves.
		Useful as a final-call cleaner for a cache folder or to remove unfinished files on interrupt.

		:return: :class:`None`
		"""
		if self.is_dir():
			all_files_in_folder = sorted(self.glob('*'))
			if len(all_files_in_folder) > 0:
				for file in all_files_in_folder:
					file.unlink()



class KDD(dict[int, Any]):
	"""
	A defaultdict maker for nested lists, to then be summarized by counts of occurences in said lists.
	
	Your first key must be the depth of a section. For example:
	
	kdd[2]["string1"]["string2"].append(value)
	kdd[1]["string1"].append(value)
	kdd[3]["string1"]["string2"]["string3"].append(value)
	"""
	
	def __missing__(self, key: int) -> int | list | defaultdict:
		self[key] = self._missing_key_maker(key)
		return self[key]
	
	@classmethod
	def _missing_key_maker(cls, count: int = 0) -> int | list | defaultdict:
		if count == 0:
			return list()
		else:
			return defaultdict(lambda: cls._missing_key_maker(count - 1))
	
	@classmethod
	def unnest(cls, dicto: dict | list):
		if isinstance(dicto, dict):
			return {k: cls.unnest(v) for k, v in sorted(dicto.items())}
		elif isinstance(dicto, list):
			return {k: dicto.count(k) for k in sorted(set(dicto))}
		else:
			raise TypeError(type(dicto))
		
	def decompile(self):
		return [self.unnest(v) for v in self.values()]

class VDD(dict[int, Any]):
	"""
	A defaultdict maker for nested lists much like KDD, but without the summarization.
	
	Your first key must be the depth of a section. For example:
	
	vdd[2]["string1"]["string2"].append(value)
	vdd[1]["string1"].append(value)
	vdd[3]["string1"]["string2"]["string3"].append(value)
	"""
	
	def __missing__(self, key: int) -> int | list | defaultdict:
		self[key] = self._missing_key_maker(key)
		return self[key]
	
	@classmethod
	def _missing_key_maker(cls, count: int = 0) -> int | list | defaultdict:
		if count == 0:
			return list()
		else:
			return defaultdict(lambda: cls._missing_key_maker(count - 1))
	
	def decompile(self):
		return [dict(v) for v in self.values()]

asciichart = {
	0x00: 'NUL',
	0x01: 'SOH',
	0x02: 'STX',
	0x03: 'ETX',
	0x04: 'EOT',
	0x05: 'ENQ',
	0x06: 'ACK',
	0x07: 'BEL',
	0x08: 'BS',
	0x09: 'HT',
	0x0A: 'LF',
	0x0B: 'VT',
	0x0C: 'FF',
	0x0D: 'CR',
	0x0E: 'SO',
	0x0F: 'SI',
	0x10: 'DLE',
	0x11: 'DC1',
	0x12: 'DC2',
	0x13: 'DC3',
	0x14: 'DC4',
	0x15: 'NAK',
	0x16: 'SYN',
	0x17: 'ETB',
	0x18: 'CAN',
	0x19: 'EM',
	0x1A: 'SUB',
	0x1B: 'ESC',
	0x1C: 'FS',
	0x1D: 'GS',
	0x1E: 'RS',
	0x1F: 'US',
	0x20: 'SP',
	0x7F: 'DEL',
}