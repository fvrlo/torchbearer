from functools import cached_property
from typing import Protocol

from mulch import StreamObject, StreamFields

__all__ = [
	"OFSZ",
	"Objects",
	"Abstracts"
]


# TODO: document this (yeah it reads the formats, but explain the structures)




class OFSZ(StreamObject):
	ofst: int = StreamFields.uint()
	size: int = StreamFields.uint()
	

class Abstracts:
	class D(Protocol):
		name_crc:           bytes
		next_id:            int
		parent_idx:         int
		flags:              bytes
		name_offset:        int
		first_child_d_id:   int
		first_child_f_id:   int
		
	class F(Protocol):
		name_crc:       bytes
		next_id:        int
		parent_idx:     int
		flags:          bytes
		name_offset:    int
		offset:         int
		size:           int
		data_crc:       bytes
		write_time:     int | None

class Objects:
	class D_AW1(StreamObject):
		name_crc:           bytes   = StreamFields.bytes(4)
		next_id:            int     = StreamFields.uint(4, 'big')
		parent_idx:         int     = StreamFields.uint(4, 'big')
		flags:              bytes   = StreamFields.bytes(4)
		name_offset:        int     = StreamFields.uint(4, 'big')
		first_child_d_id:   int     = StreamFields.uint(4, 'big')
		first_child_f_id:   int     = StreamFields.uint(4, 'big')
	
	class D_AWR(StreamObject):
		name_crc:           bytes   = StreamFields.bytes(4, rpad=4)
		next_id:            int     = StreamFields.uint(8, 'big')
		parent_idx:         int     = StreamFields.uint(8, 'big')
		flags:              bytes   = StreamFields.bytes(4, rpad=4)
		name_offset:        int     = StreamFields.uint(8, 'big')
		first_child_d_id:   int     = StreamFields.uint(8, 'big')
		first_child_f_id:   int     = StreamFields.uint(8, 'big')
	
	class D_LE7(StreamObject):
		name_crc:           bytes   = StreamFields.bytes(4)
		next_id:            int     = StreamFields.uint(4, 'little')
		parent_idx:         int     = StreamFields.uint(4, 'little')
		flags:              bytes   = StreamFields.bytes(4)
		name_offset:        int     = StreamFields.uint(4, 'little')
		first_child_d_id:   int     = StreamFields.uint(4, 'little')
		first_child_f_id:   int     = StreamFields.uint(4, 'little')
	
	class D_LE8(StreamObject):
		name_crc:           bytes   = StreamFields.bytes(4)
		next_id:            int     = StreamFields.uint(8, 'little')
		parent_idx:         int     = StreamFields.uint(8, 'little')
		flags:              bytes   = StreamFields.bytes(4)
		name_offset:        int     = StreamFields.uint(8, 'little')
		first_child_d_id:   int     = StreamFields.uint(8, 'little')
		first_child_f_id:   int     = StreamFields.uint(8, 'little')
	
	class F_AW1(StreamObject):
		name_crc:       bytes   = StreamFields.bytes(4)
		next_id:        int     = StreamFields.uint(4, 'big')
		parent_idx:     int     = StreamFields.uint(4, 'big')
		flags:          bytes   = StreamFields.bytes(4)
		name_offset:    int     = StreamFields.uint(4, 'big')
		offset:         int     = StreamFields.uint(8, 'big')
		size:           int     = StreamFields.uint(8, 'big')
		data_crc:       bytes   = StreamFields.bytes(4)
		write_time:     None    = None
	
	class F_AWR(StreamObject):
		name_crc:       bytes   = StreamFields.bytes(4, rpad=4)
		next_id:        int     = StreamFields.uint(8, 'big')
		parent_idx:     int     = StreamFields.uint(8, 'big')
		flags:          bytes   = StreamFields.bytes(4, rpad=4)
		name_offset:    int     = StreamFields.uint(8, 'big')
		offset:         int     = StreamFields.uint(8, 'big')
		size:           int     = StreamFields.uint(8, 'big')
		data_crc:       bytes   = StreamFields.bytes(4, rpad=4)
		write_time:     None    = None
	
	class F_LE7(StreamObject):
		name_crc:       bytes   = StreamFields.bytes(4)
		next_id:        int     = StreamFields.uint(4, 'little')
		parent_idx:     int     = StreamFields.uint(4, 'little')
		flags:          bytes   = StreamFields.bytes(4)
		name_offset:    int     = StreamFields.uint(4, 'little')
		offset:         int     = StreamFields.uint(8, 'little')
		size:           int     = StreamFields.uint(8, 'little')
		data_crc:       bytes   = StreamFields.bytes(4)
		write_time:     int     = StreamFields.uint(8, 'little')
	
	class F_LE8(StreamObject):
		name_crc:       bytes   = StreamFields.bytes(4)
		next_id:        int     = StreamFields.uint(8, 'little')
		parent_idx:     int     = StreamFields.uint(8, 'little')
		flags:          bytes   = StreamFields.bytes(4)
		name_offset:    int     = StreamFields.uint(8, 'little')
		offset:         int     = StreamFields.uint(8, 'little')
		size:           int     = StreamFields.uint(8, 'little')
		data_crc:       bytes   = StreamFields.bytes(4)
		write_time:     int     = StreamFields.uint(8, 'little')

	class RMDTOC_Chunk(StreamObject):
		lz4:            bool    = StreamFields.bool()
		archive_idx:    int     = StreamFields.uint(2, 'little')
		_offset:        bytes   = StreamFields.bytes(5)
		decompressed:   int     = StreamFields.uint(4, 'little')
		compressed:     int     = StreamFields.uint(4, 'little')
		
		@property
		def offset(self):
			return int.from_bytes(self._offset, 'little')
		
	class RMDTOC_D(StreamObject):
		parent_idx: int     = StreamFields.uint(4, 'little') # parent id
		next_id:    int     = StreamFields.uint(4, 'little') # first child id
		next_count: int     = StreamFields.uint(4, 'little') # child count
		file_index: int     = StreamFields.uint(4, 'little') # if file_count is not zero: index of folders that contain files
		file_count: int     = StreamFields.uint(4, 'little') # file children
		name:       OFSZ    = StreamFields.subitem(OFSZ)

	class RMDTOC_F(StreamObject):
		chunks:     OFSZ    = StreamFields.subitem(OFSZ)
		parent_idx: int     = StreamFields.uint(4, 'little')
		name:       OFSZ    = StreamFields.subitem(OFSZ)
		size:       int     = StreamFields.uint(4, 'little')
		metadata:   OFSZ    = StreamFields.subitem(OFSZ)
		
	class RMDTOC_Archive(StreamObject):
		path:   OFSZ    = StreamFields.subitem(OFSZ)
		hash:   bytes   = StreamFields.bytes(8)

	class RMDTOC_Table(StreamObject):
		"""Offset table, sized at 88 bytes."""

		magic: str = StreamFields.str(4)  # COTR, aka reversed R(emedy)TOC
		vrsn: int = StreamFields.int(4)
		tabl: OFSZ = StreamFields.subitem(OFSZ)
		arch: OFSZ = StreamFields.subitem(OFSZ)
		fldr: OFSZ = StreamFields.subitem(OFSZ)
		file: OFSZ = StreamFields.subitem(OFSZ)
		stng: OFSZ = StreamFields.subitem(OFSZ)
		mdty: OFSZ = StreamFields.subitem(OFSZ)
		mtdt: OFSZ = StreamFields.subitem(OFSZ)
		unk0: OFSZ = StreamFields.subitem(OFSZ)
		unk1: OFSZ = StreamFields.subitem(OFSZ)
		chnk: OFSZ = StreamFields.subitem(OFSZ)
		
		@cached_property
		def dcp_size(self):
			return -(
					sum(
						[
							(self.arch.size * 16),
							(self.fldr.size * 28),
							(self.file.size * 32),
							(self.mdty.size * 8),
							self.chnk.size,
							self.stng.size,
							self.mtdt.size
						]
					) // -8
			) * 8
