from __future__ import annotations

from pyglm.glm import vec2, vec3, mat3

from torchbearer.mulch import StreamFields, StreamObject, ByteStreamField
from .types_general import GID, ObjectID, RID, BoundBox, GLMFields
from .dpfile import BinFileDP




__all__ = [
	'Metadata',
	'AmbientLightInstance',
	'AnimationParameters',
	'TaskContent',
	'Script',
	'AttachmentResources_v3',
	'AttachmentContainer_v7',
	'GlobalVersion_v156',
	'VehiclePreset_v30',
	'HudGuidanceLayout_v3',
	'LensFlare_v7',
	'ParticleKillBox_v2',
	'ParticleSystem_v3',
	'PersistentResource_v1',
	'Portal_v2',
	'RadioShow_v2',
	'RestStop_v1',
	'ReverbPreset_v1',
	'Room_v4',
	'SimulatedSound_v5',
	'SimulatedSoundContent_v6',
	'SimulatedSoundControl_v3',
	'SimulatedSoundInstance_v4',
	'SkinItem_v1',
	'SoundInstance_v5',
	'SoundPreset_v2',
	'SpawnPoint_v6',
	'SpawnPointScript_v3',
	'SpawnPosition_v1',
	'SpringBone_v3',
	'SpyBird_v2',
	'ThresholdEvent_v1',
	'Throwable_v6',
	'ThrowableItem_v3',
	'Tornado_v1',
	'Vehicle_v5',
	'VehicleScript_v3',
	'VehicleSound_v10',
	'Volume_v1',
	'WeaponItem_v3',
	'AmmoItem_v3',
	'Ammo_v4',
	'AnimationAtTimeHandler_v1',
	'Battery_v3',
	'Battery_v4',
	'BatteryItem_v3',
	'BirdSwarm_v1',
	'Blocker_v2',
	'CameraPath_v2',
	'CameraSet_v7',
	'Cinematic_v5',
	'CinematicLine_v2',
	'Collectible_v2',
	'ConstraintBone_v3',
	'DBDecal_v1',
	'DBParticleSystem_v1',
	'DebugEntity_v1',
	'DialogueLine_v4',
	'InteriorDefinition_v4',
	'LoadingScreenHint_v1',
	'MatDependentSimSound_v1',
	'LightSourceItem_v3',
	'LightSource_v10',
	'GameEventHandler_v1',
	'Effect_v3',
	'AmbientLight_v2',
	'Animation_v17',
	'Animation_v19',
	'AreaTrigger_v3',
	'CellInfo_v1',
	'Character_v13',
	'Character_v17',
	'CharacterClass_v38',
	'CharacterClass_v42',
	'CharacterScript_v3',
	'DynamicObject_v11',
	'DynamicObject_v13',
	'DynamicObjectScript_v3',
	'FloatingScript_v2',
	'GameEvent_v5',
	'KeyFrame_v1',
	'KeyFrameAnimation_v5',
	'KeyFramedObject_v4',
	'KeyFramedObject_v5',
	'KeyFramer_v3',
	'NotebookPage_v2',
	'PhysicsMaterial_v2',
	'PointLight_v11',
	'PointLight_v13',
	'ScriptInstance_v1',
	'ScriptVariables_v1',
	'ScriptVariables_v2',
	'Skeleton_v25',
	'SkeletonSetup_v1',
	'Sound_v21',
	'SpotLight_v20',
	'StaticObject_v10',
	'TaskDefinition_v11',
	'TaskDefinition_v15',
	'Trigger_v18',
	'Trigger_v20',
	'Waypoint_v1',
	'Weapon_v33',
	'Weapon_v39',
]


class OBRSFields:
	class list_str(ByteStreamField[list[str], BinFileDP]):
		fixedSize: int
		
		def __init__(self, fixedSize: int):
			self.fixedSize = fixedSize
		
		def caller(self, stream, obj, extra: BinFileDP):
			return [extra.getValue(int(stream), str) for _ in range(int(stream) if self.fixedSize == 0 else self.fixedSize)]
	
	class list_binfile[T](ByteStreamField[list[T], BinFileDP]):
		tyep: type[T]
		
		def __init__(self, tyep: type[T]):
			self.tyep = tyep
		
		def caller(self, stream, obj, extra: BinFileDP):
			return extra.get_list(self.tyep, count=int(stream), offset=int(stream))
	
	class str(ByteStreamField[str, BinFileDP]):
		def caller(self, stream, obj, extra: BinFileDP):
			return extra.getValue(int(stream), str)


class _UnknownClass(StreamObject):
	def __init_subclass__(cls, size: int):
		super().__init_subclass__()
		cls._registry: list[cls] = list()
		cls.data = StreamFields.bytes(size)
	
class AttachmentResources_v3(_UnknownClass, size=24): pass
class ParticleKillBox_v2(_UnknownClass, size=64): pass
class ParticleSystem_v3(_UnknownClass, size=61): pass
class PersistentResource_v1(_UnknownClass, size=4): pass
class Portal_v2(_UnknownClass, size=28): pass
class RadioShow_v2(_UnknownClass, size=28): pass
class RestStop_v1(_UnknownClass, size=28): pass
class ReverbPreset_v1(_UnknownClass, size=72): pass
class Room_v4(_UnknownClass, size=32): pass
class SimulatedSound_v5(_UnknownClass, size=32): pass
class SimulatedSoundContent_v6(_UnknownClass, size=29): pass
class SimulatedSoundControl_v3(_UnknownClass, size=16): pass
class SimulatedSoundInstance_v4(_UnknownClass, size=69): pass
class SkinItem_v1(_UnknownClass, size=36): pass
class SoundInstance_v5(_UnknownClass, size=69): pass
class SoundPreset_v2(_UnknownClass, size=28): pass
class SpawnPoint_v6(_UnknownClass, size=96): pass
class SpawnPointScript_v3(_UnknownClass, size=48): pass
class SpawnPosition_v1(_UnknownClass, size=56): pass
class SpringBone_v3(_UnknownClass, size=36): pass
class SpyBird_v2(_UnknownClass, size=76): pass
class ThresholdEvent_v1(_UnknownClass, size=8): pass
class Throwable_v6(_UnknownClass, size=49): pass
class ThrowableItem_v3(_UnknownClass, size=86): pass
class Tornado_v1(_UnknownClass, size=64): pass
class Vehicle_v5(_UnknownClass, size=100): pass
class VehicleScript_v3(_UnknownClass, size=48): pass
class VehicleSound_v10(_UnknownClass, size=72): pass
class Volume_v1(_UnknownClass, size=68): pass
class WeaponItem_v3(_UnknownClass, size=86): pass
class AmmoItem_v3(_UnknownClass, size=86): pass
class Ammo_v4(_UnknownClass, size=56): pass
class AnimationAtTimeHandler_v1(_UnknownClass, size=8): pass
class Battery_v3(_UnknownClass, size=36): pass
class Battery_v4(_UnknownClass, size=36): pass
class BatteryItem_v3(_UnknownClass, size=86): pass
class BirdSwarm_v1(_UnknownClass, size=76): pass
class Blocker_v2(_UnknownClass, size=84): pass
class CameraPath_v2(_UnknownClass, size=13): pass
class CameraSet_v7(_UnknownClass, size=84): pass
class Cinematic_v5(_UnknownClass, size=112): pass
class CinematicLine_v2(_UnknownClass, size=26): pass
class Collectible_v2(_UnknownClass, size=33): pass
class ConstraintBone_v3(_UnknownClass, size=72): pass
class DBDecal_v1(_UnknownClass, size=36): pass
class DBParticleSystem_v1(_UnknownClass, size=12): pass
class DebugEntity_v1(_UnknownClass, size=56): pass
class DialogueLine_v4(_UnknownClass, size=35): pass
class InteriorDefinition_v4(_UnknownClass, size=56): pass
class LoadingScreenHint_v1(_UnknownClass, size=20): pass
class MatDependentSimSound_v1(_UnknownClass, size=12): pass
class LightSourceItem_v3(_UnknownClass, size=86): pass
class LightSource_v10(_UnknownClass, size=186): pass
class GameEventHandler_v1(_UnknownClass, size=8): pass
class Effect_v3(_UnknownClass, size=32): pass
class AmbientLight_v2(_UnknownClass, size=41): pass

