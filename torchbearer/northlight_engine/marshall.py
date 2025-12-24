from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar, final, Self

import numpy as np

from mulch import Stream

__all__ = [
	"OFSZ",
	"NPD"
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
			return dict(
				index=index,
				name_crc=bytes(void['name_crc']),
				next_id=int(void['next_id']),
				parent_idx=int(void['parent_idx']),
				flags=bytes(void['flags']),
			    name_offset=int(void['name_offset'])
			)
	
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
		dtype: ClassVar[np.dtype] = np.dtype([('lz4', '?'), ('archive_idx', '<u2'), ('offset', 'V5'), ('decompressed', '<u4'), ('compressed', '<u4')])
		
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
			        enumerate(np.frombuffer(stream.read(ofsz.size), dtype=cls.dtype, count=ofsz.size // 16))]  # type: ignore
	
	@dataclass
	class RMDTOC_D:
		dtype: ClassVar[np.dtype] = np.dtype([("parent_idx", '<u4'), ("next_id", '<u4'), ("next_count", '<u4'), ("file_index", '<u4'), ("file_count", '<u4'), ("name", OFSZ)])
		
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
			        enumerate(np.frombuffer(stream.read(cls.dtype.itemsize * ofsz.size), dtype=cls.dtype, count=ofsz.size))]  # type: ignore
	
	@dataclass
	class RMDTOC_F:
		dtype: ClassVar[np.dtype] = np.dtype([("chunks", OFSZ), ("parent_idx", '<u4'), ("name", OFSZ), ("size", '<u4'), ("metadata", OFSZ)])
		
		index: int
		parent_idx: int
		name: OFSZ
		chunks: OFSZ
		metadata: OFSZ
		size: int
		
		@classmethod
		def parse(cls, stream: Stream, ofsz: OFSZ) -> list[Self]:
			stream.seek(ofsz.ofst)
			return [
				cls(index=i, name=OFSZ.via_np(x['name']), chunks=OFSZ.via_np(x['chunks']), metadata=OFSZ.via_np(x['metadata']), parent_idx=int(x['parent_idx']),  # type: ignore
				    size=int(x['size'])) for i, x in
				enumerate(np.frombuffer(stream.read(cls.dtype.itemsize * ofsz.size), dtype=cls.dtype, count=ofsz.size))]  # type: ignore
	
	@dataclass
	class RMDTOC_Archive:
		dtype: ClassVar[np.dtype] = np.dtype([('path', OFSZ), ('hash', 'V8')])
		
		index: int
		path: OFSZ
		hash: bytes
		
		@classmethod
		def parse(cls, stream: Stream, ofsz: OFSZ) -> list[Self]:
			stream.seek(ofsz.ofst)
			return [cls(index=i, path=OFSZ.via_np(x['path']), hash=bytes(x['hash'])) for i, x in  # type: ignore
			        enumerate(np.frombuffer(stream.read(cls.dtype.itemsize * ofsz.size), dtype=cls.dtype, count=ofsz.size))]
	
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
				(self.arch.size * NPD.RMDTOC_Archive.dtype.itemsize),
				(self.fldr.size * NPD.RMDTOC_D.dtype.itemsize),
				(self.file.size * NPD.RMDTOC_F.dtype.itemsize),
				(self.mdty.size * 8),
				self.chnk.size, self.stng.size, self.mtdt.size]) // -8) * 8
