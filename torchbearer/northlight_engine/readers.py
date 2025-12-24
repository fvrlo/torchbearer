from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from functools import cached_property
from pathlib import Path
from typing import final, Literal, Protocol

import numpy as np
from loguru import logger

from mulch import CloseStrCache, Stream, TimerLog
from torchbearer.northlight_engine.configs import InstanceConfig
from torchbearer.northlight_engine.marshall import NPD, OFSZ

__all__ = [
	"Reader",
	"ReaderNLEv10",
	"ReaderNLEv20"
]


class Protos:
	class OffsetSized(Protocol):
		ofst: int
		size: int
	
	class Folder(Protocol):
		index: int
		parent_idx: int
	
	class File(Protocol):
		index: int
		parent_idx: int
		size: int



class Reader(ABC):
	instance: InstanceConfig
	cache_dir: Path
	version_major: int
	version_minor: int
	path: Path
	pfx: str
	
	count_d_main: int
	count_f_main: int

	main_d: list[Protos.Folder]
	main_f: list[Protos.File]
	
	_relmap_d: dict[int, list[int]] | None
	_relmap_f: dict[int, list[int]] | None
	
	@property
	def cache_dir(self) -> Path:
		return self.instance.app.cach / self.instance.key / self.path.stem
	
	def __init__(self, instance: InstanceConfig, path: Path, v_major: int, v_minor: int):
		self.instance = instance
		self.version_major = v_major
		self.version_minor = v_minor
		self.path = path
		self._relmap_f = None
		self._relmap_d = None
		self.cache_dir.mkdir(parents=True, exist_ok=True)
	
	@cached_property
	def logname(self):
		return f"{self.__class__.__name__}[{self.instance.key}/{self.path.stem}]"
	
	@cached_property
	def version(self) -> str:
		return f"v{self.version_major}.{self.version_minor}"
	
	@property
	def relmap_d(self) -> dict[int, list[int]]:
		if self._relmap_d is None:
			self._relmap_d = defaultdict(list)
			for i, x in enumerate(self.main_d):
				if x.parent_idx != -1:
					self._relmap_d[x.parent_idx].append(i)
		return self._relmap_d
	
	@property
	def relmap_f(self) -> dict[int, list[int]]:
		if self._relmap_f is None:
			self._relmap_f = defaultdict(list)
			for i, x in enumerate(self.main_f):
				self._relmap_f[x.parent_idx].append(i)
		return self._relmap_f
	
	@final
	@classmethod
	def factory(cls, instance: InstanceConfig, path: Path) -> Reader:
		match path.suffix:
			case '.rmdp':
				
				if not path.is_file():
					raise FileNotFoundError("RMDP archive exists check failed")
				if not path.stat().st_size != 0:
					raise FileNotFoundError("RMDP archive minimum size check failed")
				path_bin = path.with_suffix('.bin')
				if not path_bin.is_file():
					raise FileNotFoundError("RMDP bin exists check failed")
				if not path_bin.stat().st_size != 0:
					raise FileNotFoundError("RMDP bin minimum size check failed")
				
				return ReaderNLEv10(instance, path)
			case '.rmdtoc':
				return ReaderNLEv20(instance, path)
			case _:
				raise ValueError(path)
	
	@abstractmethod
	def build_strdict_option(self, mode: str) -> dict[int, str]:
		...