# // TODO investigate, may not be normal cid
class GlobalVersion_v156(_UnknownClass, size=4): pass


# // TODO investigate, weirdly large so idk
class VehiclePreset_v30(_UnknownClass, size=627): pass
class HudGuidanceLayout_v3(_UnknownClass, size=859): pass
class LensFlare_v7(_UnknownClass, size=489): pass
# class KeyframedObjectScript_v3(_UnknownClass, size=48): pass



"""
CID_STREAMEDCOLLISIONPACKAGE
CID_STREAMEDTEXTURE
CID_STREAMEDMESH
CID_STREAMEDHAVOKANIMATION
CID_STREAMEDSOUND
CID_STREAMEDFOLIAGEMESH
CID_STREAMEDPARTICLESYSTEM
CID_STREAMEDCLOTH
CID_STREAMEDFACEFXACTOR
CID_STREAMEDFACEFXANIMSET
CID_SKELETON
CID_ANIMATION
CID_SOUND
CID_SIMULATEDSOUND
CID_SIMULATEDSOUNDCONTROL
CID_SIMULATEDSOUNDCONTENT
CID_GAME_EVENT
CID_GAME_EVENT_HANDLER
CID_VEHICLESOUND
CID_MATDEPENDENTSOUND
CID_MATDEPENDENTSIMSOUND
CID_WEAPON
CID_AI_PROFILE
CID_AI_PROFILE_VALUE
CID_ROADMAP
CID_VEHICLE_PRESET
CID_DIALOGUE_LINE
CID_CHARACTERCLASS
CID_EFFECT
CID_NOTEBOOK_PAGE
CID_PHYSICSMATERIAL
CID_RESTSTOP
CID_MAPAREA
CID_SKELETONSETUP
CID_SPRINGBONE
CID_CONSTRAINTBONE
CID_CAMERASET
CID_COLORCORRECTION
CID_HUDGUIDANCELAYOUT
CID_CAMERAPATH
CID_LIGHTSOURCE
CID_AMMO
CID_BATTERY
CID_DBDECAL
CID_SKINITEM
CID_CINEMATIC_LINE
CID_RADIO_SHOW
CID_COLLECTIBLE
CID_TERRAIN
CID_STATICOBJECT
CID_PERSISTENTLEVELBLOCK
CID_DYNAMICOBJECT
CID_PVSBOUND
CID_TERRAINDATA
CID_FOLIAGEDATA
CID_VEHICLE
CID_CHARACTER
CID_TRIGGER
CID_TERRAINCOLLISION
CID_CELLRESOURCE
CID_PERSISTENTRESOURCE
CID_WORLDVERSION
CID_SPOTLIGHT
CID_PARTICLESYSTEM
CID_SOUNDINSTANCE
CID_SIMULATEDSOUNDINSTANCE
CID_ATTACHMENTCONTAINER
CID_PATHFINDINGMESH
CID_CHARACTERSCRIPT
CID_TRIGGERSCRIPT
CID_SPOTLIGHTSCRIPT
CID_PARTICLESYSTEMSCRIPT
CID_SOUNDSCRIPT
CID_SIMULATEDSOUNDSCRIPT
CID_FLOATINGSCRIPT
CID_TASKSCRIPT
CID_TASKDEFINITION
CID_DEBUGENTITY
CID_DEBUGENTITYSCRIPT
CID_PUBLICSCRIPTVARIABLE
CID_CINEMATIC
CID_CINEMATICSCRIPT
CID_TERRAINMATERIAL
CID_VEHICLESCRIPT
CID_DYNAMICOBJECTSCRIPT
CID_POINTLIGHT
CID_POINTLIGHTSCRIPT
CID_LOWDETAILCELLINFO
CID_GLOBALVERSION
CID_ATTACHMENTRESOURCES
CID_DBPARTICLESYSTEM
CID_INTERIORDEFINITION
CID_ROOM
CID_PORTAL
CID_SOLIDBSP
CID_CELLOVERLAP
CID_WAYPOINT
CID_WAYPOINTSCRIPT
CID_PORTALSCRIPT
CID_SPAWNPOINT
CID_SPAWNPOINTSCRIPT
CID_AMBIENTLIGHT
CID_AMBIENTLIGHTSCRIPT
CID_VOLUMETRICOCCLUSIONDATA
CID_AREATRIGGER
CID_TRACKABLE
CID_AMBIENTSOUNDINSTANCE
CID_DBFACEFXANIMSET
CID_KEYFRAMER
CID_KEYFRAMERSCRIPT
CID_KEYFRAMEANIMATION
CID_KEYFRAME
CID_KEYFRAMEDOBJECT
CID_KEYFRAMEDOBJECTSCRIPT
CID_ANIMATIONATTIMEHANDLER
CID_THRESHOLDEVENT
CID_SPATIALTEXTUREINFO
CID_COVERPOINTS
CID_PARTICLEKILLBOX
CID_ITEMSCRIPT
CID_HIGHDETAILCELLINFO
CID_OCCLUSIONVOLUME
CID_STATICLEVELGEOMETRY
CID_BLOCKER
CID_WEAPONITEM
CID_THROWABLEITEM
CID_THROWABLE
CID_SCRIPTINSTANCE
CID_SCRIPTINSTANCESCRIPT
CID_LIGHTSOURCEITEM
CID_AMMOITEM
CID_BATTERYITEM
CID_SPYBIRD
CID_SPYBIRDSCRIPT
CID_VOLUME
CID_SPAWNPOSITION
CID_SPAWNPOSITIONSCRIPT
CID_BIRDSWARM
CID_BIRDSWARMSCRIPT
CID_CLIFFEDGE
CID_BLOCKEDGE
CID_AOFIELD
CID_SKINITEMINSTANCE
CID_TORNADO
CID_TORNADOSCRIPT
CID_LENSFLARE
CID_SOUNDPRESET
CID_LENSFLARESCRIPT
CID_REVERBPRESET
CID_LOADINGSCREENHINT
CID_CELLINFO
"""


