from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generator, Literal, Self
from pathlib import Path
from functools import cached_property
from dataclasses import dataclass, field

from loguru import logger

from mulch import byter, Helper, Stream, TimerLog

from .configs import InstanceConfig
from .readers import Reader, ReaderNLEv10, ReaderNLEv20

__all__ = [
	"Admin",
	"TreeAdmin",
	"MetaAdmin",
	"DataAdmin",
	"Folder",
	"File"
]



@dataclass
class GenericVFS(ABC):
	admin:      Admin   = field(kw_only=True, repr=False)
	index:      int     = field(kw_only=True)
	parent_idx: int     = field(kw_only=True)
	name:       str     = field(kw_only=True)
	next_id:    int     = field(kw_only=True)

	@property
	@abstractmethod
	def size(self) -> int:
		...
	
	@property
	def parent(self) -> Folder | None:
		if self.parent_idx == -1:
			return None
		elif isinstance(self, Folder) and (self.parent_idx == self.index):
			return None
		else:
			return self.admin.tree.fldr[self.parent_idx]
	
	@property
	def parents(self) -> list[Folder]:
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
		rtrn = Path(f"{self.admin.export_path}\\{self.path_raw().replace(':', '_')}")
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
	file_index:         int         = field(kw_only=True)
	file_count:         int         = field(kw_only=True)
	next_count:         int         = field(kw_only=True, repr=False)
	first_child_d_id:   int         = field(kw_only=True, repr=False)
	first_child_f_id:   int         = field(kw_only=True, repr=False)
	children_d_ids:     list[int]   = field(kw_only=True, repr=False)
	children_f_ids:     list[int]   = field(kw_only=True, repr=False)
	
	@property
	def size(self) -> int:
		return len(self.children_d_ids) + len(self.children_f_ids)
	
	def dict(self) -> dict[str, Any]:
		return dict(
			vfs=super(Folder, self).dict(),
			children=self.size,
			children_folders=len(self.children_d_ids),
			children_files=len(self.children_f_ids),
		)
	
	def next(self) -> Folder | None:
		return self.admin.tree.fldr[self.next_id] if self.next_id != -1 else None


@dataclass
class File(GenericVFS):
	chunks_ids:         list[int]       = field(kw_only=True)
	out_size:           int             = field(kw_only=True)
	metadata_offset:    int             = field(kw_only=True)
	metadata_size:      int             = field(kw_only=True)
	datahash:           bytes | None    = field(kw_only=True)
	
	@property
	def size(self) -> int:
		return sum(x.size for x in self.chunks)
	
	@property
	def chunks(self) -> list[Chunk]:
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
			vfs=super(File, self).dict(),
			extension=self.extension,
			chunks_ids=self.chunks_ids,
			out_size=self.out_size,
			metadata_offset=self.metadata_offset,
			metadata_size=self.metadata_size,
			datahash=self.datahash.hex() if self.datahash is not None else "ffffffff",
		)
	
	def next(self) -> File | None:
		return self.admin.tree.file[self.next_id] if self.next_id != -1 else None
	
	def __len__(self):
		return self.out_size


@dataclass
class Admin[T_Reader: Reader]:
	path: Path
	instance: InstanceConfig
	
	_reader: T_Reader | None = field(default=None)
	_tree: TreeAdmin | None = field(default=None)
	_data: DataAdmin | None = field(default=None)
	_meta: MetaAdmin | None = field(default=None)
	
	@property
	def export_path(self):
		return self.instance.app.expo / self.instance.key / self.path.stem
	
	@property
	def is_set(self) -> bool:
		return self._reader is not None
	
	@property
	def name(self):
		return self.path.stem
	
	@property
	def extension(self):
		return self.path.suffix[1:]
	
	def reader(self) -> T_Reader:
		if self._reader is None:
			self._reader = Reader.factory(self.instance, self.path)
		return self._reader
	
	@property
	def tree(self) -> TreeAdmin:
		if self._tree is None:
			self._tree = TreeAdmin(admin=self, rdr=self.reader())
		return self._tree

	@property
	def data(self) -> DataAdmin:
		if self._data is None:
			self._data = DataAdmin(admin=self, rdr=self.reader())
		return self._data
	
	@property
	def meta(self) -> MetaAdmin:
		if self._meta is None:
			rdr = self.reader()
			if isinstance(rdr, ReaderNLEv10):
				pth = rdr.path.with_suffix('.packmeta')
				if pth.is_file():
					self._meta = MetaAdmin(admin=self, path=rdr.path.with_suffix('.packmeta'))
				else:
					self._meta = MetaAdmin(admin=self)
			elif isinstance(rdr, ReaderNLEv20):
				self._meta = MetaAdmin(admin=self, metadata_types=rdr.build_strdict_option('mdty'))
			else:
				raise ValueError
		return self._meta
	
	@property
	def extensions(self):
		return Helper.occurences([f.extension for f in self.tree.file.mapping.values()])
	
	def clear(self):
		self._reader = None
		self._tree = None
		self._data = None
		self._meta = None
	
	def dict(self):
		return {
			"File"   : self.path,
			"Version": self.reader().version,
			"Tree"   : self.tree.dict(),
			"Data"   : self.data.dict(),
		}
	
	def size(self):
		return self.path.stat().st_size
	
	def __len__(self):
		return self.path.stat().st_size


