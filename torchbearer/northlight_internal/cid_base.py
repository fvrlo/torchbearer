from __future__ import annotations

from collections import defaultdict
from weakref import WeakSet

from abc import ABC
from typing import ClassVar, final, Self

from loguru import logger

from mulch import Stream, ByteStreamField, StreamFields, StreamObject

from .types_general import BoundBox, RID

class Datastream[CType](ABC, StreamObject):
	__ds_meta_scls__: ClassVar[set[type[Datastream]]]                       = set()
	__ds_meta_dcls__: ClassVar[dict[str, type[Datastream]]]                 = dict()
	__ds_meta_objs__: ClassVar[dict[type[Datastream], WeakSet[Datastream]]] = defaultdict(WeakSet)
	
	__ds_name__: ClassVar[str]; """Datastream subclass name"""
	__ds_hash__: ClassVar[str]; """Datastream subclass hash"""
	__ds_vrsn__: ClassVar[int]; """Datastream subclass version"""

	container: CType
	
	@classmethod
	def __ds_inst__(cls) -> WeakSet[Self]:
		return Datastream.__ds_meta_objs__[cls]
	
	@classmethod
	def __ds_iden__(cls) -> str:
		return f"{cls.__ds_hash__} v{cls.__ds_vrsn__}"
	
	def __init__(self, container: CType, stream: Stream):
		self.container = container
		StreamObject.__init__(self, stream)
	
	def __init_subclass__(cls, *, name: str, vrsn: int, typehash: str = "FFFFFFFF"):
		cls.__ds_name__ = name
		cls.__ds_vrsn__ = vrsn
		cls.__ds_hash__ = typehash
		if typehash != "FFFFFFFF":
			iden = cls.__ds_iden__()
			if iden in Datastream.__ds_meta_dcls__.keys():
				logger.error(f"Duplicate subclass! '{iden}' is already defined as '{Datastream.__ds_meta_dcls__[iden].__name__}'")
				raise KeyError(iden)
			Datastream.__ds_meta_dcls__[iden] = cls
		Datastream.__ds_meta_scls__.add(cls)
		super().__init_subclass__()
	
	def __new__(cls, *args, **kwargs):
		if cls is Datastream:
			raise TypeError(f"Only children of Datastream may be instantiated.")
		instance = super().__new__(cls)
		Datastream.__ds_meta_objs__[cls].add(instance)
		return instance

	@final
	@classmethod
	def process(cls, container: DSC, data: bytes) -> Datastream[DSC]:
		key = container.typekey
		if key in Datastream.__ds_meta_dcls__.keys():
			with Stream(data) as stream:
				x = Datastream.__ds_meta_dcls__[key](container, stream)
				try:
					assert len(stream) == stream.tell(), (len(stream), stream.tell(), key)
				except AssertionError as e:
					logger.error(f"Process read too little with key {key}, read {stream.tell()}/{len(stream)}. All data (truncated at 512):\n{Stream.debug.print(data, decode=False)}")
					raise e
				return x
		else:
			return UnknownBinData(container, data, key)
	
	@final
	@classmethod
	def containerless(cls, stream: Stream):
		if cls == Datastream:
			raise NotImplementedError(f"Only children of Datastream may process data.")
		else:
			return cls(None, stream)
	
	@final
	@classmethod
	def beef_container(cls, stream: Stream) -> DSC[Datastream[DSC]]:
		peeker = stream.peek(4)[::-1].hex().upper()
		match peeker:
			case 'D34DB33F':
				return DSCv2(stream, datatype=cls if cls is not Datastream else None)
			case 'DEADBEEF':
				return DSCv1(stream, datatype=cls if cls is not Datastream else None)
			case _:
				logger.error(f"Encountered an error trying to determine the container type. Expected a deadbeef, got {peeker}")
				prevlen = min(stream.tell(), 32)
				raise ValueError(f"{Stream.debug.print(stream.peekskip(-prevlen, prevlen), decode=False)}  -> {Stream.debug.print(stream.peek(4), decode=False)} <-  {Stream.debug.print(stream.peekskip(4, 12), decode=False)}")



class UnknownBinData(Datastream, name='UnknownBinData', typehash='', vrsn=0):
	__bin_unkw__: ClassVar[set[str]] = set()
	
	key: str
	data: bytes
	
	def __init__(self, container: DSC | None, data: bytes, key: str):
		datlen = len(data)
		if key not in UnknownBinData.__bin_unkw__:
			logger.error(
				f"Can't find class for {key} (initial encounter data ({datlen}): {Stream.debug.print(data[:256] if datlen > 256 else data, decode=False)})")
		UnknownBinData.__bin_unkw__.add(key)
		super().__init__(container, Stream(data))
		self.data = data
		self.key = key
		
	def dict(self):
		return {'key': self.key, 'data': self.data.hex().upper()}







class HashedDSC[ETYPE: Datastream]:
	lutval: bytes
	dscval: DSC[ETYPE]
	
	def __init__(self, lutval: bytes, stream: Stream):
		self.lutval = lutval
		self.dscval = Datastream.beef_container(stream)


class BatchDSC[ETYPE: Datastream](StreamObject[str]):
	name:       str = StreamFields.callextra(lambda x: x)
	vrsn:       int = StreamFields.int() # content version
	ctyp:       int = StreamFields.int() # content type
	sections:   int = StreamFields.int()
	unko:       int = StreamFields.int()
	lut:        list[bytes] = StreamFields.callstreamself(lambda x, y: [x[8] for _ in range(y.sections)])
	entries:    list[HashedDSC[ETYPE]]
	
	encountered: ClassVar[set[str]] = set()
	
	@property
	def encounter_str(self):
		return f"{self.name}_{self.vrsn}_{self.ctyp}_{self.unko}"
	
	def __init__(self, stream: Stream, name: str):
		super().__init__(stream, extra=name)
		if self.encounter_str not in BatchDSC.encountered:
			logger.info(f"Encountering BatchDSC with values name={name}, vrsn={self.vrsn}, ctyp={self.ctyp}, unko={self.unko}")
			BatchDSC.encountered.add(self.encounter_str)
		self.entries = [HashedDSC(lutval, stream) for lutval in self.lut]
	
	def entry_types(self) -> str:
		return ', '.join(set(x.dscval.data.__ds_iden__() for x in self.entries))
	
	def dict(self):
		return {
			'name': self.name,
			'sections': self.sections,
			'vrsn': self.vrsn,
			'ctyp': self.ctyp,
			'unko': self.unko,
			'entries': {x.lutval.hex().upper(): x.dscval.dict() for x in self.entries}
		}