class Metadata:
	class TextureMetadata_v1(StreamObject):
		type:                       int         = StreamFields.uint()                       # variable('type', textureMetadata.type);
		format:                     int         = StreamFields.uint()                       # variable('format', textureMetadata.format);
		filter:                     int         = StreamFields.uint()                       # variable('filter', textureMetadata.format);
		width:                      int         = StreamFields.uint()                       # variable('width', textureMetadata.width);
		height:                     int         = StreamFields.uint()                       # variable('height', textureMetadata.height);
		depth:                      int         = StreamFields.uint()                       # variable('depth', textureMetadata.depth);
		skip:                       bytes       = StreamFields.bytes(4)                     # skip(4);
		mipmapOffsets:              list[int]   = StreamFields.iter(lambda x: x.i_4s, 8)    # variable('mipmapOffsets', textureMetadata.mipmapOffsets, 8lu);
		highDetailStreamDistance:   float       = StreamFields.float()                      # variable('highDetailStreamDistance', textureMetadata.highDetailStreamDistance);
		useTextureLOD:              bool        = StreamFields.bool()                       # variable('useTextureLOD', textureMetadata.useTextureLOD);
	
	class FileInfoMetadata_v1(StreamObject):
		fileSize:                   int         = StreamFields.uint()                       # variable('fileSize', fileInfoMetadata.fileSize);
		fileDataCRC:                int         = StreamFields.uint()                       # variable('fileDataCRC', fileInfoMetadata.fileDataCRC);
		flags:                      int         = StreamFields.uint()                       # variable('flags', fileInfoMetadata.flags);
	
	class HavokAnimationMetadata_v1(StreamObject):
		animationEventPath:         str         = StreamFields.str(-1)                      # variable('animationEventPath', havokAnimationMetadata.animationEventPath, false);
	
	class ParticleSystemMetadata_v1(StreamObject):
		textureResources:           list[RID]   = StreamFields.iter(RID)                    # objects('textureResources', particleSystemMetadata.textureRids, kRID);
	
	class MeshMetadata_v1(StreamObject):
		vertexBufferBytes:          int         = StreamFields.uint()                       # variable('vertexBufferBytes', meshMetadata.vertexBufferBytes);
		indexCount:                 int         = StreamFields.uint()                       # variable('indexCount', meshMetadata.indexCount);
		boundBox:                   BoundBox    = StreamFields.call(BoundBox)               # object('boundBox', meshMetadata.boundBox, kAABB);
		hasBones:                   bool        = StreamFields.bool()                       # variable('hasBones', meshMetadata.hasBones);
		textureRids:                list[RID]   = StreamFields.iter(RID)                    # objects('textureResources', meshMetadata.textureRids, kRID);
	
	class FoliageMeshMetadata_v1(StreamObject):
		vertexBufferBytes:          int         = StreamFields.uint()                       # variable('vertexBufferBytes', foliageMeshMetadata.vertexBufferBytes);
		indexCount:                 int         = StreamFields.uint()                       # variable('indexCount', foliageMeshMetadata.indexCount);
		boundBox:                   BoundBox    = StreamFields.call(BoundBox)               # object('boundBox', foliageMeshMetadata.boundBox, kAABB);
		textureRids:                list[RID]   = StreamFields.iter(RID)                    # objects('textureResources', foliageMeshMetadata.textureRids, kRID);
	
class PhysicsMaterial_v2(StreamObject):
	gid:    GID = StreamFields.call(GID)
	index:  int = StreamFields.uint(1)
	name:   str = StreamFields.str()

class Skeleton_v25(StreamObject[BinFileDP]):
	gid:    GID  = StreamFields.call(GID)   # variable('gid', skeleton.gid);
	name:   str  = OBRSFields.str()         # variable('name', skeleton.name, true);
	rid:    RID  = StreamFields.call(RID)   # object('resource', skeleton.rid, kRID);
	id:     int  = StreamFields.int()       # variable('id', skeleton.id);

class SkeletonSetup_v1(StreamObject[BinFileDP]):
	rootBoneGid:    GID     = StreamFields.call(GID)    # variable('rootBoneGid', skeletonSetup.rootBoneGid);
	identifier:     str     = OBRSFields.str()          # variable('identifier', skeletonSetup.identifier, true);
	unknown:        bytes   = StreamFields.bytes(7)     # skip(7);

class CellInfo_v1(StreamObject):
	x:                      int  = StreamFields.uint() # variable('x', cellInfo.x);
	y:                      int  = StreamFields.uint() # variable('y', cellInfo.y);
	lowDetailFoliageCount:  int  = StreamFields.sint() # variable('lowDetailFoliageCount', cellInfo.lowDetailFoliageCount);
	highDetailFoliageCount: int  = StreamFields.sint() # variable('highDetailFoliageCount', cellInfo.highDetailFoliageCount);

class AnimationParameters(StreamObject):
	animationBlendTime: float   = StreamFields.float()  # variable('animationBlendTime', animationParameters.animationBlendTime);
	halfRotationTime:   float   = StreamFields.float()  # variable('halfRotationTime', animationParameters.halfRotationTime);
	tiltGain:           float   = StreamFields.float()  # variable('tiltGain', animationParameters.tiltGain);
	tiltRegression:     float   = StreamFields.float()  # variable('tiltRegression', animationParameters.tiltRegression);
	tiltAngleRadians:   float   = StreamFields.float()  # variable('tiltAngleRadians', animationParameters.tiltAngleRadians);
	tiltAgility:        float   = StreamFields.float()  # variable('tiltAgility', animationParameters.tiltAgility);
	tiltScaleForward:   float   = StreamFields.float()  # variable('tiltScaleForward', animationParameters.tiltScaleForward);
	tiltScaleBackwards: float   = StreamFields.float()  # variable('tiltScaleBackwards', animationParameters.tiltScaleBackwards);
	animationProfile:   int     = StreamFields.uint()   # variable('animationProfile', animationParameters.animationProfile);
	
class ScriptInstance_v1(StreamObject):
	attachmentGid:  GID         = StreamFields.call(GID)        # variable('attachmentGid', scriptInstance.attachmentGid);
	gid:            GID         = StreamFields.call(GID)        # variable('gid', scriptInstance.gid);
	rotation:       mat3        = GLMFields.mat3()   # variable('rotation', scriptInstance.rotation);
	position:       vec3        = GLMFields.vec3()   # variable('position', scriptInstance.position);
	
class DynamicObject_v11(StreamObject[BinFileDP]):
	rot:                    mat3    = GLMFields.mat3()       #   variable('rotation', dynamicObject.rotation);
	pos:                    vec3    = GLMFields.vec3()       #   variable('position', dynamicObject.position);
	physicsResource:        RID         = StreamFields.call(RID)            #   object('physicsResource', dynamicObject.physicsResource, kRID);
	resourcePath:           str         = OBRSFields.str()              #   variable('resourcePath', dynamicObject.resourcePath, true);
	meshResource:           RID         = StreamFields.call(RID)            #   object('meshResource', dynamicObject.meshResource, kRID);
	identifier:             str         = OBRSFields.str()              #   variable('identifier', dynamicObject.identifier, true);
	value_unknown1:         int         = StreamFields.int()                #   variable('', unknown1);
	attachmentContainer:    ObjectID    = StreamFields.call(ObjectID)       #   variable('attachmentContainer', dynamicObject.attachmentContainer);
	value_unknown3:         int         = StreamFields.int()                #   variable('', unknown3);
	value_name3:            int         = StreamFields.int()                #   skip(4); //std::string name3 = _dp->getString(cid.readUint32LE());
	gid:                    GID         = StreamFields.call(GID)            #   variable('gid', dynamicObject.gid);
	skip:                   bytes       = StreamFields.bytes(9)             #   skip(9)
	
class DynamicObject_v13(StreamObject[BinFileDP]):
	rot:                    mat3        = GLMFields.mat3()                  #   variable('rotation', dynamicObject.rotation);
	pos:                    vec3        = GLMFields.vec3()                  #   variable('position', dynamicObject.position);
	physicsResource:        RID         = StreamFields.call(RID)            #   object('physicsResource', dynamicObject.physicsResource, kRID);
	resourcePath:           str         = OBRSFields.str()                  #   variable('resourcePath', dynamicObject.resourcePath, true);
	meshResource:           RID         = StreamFields.call(RID)            #   object('meshResource', dynamicObject.meshResource, kRID);
	identifier:             str         = OBRSFields.str()                  #   variable('identifier', dynamicObject.identifier, true);
	value_unknown1:         int         = StreamFields.int()                #   variable('', unknown1);
	attachmentContainer:    ObjectID    = StreamFields.call(ObjectID)       #   variable('attachmentContainer', dynamicObject.attachmentContainer);
	value_unknown3:         int         = StreamFields.int()                #   variable('', unknown3);
	value_name3:            int         = StreamFields.int()                #   skip(4); //std::string name3 = _dp->getString(cid.readUint32LE());
	gid:                    GID         = StreamFields.call(GID)            #   variable('gid', dynamicObject.gid);
	skip:                   bytes       = StreamFields.bytes(13)            #   skip(9)
	