class TreeAdmin:
	admin: Admin
	fldr: Mapper[Folder]
	file: Mapper[File]
	prefix: str
	
	def dict(self):
		return {
			"Prefix" : self.prefix,
			"Folders": len(self.fldr.list),
			"Files"  : len(self.file.list),
			"Size"   : byter(self.file.total_size),
		}
	
	def __init__(self, admin: Admin, rdr: Reader):
		self.admin = admin
		self.prefix = rdr.pfx
		with TimerLog(f'TreeAdmin[{rdr.logname}] - filesystem mapping'):
			fldr_names = rdr.build_strdict_option('fldr')
			file_names = rdr.build_strdict_option('file')
			with TimerLog(f'TreeAdmin[{rdr.logname}] - fldr mapping (<le>{len(rdr.main_d)}</le> fldrs)'):
				if isinstance(rdr, ReaderNLEv10):
					m_d = {i: Folder(
							admin=admin, index=i, parent_idx=x.parent_idx, next_id=x.next_id, name=fldr_names[i],
							file_index=i,
							file_count=len(rdr.relmap_f[i]),
							next_count=len(rdr.relmap_d[i]) + len(rdr.relmap_f[i]),
							first_child_d_id=x.first_child_d_id,
							first_child_f_id=x.first_child_f_id,
							children_d_ids=rdr.relmap_d.get(i, list()),
							children_f_ids=rdr.relmap_f.get(i, list()),
						) for i, x in enumerate(rdr.main_d)}
				elif isinstance(rdr, ReaderNLEv20):
					m_d = {i: Folder(
							admin=admin, index=i, parent_idx=x.parent_idx, next_id=x.next_id, name=fldr_names[i],
							file_index=x.file_index,
							file_count=x.file_count,
							next_count=x.next_count,
							first_child_d_id=(rdr.relmap_d[i][0] if len(rdr.relmap_d[i]) > 0 else -1) if i in rdr.relmap_d.keys() else -1,
							first_child_f_id=(rdr.relmap_f[i][0] if len(rdr.relmap_f[i]) > 0 else -1) if i in rdr.relmap_f.keys() else -1,
							children_d_ids=rdr.relmap_d.get(i, list()),
							children_f_ids=rdr.relmap_f.get(i, list()),
						) for i, x in enumerate(rdr.main_d)}
				else:
					raise ValueError(type(rdr))
			with TimerLog(f'TreeAdmin[{rdr.logname}] - file mapping (<le>{len(rdr.main_f)}</le> files)'):
				if isinstance(rdr, ReaderNLEv10):
					m_f = {i: File(
							admin=admin, index=i, parent_idx=x.parent_idx, name=file_names[i],
							next_id=x.next_id,
							out_size=x.size,
							metadata_offset=0,
							metadata_size=0,
							chunks_ids=[i],
							datahash=x.data_crc
						) for i, x in enumerate(rdr.main_f)}
				elif isinstance(rdr, ReaderNLEv20):
					m_f = {i: File(
							admin=admin, index=i, parent_idx=x.parent_idx, name=file_names[i],
							next_id=i + 1 if i != len(rdr.main_f) else -1,
							out_size=x.size,
							metadata_offset=x.metadata.ofst,
							metadata_size=x.metadata.size,
							chunks_ids=list(zz // 16 for zz in range(x.chunks.ofst, x.chunks.ofst + x.chunks.size, 16)),
							datahash=None,
						) for i, x in enumerate(rdr.main_f)}
				else:
					raise ValueError(type(rdr))
		self.fldr = Mapper(admin=admin, mapping=m_d)
		self.file = Mapper(admin=admin, mapping=m_f)
	

class DataAdmin:
	admin: Admin
	chnk: Mapper[Chunk]
	arch: Mapper[Archive]
	
	def __init__(self, admin: Admin, rdr: Reader):
		self.admin = admin
		if isinstance(rdr, ReaderNLEv10):
			self.chnk = Mapper(
				admin=admin,
				mapping={
					i: Chunk(
						admin=admin,
						index=i,
						compressed=False,
						archive_idx=0,
						offset=x.offset,
						size_decompressed=x.size,
						size_compressed=0
					) for i, x in enumerate(rdr.main_f)
				}
			)
			self.arch = Mapper(admin=admin, mapping={0: Archive(admin=admin, index=0, path=rdr.path)})
		elif isinstance(rdr, ReaderNLEv20):
			self.chnk = Mapper(
				admin=admin,
				mapping={
					i: Chunk(
						admin=admin,
						index=i,
						compressed='lz4' if x.lz4 else False,
						archive_idx=x.archive_idx,
						offset=x.offset,
						size_decompressed=x.decompressed,
				        size_compressed=x.compressed
					) for i, x in enumerate(rdr.cache_chnk)
				}
			)
			pathdict_arch = rdr.build_strdict_option('arch')
			self.arch = Mapper(admin=admin, mapping={i: Archive(admin=admin, index=i, path=rdr.path.parent / pathdict_arch[i], hash=x.hash) for i, x in enumerate(rdr.cache_arch)})
		else:
			raise ValueError(type(rdr))
	
	def dict(self):
		return {
			"Chunks"  : len(self.chnk.list),
			"Archives": len(self.arch.list)
		}

@dataclass
class MetaAdmin:
	admin: Admin
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

# @property
# def metadata(self) -> bytes:
#	return self.admin.meta.get(self.metadata_offset, self.metadata_size)





@dataclass
class Archive:
	admin: Admin = field(kw_only=True, repr=False)
	index: int = field(kw_only=True)
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
class Chunk:
	admin: Admin = field(kw_only=True, repr=False)
	index: int = field(kw_only=True)
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


@dataclass
class Mapper[T: Folder | File | Archive | Chunk]:
	admin: Admin = field(kw_only=True, repr=False)
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