class RMDL_DSC[ETYPE: Datastream[None]]:
	eof_len: int
	eof_ofs: int
	eof_cnt: int
	e_list: list[dict]
	entries: dict[str, BatchDSC]
	
	def __init__(self, stream: Stream):
		start = stream.tell()
		assert b"RMDL" == stream[4]
		self.eof_len = int(stream)
		self.eof_ofs = stream.seek(-self.eof_len, 2)
		self.eof_cnt = int(stream)
		assert self.eof_ofs + self.eof_len == len(stream)
		self.e_list = list()
		self.entries = dict()
		
		for i in range(self.eof_cnt):
			entry_size = int(stream)
			entry_name = stream.string(int(stream))
			entry_ofst = 8 if i == 0 else (entry_size + self.e_list[i-1]['size'])
			self.e_list.append({'size': entry_size, 'name': entry_name, 'ofst': entry_ofst})
		stream.seek(start + 8)
		for v in self.e_list:
			if v['name'][:3] == 'dp_':
				stream.skip(v['size'])
			else:
				self.entries[v['name']] = BatchDSC(stream, v['name'])
	
	def dict(self):
		return {k: {'types': v.entry_types(), 'dict': v.dict()} for k, v in self.entries.items()}


class DSC[T: Datastream[DSC]](ABC):
	size:       int  # size
	typehash:   str  # contentHash (crc32 of lowercase name)
	vrsn:       int  # tagVersion
	typekey:    str
	data:       T

	__dsc_objs__: ClassVar[dict[type[DSC], WeakSet[DSC]]]   = defaultdict(WeakSet)

	def __new__(cls, *args, **kwargs):
		instance = super().__new__(cls)
		DSC.__dsc_objs__[cls].add(instance)
		return instance
	
	def dict(self):
		return {
			'size'    : self.size,
			'typehash': self.typehash,
			'vrsn'    : self.vrsn,
			'data'    : self.data.dict()
		}
	


class DSCv1[T](DSC[T]):
	def __init__(self, stream: Stream, /, *, datatype: type[T] | None = None) -> None:
		assert stream.crc == 'DEADBEEF'
		self.size = int(stream)
		self.typehash = stream.crc
		self.vrsn = int(stream)
		self.typekey = f"{self.typehash} v{self.vrsn}"
		self.data = Datastream.process(self, stream[self.size - 20]) if datatype is None else datatype(self, stream)
		assert stream.crc == 'DEADBEEF'
	

class DSCv2[T](DSC[T]):
	unko:       int
	xtra:       int | None
	
	def __init__(self, stream: Stream, /, *, datatype: type[T] | None = None) -> None:
		assert stream.crc == 'D34DB33F'
		self.unko = int(stream)
		self.size = int(stream)
		self.typehash = stream.crc
		self.vrsn = int(stream)
		self.xtra = int(stream) if self.unko == 1 else None
		self.typekey = f"{self.typehash} v{self.vrsn}"
		self.data = Datastream.process(self, stream[self.size - (24 if self.xtra is None else 28)]) if datatype is None else datatype(self, stream)
		assert stream.crc == 'D34DB33F'


class DSF:
	"""
	Datastream fields
	
	investigate this: https://stackoverflow.com/questions/31626653/why-do-people-default-owner-parameter-to-none-in-get/31767475#31767475
	"""
	
	
	class dsc(ByteStreamField[DSC, None]):
		def caller(self, stream, obj, extra):
			return Datastream.beef_container(stream)

	class iter_dsc(ByteStreamField[list[DSC], None]):
		length: int | None
		
		def __init__(self, length: int | None = None):
			self.length = length
		
		def caller(self, stream, obj, extra):
			return [Datastream.beef_container(stream) for _ in range(stream.integer(4, signed=False, endi='little') if self.length is None else self.length)]
	

"""
C2F5BB69    ui::PageResource::EventDefinition
83828A3B    ui::PageResource::FactBindingDefinition
92320439    ui::PageResource::FactBindingListDefinition
F3931E14    ui::PageResource::FactBindingObjectListDefinition
B8433619    ui::PageResource::NavigationContextDefinition
ED153D2E    ui::PageResource::StateStackDefinition
75C44AA7    ui::PageResource::TransformArgumentDefinition
5AE54C4C    ui::PageResource::TransformArgumentValueDefinition
"""


class ClothProfile(Datastream, typehash="98DD1A29", vrsn=1, name="physics::ClothProfile"):
	GravityMultiplier: float = StreamFields.float(2)
	DampingMultiplier: float = StreamFields.float(2)
	LinearInertiaScaleMultiplier: float = StreamFields.float(2)
	AngularInertiaScaleMultiplier: float = StreamFields.float(2)


class DialogueVoiceProfile(Datastream, typehash="58ED0605", vrsn=0, name="content::DialogueVoiceProfile"):
	unko: int = StreamFields.int()
	rid: RID = StreamFields.call(RID.long)
	rids: list[RID] = StreamFields.iter(RID.long)


class DialogueType(Datastream, typehash="0534C4EC", vrsn=3, name="content::DialogueType"):
	Urgency: int = StreamFields.int()
	DefaultDelay: float = StreamFields.float()
	SoundEvent: str = StreamFields.istr()
	DialogueLine: str = StreamFields.istr()
	SoundFXStart: str = StreamFields.istr()
	SoundFXEnd: str = StreamFields.istr()
	FacialAnimBlendTime: float = StreamFields.float()
	PreventsSave: bool = StreamFields.bool()
	ForceSubtitle: bool = StreamFields.bool()
	SubtitleRange: float = StreamFields.float()


class r_Resource_v1(Datastream, typehash="D0B4291C", vrsn=1, name="r::Resource"):
	pass