class AreaTrigger_v3(StreamObject[BinFileDP]):
	gid:        GID             = StreamFields.call(GID)    # variable('gid', areaTrigger.gid)
	value:      int             = StreamFields.int()        # variable('', uint)
	identifier: str             = OBRSFields.str()      # variable('identifier', areaTrigger.identifier, true)
	positions:  list[vec2]      = OBRSFields.list_binfile(lambda x: vec2(x.f4, x.f4))    # variable('positions', areaTrigger.positions)
	skip:       bytes           = StreamFields.bytes(32)    # skip(32)

class Trigger_v20(StreamObject[BinFileDP]):
	attachmentGid:  GID         = StreamFields.call(GID)    # 	variable('attachmentGid', trigger.attachmentGid);
	gid:            GID         = StreamFields.call(GID)    # 	variable('gid', trigger.gid);
	skip1:          bytes       = StreamFields.bytes(4)     # 	skip(4); // Priority?
	identifier:     str         = OBRSFields.str()      # 	variable('identifier', trigger.identifier, true);
	skip2:          bytes       = StreamFields.bytes(4)     # 	skip(4);
	localeString:   str         = OBRSFields.str()      # 	variable('localeString', trigger.localeString, true);
	skip3:          bytes       = StreamFields.bytes(12)    # 	skip(12);
	values:         list[int]   = OBRSFields.list_binfile(lambda x: x.i_4s)   #   std::vector<sint> values; variable('', values);
	skip4:          bytes       = StreamFields.bytes(7)     #   skip(7)

class Trigger_v18(StreamObject[BinFileDP]):
	attachmentGid:  GID         = StreamFields.call(GID)    # 	variable('attachmentGid', trigger.attachmentGid);
	gid:            GID         = StreamFields.call(GID)    # 	variable('gid', trigger.gid);
	skip1:          bytes       = StreamFields.bytes(4)     # 	skip(4); // Priority?
	identifier:     str         = OBRSFields.str()      # 	variable('identifier', trigger.identifier, true);
	skip2:          bytes       = StreamFields.bytes(4)     # 	skip(4);
	localeString:   str         = OBRSFields.str()      # 	variable('localeString', trigger.localeString, true);
	skip3:          bytes       = StreamFields.bytes(12)    # 	skip(12);
	values:         list[int]   = OBRSFields.list_binfile(lambda x: x.i_4s)   #   std::vector<sint> values; variable('', values);
	skip4:          bytes       = StreamFields.bytes(3)     #   skip(3)

class KeyFrame_v1(StreamObject):
	position: vec3  = GLMFields.vec3()   # variable('position', keyFrame.position);
	rotation: mat3  = GLMFields.mat3()   # variable('rotation', keyFrame.rotation);

class Waypoint_v1(StreamObject):
	gid: GID    = StreamFields.call(GID)        # variable('gid', waypoint.gid);
	rot: mat3   = GLMFields.mat3()   # variable('rotation', waypoint.rotation);
	pos: vec3   = GLMFields.vec3()   # variable('position', waypoint.position);

class StaticObject_v10(StreamObject):
	rotation:           mat3    = GLMFields.mat3()   # variable('rotation', staticObject.rotation);
	position:           vec3    = GLMFields.vec3()   # variable('position', staticObject.position);
	physicsResource:    RID     = StreamFields.call(RID)        # object('physicsResource', staticObject.physicsResource, kRID);
	skip_4:             bytes   = StreamFields.bytes(4)         # skip(4);
	meshResource:       RID     = StreamFields.call(RID)        # object('meshResource', staticObject.meshResource, kRID);
	skip_17:            bytes   = StreamFields.bytes(17)        # skip(17);

class ScriptVariables_v1(StreamObject):
	code_count:             int = StreamFields.int()
	code_ofset:             int = StreamFields.int()
	handlers_count:         int = StreamFields.int()
	handlers_ofset:         int = StreamFields.int()
	variables_count:        int = StreamFields.int()
	variables_ofset:        int = StreamFields.int()
	signals_count:          int = StreamFields.int()
	signals_ofset:          int = StreamFields.int()
	
class ScriptVariables_v2(StreamObject):
	code_count:             int = StreamFields.int()
	code_ofset:             int = StreamFields.int()
	handlers_count:         int = StreamFields.int()
	handlers_ofset:         int = StreamFields.int()
	variables_count:        int = StreamFields.int()
	variables_ofset:        int = StreamFields.int()
	signals_count:          int = StreamFields.int()
	signals_ofset:          int = StreamFields.int()
	debugEntries_count:     int = StreamFields.int()
	debugEntries_ofset:     int = StreamFields.int()

class DynamicObjectScript_v3(StreamObject):
	gid:    GID                 = StreamFields.call(GID)                    # variable('gid', dynamicObjectScript.gid);
	script: ScriptVariables_v1  = StreamFields.subitem(ScriptVariables_v1)  # object('scriptVariables', dynamicObjectScript.script, kScriptVariables);
	name:   str                 = StreamFields.call(lambda x: '')           # N/A
	value:  int                 = StreamFields.int()                        # uint value; variable('', value);
	skip:   bytes               = StreamFields.bytes(4)                     # skip(4);

class CharacterScript_v3(StreamObject):
	gid:    GID                 = StreamFields.call(GID)                    # variable('gid', dynamicObjectScript.gid);
	script: ScriptVariables_v1  = StreamFields.subitem(ScriptVariables_v1)  # object('scriptVariables', dynamicObjectScript.script, kScriptVariables);
	skip:   bytes               = StreamFields.bytes(8)                     # skip(8); // Always 0?

class Script(StreamObject):
	gid:    GID                 = StreamFields.call(GID)                    # variable('gid', dynamicObjectScript.gid);
	script: ScriptVariables_v1  = StreamFields.subitem(ScriptVariables_v1)  # object('scriptVariables', dynamicObjectScript.script, kScriptVariables);

class FloatingScript_v2(StreamObject):
	gid:        GID                 = StreamFields.call(GID)                    # variable('gid', dynamicObjectScript.gid);
	script:     ScriptVariables_v1  = StreamFields.subitem(ScriptVariables_v1)  # object('scriptVariables', dynamicObjectScript.script, kScriptVariables);
	rotation:   mat3                = GLMFields.mat3()               # variable('rotation', floatingScript.rotation);
	position:   vec3                = GLMFields.vec3()               # variable('position', floatingScript.position);

class GameEvent_v5(StreamObject[BinFileDP]):
	script: ScriptVariables_v1      = StreamFields.subitem(ScriptVariables_v1)  # object('scriptVariables', gameEvent.script, kScriptVariables);
	gid:    GID                     = StreamFields.call(GID)                    # variable('gid', gameEvent.gid);
	name:   str                     = OBRSFields.str()                      # variable('name', gameEvent.name, true);
	skip:   bytes                   = StreamFields.bytes(8)                     # skip(8);
	
class KeyFrameAnimation_v5(StreamObject[BinFileDP]):
	gid:                GID         = StreamFields.call(GID)        # 	variable('gid', keyFrameAnimation.gid);
	startKeyFrame:      int         = StreamFields.int()            # 	variable('startKeyFrame', keyFrameAnimation.startKeyFrame);
	endKeyFrame:        int         = StreamFields.int()            # 	variable('endKeyFrame', keyFrameAnimation.endKeyFrame);
	length:             float       = StreamFields.float()          # 	variable('length', keyFrameAnimation.length);
	unk1:               list[int]   = OBRSFields.list_binfile(int)    # 	variable('', std::vector<uint>);    // Unknown values
	unk2:               list[float] = OBRSFields.list_binfile(float)       # 	variable('', std::vector<float>);       // Unknown values
	unk3:               list[float] = OBRSFields.list_binfile(float)       # 	variable('', std::vector<float>);       // Unknown values
	animationResource:  RID         = StreamFields.call(RID)        #   object('animationResource', keyFrameAnimation.animationResource, kRID);
	skip:               bytes       = StreamFields.bytes(4)         #   skip(4);
	nextAnimation:      GID         = StreamFields.call(GID)        #   variable('nextAnimation', keyFrameAnimation.nextAnimation);

