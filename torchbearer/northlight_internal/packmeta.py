from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from pathlib import Path
from zlib import crc32
from loguru import logger

from mulch import Stream
from .cid_base import Datastream, DSC, FileMetadataEntry_v1, FileMetadataEntry_v2, ResourceID_content_v1, ResourceID_v1
from .types_general import RID





# valid versions for packmeta: 1.7, 1.8, 1.9
# 1.2/1.3 don't have a metadata system like this, and 2.x uses a very different one





# 1.7 predefines metadata types for the PackMetaType list, only providing counts.
packmeta_7_nameindex = [
	"content::FileInfoMetadata",
	"content::ResourceMetadata",
	"content::VersionsMetadata",
	"content::TextureMetadata",
	"content::MeshMetadata",
	"content::FoliageMeshMetadata",
	"content::HavokAnimationMetadata",
	"content::ParticleSystemMetadata",
]


class PackMetaType:
	inum: int
	hash: str
	name: str
	size: int

	def __init__(self, inum: int, stream: Stream, vrsn_minor: int):
		self.inum = inum
		if vrsn_minor == 7:
			self.name = packmeta_7_nameindex[inum]
			self.hash = crc32(self.name.lower().encode()).to_bytes(4,'big').hex().upper()
		else:
			self.hash = stream[4].hex().upper()
			self.name = stream.string(int(stream))
		self.size = int(stream)
		
	def dict(self):
		return {'MetadataType': f'hash={self.hash}, name={self.name}, size={self.size}'}


@dataclass
class PackMetaFile:
	ofst:   int                         = field(kw_only=True)
	name:   str                         = field(kw_only=True)
	rid:    RID | None                  = field(kw_only=True)
	meta:   list[DSC]   = field(kw_only=True)

	def dict(self):
		try:
			return {"Offset": self.ofst, "Name": self.name, "RID": self.rid, "Meta": [x.dict() for x in self.meta]}
		except AttributeError as e:
			logger.error(f"PackMetaFile name={self.name}, offset={self.ofst}")
			for i, x in enumerate(self.meta):
				logger.error(f"PackMetaFile meta {i}: {x.dict()}")
			raise e


class PackMeta:
	file:           Path
	count_files:    int                 # file count
	count_mtdtt:    int                 # idk, metadata tree count?
	count_telem:    int                 # elements on the metadata trees
	count_nsize:    int                 # namesize
	names:          list[str]           # element names
	ofsts:          list[int]           # element offsets
	rid_ofsts:      dict[int, ResourceID_content_v1| ResourceID_v1]      # dict of offset key for RID value
	pmt_defs:       list[PackMetaType]
	pmf_defs:       list[PackMetaFile]
	
	def __init__(self, file: Path, vrsn_minor: int):
		self.file = file
		with Stream(file) as stream:
			logger.info(f"Processing packmeta file '{file}' (length: {len(stream)}, minor version: {vrsn_minor})")
			stream.seek(0)
			
			self.count_files = int(stream)
			self.count_mtdtt = int(stream)
			self.count_telem = int(stream)
			self.count_nsize = int(stream)
			self.names = [stream.nts() for _ in range(self.count_files)]
			assert stream.tell() == self.count_nsize + 16
			self.ofsts = [int(stream) for _ in range(self.count_files)]
			self.rid_ofsts = {int(stream): x for x in [ResourceID_content_v1.containerless(stream) if vrsn_minor == 7 else ResourceID_v1.containerless(stream) for _ in range(int(stream))]}
			# logger.info(f"files={self.head.files}, mtdtt={self.head.mtdtt}, telem={self.head.telem}, nsize={self.head.nsize}, rids={len(self.rids.items)}")
			
			self.pmt_defs = [PackMetaType(i, stream, vrsn_minor) for i in range(int(stream))]
			
			tree: list[list[DSC]] = [[Datastream.beef_container(stream) for _ in range(x.size)] for x in self.pmt_defs]
			fme_list: list[DSC[FileMetadataEntry_v1 | FileMetadataEntry_v2]] = [Datastream.beef_container(stream) for _ in range(self.count_files)] # type: ignore
			fme_dict = {x.data.ofst: x for x in fme_list}
		
		self.pmf_defs = list()
		for i, k in enumerate(self.ofsts):
			fmeget = fme_dict.get(k, None)
			metas = [tree[x.data.meta_index][x.data.file_index] for x in fmeget.data.subitems] if fmeget is not None else []
			self.pmf_defs.append(PackMetaFile(ofst=k, name=self.names[i], rid=self.rid_ofsts.get(k, None), meta=metas))
	
	def dict(self) -> dict:
		return {'tdefs': [x.dict() for x in self.pmt_defs], 'files': [x.dict() for x in self.pmf_defs]}
	
	def log_partial_files(self):
		for x in self.pmf_defs:
			if len(x.meta) == 0:
				if x.rid is None:
					logger.info(f"File with no metadata: {x.name}")
				else:
					logger.info(f"File with no metadata: {x.name} (RID {x.rid})")
			elif x.rid is None:
				logger.info(f"File with no RID: {x.name}")
	
	@staticmethod
	def log_instances_containers():
		for k, v in DSC.__dsc_objs__.items():
			logger.info(f"Container instance count for {k.__name__}: {len(v)}")
		
	@staticmethod
	def log_instances_datastream():
		for k, v in Datastream.__ds_meta_objs__.items():
			logger.info(f"Datastream instance count for {k.__ds_name__} v{k.__ds_vrsn__}: {len(v)}")
	
	@staticmethod
	def log_unknown_dsc_subtypes():
		for k, v in Datastream.__ds_meta_objs__.items():
			annos = inspect.get_annotations(k)
			for subfield in k.__so_fields__():
				annotype = annos[subfield.__bsf_orig__]
				if annotype == "DatastreamContainer":
					flds = ' | '.join({subfield.__get__(instance, k).data.__class__.__name__ for instance in k.__ds_inst__()})
					logger.info(f"Likely subtype on class {k.__name__} for field {subfield.__bsf_orig__}: DatastreamContainer[{flds}]")
				elif annotype == "list[DatastreamContainer]":
					listinstances = [subfield.__get__(instance, k) for instance in k.__ds_inst__()]
					flds = ' | '.join({x.data.__class__.__name__ for y in listinstances for x in y})
					logger.info(f"Likely subtype on class {k.__name__} for field {subfield.__bsf_orig__}: list[DatastreamContainer[{flds}]]")
	
	@staticmethod
	def debug_all_packmetas():
		z = list()
		for pmf in Path('D:/northlight').rglob('*.packmeta'):
			if 'control' in str(pmf).lower():
				z.append(PackMeta(pmf, 9))
			elif 'quantum' in str(pmf).lower():
				z.append(PackMeta(pmf, 8))
			else:
				z.append(PackMeta(pmf, 7))
		
		PackMeta.log_instances_containers()
		PackMeta.log_instances_datastream()
		PackMeta.log_unknown_dsc_subtypes()


if __name__ == '__main__':
	PackMeta.debug_all_packmetas()