class PageResource_Header_v3(Datastream, typehash="4EDAE845", vrsn=3, name="ui::PageResource::Header"):
	pathname:   str         = StreamFields.istr()
	resource:   DSC         = DSF.dsc()
	dataOffset: int         = StreamFields.int()
	unko1:      list[DSC]   = DSF.iter_dsc()
	dataSize:   int         = StreamFields.int()
	unko2:      list[DSC]   = DSF.iter_dsc()


class PageResource_v7(Datastream, typehash="70635A61", vrsn=7, name="ui::PageResource"):
	rsc:        DSC[r_Resource_v1]                  = DSF.dsc()
	path:       str                                 = StreamFields.istr()
	headers:    list[DSC[PageResource_Header_v3]]   = DSF.iter_dsc()
	data:       str                                 = StreamFields.istr()
	i1:         list[DSC]                           = DSF.iter_dsc()
	i2:         list[DSC]                           = DSF.iter_dsc()
	i3:         list[DSC]                           = DSF.iter_dsc()
	i4:         list[DSC]                           = DSF.iter_dsc()
	i5:         list[DSC]                           = DSF.iter_dsc()
	i6:         list[DSC]                           = DSF.iter_dsc()
	i7:         list[DSC]                           = DSF.iter_dsc()

"""

m_eType
m_vecTextures
m_vecUITextures
m_vecVideoTextures

m_ridResource
m_uDataOffset
m_uDataSize
m_vecRequiredFiles
m_vecResourceGroups

"""


class TransformComponent_v2(Datastream, typehash="3C0CC124", vrsn=2, name="content::TransformComponent"):
	gencom:     DSC[GenericComponent_v5] = DSF.dsc()
	integer:    int = StreamFields.int()
	floats:     list[float] = StreamFields.iter(float, 10)


class AudioControllerComponent_v1(Datastream, typehash="7BB800D1", vrsn=1, name="content::AudioControllerComponent"):
	gencom:     DSC[GenericComponent_v5] = DSF.dsc()


class AudioAcousticsComponent_v1(Datastream, typehash="E2382732", vrsn=1, name="content::AudioAcousticsComponent"):
	gencom:     DSC[GenericComponent_v5] = DSF.dsc()
	bool1: bool = StreamFields.bool()
	bool2: bool = StreamFields.bool()
	floaty: float = StreamFields.float()


class SoundComponent_v9(Datastream, typehash="C88AB15A", vrsn=9, name="content::SoundComponent"):
	gencom:     DSC[GenericComponent_v5] = DSF.dsc()
	booly: bool = StreamFields.bool()
	str1: str = StreamFields.str(-1)
	str2: str = StreamFields.str(-1)
	subitems: DSC = StreamFields.iter(Datastream.beef_container)
	i1: int = StreamFields.int()
	i2: int = StreamFields.int()
	i3: int = StreamFields.int()
	i4: int = StreamFields.int()
	i5: int = StreamFields.int()
	bool1: bool = StreamFields.bool()
	bool2: bool = StreamFields.bool()


class RigidBodyToWorldTransformComponent_v0(Datastream, typehash="BBBF773C", vrsn=0, name="contentcore::RigidBodyToWorldTransformComponent"):
	gencom: DSC[GenericComponent_v5] = DSF.dsc()


class EquippableComponent_v1(Datastream, typehash="BD31C385", vrsn=1, name="content::EquippableComponent"):
	gencom: DSC[GenericComponent_v5] = DSF.dsc()


class AnimationEventComponent_v3(Datastream, typehash="093897D6", vrsn=3, name="content::AnimationEventComponent"):
	gencom: DSC[GenericComponent_v5] = DSF.dsc()


class GameCursorInteractableComponent_v2(Datastream, typehash="D37CCD24", vrsn=2, name="content::GameCursorInteractableComponent"):
	gencom: DSC[GenericComponent_v5] = DSF.dsc()
	b1: bool = StreamFields.bool()
	b2: bool = StreamFields.bool()
	b3: bool = StreamFields.bool()


class EquippableAnimationIDComponent_v1(Datastream, typehash="D7AA7140", vrsn=1, name="content::EquippableAnimationIDComponent"):
	gencom: DSC[GenericComponent_v5] = DSF.dsc()
	unko: int = StreamFields.int()


class AttachmentSocketComponent_v4(Datastream, typehash="40AE554B", vrsn=4, name="content::AttachmentSocketComponent"):
	gencom: DSC[GenericComponent_v5] = DSF.dsc()
	string: str = StreamFields.str(-1)


class AnimationSlaveComponent_v7(Datastream, typehash="40AE554B", vrsn=7, name="content::AnimationSlaveComponent"):
	gencom: DSC[GenericComponent_v5] = DSF.dsc()
	b1: bool = StreamFields.bool()
	b2: bool = StreamFields.bool()
	b3: bool = StreamFields.bool()
	string: str = StreamFields.str(-1)
	unko: bytes = StreamFields.bytes(4)


class HolsterableComponent_v1(Datastream, typehash="4798B260", vrsn=1, name="content::HolsterableComponent"):
	gencom: DSC[GenericComponent_v5] = DSF.dsc()
	b1: bool = StreamFields.bool()
	b2: bool = StreamFields.bool()
	b3: bool = StreamFields.bool()
	b4: bool = StreamFields.bool()
	b5: bool = StreamFields.bool()
	string: str = StreamFields.str(-1)
	unko: bytes = StreamFields.bytes(4)


class SkeletonComponent_v5(Datastream, typehash="46B56566", vrsn=5, name="content::SkeletonComponent"):
	gencom: DSC[GenericComponent_v5] = DSF.dsc()
	rsc_id: DSC[ResourceID_v1] = DSF.dsc()


class AnimationGraphComponent_v0(Datastream, typehash="EAFB8C39", vrsn=0, name="content::AnimationGraphComponent"):
	gencom: DSC[GenericComponent_v5] = DSF.dsc()
	unko: DSC = DSF.dsc()


class CollisionResourceComponent_v4(Datastream, typehash="345FA276", vrsn=4, name="content::CollisionResourceComponent"):
	gencom: DSC[GenericComponent_v5] = DSF.dsc()
	unko: DSC = DSF.dsc()
	unkoi: int = StreamFields.int()