class Sound_v21(StreamObject):
	gid:                GID     = StreamFields.call(GID)    # variable('gid', sound.gid);
	threed:             bool    = StreamFields.bool()       # variable('threed', sound.threed);
	streamed:           bool    = StreamFields.bool()       # variable('streamed', sound.streamed);
	looping:            int     = StreamFields.int()        # variable('looping', sound.looping);
	volume:             float   = StreamFields.float()      # variable('volume', sound.volume);
	hotspot:            float   = StreamFields.float()      # variable('hotspot', sound.hotspot);
	falloff:            float   = StreamFields.float()      # variable('falloff', sound.falloff);
	volumeVariation:    float   = StreamFields.float()      # variable('volumeVariation', sound.volumeVariation);
	frequencyVariation: float   = StreamFields.float()      # variable('frequencyVariation', sound.frequencyVariation);
	skip1:              bytes   = StreamFields.bytes(0x26)  # skip(0x26);
	rid:                RID     = StreamFields.call(RID)    # object('resource', sound.rid, kRID);
	skip2:              bytes   = StreamFields.bytes(7)     # skip(7);

class AttachmentContainer_v7(StreamObject[BinFileDP]):
	spotLights:                 list[GID] = OBRSFields.list_binfile(GID)   # variable('spotLights', attachmentContainer.spotLights);
	particleSystems:            list[GID] = OBRSFields.list_binfile(GID)   # variable('particleSystems', attachmentContainer.particleSystems);
	soundInstances:             list[GID] = OBRSFields.list_binfile(GID)   # variable('soundInstances', attachmentContainer.soundInstances);
	simulatedSoundInstances:    list[GID] = OBRSFields.list_binfile(GID)   # variable('simulatedSoundInstances', attachmentContainer.simulatedSoundInstances);
	pointLights:                list[GID] = OBRSFields.list_binfile(GID)   # variable('pointLights', attachmentContainer.pointLights);
	ambientLights:              list[GID] = OBRSFields.list_binfile(GID)   # variable('ambientLights', attachmentContainer.ambientLights);
	triggers:                   list[GID] = OBRSFields.list_binfile(GID)   # variable('triggers', attachmentContainer.triggers);
	scriptInstances:            list[GID] = OBRSFields.list_binfile(GID)   # variable('scriptInstances', attachmentContainer.scriptInstances);
	lensFlares:                 list[GID] = OBRSFields.list_binfile(GID)   # variable('lensFlares', attachmentContainer.lensFlares); // ?

class AmbientLightInstance(StreamObject):
	scriptGid:  GID         = StreamFields.call(GID)        # variable('scriptGid', ambientLightInstance.scriptGid);
	gid:        GID         = StreamFields.call(GID)        # variable('gid', ambientLightInstance.gid);
	position:   vec3        = GLMFields.vec3()   # variable('position', ambientLightInstance.position);
	color:      vec3        = GLMFields.vec3()   # variable('color', ambientLightInstance.color);
	decay:      float       = StreamFields.float()          # variable('decay', ambientLightInstance.decay);
	autoStart:  bool        = StreamFields.bool()           # variable('autoStart', ambientLightInstance.autoStart);
	intensity:  float       = StreamFields.float()          # variable('intensity', ambientLightInstance.intensity);

class TaskContent(StreamObject[BinFileDP]):
	skip1:      bytes               = StreamFields.bytes(12)                    # skip(12);
	resources:  list[RID]           = OBRSFields.list_binfile(RID)                     # variable('resources', taskContent.rids);    // List of rids
	skip2:      bytes               = StreamFields.bytes(8)                     # skip(8);    // List of gids + 8byte padding
	container:  AttachmentResources_v3 = StreamFields.subitem(AttachmentResources_v3) # object('', attachmentResource, kAttachmentResources);   // Unknown beef_container
	value:      list[int]           = StreamFields.iter(lambda x: int(x))               # variable('', std::vector<uint>, false);

class NotebookPage_v2(StreamObject[BinFileDP]):
	gid:                GID     = StreamFields.call(GID)    # variable('gid', notebookPage.gid);
	name:               str     = OBRSFields.str()      # variable('name', notebookPage.name, true);
	skip:               bytes   = StreamFields.bytes(8)     # skip(8);    // Probably GID?
	episodeNumber:      int     = StreamFields.int()        # variable('episodeNumber', notebookPage.episodeNumber);
	id:                 int     = StreamFields.int()        # variable('id', notebookPage.id);
	onlyInNightmare:    bool    = StreamFields.bool()       # variable('onlyInNightmare', notebookPage.onlyInNightmare);

class Character_v17(StreamObject):
	gid:                    GID         = StreamFields.call(GID)        # 	variable('gid', character.gid);
	classGid:               GID         = StreamFields.call(GID)        # 	variable('classGid', character.classGid);
	meshResource:           RID         = StreamFields.call(RID)        # 	object('meshResource', character.meshResource, kRID); // Mesh
	rotation:               mat3        = GLMFields.mat3()   # 	variable('rotation', character.rotation);
	position:               vec3        = GLMFields.vec3()   # 	variable('position', character.position);
	resources:              list[RID]   = StreamFields.iter(RID)        # 	objects('resources', character.resources, kRID);
	skip:                   bytes       = StreamFields.bytes(4)         #   skip(58);
	identifier:             str         = StreamFields.str(-1)          # variable('identifier', character.identifier, false);
	clothResource:          RID         = StreamFields.call(RID)        # object('clothResource', character.clothResource, kRID);
	clothparams:            bytes       = StreamFields.bytes(48)        # skip(48); // TODO: Cloth Parameters
	fxaResource:            RID         = StreamFields.call(RID)        # object('fxaResource', character.fxaResource, kRID); // FaceFX
	skip2:                  bytes       = StreamFields.bytes(1)         # skip(1);
	animgraphResource:      RID         = StreamFields.call(RID)        # object('animgraphResource', character.animgraphResource, kRID); // Animgraphs
	skip3:                  bytes       = StreamFields.bytes(9)         # skip(9);
	unkr1:                  RID         = StreamFields.call(RID)        # object('unkr1', rid_t, kRID); // Additional resources
	unkr2:                  RID         = StreamFields.call(RID)        # object('unkr2', rid_t, kRID); // Additional resources
	unkr3:                  RID         = StreamFields.call(RID)        # object('unkr3', rid_t, kRID); // Additional resources
	unkr4:                  RID         = StreamFields.call(RID)        # object('unkr4', rid_t, kRID); // Additional resources

class Character_v13(StreamObject):
	gid:                    GID         = StreamFields.call(GID)        # 	variable('gid', character.gid);
	classGid:               GID         = StreamFields.call(GID)        # 	variable('classGid', character.classGid);
	skip1:                  bytes       = StreamFields.bytes(1)         # 	if (version == 13): skip(1);
	meshResource:           RID         = StreamFields.call(RID)        # 	object('meshResource', character.meshResource, kRID); // Mesh
	rotation:               mat3        = GLMFields.mat3()   # 	variable('rotation', character.rotation);
	position:               vec3        = GLMFields.vec3()   # 	variable('position', character.position);
	resources:              list[RID]   = StreamFields.iter(RID)        # 	objects('resources', character.resources, kRID);
	skip:                   bytes       = StreamFields.bytes(58)        #   skip(58);
	
