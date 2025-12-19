from __future__ import annotations

from collections import defaultdict

import numpy as np

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Generator, Literal, Self, final
from pathlib import Path
from functools import cached_property
from dataclasses import dataclass, field

from loguru import logger

from torchbearer.mulch import byter, Helper, Stream, CloseStrCache, TimerLog

from .configs import InstanceConfig

__all__ = [
	"Northlight",
	"Reader",
	"ReaderNLEv10",
	"ReaderNLEv20"
]


# TODO: document this (yeah it reads the formats, but explain the structures)


@dataclass
class OFSZ:
	dtype: ClassVar[np.dtype] = np.dtype([('ofst', '<u4'), ('size', '<u4')])
	
	ofst: int
	size: int
	
	@classmethod
	def via_np(cls, void: np.void):
		return cls(ofst=int(void['ofst']), size=int(void['size']))
	
	@classmethod
	def via_stream(cls, stream: Stream):
		return cls(ofst=int(stream), size=int(stream))
	
	def parse(self, stream: Stream) -> list[Self]:
		stream.seek(self.ofst)
		return [self.via_np(x) for x in np.frombuffer(stream.read(8 * self.size), dtype=self, count=self.size)]


class NPD:
	DT_VFS_AW1 = np.dtype(
		{'names': ['name_crc', 'next_id', 'parent_idx', 'flags', 'name_offset'], 'formats': ['V4', '>i4', '>i4', 'V4', '>i4'], 'offsets': [0, 4, 8, 12, 16], 'itemsize': 20})
	DT_VFS_AWR = np.dtype(
		{'names': ['name_crc', 'next_id', 'parent_idx', 'flags', 'name_offset'], 'formats': ['V4', '>i8', '>i8', 'V4', '>i8'], 'offsets': [0, 8, 16, 24, 32], 'itemsize': 40})
	DT_VFS_LE7 = np.dtype(
		{'names': ['name_crc', 'next_id', 'parent_idx', 'flags', 'name_offset'], 'formats': ['V4', '<i4', '<i4', 'V4', '<i4'], 'offsets': [0, 4, 8, 12, 16], 'itemsize': 20})
	DT_VFS_LE8 = np.dtype(
		{'names': ['name_crc', 'next_id', 'parent_idx', 'flags', 'name_offset'], 'formats': ['V4', '<i8', '<i8', 'V4', '<i8'], 'offsets': [0, 4, 12, 20, 24], 'itemsize': 32})
	
	DT_D_AW1 = np.dtype({'names': ['vfs', 'first_child_d_id', 'first_child_f_id'], 'formats': [DT_VFS_AW1, '>i4', '>i4'], 'offsets': [0, 20, 24], 'itemsize': 28})
	DT_D_AWR = np.dtype({'names': ['vfs', 'first_child_d_id', 'first_child_f_id'], 'formats': [DT_VFS_AWR, '>i8', '>i8'], 'offsets': [0, 40, 48], 'itemsize': 56})
	DT_D_LE7 = np.dtype({'names': ['vfs', 'first_child_d_id', 'first_child_f_id'], 'formats': [DT_VFS_LE7, '<i4', '<i4'], 'offsets': [0, 20, 24], 'itemsize': 28})
	DT_D_LE8 = np.dtype({'names': ['vfs', 'first_child_d_id', 'first_child_f_id'], 'formats': [DT_VFS_LE8, '<i8', '<i8'], 'offsets': [0, 32, 40], 'itemsize': 48})
	
	DT_F_AW1 = np.dtype({'names': ['vfs', 'offset', 'size', 'data_crc'], 'formats': [DT_VFS_AW1, '>u8', '>u8', 'V4'], 'offsets': [0, 20, 28, 36], 'itemsize': 40})
	DT_F_AWR = np.dtype({'names': ['vfs', 'offset', 'size', 'data_crc'], 'formats': [DT_VFS_AWR, '>u8', '>u8', 'V4'], 'offsets': [0, 40, 48, 56], 'itemsize': 64})
	DT_F_LE7 = np.dtype(
		{'names': ['vfs', 'offset', 'size', 'data_crc', 'write_time'], 'formats': [DT_VFS_LE7, '<u8', '<u8', 'V4', '<i8'], 'offsets': [0, 20, 28, 36, 40], 'itemsize': 48})
	DT_F_LE8 = np.dtype(
		{'names': ['vfs', 'offset', 'size', 'data_crc', 'write_time'], 'formats': [DT_VFS_LE8, '<u8', '<u8', 'V4', '<i8'], 'offsets': [0, 32, 40, 48, 52], 'itemsize': 60})
	
	DT_TOC_CHNK = np.dtype([('lz4', '?'), ('archive_idx', '<u2'), ('offset', 'V5'), ('decompressed', '<u4'), ('compressed', '<u4')])
	DT_TOC_ARCH = np.dtype([('path', OFSZ), ('hash', 'V8')])
	DT_TOC_VFS_D = np.dtype([("parent_idx", '<u4'), ("next_id", '<u4'), ("next_count", '<u4'), ("file_index", '<u4'), ("file_count", '<u4'), ("name", OFSZ)])
	DT_TOC_VFS_F = np.dtype([("chunks", OFSZ), ("parent_idx", '<u4'), ("name", OFSZ), ("out_size", '<u4'), ("metadata", OFSZ)])
	
	@dataclass
	class RMDP_VFS:
		index: int
		name_crc: bytes
		next_id: int
		parent_idx: int
		flags: bytes
		name_offset: int
		
		@final
		@staticmethod
		def _vfs_dict(index: int, void: np.void):
			return dict(index=index, name_crc=bytes(void['name_crc']), next_id=int(void['next_id']), parent_idx=int(void['parent_idx']), flags=bytes(void['flags']),
			            name_offset=int(void['name_offset']))
	
	@dataclass
	class RMDP_D(RMDP_VFS):
		"""A directory/folder item."""
		first_child_d_id: int
		first_child_f_id: int
		
		@classmethod
		def via_void(cls, index: int, void: np.void):
			return cls(**cls._vfs_dict(index, void['vfs']), first_child_d_id=int(void['first_child_d_id']), first_child_f_id=int(void['first_child_f_id']))
	
	@dataclass
	class RMDP_F(RMDP_VFS):
		"""A file item."""
		offset: int
		size: int
		data_crc: bytes
		write_time: int | None
		
		@classmethod
		def via_void(cls, index: int, void: np.void):
			try:
				write_time = void['write_time']
			except ValueError:
				write_time = None
			return cls(**cls._vfs_dict(index, void['vfs']), offset=int(void['offset']), size=int(void['size']), data_crc=bytes(void['data_crc']), write_time=write_time)
	
	@dataclass
	class RMDTOC_Chunk:
		index: int
		lz4: bool
		archive_idx: int
		offset: int
		decompressed: int
		compressed: int
		
		@classmethod
		def parse(cls, stream: Stream, ofsz: OFSZ) -> list[Self]:
			stream.seek(ofsz.ofst)
			return [cls(index=i, lz4=bool(x['lz4']), archive_idx=int(x['archive_idx']), decompressed=int(x['decompressed']), compressed=int(x['compressed']),  # type: ignore
			            offset=int.from_bytes(bytes(x['offset']), byteorder='little')) for i, x in
			        enumerate(np.frombuffer(stream.read(ofsz.size), dtype=NPD.DT_TOC_CHNK, count=ofsz.size // 16))]  # type: ignore
	
	@dataclass
	class RMDTOC_VFS_D:
		index: int
		parent_idx: int  # parent id
		name: OFSZ
		next_id: int  # first child id
		next_count: int  # child count
		file_index: int  # if file_count is not zero: index of folders that contain files
		file_count: int  # file children
		
		@classmethod
		def parse(cls, stream: Stream, ofsz: OFSZ) -> list[Self]:
			stream.seek(ofsz.ofst)
			return [cls(index=i, name=OFSZ.via_np(x['name']), parent_idx=int(x['parent_idx']), next_id=int(x['next_id']), next_count=int(x['next_count']),  # type: ignore
			            file_index=int(x['file_index']), file_count=int(x['file_count'])) for i, x in  # type: ignore
			        enumerate(np.frombuffer(stream.read(NPD.DT_TOC_VFS_D.itemsize * ofsz.size), dtype=NPD.DT_TOC_VFS_D, count=ofsz.size))]  # type: ignore
	
	@dataclass
	class RMDTOC_VFS_F:
		index: int
		parent_idx: int
		name: OFSZ
		chunks: OFSZ
		metadata: OFSZ
		out_size: int
		
		@classmethod
		def parse(cls, stream: Stream, ofsz: OFSZ) -> list[Self]:
			stream.seek(ofsz.ofst)
			return [
				cls(index=i, name=OFSZ.via_np(x['name']), chunks=OFSZ.via_np(x['chunks']), metadata=OFSZ.via_np(x['metadata']), parent_idx=int(x['parent_idx']),  # type: ignore
				    out_size=int(x['out_size'])) for i, x in
				enumerate(np.frombuffer(stream.read(NPD.DT_TOC_VFS_F.itemsize * ofsz.size), dtype=NPD.DT_TOC_VFS_F, count=ofsz.size))]  # type: ignore
	
	@dataclass
	class RMDTOC_Archive:
		index: int
		path: OFSZ
		hash: bytes
		
		@classmethod
		def parse(cls, stream: Stream, ofsz: OFSZ) -> list[Self]:
			stream.seek(ofsz.ofst)
			return [cls(index=i, path=OFSZ.via_np(x['path']), hash=bytes(x['hash'])) for i, x in  # type: ignore
			        enumerate(np.frombuffer(stream.read(NPD.DT_TOC_ARCH.itemsize * ofsz.size), dtype=NPD.DT_TOC_ARCH, count=ofsz.size))]
	
	class RMDTOC_Table:
		magic: str  # COTR, aka reversed R(emedy)TOC
		version: int
		tabl: OFSZ
		arch: OFSZ
		fldr: OFSZ
		file: OFSZ
		stng: OFSZ
		mdty: OFSZ
		mtdt: OFSZ
		unk0: OFSZ
		unk1: OFSZ
		chnk: OFSZ
		
		def __init__(self, stream: Stream):
			self.magic = stream.string(4)
			self.version = int(stream)
			self.tabl = OFSZ.via_stream(stream)
			self.arch = OFSZ.via_stream(stream)
			self.fldr = OFSZ.via_stream(stream)
			self.file = OFSZ.via_stream(stream)
			self.stng = OFSZ.via_stream(stream)
			self.mdty = OFSZ.via_stream(stream)
			self.mtdt = OFSZ.via_stream(stream)
			self.unk0 = OFSZ.via_stream(stream)
			self.unk1 = OFSZ.via_stream(stream)
			self.chnk = OFSZ.via_stream(stream)
		
		@cached_property
		def dcp_size(self):
			return -(sum([
				(self.arch.size * NPD.DT_TOC_ARCH.itemsize),
				(self.fldr.size * NPD.DT_TOC_VFS_D.itemsize),
				(self.file.size * NPD.DT_TOC_VFS_F.itemsize),
				(self.mdty.size * 8),
				self.chnk.size, self.stng.size, self.mtdt.size]) // -8) * 8


class Reader(ABC):
	cache_dir: Path
	version_major: int
	version_minor: int
	path: Path
	pfx: str
	
	count_d_main: int
	count_f_main: int
	
	main_f: list
	main_d: list
	
	_relmap_d: dict[int, list[int]] | None
	_relmap_f: dict[int, list[int]] | None
	
	def __init__(self, cache_dir: Path, path: Path, v_major: int, v_minor: int):
		self.cache_dir = cache_dir
		self.version_major = v_major
		self.version_minor = v_minor
		self.path = path
		self.cache_dir.mkdir(parents=True, exist_ok=True)
		self._relmap_f = None
		self._relmap_d = None
	
	@cached_property
	def logname(self):
		return f"{self.__class__.__name__}[{self.cache_dir.parent.stem}/{self.cache_dir.stem}]"
	
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
	def factory(cls, config_path: Path, path: Path) -> Reader:
		match path.suffix:
			case '.rmdp':
				return ReaderNLEv10(config_path, path)
			case '.rmdtoc':
				return ReaderNLEv20(config_path, path)
			case _:
				raise ValueError(path)
	
	@abstractmethod
	def build_strdict_option(self, mode: str) -> dict[int, str]:
		...


class ReaderNLEv10(Reader):
	"""
	Attributes:
        nsz (int): Name array size.
        eoh (int): End of header data.
        eoa (int): End of filesystem array.
        pfx (str): Filesystem prefix.
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
	"""
	120 bytes of unknown header data, might be something.

	When version_minor == 2, it's usually fragments of a packed file (ex. I found XML/ZLIB data), always starting with 0x00746F727900 (aka ' tory ') as the first 6 bytes.
	Is 'tory' a keyword to reserve the array? Is is just junk? Tory as in a name? (Inven)tory? (S)tory? (Direc)tory?

	I would assume it's just random data left over from bin creation, but maybe it's reserved for version-specific data. If so, it's weird to be prepended by a null-termed string.

	Also of note, does not have an equivalent in RMDTOC files.
	"""
	
	def build_strdict_option(self, mode: Literal['fldr', 'file']) -> dict[int, str]:
		strcache = self.cache_dir / f"{self.path.stem}.strarray_{mode}"
		if not strcache.is_file():
			with Stream(self.path_bin) as str_stream:
				match mode:
					case 'fldr':
						CloseStrCache.write(strcache, {i: str_stream.nts_at(self.eoa + x.name_offset) if x.name_offset != -1 else '' for i, x in enumerate(self.main_d)})
					case 'file':
						CloseStrCache.write(strcache, {i: str_stream.nts_at(self.eoa + x.name_offset) if x.name_offset != -1 else '' for i, x in enumerate(self.main_f)})
					case _:
						raise ValueError(mode)
		return CloseStrCache.read(strcache)
	
	def __init__(self, cache_dir: Path, rmdp_path: Path):
		self.path_bin = rmdp_path.with_suffix('.bin')
		self.path_meta = rmdp_path.with_suffix('.packmeta')
		
		if not rmdp_path.is_file():
			raise FileNotFoundError("RMDP archive exists check failed")
		if not rmdp_path.stat().st_size != 0:
			raise ValueError("RMDP archive minimum size check failed")
		
		if not self.path_bin.is_file():
			raise FileNotFoundError("RMDP bin exists check failed")
		if not self.path_bin.stat().st_size != 0:
			raise ValueError("RMDP bin minimum size check failed")
		
		with Stream(self.path_bin) as stream:
			stream.endi = 'big' if bool(stream) else 'little'
			v_minor = int(stream)
			super(ReaderNLEv10, self).__init__(cache_dir=cache_dir, path=rmdp_path, v_major=1, v_minor=v_minor)
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
	
	def __init__(self, cache_dir: Path, path: Path):
		with TimerLog(f'ReaderNLEv20[{cache_dir.parent.stem}/{path.stem}] - base class init'):
			if path.suffix != '.rmdtoc':
				raise ValueError(f"Path extension invalid, expected '.rmdtoc' but got '{path.suffix}'")
			with Stream(path) as temp:
				self.table = NPD.RMDTOC_Table(temp)
			super().__init__(cache_dir=cache_dir, path=path, v_major=2, v_minor=self.table.version)
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
	
	@property
	def count_d_main(self):
		return self.table.fldr.size
	
	@property
	def count_f_main(self):
		return self.table.file.size
	
	@cached_property
	def main_d(self) -> list[NPD.RMDTOC_VFS_D]:
		with TimerLog(f'{self.logname} - fldr cache gen'):
			with Stream(self.data_dcp) as stream:
				return NPD.RMDTOC_VFS_D.parse(stream, self.table.fldr)
	
	@cached_property
	def main_f(self) -> list[NPD.RMDTOC_VFS_F]:
		with TimerLog(f'{self.logname} - file cache gen'):
			with Stream(self.data_dcp) as stream:
				return NPD.RMDTOC_VFS_F.parse(stream, self.table.file)
	
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


@dataclass
class GenericItem(ABC):
	admin: Northlight.Admin = field(kw_only=True, repr=False)
	index: int = field(kw_only=True)
	
	@property
	@abstractmethod
	def size(self) -> int:
		...

	@abstractmethod
	def dict(self) -> dict[str, Any]:
		...


class Northlight:
	@dataclass
	class Admin[T_Reader: Reader]:
		path: Path
		instance: InstanceConfig
		
		_reader: T_Reader | None = field(default=None)
		_tree: Northlight.TreeAdmin | None = field(default=None)
		_data: Northlight.DataAdmin | None = field(default=None)
		_meta: Northlight.MetaAdmin | None = field(default=None)
		
		def clear(self):
			del self._reader
			del self._tree
			del self._data
			del self._meta
		
		def extensions(self):
			return Helper.occurences([f.extension for f in self.tree.file.mapping.values()])
		
		@cached_property
		def cache_dir(self) -> Path:
			return self.instance.app.cach / self.instance.key / self.path.stem
		
		@property
		def is_set(self) -> bool:
			return self._reader is not None
		
		@property
		def name(self):
			return self.path.stem
		
		@property
		def extension(self):
			return self.path.suffix[1:]
		
		@property
		def reader(self) -> T_Reader:
			if self._reader is None:
				self._reader = Reader.factory(self.cache_dir, self.path)
			return self._reader
		
		@reader.deleter
		def reader(self):
			self._reader = None
		
		@property
		def tree(self) -> Northlight.TreeAdmin:
			if self._tree is None:
				with TimerLog(f'Admin[{self.reader.logname}] - filesystem mapping'):
					fldr_names = self.reader.build_strdict_option('fldr')
					file_names = self.reader.build_strdict_option('file')
					with TimerLog(f'Admin[{self.reader.logname}] - fldr mapping (<le>{len(self.reader.main_d)}</le> fldrs)'):
						if isinstance(self.reader, ReaderNLEv10):
							m_d = {
								i: Northlight.Folder(
									admin=self, index=i, parent_idx=x.parent_idx, next_id=x.next_id, name=fldr_names[i],
									file_index=i,
									file_count=len(self.reader.relmap_f[i]),
									next_count=len(self.reader.relmap_d[i]) + len(self.reader.relmap_f[i]),
									first_child_d_id=x.first_child_d_id,
									first_child_f_id=x.first_child_f_id,
									children_d_ids=self.reader.relmap_d.get(i, list()),
									children_f_ids=self.reader.relmap_f.get(i, list()),
								) for i, x in enumerate(self.reader.main_d)
							}
						elif isinstance(self.reader, ReaderNLEv20):
							m_d = {
								i: Northlight.Folder(
									admin=self, index=i, parent_idx=x.parent_idx, next_id=x.next_id, name=fldr_names[i],
									file_index=x.file_index,
									file_count=x.file_count,
									next_count=x.next_count,
									first_child_d_id=(self.reader.relmap_d[i][0] if len(self.reader.relmap_d[i]) > 0 else -1) if i in self.reader.relmap_d.keys() else -1,
									first_child_f_id=(self.reader.relmap_f[i][0] if len(self.reader.relmap_f[i]) > 0 else -1) if i in self.reader.relmap_f.keys() else -1,
									children_d_ids=self.reader.relmap_d.get(i, list()),
									children_f_ids=self.reader.relmap_f.get(i, list()),
								) for i, x in enumerate(self.reader.main_d)
							}
						else:
							raise ValueError(type(self.reader))
					with TimerLog(f'Admin[{self.reader.logname}] - file mapping (<le>{len(self.reader.main_f)}</le> files)'):
						if isinstance(self.reader, ReaderNLEv10):
							m_f = {
								i: Northlight.File(
									admin=self, index=i, parent_idx=x.parent_idx, name=file_names[i],
									next_id=x.next_id,
									out_size=x.size,
									metadata_offset=0,
									metadata_size=0,
									chunks_ids=[i],
									datahash=x.data_crc
								) for i, x in enumerate(self.reader.main_f)
							}
						elif isinstance(self.reader, ReaderNLEv20):
							m_f = {
								i: Northlight.File(
									admin=self, index=i, parent_idx=x.parent_idx, name=file_names[i],
									next_id=i + 1 if i != len(self.reader.main_f) else -1,
									out_size=x.out_size,
									metadata_offset=x.metadata.ofst,
									metadata_size=x.metadata.size,
									chunks_ids=list(zz // 16 for zz in range(x.chunks.ofst, x.chunks.ofst + x.chunks.size, 16)),
									datahash=None,
								) for i, x in enumerate(self.reader.main_f)
							}
						else:
							raise ValueError(type(self.reader))
					self._tree = Northlight.TreeAdmin(admin=self, fldr=Northlight.Mapper(admin=self, mapping=m_d), file=Northlight.Mapper(admin=self, mapping=m_f),
					                                  prefix=self.reader.pfx)
			return self._tree
		
		@tree.deleter
		def tree(self):
			self._tree = None
		
		@property
		def data(self) -> Northlight.DataAdmin:
			if self._data is None:
				rdr = self.reader  # type: ignore
				if isinstance(rdr, ReaderNLEv10):
					chnk = {i: Northlight.Chunk(admin=self, index=i, compressed=False, archive_idx=0, offset=x.offset, size_decompressed=x.size, size_compressed=0) for i, x in
					        enumerate(rdr.main_f)}
					arch = Northlight.Mapper(admin=self, mapping={0: Northlight.Archive(admin=self, index=0, path=rdr.path)})
				elif isinstance(rdr, ReaderNLEv20):
					chnk = {
						i: Northlight.Chunk(admin=self, index=i, compressed='lz4' if x.lz4 else False, archive_idx=x.archive_idx, offset=x.offset, size_decompressed=x.decompressed,
						                    size_compressed=x.compressed) for i, x in enumerate(rdr.cache_chnk)}
					pathdict_arch = rdr.build_strdict_option('arch')
					arch: Northlight.Mapper[Northlight.Archive] = Northlight.Mapper(admin=self, mapping={
						i: Northlight.Archive(admin=self, index=i, path=rdr.path.parent / pathdict_arch[i], hash=x.hash) for i, x in enumerate(rdr.cache_arch)})
				else:
					raise ValueError(type(self.reader))
				self._data = Northlight.DataAdmin(admin=self, chnk=Northlight.Mapper(admin=self, mapping=chnk), arch=arch)
			return self._data
		
		@data.deleter
		def data(self):
			self._data = None
		
		@property
		def meta(self) -> Northlight.MetaAdmin:
			if self._meta is None:
				if isinstance(self.reader, ReaderNLEv10):
					pth = self.reader.path.with_suffix('.packmeta')
					if pth.is_file():
						self._meta = Northlight.MetaAdmin(admin=self, path=self.reader.path.with_suffix('.packmeta'))
					else:
						self._meta = Northlight.MetaAdmin(admin=self)
				elif isinstance(self.reader, ReaderNLEv20):
					self._meta = Northlight.MetaAdmin(admin=self, metadata_types=self.reader.build_strdict_option('mdty'))
				else:
					raise ValueError
			return self._meta
		
		@meta.deleter
		def meta(self):
			self._meta = None
		
		def dict(self):
			return {
				"File"   : self.path,
				"Version": self.reader.version,
				"Tree"   : self.tree.dict(),
				"Data"   : self.data.dict(),
			}
		
		def size(self):
			return self.path.stat().st_size
		
		def __len__(self):
			return self.path.stat().st_size
	
	@dataclass
	class TreeAdmin:
		admin: Northlight.Admin
		fldr: Northlight.Mapper[Northlight.Folder]
		file: Northlight.Mapper[Northlight.File]
		prefix: str
		
		def dict(self):
			return {
				"Prefix" : self.prefix,
				"Folders": len(self.fldr.list),
				"Files"  : len(self.file.list),
				"Size"   : byter(self.file.total_size),
			}
	
	@dataclass
	class DataAdmin:
		admin: Northlight.Admin
		chnk: Northlight.Mapper[Northlight.Chunk]
		arch: Northlight.Mapper[Northlight.Archive]
		export_path: Path = field(init=False)
		
		def __post_init__(self):
			self.export_path = self.admin.instance.app.expo / self.admin.instance.key / self.admin.path.stem
		
		def dict(self):
			return {
				"Chunks"  : len(self.chnk.list),
				"Archives": len(self.arch.list)
			}
	
	@dataclass
	class MetaAdmin:
		admin: Northlight.Admin
		path: Path | None = field(default=None)
		metadata_types: dict[int, str] = field(default_factory=dict)
		
		def dict(self):
			return {
				"Path"          : str(self.path),
				"Metadata Types": self.metadata_types
			}
		
		def get(self, offset: int, size: int) -> bytes:
			if self.path is None:
				return b''
			else:
				with Stream(self.path, spos=offset) as f:
					return f[size]
	
	@dataclass
	class GenericVFS(GenericItem, ABC):
		parent_idx: int = field(kw_only=True)
		name: str = field(kw_only=True)
		next_id: int = field(kw_only=True)
		
		@property
		def parent(self) -> Northlight.Folder | None:
			if self.parent_idx == -1:
				return None
			elif isinstance(self, Northlight.Folder) and (self.parent_idx == self.index):
				return None
			else:
				return self.admin.tree.fldr[self.parent_idx]
		
		@property
		def parents(self) -> list[Northlight.Folder]:
			parentlist = list()
			if self.parent is not None:
				parentlist.append(self.parent)
				parentlist.extend(self.parent.parents)
			return parentlist
		
		@cached_property
		def depth(self) -> int:
			if self.parent is None:
				return 0
			else:
				return self.parent.depth + 1
		
		@cached_property
		def export_path(self) -> Path:
			rtrn = Path(f"{self.admin.data.export_path}\\{self.path_raw().replace(':', '_')}")
			rtrn.parent.mkdir(parents=True, exist_ok=True)
			return rtrn
		
		def path(self, mode: Literal['std', 'raw'] = 'std') -> str:
			if self.parent is None:
				return self.name if mode == 'raw' else '/'.join([self.admin.tree.prefix, self.name])
			else:
				return '/'.join([self.parent.path(mode), self.name])
		
		def path_raw(self) -> str:
			if self.parent is None:
				return self.name
			else:
				return '/'.join([self.parent.path_raw(), self.name])
		
		def dict(self) -> dict[str, int | str]:
			return dict(
				index=self.index,
				parent_idx=self.parent_idx,
				name=self.name,
				path=self.path('raw'),
				next_id=self.next_id,
			)
		
		@abstractmethod
		def next(self) -> Self | None:
			...
	
	@dataclass
	class Folder(GenericVFS):
		file_index: int = field(kw_only=True)
		file_count: int = field(kw_only=True)
		next_count: int = field(kw_only=True, repr=False)
		first_child_d_id: int = field(kw_only=True, repr=False)
		first_child_f_id: int = field(kw_only=True, repr=False)
		children_d_ids: list[int] = field(kw_only=True, repr=False)
		children_f_ids: list[int] = field(kw_only=True, repr=False)
		
		def nested_children(self) -> list[Northlight.Folder | Northlight.File]:
			all_kids = self.children()
			for child in self.children():
				if isinstance(child, Northlight.Folder):
					all_kids.extend(child.nested_children())
			return all_kids
		
		def nested_children_folders(self) -> list[Northlight.Folder]:
			all_kids = self.children_folders()
			for child in self.children():
				if isinstance(child, Northlight.Folder):
					all_kids.extend(child.nested_children_folders())
			return all_kids
		
		def nested_children_files(self) -> list[Northlight.File]:
			all_kids = self.children_files()
			for child in self.children():
				if isinstance(child, Northlight.File):
					all_kids.append(child)
				if isinstance(child, Northlight.Folder):
					all_kids.extend(child.nested_children_files())
			return all_kids
		
		def children(self) -> list[Northlight.Folder | Northlight.File]:
			return [*self.children_folders(), *self.children_files()]
		
		def children_folders(self) -> list[Northlight.Folder]:
			return [self.admin.tree.fldr[x] for x in self.children_d_ids]
		
		def children_files(self) -> list[Northlight.File]:
			return [self.admin.tree.file[x] for x in self.children_f_ids]
		
		def first_child_folder(self) -> Northlight.Folder | None:
			return self.admin.tree.fldr[self.first_child_d_id] if self.first_child_d_id != -1 else None
		
		def first_child_file(self) -> Northlight.File | None:
			return self.admin.tree.file[self.first_child_f_id] if self.first_child_f_id != -1 else None
		
		@property
		def size(self) -> int:
			return len(self.children_d_ids) + len(self.children_f_ids)
		
		def dict(self) -> dict[str, Any]:
			return dict(
				vfs=super(Northlight.Folder, self).dict(),
				children=self.size,
				children_folders=len(self.children_folders()),
				children_files=len(self.children_files()),
			)
		
		def next(self) -> Northlight.Folder | None:
			return self.admin.tree.fldr[self.next_id] if self.next_id != -1 else None
	
	@dataclass
	class File(GenericVFS):
		chunks_ids: list[int] = field(kw_only=True)
		out_size: int = field(kw_only=True)
		metadata_offset: int = field(kw_only=True)
		metadata_size: int = field(kw_only=True)
		datahash: bytes | None = field(kw_only=True)
		
		@property
		def size(self) -> int:
			return sum(x.size for x in self.chunks)
		
		@property
		def chunks(self) -> list[Northlight.Chunk]:
			return [self.admin.data.chnk.mapping[x] for x in self.chunks_ids]
		
		@property
		def is_exported(self) -> bool:
			return self.export_path.is_file()
		
		def export(self):
			self.export_path.write_bytes(self._read())
		
		@property
		def data(self) -> bytes:
			if not self.is_exported:
				self.export()
			return self.export_path.read_bytes()
		
		def getdata(self) -> bytes:
			if not self.is_exported:
				self.export()
			return self.export_path.read_bytes()
		
		@property
		def extension(self) -> str:
			return self.name.split('.')[-1]
		
		def _read(self) -> bytes:
			return b''.join([chunk.read() for chunk in self.chunks])
		
		def read_first_chunk(self) -> bytes:
			if len(self.chunks_ids) == 0:
				logger.error("Tried reading a file with no chunks...")
				return b''
			else:
				return self.chunks[0].read()
		
		def dict(self):
			return dict(
				vfs=super(Northlight.File, self).dict(),
				extension=self.extension,
				chunks_ids=self.chunks_ids,
				out_size=self.out_size,
				metadata_offset=self.metadata_offset,
				metadata_size=self.metadata_size,
				datahash=self.datahash.hex() if self.datahash is not None else "ffffffff",
			)
		
		def next(self) -> Northlight.File | None:
			return self.admin.tree.file[self.next_id] if self.next_id != -1 else None
		
		def __len__(self):
			return self.out_size
	
	# @property
	# def metadata(self) -> bytes:
	#	return self.admin.meta.get(self.metadata_offset, self.metadata_size)
	
	@dataclass
	class Mapper[T: GenericItem]:
		admin: Northlight.Admin = field(kw_only=True)
		mapping: dict[int, T] = field(kw_only=True)
		
		def __int__(self) -> int:
			return self.total_size
		
		def __len__(self) -> int:
			return len(self.mapping)
		
		def __getitem__(self, key: int) -> T:
			return self.mapping[key]
		
		def __iter__(self) -> Generator[T, None, None]:
			for item in self.list:
				yield item
		
		@property
		def list(self) -> list[T]:
			return list(self.mapping.values())
		
		@property
		def total_size(self) -> int:
			return sum(self.size_dict.values())
		
		@property
		def size_dict(self) -> dict[int, int]:  # noinspection PyTypeChecker
			return {k: v.size for k, v in self.mapping.items()}
	
	@dataclass
	class Archive(GenericItem):
		path: Path = field(kw_only=True)
		hash: bytes | None = field(kw_only=True, default=None)
		
		@cached_property
		def size(self) -> int:
			return self.path.stat().st_size
		
		@property
		def chunks(self):
			for chunk in self.admin.data.chnk.mapping.values():
				if chunk.archive_idx == self.index:
					yield chunk
		
		def dict(self):
			return {
				'path': self.path,
				'hash': self.hash
			}
	
	@dataclass
	class Chunk(GenericItem):
		compressed: Literal['lz4', False] = field(kw_only=True)
		archive_idx: int = field(kw_only=True)
		offset: int = field(kw_only=True)
		size_decompressed: int = field(kw_only=True)
		size_compressed: int = field(kw_only=True)
		
		@property
		def size(self) -> int:
			return self.size_compressed if self.compressed else self.size_decompressed
		
		@property
		def decompressed_size(self) -> int:
			return self.size_decompressed if self.compressed else self.size_compressed
		
		@property
		def compression_ratio(self) -> float:
			return round((self.size / self.decompressed_size) * 100, 2)
		
		@property
		def archive(self):
			return self.admin.data.arch[self.archive_idx]
		
		def read(self) -> bytes:
			with Stream(self.archive.path, spos=self.offset) as f:
				match self.compressed:
					case 'lz4':
						return f.read_lz4_block(offset=self.offset, cmp_size=self.size_compressed, dcp_size=self.size_decompressed, is_compressed=bool(self.compressed))
					case False:
						return f.read(self.size)
		
		def dict(self):
			return {
				'compressed': self.compressed,
				'archive_idx': self.archive_idx,
				'offset': self.offset,
				'size_decompressed': self.size_decompressed,
				'size_compressed': self.size_compressed,
			}