class GameRayCastDamageActionComponent_v10(Datastream, typehash="F933DD32", vrsn=10, name="content::GameRayCastDamageActionComponent"):
	gencom: DSC[GenericComponent_v5] = DSF.dsc()
	unko1: bytes = StreamFields.bytes(8)
	name: str = StreamFields.istr()
	unko2: bytes = StreamFields.bytes(4)
	
	
"""
class Unknown1(Datastream, typehash="383FCF03", vrsn=1, name="UNKNOWN_1"):
	gencom: DSC[GenericComponent_v5] = DSF.dsc()


94E7CF08 v26    content::DynamicCollisionComponent          055F03B7 | 01 __ 01 __ | __ __ __ __ | __ 01 __ __ | __ __ 01 __ | __ __ __ __ | __ __ 05 __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | 80 3f __ __ | 80 3f __ __ | 80 3f __ __ | __ __ __)
B48A5F49 v11    content::GameWeaponKickbackComponent        055F03B7 | 97 __ 5a 57 | 73 33 a3 2c | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __)
77EA7BE0 v8     content::GameWeaponDispersionComponent      055F03B7 | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ __ __)
402182E3 v15    content::MeshComponent                      055F03B7 | 3f b3 4d d3 | 02 __ __ __ | 40 __ __ __ | 34 b1 b5 0b | 01 __ __ __ | __ __ __ __ | 3f b3 4d d3 | 02 __ __ __ | 20 __ __ __ | d5 72 fc 1b | 01 __ __ __ | 24 90 75 60 | 81 1c bb 91 | 3f b3 4d d3 | __ __ __ __ | 3f b3 4d d3 | __ 01 02 __ | __ __ __ __ | __ __ __ __ | __ __ __ __ | __ __ 01 01 | __ __ 80 bf | __ __ 80 3f | __ __ 80 3f | __ __ 80 3f)
F9397A72 v4     content::AutoAimComponent                   055F03B7 | __ __ 48 43 | __ __ __ __ | __ __ __ __ | 24 __ __ __ | 46 46 46 46 | 46 46 46 46 | 2d 46 46 46 | 46 2d 46 46 | 46 46 2d 46 | 46 46 46 2d | 46 46 46 46 | 46 46 46 46 | 46 46 46 46 | __ __ __ __ | __ __ __ __ | __ __ __ __ | 24 __ __ __ | 46 46 46 46 | 46 46 46 46 | 2d 46 46 46 | 46 2d 46 46 | 46 46 2d 46 | 46 46 46 2d | 46 46 46 46 | 46 46 46 46 | 46 46 46 46 | __ __ __ __ | __ __ __ __ | __ __ __ __ | 24 __ __ __ | 46 46 46 46 | 46 46 46 46 | 2d 46 46 46 | 46 2d 46 46 | 46 46 2d 46 | 46 46 46 2d | 46 46 46 46 | 46 46 46 46 | 46 46 46 46 | __ __ __ __ | __ __ __ __ | __ __ __ __ | 24 __ __ __ | 46 46 46 46 | 46 46 46 46 | 2d 46 46 46 | 46 2d 46 46 | 46 46 2d 46 | 46 46 46 2d | 46 46 46 46 | 46 46 46 46 | 46 46 46 46 | __ __ __ __ | cd cc 4c 3e)
49742FC9 v34    content::GameWeaponComponent                055F03B7 | 01 __ __ __ | __ __ __ __ | 01 3f b3 4d | d3 02 __ __ | __ 73 __ __ | __ 35 bc 76 | f7 02 __ __ | __ 13 __ __ | __ 55 6e 6e | 61 6d 65 64 | 20 4e 6f 69 | 73 65 20 45 | 76 65 6e 74 | 89 13 0c 9b | e7 d6 71 0a | __ __ f0 41 | 97 40 9a 97 | 43 04 7b 3d | 24 __ __ __ | 46 46 46 46 | 46 46 46 46 | 2d 46 46 46 | 46 2d 46 46 | 46 46 2d 46 | 46 46 46 2d | 46 46 46 46 | 46 46 46 46 | 46 46 46 46 | __ __ __ __ | __ __ __ __ | 3f b3 4d d3 | 3f b3 4d d3 | 02 __ __ __ | 73 __ __ __ | 35 bc 76 f7 | 02 __ __ __ | 13 __ __ __ | 55 6e 6e 61 | 6d 65 64 20 | 4e 6f 69 73 | 65 20 45 76 | 65 6e 74 89 | 13 0c 9b e7 | d6 71 0a __ | __ 48 42 97 | 40 9a 97 43 | 04 7b 3d 24 | __ __ __ 46 | 46 46 46 46 | 46 46 46 2d | 46 46 46 46 | 2d 46 46 46 | 46 2d 46 46 | 46 46 2d 46 | 46 46 46 46 | 46 46 46 46 | 46 46 46 __ | __ __ __ 04)
B2209AC4 v3     content::WeaponUpgradesComponent            055F03B7 | 02 __ __ __ | 3f b3 4d d3 | 02 __ __ __ | 63 __ __ __ | f8 25 e5 0f | 03 __ __ __ | 11 __ __ __ | 55 70 67 72 | 61 64 65 5f | 50 69 73 74 | 6f 6c 5f 30 | 31 __ 01 4d | 40 b9 6c fa | 10 e9 11 24 | __ __ __ 46 | 46 46 46 46 | 46 46 46 2d | 46 46 46 46 | 2d 46 46 46 | 46 2d 46 46 | 46 46 2d 46 | 46 46 46 46 | 46 46 46 46 | 46 46 46 __ | __ __ __ 3f | b3 4d d3 3f | b3 4d d3 02 | __ __ __ 63 | __ __ __ f8 | 25 e5 0f 03 | __ __ __ 11 | __ __ __ 55 | 70 67 72 61 | 64 65 5f 50 | 69 73 74 6f | 6c 5f 30 32 | __ 01 4d c0 | cd 50 68 41 | db 3e 24 __ | __ __ 46 46 | 46 46 46 46 | 46 46 2d 46 | 46 46 46 2d | 46 46 46 46 | 2d 46 46 46 | 46 2d 46 46 | 46 46 46 46 | 46 46 46 46 | 46 46 __ __ | __ __ 3f b3 | 4d d3 01 __ | __ __ __ 04 | __ __ __ 3f | b3 4d d3 02 | __ __ __ 20 | __ __ __ ef | 86 e4 38 01 | __ __ __ __)
"""