class ReaderNLEv10(Reader):
	"""
	Attributes:
		path_bin (Path): Path to reader's .bin file.
		path_meta (Path): Path to reader's .packmeta file if it exists.
        nsz (int): Name array size.
        eoh (int): End of header data.
        eoa (int): End of filesystem array.
        pfx (str): Filesystem prefix.
        uhd (bytes): 120 bytes of unknown header data, might be something.
        
    Notes on `uhd`:
    
		When version_minor == 2, it's usually fragments of a packed file (ex. I found XML/ZLIB data), always starting with 0x00746F727900 (aka ' tory ') as the first 6 bytes.
		Is 'tory' a keyword to reserve the array? Is it just junk? Tory as in a name? (Inven)tory? (S)tory? (Direc)tory?
		
		I would assume it's just random data left over from bin creation, but maybe it's reserved for version-specific data. If so, it's weird to be prepended by a null-termed string.
		
		Also of note, does not have an equivalent in RMDTOC files.
	"""
	
	path_bin: Path
	path_meta: Path
	
	nsz: int
	eoh: int
	eoa: int
	
	count_d_root: int
	count_f_root: int
	
	main_d: list[NPD.RMDP_D]
	main_f: list[NPD.RMDP_F]
	root_d: list[NPD.RMDP_D]
	root_f: list[NPD.RMDP_F]
	
	uhd: bytes
	
	def build_strdict_option(self, mode: Literal['fldr', 'file']) -> dict[int, str]:
		strcache = self.cache_dir / f"{self.path.stem}.strarray_{mode}"
		if not strcache.is_file():
			with Stream(self.path_bin) as stream:
				match mode:
					case 'fldr':
						CloseStrCache.write(strcache, {i: stream.nts_at(self.eoa + x.name_offset) if x.name_offset != -1 else '' for i, x in enumerate(self.main_d)})
					case 'file':
						CloseStrCache.write(strcache, {i: stream.nts_at(self.eoa + x.name_offset) if x.name_offset != -1 else '' for i, x in enumerate(self.main_f)})
		return CloseStrCache.read(strcache)
	
	def __init__(self, instance: InstanceConfig, rmdp_path: Path):
		self.path_bin = rmdp_path.with_suffix('.bin')
		self.path_meta = rmdp_path.with_suffix('.packmeta')
		
		with Stream(self.path_bin) as stream:
			stream.endi = 'big' if bool(stream) else 'little'
			super(ReaderNLEv10, self).__init__(instance=instance, path=rmdp_path, v_major=1, v_minor=int(stream))
			self.count_d_main = int(stream)
			self.count_f_main = int(stream)
			match self.version_minor:
				case 2 | 3:
					self.count_d_root, self.count_f_root = 0, 0
				case 7 | 8 | 9:
					self.count_d_root, self.count_f_root = int(stream), int(stream)
				case _:
					raise ValueError(self.version_minor)
			self.nsz = int(stream)
			self.eoa = len(stream) - self.nsz
			self.pfx = stream.nts(8)
			self.uhd = stream[120]
			self.eoh = stream.tell()
			if self.version_minor == 2:
				self.version_minor = 2 if (40 * self.count_f_main) + (28 * self.count_d_main) == (self.eoa - self.eoh) else 3
				logger.opt(colors=True).info(
					f"RMDP version 2 decoder (dc=<le>{self.count_d_main}</le>, fc=<le>{self.count_f_main}</le>, eoh=<le>{self.eoh}</le>, eoa=<le>{self.eoa}</le>) resulted in decision <le>{self.version_minor}</le>")
			match self.version_minor:
				case 2:
					d_type, f_type = NPD.DT_D_AW1, NPD.DT_F_AW1
				case 3:
					d_type, f_type = NPD.DT_D_AWR, NPD.DT_F_AWR
				case 7:
					d_type, f_type = NPD.DT_D_LE7, NPD.DT_F_LE7
				case 8 | 9:
					d_type, f_type = NPD.DT_D_LE8, NPD.DT_F_LE8
				case _:
					raise ValueError(self.version_minor)
			self.main_d = [NPD.RMDP_D.via_void(i, x) for i, x in
			               enumerate(np.frombuffer(stream.read(d_type.itemsize * self.count_d_main), dtype=d_type, count=self.count_d_main))]  # type: ignore
			self.main_f = [NPD.RMDP_F.via_void(i, x) for i, x in
			               enumerate(np.frombuffer(stream.read(f_type.itemsize * self.count_f_main), dtype=f_type, count=self.count_f_main))]  # type: ignore
			self.root_d = [NPD.RMDP_D.via_void(i, x) for i, x in
			               enumerate(np.frombuffer(stream.read(d_type.itemsize * self.count_d_root), dtype=d_type, count=self.count_d_root))]  # type: ignore
			self.root_f = [NPD.RMDP_F.via_void(i, x) for i, x in
			               enumerate(np.frombuffer(stream.read(f_type.itemsize * self.count_f_root), dtype=f_type, count=self.count_f_root))]  # type: ignore