class SpotLight_v20(StreamObject):
	attachmentGid:          GID         = StreamFields.call(GID)        # variable("attachmentGid",       GID
	gid:                    GID         = StreamFields.call(GID)        # variable("gid",                 GID
	position:               vec3        = GLMFields.vec3()   # variable("position",            glm::vec3
	rotation:               mat3        = GLMFields.mat3()   # variable("rotation",            glm::mat3
	color:                  vec3        = GLMFields.vec3()   # variable("color",               glm::vec3
	coneAngle:              float       = StreamFields.float()          # variable("coneAngle",           float
	decay:                  float       = StreamFields.float()          # variable("decay",               float
	lightMap:               RID         = StreamFields.call(RID)        # object("lightMap",              rid_t
	shadowMap:              RID         = StreamFields.call(RID)        # object("shadowMap",             rid_t
	castShadows:            bool        = StreamFields.bool()           # variable("castShadows",         bool
	shadowMapResolution:    int         = StreamFields.int()            # variable("shadowMapResolution", uint32_t
	shadowMapFiltering:     int         = StreamFields.int()            # variable("shadowMapFiltering",  uint32_t
	autostart:              bool        = StreamFields.bool()           # variable("autostart",           bool
	volumetric:             bool        = StreamFields.bool()           # variable("volumetric",          bool
	intensity:              float       = StreamFields.float()          # variable("intensity",           float
	volumetricDecay:        float       = StreamFields.float()          # variable("volumetricDecay",     float
	lightVolumeResource:    RID         = StreamFields.call(RID)        # object("lightVolumeResource",   rid_t
	volumetricEffect:       int         = StreamFields.int()            # variable("volumetricEffect",    uint32_t
	meshResource:           RID         = StreamFields.call(RID)        # object("meshResource",          rid_t
	meshPosition:           vec3        = GLMFields.vec3()   # variable("meshPosition",        glm::vec3
	meshRotation:           vec3        = GLMFields.vec3()   # variable("meshRotation",        glm::mat3
	near:                   float       = StreamFields.float()          # variable("near",                float
	depthBias:              float       = StreamFields.float()          # variable("depthBias",           float
	depthSlopeBias:         float       = StreamFields.float()          # variable("depthSlopeBias",      float
	far:                    float       = StreamFields.float()          # variable("far",                 float
	drainMultiplier:        float       = StreamFields.float()          # variable("drainMultiplier",     float
	controllable:           bool        = StreamFields.bool()           # variable("controllable",        bool
	enableSpecular:         bool        = StreamFields.bool()           # variable("enableSpecular",      bool
	volumetricOnly:         bool        = StreamFields.bool()           # variable("volumetricOnly",      bool
	skip:                   bytes       = StreamFields.bytes(8)         # skip(8);
	volumetricQuality:      int         = StreamFields.int()            # variable("volumetricQuality",   uint32_t

class KeyFramer_v3(StreamObject[BinFileDP]):
	gid:                    GID             = StreamFields.call(GID)        # variable('gid', keyFramer.gid);
	keyFrames:              list[ObjectID]  = OBRSFields.list_binfile(ObjectID)    # variable('keyFrames', keyFramer.keyFrames);
	keyFrameAnimations:     list[ObjectID]  = OBRSFields.list_binfile(ObjectID)    # variable('keyFrameAnimations', keyFramer.keyFrameAnimations);
	parentKeyFramer:        ObjectID        = StreamFields.call(ObjectID)   # variable('parentKeyFramer', keyFramer.parentKeyFramer);
	initialKeyframe:        int             = StreamFields.int()            # variable('initialKeyframe', keyFramer.initialKeyframe);
	attachmentContainer:    ObjectID        = StreamFields.call(ObjectID)   # variable('attachmentContainer', keyFramer.attachmentContainer);
	resources:              list[RID]       = OBRSFields.list_binfile(RID)         # variable('resources', keyFramer.resources);
	val1:                   bool            = StreamFields.bool()           # bool val1 = false; variable('', val1);

class KeyFramedObject_v4(StreamObject[BinFileDP]):
	rotation:           mat3        = GLMFields.mat3()                       # 	variable('rotation', keyFramedObject.rotation);
	position:           vec3        = GLMFields.vec3()                       # 	variable('position', keyFramedObject.position);
	physicsResource:    RID         = StreamFields.call(RID)                            # 	object('physicsResource', keyFramedObject.physicsResource, kRID);
	source:             str         = OBRSFields.str()                              # 	variable('source', keyFramedObject.source, true);
	meshResource:       RID         = StreamFields.call(RID)                            # 	object('meshResource', keyFramedObject.meshResource, kRID);
	name:               str         = OBRSFields.str()                              # 	variable('name', keyFramedObject.name, true);
	skip1:              bytes       = StreamFields.bytes(8)                             # 	skip(8);
	resources:          list[RID]   = OBRSFields.list_binfile(RID)                             # 	variable('resources', keyFramedObject.resources);
	gid:                GID         = StreamFields.call(GID)                            # 	variable('gid', keyFramedObject.gid);
	keyFramer:          ObjectID    = StreamFields.call(ObjectID)                       # 	variable('keyFramer', keyFramedObject.keyFramer);
	skip2:              bytes       = StreamFields.bytes(5)                             # 	skip(5);
	rotation2:          mat3        = mat3(0, 0, 0, 0, 0, 0, 0, 0, 0)   #   keyFramedObject.rotation2 = glm::identity<glm::mat3>();
	position2:          vec3        = vec3(0, 0, 0)                     #   keyFramedObject.position2 = glm::zero<glm::vec3>();
	
class KeyFramedObject_v5(StreamObject[BinFileDP]):
	rotation:           mat3    = GLMFields.mat3()   # 	variable('rotation', keyFramedObject.rotation);
	position:           vec3    = GLMFields.vec3()   # 	variable('position', keyFramedObject.position);
	physicsResource:    RID         = StreamFields.call(RID)        # 	object('physicsResource', keyFramedObject.physicsResource, kRID);
	source:             str         = OBRSFields.str()          # 	variable('source', keyFramedObject.source, true);
	meshResource:       RID         = StreamFields.call(RID)        # 	object('meshResource', keyFramedObject.meshResource, kRID);
	name:               str         = OBRSFields.str()          # 	variable('name', keyFramedObject.name, true);
	skip1:              bytes       = StreamFields.bytes(8)         # 	skip(8);
	resources:          list[RID]   = OBRSFields.list_binfile(RID)         # 	variable('resources', keyFramedObject.resources);
	gid:                GID         = StreamFields.call(GID)        # 	variable('gid', keyFramedObject.gid);
	keyFramer:          ObjectID    = StreamFields.call(ObjectID)   # 	variable('keyFramer', keyFramedObject.keyFramer);
	skip2:              bytes       = StreamFields.bytes(5)         # 	skip(5);
	rotation2:          mat3    = GLMFields.mat3()   #   variable('rotation2', keyFramedObject.rotation2)
	position2:          vec3    = GLMFields.vec3()   #   variable('position2', keyFramedObject.position2)

class CharacterClass_v38(StreamObject[BinFileDP]):
	gid:                        GID         = StreamFields.call(GID)        # variable('gid', characterClass.gid);
	name:                       str         = OBRSFields.str()          # variable('name', characterClass.name, true);
	baseClasses:                list[str]   = OBRSFields.list_str(4)        # variable('baseClasses', characterClass.baseClasses, 4);
	skeletonGid:                GID         = StreamFields.call(GID)        # variable('skeletonGid', characterClass.skeletonGid);
	strongShield:               bool        = StreamFields.bool()           # variable('strongShield', characterClass.strongShield);
	kickbackMultiplier:         float       = StreamFields.float()          # variable('kickbackMultiplier', characterClass.kickbackMultiplier);
	timeBetweenDazzles:         float       = StreamFields.float()          # variable('timeBetweenDazzles', characterClass.timeBetweenDazzles);
	endskip:                    bytes       = StreamFields.bytes(0x49)      # skip(0x49);
	