# F9546E19 v2     content::BehaviorTreeData                   (len 348):  01 c9 6d 6b | db 3f b3 4d | d3 02 __ __ | __ ce __ __ | __ c9 6d 6b | db 01 __ __ | __ 3f b3 4d | d3 02 __ __ | __ b6 __ __ | __ 3f 75 d8 | d1 02 __ __ | __ 3f b3 4d | d3 02 __ __ | __ 18 __ __ | __ ca cd 0c | d9 01 __ __ | __ 3f b3 4d | d3 __ __ __ | __ __ __ __ | __ 01 __ __ | __ 01 ed fb | ed 15 3f b3 | 4d d3 02 __ | __ __ 75 __ | __ __ ed fb | ed 15 05 __ | __ __ 3f b3 | 4d d3 02 __ | __ __ 54 __ | __ __ 8e dc | 56 ef 01 __ | __ __ 3f b3 | 4d d3 02 __ | __ __ 3c __ | __ __ 3f 75 | d8 d1 02 __ | __ __ 3f b3 | 4d d3 02 __ | __ __ 18 __ | __ __ ca cd | 0c d9 01 __ | __ __ 3f b3 | 4d d3 __ __ | __ __ __ __ | __ __ __ __ | __ __ 3f b3 | 4d d3 3f b3 | 4d d3 __ __ | 80 3f __ __ | 40 40 __ 3f | b3 4d d3 3f | b3 4d d3 3f | b3 4d d3 02 | __ __ __ 09 | __ __ __ 52 | 6f 6f 74 20 | 4e 6f 64 65 | bf bb 0b f1 | a1 c5 1e df | __ __ __ __ | __ __ __ __ | __ __ __ __ | 02 __ __ __ | 24 __ __ __)



class Unknown1(Datastream, typehash="383FCF03", vrsn=1, name="UNKNOWN_1"):  # unknown, found in the iterlists of ui::PageMetadata::ResourceGroup
	f1: int = StreamFields.int()
	v1: DSC[ResourceID_v1] = DSF.dsc()
	f2: int = StreamFields.int()


class Unknown2(Datastream, typehash="B6866F79", vrsn=1, name="UNKNOWN_2"):  # unknown, found in the iterlists of ui::PageMetadata::ResourceGroup)
	f1: int = StreamFields.int()
	v1: DSC[ResourceID_v1] = DSF.dsc()
	f2: int = StreamFields.int()


class Unknown3(Datastream, typehash="38ABEE66", vrsn=1, name="UNKNOWN_3"):
	f1: int = StreamFields.int()
	v1: DSC[ResourceID_v1] = DSF.dsc()
	f2: int = StreamFields.int()


class ShapeInfo(Datastream, typehash="F6A9FDA3", vrsn=0, name="physics::CollisionPackageMetadata::ShapeInfo"):
	Name:                   str = StreamFields.str(-1)
	PhysicsMaterialName:    str = StreamFields.str(-1)
	LayerName:              str = StreamFields.str(-1)


class RigidBodyInfo(Datastream, typehash="396302B5", vrsn=2, name="physics::CollisionPackageMetadata::RigidBodyInfo"):
	VisibilityIndex: int = StreamFields.uint()
	Name: str = StreamFields.str(-1)
	PhysicsMaterialName: str = StreamFields.str(-1)
	LayerName: str = StreamFields.str(-1)
	Keyframeable: bool = StreamFields.bool()
	ShapeInfos: list[DSC[ShapeInfo]] = StreamFields.iter(Datastream.beef_container)


class MorphemePackMetadata(Datastream, typehash="2C487205", vrsn=0, name="physics::MorphemePackMetadata"):
	strings: list[str] = StreamFields.iter(lambda x: x.string(-1))


class FileInfoMetadata_v0(Datastream, typehash="95E8C0EF", vrsn=0, name="r::FileInfoMetadata"):
	filesize: int = StreamFields.uint(8)
	checksum: str = StreamFields.crc()
	flags: int = StreamFields.uint()


class FileInfoMetadata_v1(Datastream, typehash="95E8C0EF", vrsn=1, name="r::FileInfoMetadata"):
	filesize: int = StreamFields.uint()
	checksum: str = StreamFields.crc()
	flags: int = StreamFields.uint()


class FileInfoMetadata_content_v0(Datastream, typehash="BB2F78AB", vrsn=0, name="content::FileInfoMetadata"):
	filesize: int = StreamFields.uint()
	checksum: str = StreamFields.crc()
	flags: int = StreamFields.uint()


class ResourceID_content_v1(Datastream, typehash="B862238F", vrsn=1, name="content::ResourceID"):
	rid: RID = StreamFields.call(RID)


class ResourceMetadata_v1(Datastream, typehash="184CFA41", vrsn=1, name="content::ResourceMetadata"):
	rid: DSC[ResourceID_content_v1] = StreamFields.call(lambda x: Datastream.beef_container(x))
	resourceType: int = StreamFields.uint()
	
	def dict(self):
		return {
			'RID'         : str(self.rid.data.rid),
			'resourceType': self.resourceType,
		}


class ResourceMetadata_v3(Datastream, typehash="368B4205", vrsn=3, name="r::ResourceMetadata"):
	rids: DSC[ResourceID_v1] = StreamFields.call(lambda x: Datastream.beef_container(x))
	dependencies: list[DSC[ResourceID_v1]] = StreamFields.iter(lambda x: Datastream.beef_container(x))


class EntityArchetype_v3_item(StreamObject):
	booli: bool = StreamFields.bool()
	typer: str = StreamFields.crc()
	item: DSC = DSF.dsc()


class EntityArchetype_v3(Datastream, typehash="6C5538CE", vrsn=3, name="content::EntityArchetype"):
	name: str = StreamFields.str(-1)
	content: DSC[GenericEntity_v10] = StreamFields.call(lambda x: Datastream.beef_container(x))
	items_1: list[EntityArchetype_v3_item] = StreamFields.iter(EntityArchetype_v3_item)
	items_2: list = StreamFields.iter(Datastream.beef_container)