class ReaderNLEv20(Reader):
	table: NPD.RMDTOC_Table
	data_dcp: Path
	
	def __init__(self, instance: InstanceConfig, path: Path):
		with TimerLog(f'ReaderNLEv20[{instance.key}/{path.stem}] - base class init'):
			if path.suffix != '.rmdtoc':
				raise ValueError(f"Path extension invalid, expected '.rmdtoc' but got '{path.suffix}'")
			with Stream(path) as temp:
				self.table = NPD.RMDTOC_Table(temp)
			super().__init__(instance=instance, path=path, v_major=2, v_minor=self.table.version)
			self.pfx = ''
			self.data_dcp = self.cache_dir / (self.path.stem + '.rmdtoc_decompressed')
			make_cache = False
			if not self.data_dcp.is_file():
				make_cache = True
			elif self.data_dcp.stat().st_size != self.table.dcp_size:
				logger.info(f"Existing .rmdtoc_decompressed size: {self.data_dcp.stat().st_size}")
				logger.info(f"Predicted .rmdtoc_decompressed size: {self.table.dcp_size}")
				make_cache = True
			if make_cache:
				with TimerLog(f'{self.logname} - decompressing table ({self.table.tabl.size // 16} chunks)'):
					dcpdat = bytearray()
					with Stream(self.path) as stream:
						for c in NPD.RMDTOC_Chunk.parse(stream, self.table.tabl):
							dcpdat += stream.read_lz4_block(c.compressed, c.decompressed, c.lz4, offset=c.offset)
					self.data_dcp.write_bytes(dcpdat)
	
	@cached_property
	def main_d(self) -> list[NPD.RMDTOC_D]:
		with TimerLog(f'{self.logname} - fldr cache gen'):
			with Stream(self.data_dcp) as stream:
				return NPD.RMDTOC_D.parse(stream, self.table.fldr)
	
	@cached_property
	def main_f(self) -> list[NPD.RMDTOC_F]:
		with TimerLog(f'{self.logname} - file cache gen'):
			with Stream(self.data_dcp) as stream:
				return NPD.RMDTOC_F.parse(stream, self.table.file)
	
	@cached_property
	def cache_arch(self) -> list[NPD.RMDTOC_Archive]:
		with TimerLog(f'{self.logname} - arch cache gen'):
			with Stream(self.data_dcp) as stream:
				return NPD.RMDTOC_Archive.parse(stream, self.table.arch)
	
	@cached_property
	def cache_chnk(self) -> list[NPD.RMDTOC_Chunk]:
		with TimerLog(f'{self.logname} - chnk cache gen'):
			with Stream(self.data_dcp) as stream:
				return NPD.RMDTOC_Chunk.parse(stream, self.table.chnk)
	
	@cached_property
	def cache_mdty(self) -> list[OFSZ]:
		with TimerLog(f'{self.logname} - mdty cache gen'):
			with Stream(self.data_dcp) as stream:
				return self.table.mdty.parse(stream)
	
	@cached_property
	def data_stng(self) -> bytes:
		with TimerLog(f'{self.logname} - stng cache gen'):
			with Stream(self.data_dcp, spos=self.table.stng.ofst) as stream:
				return stream[self.table.stng.size]
	
	@cached_property
	def data_mtdt(self) -> bytes:
		with TimerLog(f'{self.logname} - mtdt cache gen'):
			with Stream(self.data_dcp, spos=self.table.mtdt.ofst) as stream:
				return stream[self.table.mtdt.size]
	
	def build_strdict_option(self, mode: Literal['fldr', 'file', 'arch', 'mdty']) -> dict[int, str]:
		strcache = self.cache_dir / f"{self.path.stem}.strarray_{mode}"
		if not strcache.is_file():
			with Stream(self.data_stng) as stream:
				match mode:
					case 'fldr':
						CloseStrCache.write(strcache, {i: stream.read_at(x.name.ofst, x.name.size).decode() for i, x in enumerate(self.main_d)})
					case 'file':
						CloseStrCache.write(strcache, {i: stream.read_at(x.name.ofst, x.name.size).decode() for i, x in enumerate(self.main_f)})
					case 'arch':
						CloseStrCache.write(strcache, {i: stream.read_at(x.path.ofst, x.path.size).decode() for i, x in enumerate(self.cache_arch)})
					case 'mdty':
						CloseStrCache.write(strcache, {i: stream.read_at(x.ofst, x.size).decode() for i, x in enumerate(self.cache_mdty)})
		return CloseStrCache.read(strcache)