class CharacterClass_v42(StreamObject[BinFileDP]):
	gid:                        GID                 = StreamFields.call(GID)                    # variable('gid', characterClass.gid);
	name:                       str                 = OBRSFields.str()                      # variable('name', characterClass.name, true);
	baseClasses:                list[str]           = OBRSFields.list_str(0)                    # variable('baseClasses', characterClass.baseClasses);
	skeletonGid:                GID                 = StreamFields.call(GID)                    # variable('skeletonGid', characterClass.skeletonGid);
	parentName:                 str                 = OBRSFields.str()                      # variable('parentName', characterClass.parentName, true);
	capsuleHeight:              float               = StreamFields.float()                      # variable('capsuleHeight', characterClass.capsuleHeight);
	capsuleRadius:              float               = StreamFields.float()                      # variable('capsuleRadius', characterClass.capsuleRadius);
	lethalDoseOfHitEnergy:      float               = StreamFields.float()                      # variable('lethalDoseOfHitEnergy', characterClass.lethalDoseOfHitEnergy);
	healthRecoveryStartDelay:   float               = StreamFields.float()                      # variable('healthRecoveryStartDelay', characterClass.healthRecoveryStartDelay);
	healthRecoveryTime:         float               = StreamFields.float()                      # variable('healthRecoveryTime', characterClass.healthRecoveryTime);
	shadowShieldStrength:       float               = StreamFields.float()                      # variable('shadowShieldStrength', characterClass.shadowShieldStrength);
	strongShield:               bool                = StreamFields.bool()                       # variable('strongShield', characterClass.strongShield);
	kickbackMultiplier:         float               = StreamFields.float()                      # variable('kickbackMultiplier', characterClass.kickbackMultiplier);
	timeBetweenDazzles:         float               = StreamFields.float()                      # variable('timeBetweenDazzles', characterClass.timeBetweenDazzles);
	animations:                 list[ObjectID]      = OBRSFields.list_binfile(ObjectID)                # variable('animations', characterClass.animations);
	animationParameters:        AnimationParameters = StreamFields.subitem(AnimationParameters) # object('animationParameters', characterClass.animationParameters, kAnimationParameters);
	type:                       str                 = OBRSFields.str()                      # variable('type', characterClass.type, true);
	skip:                       bytes               = StreamFields.bytes(8)                     # skip(8); // Arcade Score, Arcade Multiplier
	
class PointLight_v11(StreamObject):
	attachmentGid:  GID     = StreamFields.call(GID)    # variable('attachmentGid', pointLight.attachmentGid);
	skip:           bytes   = StreamFields.bytes(12)    # skip(12)
	
class PointLight_v13(StreamObject):
	attachmentGid:      GID         = StreamFields.call(GID)        # variable('attachmentGid', pointLight.attachmentGid);
	gid:                GID         = StreamFields.call(GID)        # variable('gid', pointLight.gid);
	rotation:           mat3    = GLMFields.mat3()   # variable('rotation', pointLight.rotation);
	position:           vec3    = GLMFields.vec3()   # variable('position', pointLight.position);
	color:              vec3    = GLMFields.vec3()   # variable('color', pointLight.color);
	decay:              float       = StreamFields.float()          # variable('decay', pointLight.decay);
	directionalFalloff: float       = StreamFields.float()          # variable('directionalFalloff', pointLight.directionalFalloff);
	autoStart:          bool        = StreamFields.bool()           # variable('autoStart', pointLight.autoStart);
	castShadows:        bool        = StreamFields.bool()           # variable('castShadows', pointLight.castShadows);
	intensity:          float       = StreamFields.float()          # variable('intensity', pointLight.intensity);
	meshRid:            RID         = StreamFields.call(RID)        # object('meshResource', pointLight.meshRid, kRID);
	staticShadowMapRid: RID         = StreamFields.call(RID)        # object('staticShadowMapRsource', pointLight.staticShadowMapRid, kRID);
	meshRotation:       mat3    = GLMFields.mat3()   # variable('meshRotation', pointLight.meshRotation);
	meshPosition:       vec3    = GLMFields.vec3()   # variable('meshPosition', pointLight.meshPosition);
	drainMultiplier:    float       = StreamFields.float()          # variable('drainMultiplier', pointLight.drainMultiplier);
	enableSpecular:     bool        = StreamFields.bool()           # variable('enableSpecular', pointLight.enableSpecular);
	shadowMapRange:     float       = StreamFields.float()          # variable('shadowMapRange', pointLight.shadowMapRange);
	enableRangeClip:    bool        = StreamFields.bool()           # variable('enableRangeClip', pointLight.enableRangeClip);
	rangeClip:          float       = StreamFields.float()          # variable('rangeClip', pointLight.rangeClip);
	skip:               bytes       = StreamFields.bytes(0x94)      # skip(0x94)
	
class TaskDefinition_v15(StreamObject[BinFileDP]):
	name:                   str         = OBRSFields.str()          # variable('name', taskDefinition.name, true);
	values:                 list[int]   = OBRSFields.list_binfile(int)    # variable('', std::vector<uint32_t>);
	skip:                   bytes       = StreamFields.bytes(8)         # skip(8); // Another offset and count into the dp file
	rootTask:               bool        = StreamFields.bool()           # variable('rootTask', taskDefinition.rootTask);
	topLevelTask:           bool        = StreamFields.bool()           # variable('topLevelTask', taskDefinition.topLevelTask);
	rotation_task:          mat3    = GLMFields.mat3()   # variable('rotation', taskDefinition.rotation);
	position_task:          vec3    = GLMFields.vec3()   # variable('position', taskDefinition.position);
	activateOnStartup:      bool        = StreamFields.bool()           # variable('activateOnStartup', taskDefinition.activateOnStartup);
	activateOnStartupRound: list[bool]  = StreamFields.iter(bool, 3)    # variable('activateOnStartupRound', taskDefinition.activateOnStartupRound, 3);
	gidlessTask:            bool        = StreamFields.bool()           # variable('', bool gidlessTask = false);
	gid:                    GID         = StreamFields.call(GID)        # variable('gid', taskDefinition.gid);
	b2:                     bool        = StreamFields.bool()           # variable('', bool b2 = false); // If it is a non zero position?
	rot_player:             mat3    = GLMFields.mat3()   # variable('rotationPlayer', taskDefinition.rotationPlayer);
	pos_player:             vec3    = GLMFields.vec3()   # variable('positionPlayer', taskDefinition.positionPlayer);
	playerCharacter1:       GID         = StreamFields.call(GID)        # variable('playerCharacter1', taskDefinition.playerCharacter[0]);
	skip2:                  bytes       = StreamFields.bytes(8)         # skip(8);
	cinematic:              str         = OBRSFields.str()          # variable('cinematic', taskDefinition.cinematic, true);
	playerCharacter2:       GID         = StreamFields.call(GID)        # variable('playerCharacter2', taskDefinition.playerCharacter[1]);
	playerCharacter3:       GID         = StreamFields.call(GID)        # variable('playerCharacter3', taskDefinition.playerCharacter[2]);
	