class ContentEntityBase_v0(Datastream, typehash="64AE5E6B", vrsn=0, name="r::ContentEntityBase"):
	i1: int = StreamFields.int()
	i2: int = StreamFields.int()
	i3: int = StreamFields.int()

class NavmeshTemplateData_v1(Datastream, typehash="375596F6", vrsn=1, name="coreshared::NavmeshTemplateData"):
	ints: list[int] = StreamFields.iter(int, 8)


class GenericEntity_v10(Datastream, typehash="5150B030", vrsn=10, name="content::GenericEntity"):
	subitem:    DSC         = StreamFields.call(lambda x: Datastream.beef_container(x))
	floats:     list[float] = StreamFields.iter(float, 12)
	string1:    str         = StreamFields.str(-1)
	iter_rid:   list[RID]   = StreamFields.iter(RID.long)
	booli:      bool        = StreamFields.bool()


class FileMetadataEntry_v1(Datastream, typehash="54034281", vrsn=1, name="FileMetadataEntry"):
	class Metadata(Datastream, typehash="ADC4584F", vrsn=1, name="FileMetadataEntry::Metadata"):
		meta_index: int = StreamFields.uint()
		file_index: int = StreamFields.uint()
	
	ofst: int = StreamFields.uint()
	subitems: list[DSC[Metadata]] = StreamFields.iter(Metadata.beef_container)


class FileMetadataEntry_v2(Datastream, typehash="E974FDFF", vrsn=2, name="r::PackFileMetadataManager::FileMetadataEntry"):
	class Metadata(Datastream, typehash="35AE54C1", vrsn=2, name="r::PackFileMetadataManager::FileMetadataEntry::Metadata"):
		meta_index: int = StreamFields.uint()  # type index
		file_index: int = StreamFields.uint()  # file index
	
	ofst: int = StreamFields.uint()
	subitems: list[DSC[Metadata]] = StreamFields.iter(Metadata.beef_container)


class ResourceID_v1(Datastream, typehash="1BFC72D5", vrsn=1, name="r::ResourceID"):
	rid: RID = StreamFields.call(RID.long)


class MeshMetadata_v21(Datastream, typehash="FE276448", vrsn=21, name="rend::MeshMetadata"):
	meshformat: DSC[MeshFormat_rend_v3] = StreamFields.call(lambda x: Datastream.beef_container(x))
	b1: bool = StreamFields.bool()  # maybe m_bMissingMaterialBinds
	b2: bool = StreamFields.bool()  # maybe m_bHasBones
	b3: bool = StreamFields.bool()  # maybe m_bHasExtraMaterialBinds
	rid: DSC[ResourceID_v1] = StreamFields.call(lambda x: Datastream.beef_container(x))  # maybe m_ridSkeleton
	str_1: str = StreamFields.str(-1)  # maybe m_strMaxFilePath
	num_1: int = StreamFields.int(1)  # maybe m_bIsOccluder
	val_1: bytes = StreamFields.bytes(4)  # maybe m_iNumAnimationFrames
	str_2: str = StreamFields.str(-1)  # maybe m_strLodTemplatePath
	num_2: int = StreamFields.int()  # maybe m_iRBFCutoffLod
	val_2: bytes = StreamFields.bytes(4)  # maybe m_uLodInformationFlags
	f1: int = StreamFields.uint()  # maybe m_iAnimSet1Lod
	f2: int = StreamFields.uint()  # maybe m_iWrinkleCutoffLod
	f3: int = StreamFields.uint()  # maybe m_uUserCreatedLodBytes
	f4: int = StreamFields.uint()  # maybe m_uGeneratedLodBytes or m_uVertexBufferSizeBytes
	rid_list: list[DSC[ResourceID_v1]] = StreamFields.iter(lambda x: Datastream.beef_container(x))  # maybe m_ridSubMeshes


class MeshMetadata_v15(Datastream, typehash="FE276448", vrsn=15, name="rend::MeshMetadata"):
	fmt: DSC[MeshFormat_rend_v3] = StreamFields.call(lambda x: Datastream.beef_container(x))
	b1: bool = StreamFields.bool()  # maybe m_bMissingMaterialBinds
	b2: bool = StreamFields.bool()  # maybe m_bHasBones
	b3: bool = StreamFields.bool()  # maybe m_bHasExtraMaterialBinds
	rid1: DSC[ResourceID_v1] = StreamFields.call(lambda x: Datastream.beef_container(x))  # maybe m_ridSkeleton
	rid2: DSC[ResourceID_v1] = StreamFields.call(lambda x: Datastream.beef_container(x))  # maybe m_ridSkeleton
	str_1: str = StreamFields.str(-1)
	num_1: int = StreamFields.int(1)
	val_1: bytes = StreamFields.bytes(4)
	str_2: str = StreamFields.str(-1)
	num_2: int = StreamFields.int()
	val_2: bytes = StreamFields.bytes(4)
	f1: int = StreamFields.uint()


class MeshFormat_v2(Datastream, typehash="858A1F4C", vrsn=2, name="content::MeshFormat"):
	f1: int = StreamFields.uint()
	f2: int = StreamFields.uint()
	f3: int = StreamFields.uint()
	boundbox: DSC[rBoundBox_v1] = DSF.dsc()


class MeshFormat_rend_v3(Datastream, typehash="BF008D7D", vrsn=3, name="rend::MeshFormat"):
	f1: int = StreamFields.uint()
	f2: int = StreamFields.uint()
	f3: int = StreamFields.uint()
	f4: int = StreamFields.uint()
	f5: int = StreamFields.uint()
	f6: int = StreamFields.uint()
	f7: int = StreamFields.uint()
	bbox: DSC[rBoundBox_v1] = StreamFields.call(lambda x: Datastream.beef_container(x))


class ParticleSystemMetadata_v4(Datastream, typehash="32F0DE4B", vrsn=4, name="rend::ParticleSystemMetadata"):
	f1: int = StreamFields.uint()


class ParticleSystemMetadata_v6(Datastream, typehash="32F0DE4B", vrsn=6, name="rend::ParticleSystemMetadata"):
	f1: int = StreamFields.uint()
	f2: int = StreamFields.uint()
	f3: int = StreamFields.uint()


class PageMetadata_v3(Datastream, typehash="83E69A63", vrsn=3, name="ui::PageMetadata"):
	listo_str: list[str] = StreamFields.iter(lambda x: x.string(int(x)))
	iterlist: list[DSC[ResourceGroup_v2]] = StreamFields.iter(lambda x: Datastream.beef_container(x))
	unko1: int = StreamFields.int()
	unko2: bool = StreamFields.bool()


class PhysXClothMetadata_v2(Datastream, typehash="CF1FBC60", vrsn=2, name="physics::PhysXClothMetadata"):
	unko1: list[bytes] = StreamFields.iter(lambda x: x[12])
	unko2: list[int] = StreamFields.iter(int)


class SkeletonMetadata_v2(Datastream, typehash="338D8396", vrsn=2, name="puppet::SkeletonMetadata"):
	rids: list[RID] = StreamFields.iter(RID)


class TextureMetadata_v1(Datastream, typehash="968A49B7", vrsn=1, name="rend::TextureMetadata"):
	desc: DSC[TextureDesc_rend_v4] = StreamFields.call(lambda x: Datastream.beef_container(x))
	unkwn_end: bytes = StreamFields.bytes(6)


class TextureMetadata_v5(Datastream, typehash="968A49B7", vrsn=5, name="rend::TextureMetadata"):
	desc: DSC[TextureDesc_rend_v5] = StreamFields.call(lambda x: Datastream.beef_container(x))
	unkwn_end: bytes = StreamFields.bytes(21)


class CollisionPackageMetadata_v10(Datastream, typehash="CC074B60", vrsn=10, name="physics::CollisionPackageMetadata"):
	iter1: list[DSC[OSPHackSIMDTransform_v1]] = StreamFields.iter(Datastream.beef_container)
	iter2: list[DSC[RenderBones_v1]] = StreamFields.iter(Datastream.beef_container)
	end3: bytes = StreamFields.bytes(3)


class CollisionPackageMetadata_v6(Datastream, typehash="CC074B60", vrsn=6, name="physics::CollisionPackageMetadata"):
	f1: int = StreamFields.uint()
	iter: list[DSC[RigidBodyInfo]] = StreamFields.iter(Datastream.beef_container)
	end2: bytes = StreamFields.bytes(2)


class ResourceGroup_v2(Datastream, typehash="48BB28E2", vrsn=2, name="ui::PageMetadata::ResourceGroup"):
	name: str = StreamFields.str(-1)
	unko_int1: int = StreamFields.int()
	unko_1: list[DSC[Unknown1]] = StreamFields.iter(lambda x: Datastream.beef_container(x))
	unko_2: list[DSC[Unknown2]] = StreamFields.iter(lambda x: Datastream.beef_container(x))
	unko_3: list[DSC] = StreamFields.iter(lambda x: Datastream.beef_container(x))


class TextureDesc_rend_v4(Datastream, typehash="5AB63F81", vrsn=4, name="rend::TextureDesc"):
	type: int = StreamFields.uint()
	format: int = StreamFields.uint()
	filter: int = StreamFields.uint()
	width: int = StreamFields.uint()
	height: int = StreamFields.uint()
	depth: int = StreamFields.uint()
	mipmapcount: int = StreamFields.uint()
	mipoffsets: list[int] = StreamFields.iter(lambda x: x.integer(8))
	IsTiled: bool = StreamFields.bool()
	IsVideoTexture2: bool = StreamFields.bool()


class TextureDesc_rend_v5(Datastream, typehash="5AB63F81", vrsn=5, name="rend::TextureDesc"):
	type: int = StreamFields.uint()
	format: int = StreamFields.uint()
	filter: int = StreamFields.uint()
	width: int = StreamFields.uint()
	height: int = StreamFields.uint()
	depth: int = StreamFields.uint()
	mipmapcount: int = StreamFields.uint()
	mipoffsets: list[int] = StreamFields.iter(lambda x: x.integer(8))
	IsTiled: bool = StreamFields.bool()
	IsVideoTexture2: bool = StreamFields.bool()
	HighDetailStreamDistance: int = StreamFields.uint()


class DialogueLine_v18(Datastream, typehash="58FE2733", vrsn=18, name="content::DialogueLine"):
	HumanReadableID: str = StreamFields.str(-1)
	DialogueString: RID = StreamFields.call(RID.long)
	DialogueType: RID = StreamFields.call(RID.long)
	delay: float = StreamFields.float()
	NoSubtitles: bool = StreamFields.bool()
	IsGenericLine: bool = StreamFields.bool()
	Sound: DSC = DSF.dsc()
	AnimationBundle: DSC = DSF.dsc()
	IsCinematicLine: bool = StreamFields.bool()
	XMDOffset: float = StreamFields.float(2)
	AnimationOffset: float = StreamFields.float(2)
	ForceSubtitles: bool = StreamFields.bool()
	Duration: float = StreamFields.float()


class DialogueString_v0(Datastream, typehash="4135DAB6", vrsn=0, name="content::DialogueString"):
	text: str = StreamFields.str(-1)
	speaker: str = StreamFields.str(-1)


class DialogueString_v2(Datastream, typehash="4135DAB6", vrsn=2, name="content::DialogueString"):
	unknown: int = StreamFields.int()
	text: str = StreamFields.str(-1)
	speaker: str = StreamFields.str(-1)


class TextureMetadata_v0(Datastream, typehash="D489B181", vrsn=0, name="content::TextureMetadata"):
	desc: DSC[TextureDesc_v1] = StreamFields.call(lambda x: Datastream.beef_container(x))
	HighDetailStreamDistance: float = StreamFields.float()
	UseTextureLOD: int = StreamFields.bool()


class HavokAnimationMetadata_v1(Datastream, typehash="FE16BFD8", vrsn=1, name="content::HavokAnimationMetadata"):
	AnimationEventPath: str = StreamFields.str(-1)
	Length: float = StreamFields.float()