class TaskDefinition_v11(StreamObject[BinFileDP]):
	name:                   str         = OBRSFields.str()          # variable('name', taskDefinition.name, true);
	values:                 list[int]   = OBRSFields.list_binfile(int)    # variable('', std::vector<uint32_t>);
	skip:                   bytes       = StreamFields.bytes(8)         # skip(8); // Another offset and count into the dp file
	rootTask:               bool        = StreamFields.bool()           # variable('rootTask', taskDefinition.rootTask);
	topLevelTask:           bool        = StreamFields.bool()           # variable('topLevelTask', taskDefinition.topLevelTask);
	rotation_task:          mat3    = GLMFields.mat3()   # variable('rotation', taskDefinition.rotation);
	position_task:          vec3    = GLMFields.vec3()   # variable('position', taskDefinition.position);
	activateOnStartup:      bool        = StreamFields.bool()           # variable('activateOnStartup', taskDefinition.activateOnStartup);
	gidlessTask:            bool        = StreamFields.bool()           # variable('', bool gidlessTask = false);
	gid:                    GID         = StreamFields.call(GID)        # variable('gid', taskDefinition.gid);
	b2:                     bool        = StreamFields.bool()           # variable('', bool b2 = false); // If it is a non zero position?
	end_data:               bytes       = StreamFields.bytes(0x44)      # skip(0x44);
	
class Animation_v17(StreamObject[BinFileDP]):
	gid:                    GID     = StreamFields.call(GID)    # variable('gid', animation.gid);
	skeletonGid:            GID     = StreamFields.call(GID)    # variable('skeletonGid', animation.skeletonGid);
	id:                     int     = StreamFields.int()        # variable('id', animation.id);
	rid:                    RID     = StreamFields.call(RID)    # object<rid_t>('animationResource', animation.rid, kRID);
	skip:                   bytes   = StreamFields.bytes(1)     # object<rid_t>('animationResource', animation.rid, kRID);
	name:                   str     = OBRSFields.str()      # variable('name', animation.name, true);
	useFingersLeft:         bool    = StreamFields.bool()       # variable('useFingersLeft', animation.useFingersLeft);
	useFingersRight:        bool    = StreamFields.bool()       # variable('useFingersRight', animation.useFingersRight);
	useFootIK:              bool    = StreamFields.bool()       # variable('useFootIK', animation.useFootIK);
	attachLeftHand:         bool    = StreamFields.bool()       # variable('attachLeftHand', animation.attachLeftHand);
	legSyncLoopCount:       int     = StreamFields.int()        # variable('legSyncLoopCount', animation.legSyncLoopCount);
	scriptedBlendIn:        bool    = StreamFields.bool()       # variable('scriptedBlendIn', animation.scriptedBlendIn);
	scriptedBlendInTime:    float   = StreamFields.float()      # variable('scriptedBlendInTime', animation.scriptedBlendInTime);
	scriptedBlendOut:       bool    = StreamFields.bool()       # variable('scriptedBlendOut', animation.scriptedBlendOut);
	scriptedMoveCapsule:    bool    = StreamFields.bool()       # variable('scriptedMoveCapsule', animation.scriptedMoveCapsule);

class Animation_v19(StreamObject[BinFileDP]):
	gid:                    GID     = StreamFields.call(GID)    # variable('gid', animation.gid);
	skeletonGid:            GID     = StreamFields.call(GID)    # variable('skeletonGid', animation.skeletonGid);
	id:                     int     = StreamFields.int()        # variable('id', animation.id);
	rid:                    RID     = StreamFields.call(RID)    # object<rid_t>('animationResource', animation.rid, kRID);
	name:                   str     = OBRSFields.str()      # variable('name', animation.name, true);
	useFingersLeft:         bool    = StreamFields.bool()       # variable('useFingersLeft', animation.useFingersLeft);
	useFingersRight:        bool    = StreamFields.bool()       # variable('useFingersRight', animation.useFingersRight);
	useFootIK:              bool    = StreamFields.bool()       # variable('useFootIK', animation.useFootIK);
	attachLeftHand:         bool    = StreamFields.bool()       # variable('attachLeftHand', animation.attachLeftHand);
	legSyncLoopCount:       int     = StreamFields.int()        # variable('legSyncLoopCount', animation.legSyncLoopCount);
	scriptedBlendIn:        bool    = StreamFields.bool()       # variable('scriptedBlendIn', animation.scriptedBlendIn);
	scriptedBlendInTime:    float   = StreamFields.float()      # variable('scriptedBlendInTime', animation.scriptedBlendInTime);
	scriptedBlendOut:       bool    = StreamFields.bool()       # variable('scriptedBlendOut', animation.scriptedBlendOut);
	scriptedMoveCapsule:    bool    = StreamFields.bool()       # variable('scriptedMoveCapsule', animation.scriptedMoveCapsule);

class Weapon_v33(StreamObject[BinFileDP]):
	gid:                GID     = StreamFields.call(GID)    # variable('gid', weapon.gid);
	name:               str     = OBRSFields.str()      # variable('name', weapon.name, true);
	physicsResource:    RID     = StreamFields.call(RID)    # object('physicsResource', weapon.physicsResource, kRID);
	meshResource:       RID     = StreamFields.call(RID)    # object('meshResource', weapon.meshResource, kRID);
	path:               str     = OBRSFields.str()      # variable('path', weapon.path, true);
	skip:               bytes   = StreamFields.bytes(103)   # skip(103)
	
class Weapon_v39(StreamObject[BinFileDP]):
	gid:                GID     = StreamFields.call(GID)    # variable('gid', weapon.gid);
	name:               str     = OBRSFields.str()      # variable('name', weapon.name, true);
	physicsResource:    RID     = StreamFields.call(RID)    # object('physicsResource', weapon.physicsResource, kRID);
	meshResource:       RID     = StreamFields.call(RID)    # object('meshResource', weapon.meshResource, kRID);
	path:               str     = OBRSFields.str()      # variable('path', weapon.path, true);
	melee:              bool    = StreamFields.bool()       # variable('melee', weapon.melee);
	accuracy:           float   = StreamFields.float()      # variable('accuracy', weapon.accuracy);
	energy:             float   = StreamFields.float()      # variable('energy', weapon.energy);
	scatterCount:       int     = StreamFields.int()        # variable('scatterCount', weapon.scatterCount);
	energyHotspotRange: float   = StreamFields.float()      # variable('energyHotspotRange', weapon.energyHotspotRange);
	energyFalloffRange: float   = StreamFields.float()      # variable('energyHotspotRange', weapon.energyFalloffRange);
	maxCarriedBullets:  int     = StreamFields.int()        # variable('maxCarriedBullets', weapon.maxCarriedBullets);
	clipSize:           int     = StreamFields.int()        # variable('clipSize', weapon.clipSize);
	twoHanded:          bool    = StreamFields.bool()       # variable('twoHanded', weapon.twoHanded);
	timeBetweenShots:   float   = StreamFields.float()      # variable('timeBetweenShots', weapon.timeBetweenShots);
	shootsFlares:       bool    = StreamFields.bool()       # variable('shootsFlares', weapon.shootsFlares);
	pumpAction:         bool    = StreamFields.bool()       # variable('pumpAction', weapon.pumpAction);
	lowClipLimit:       int     = StreamFields.int()        # variable('lowClipLimit', weapon.lowClipLimit);
	lowAmmoLimit:       int     = StreamFields.int()        # variable('lowAmmoLimit', weapon.lowAmmoLimit);
	recoil:             float   = StreamFields.float()      # variable('Recoil', weapon.recoil);
	aimFovMultiplier:   float   = StreamFields.float()      # variable('aimFovMultiplier', weapon.aimFovMultiplier);
	pickupAmmoCount:    int     = StreamFields.int()        # variable('pickupAmmoCount', weapon.pickupAmmoCount);
	autoAimDistance:    float   = StreamFields.float()      # variable('autoAimDistance', weapon.autoAimDistance);
	automatic:          bool    = StreamFields.bool()       # //variable('automatic', weapon.automatic);
	takenKickBack:      float   = StreamFields.float()      # variable('takenKickBack', weapon.takenKickBack);
	skip_39:            bytes   = StreamFields.bytes(4)     # skip(4); // TODO
	identifier:         str     = OBRSFields.str()      # variable('identifier', weapon.identifier, true);
	skip:               bytes   = StreamFields.bytes(38)    # skip(38)