class MeshMetadata_v1(Datastream, typehash="267BAB18", vrsn=1, name="content::MeshMetadata"):
	format: DSC[MeshFormat_v2] = DSF.dsc()
	HasBones: bool = StreamFields.bool()
	textureResourceIDs: list[DSC[ResourceID_content_v1]] = StreamFields.iter(lambda x: Datastream.beef_container(x))


class FoliageMeshMetadata_v1(Datastream, typehash="204283E3", vrsn=1, name="content::FoliageMeshMetadata"):
	format: DSC[MeshFormat_v2] = DSF.dsc()
	TextureCount: int = StreamFields.uint()
	textureResourceIDs: list[DSC[ResourceID_content_v1]] = StreamFields.iter(lambda x: Datastream.beef_container(x))


class TextureDesc_v1(Datastream, typehash="0B52B529", vrsn=1, name="content::TextureDesc"):
	type: int = StreamFields.uint()
	format: int = StreamFields.uint()
	filter: int = StreamFields.uint()
	width: int = StreamFields.uint()
	height: int = StreamFields.uint()
	depth: int = StreamFields.uint()
	mipmapcount: int = StreamFields.uint()
	mipoffsets: list[int] = StreamFields.iter(lambda x: int(x))


class ParticleSystemMetadata_v2(Datastream, typehash="763F3F31", vrsn=2, name="content::ParticleSystemMetadata"):
	rids: list[DSC[ResourceID_content_v1]] = StreamFields.iter(lambda x: Datastream.beef_container(x))
	f2: int = StreamFields.uint()


class OSPHackSIMDTransform_v1(Datastream, typehash="81296CA2", vrsn=1, name="r::OSPHackSIMDTransform"):
	iterlist_unknown: list[int] = StreamFields.iter(int)


class RenderBones_v1(Datastream, typehash="156AA42D", vrsn=1, name="physics::CollisionPackageMetadata::RenderBones"):
	unko: list[int] = StreamFields.iter(lambda x: x.integer(2))


class rBoundBox_v1(Datastream, typehash="D8763D8B", vrsn=1, name="r::BoundBox"):
	box: BoundBox = StreamFields.call(BoundBox)


class RuntimeVersion_v4(Datastream, typehash="A750BFB5", vrsn=4, name="content::RuntimeVersion"):
	pass


class GfxGraphMetadata_v1(Datastream, typehash="97B97719", vrsn=1, name="coreshared::GfxGraphMetadata"):
	pass


class ClothProfileMetadata_v1(Datastream, typehash="2555EDC9", vrsn=1, name="physics::ClothProfileMetadata"):
	pass


class BehaviorTreeMetadata_v1(Datastream, typehash="792D12F4", vrsn=1, name="bonsai::BehaviorTreeMetadata"):
	pass


class RBFMetadata_v0(Datastream, typehash="30231D43", vrsn=0, name="physics::RBFMetadata"):
	pass


class DialogueMetadata_v0(Datastream, typehash="9F5DCB8E", vrsn=0, name="snd::DialogueMetadata"):
	pass


class ExternalSourceMetadata_v1(Datastream, typehash="414CDC22", vrsn=1, name="snd::ExternalSourceMetadata"):
	pass


class GenericComponent_v5(Datastream, typehash="055F03B7", vrsn=5, name="content::GenericComponent"):
	pass


class DialogueStringTableMetadata_v0(Datastream, typehash="4977674C", vrsn=0, name="snd::DialogueStringTableMetadata"):
	pass


class FlareMetadata_v0(Datastream, typehash="04D1FCAE", vrsn=0, name="rend::FlareMetadata"):
	pass


class IlluminationVolumeGIDataMetadata_v0(Datastream, typehash="B194D640", vrsn=0, name="rend::IlluminationVolumeGIDataMetadata"):
	pass


class IlluminationVolumeTreeMetadata_v0(Datastream, typehash="FD2565A2", vrsn=0, name="rend::IlluminationVolumeTreeMetadata"):
	pass


class RagdollProfileMetadata_v1(Datastream, typehash="CD632CB4", vrsn=1, name="physics::RagdollProfileMetadata"):
	pass


class BlendSpaceMetadata_v1(Datastream, typehash="FDC51EAA", vrsn=1, name="puppet::BlendSpaceMetadata"):
	pass


class ClipMetadata_v1(Datastream, typehash="5215F16F", vrsn=1, name="puppet::ClipMetadata"):
	pass


class MixerMetadata_v1(Datastream, typehash="191A97F6", vrsn=1, name="puppet::MixerMetadata"):
	pass


class SystemicDialogueMetadata_v0(Datastream, typehash="2B9D7D52", vrsn=0, name="snd::SystemicDialogueMetadata"):
	pass


class MotionDatabaseMetadata_v1(Datastream, typehash="1B92F6C5", vrsn=1, name="puppet::MotionDatabaseMetadata"):
	pass


class EQSQueryMetadata_v1(Datastream, typehash="884E0523", vrsn=1, name="bonsai::EQSQueryMetadata"):
	pass


class SDFVolumeMetadata_v0(Datastream, typehash="53CD678D", vrsn=0, name="rend::SDFVolumeMetadata"):
	pass


class TimelineMetadata_v0(Datastream, typehash="826DAE80", vrsn=0, name="coregame::TimelineMetadata"):
	pass


class SoundBankMetadata_v1(Datastream, typehash="D084E551", vrsn=1, name="snd::SoundBankMetadata"):
	pass


class GraphMetadata_v1(Datastream, typehash="731DC02F", vrsn=1, name="puppet::GraphMetadata"):
	pass


class BinaryBlobMetadata_v0(Datastream, typehash="AA33CC20", vrsn=0, name="r::BinaryBlobMetadata"):
	pass


class DMMAnimationMetadata(Datastream, typehash="D7D8E623", vrsn=0, name="physics::DMMAnimationMetadata"):
	pass


class HavokClothMetadata(Datastream, typehash="02F5828F", vrsn=1, name="physics::HavokClothMetadata"):
	pass


class MorphemeMetadata(Datastream, typehash="97D14740", vrsn=6, name="physics::MorphemeMetadata"):
	pass


class SkeletonMetadata(Datastream, typehash="81BD379E", vrsn=0, name="physics::SkeletonMetadata"):
	pass
