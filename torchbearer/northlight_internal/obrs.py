from __future__ import annotations

from loguru import logger

from torchbearer.mulch import Stream
from .dpfile import BinFileDP
from .types_general import BoundBox, RID
from .obrs_objects import AmbientLight_v2, AmbientLightInstance, Ammo_v4, AmmoItem_v3, Animation_v17, Animation_v19, AnimationAtTimeHandler_v1, AnimationParameters, \
	AreaTrigger_v3, AttachmentContainer_v7, AttachmentResources_v3, Battery_v3, Battery_v4, BatteryItem_v3, BirdSwarm_v1, Blocker_v2, CameraPath_v2, CameraSet_v7, CellInfo_v1, \
	Character_v13, Character_v17, CharacterClass_v38, CharacterClass_v42, CharacterScript_v3, Cinematic_v5, CinematicLine_v2, Collectible_v2, ConstraintBone_v3, DBDecal_v1, \
	DBParticleSystem_v1, DebugEntity_v1, DialogueLine_v4, DynamicObject_v11, DynamicObject_v13, DynamicObjectScript_v3, PhysicsMaterial_v2, \
	Effect_v3, FloatingScript_v2, GameEvent_v5, GameEventHandler_v1, InteriorDefinition_v4, KeyFrame_v1, KeyFrameAnimation_v5, KeyFramedObject_v4, KeyFramedObject_v5, KeyFramer_v3, \
	LightSource_v10, LightSourceItem_v3, LoadingScreenHint_v1, MatDependentSimSound_v1, Metadata, NotebookPage_v2, ParticleKillBox_v2, ParticleSystem_v3, PersistentResource_v1, \
	PointLight_v11, PointLight_v13, Portal_v2, RadioShow_v2, RestStop_v1, ReverbPreset_v1, Room_v4, Script, ScriptInstance_v1, ScriptVariables_v1, ScriptVariables_v2, \
	SimulatedSound_v5, SimulatedSoundContent_v6, SimulatedSoundControl_v3, SimulatedSoundInstance_v4, Skeleton_v25, SkeletonSetup_v1, SkinItem_v1, Sound_v21, SoundInstance_v5, \
	SoundPreset_v2, SpawnPoint_v6, SpawnPointScript_v3, SpawnPosition_v1, SpotLight_v20, SpringBone_v3, SpyBird_v2, StaticObject_v10, TaskContent, \
	TaskDefinition_v11, TaskDefinition_v15, ThresholdEvent_v1, Throwable_v6, ThrowableItem_v3, Tornado_v1, Trigger_v18, Trigger_v20, Vehicle_v5, VehicleScript_v3, VehicleSound_v10, \
	Volume_v1, Waypoint_v1, Weapon_v33, Weapon_v39, WeaponItem_v3


class UnknownObjectOBRS:
	name: str
	data: bytes
	
	cache = set()
	count = list()
	
	def __init__(self, name: str, stream: Stream, length: int, version: int | str):
		self.name = name
		self.data = stream[length]
		infostr = f"| {name} | v{version} | {length} bytes |"
		self.cache.add(infostr)
		self.count.append(infostr)
	
	def dict(self):
		return {
			'name': self.name,
			'data': self.data,
		}



"""
CID_ABILITY
CID_ACHIEVEMENT
CID_ACTIONPOINT
CID_AICOVERSET
CID_AIGRIDBLOCK
CID_AI_PROFILE
CID_AI_PROFILE_VALUE
CID_AI_TICKET_SETTING
CID_AMBIENTLIGHT
CID_AMBIENTLIGHTSCRIPT
CID_AMBIENTSOUNDINSTANCE
CID_AMMO
CID_AMMOBOX
CID_AMMOITEM
CID_ANIMATEDOBJECT
CID_ANIMATEDOBJECT_COMBINED
CID_ANIMATION
CID_ANIMATIONATFRAMEHANDLER
CID_ANIMATIONATTIMEHANDLER
CID_ANIMATIONBIND
CID_ANIMATIONSCENE
CID_ANIMATION_SYSTEM_GLOBAL
CID_AOFIELD
CID_ARCHETYPE_REFERENCE
CID_AREATRIGGER
CID_AREATRIGGERSCRIPT
CID_ATTACHMENTCONTAINER
CID_ATTACHMENTRESOURCES
CID_AUDIO_ENVIRONMENT
CID_BALANCING_DATA
CID_BATTERY
CID_BATTERYITEM
CID_BIRDSWARM
CID_BIRDSWARMSCRIPT
CID_BLOCKEDGE
CID_BLOCKER
CID_BLOCKERSCRIPT
CID_BLUEPRINT
CID_BUNDLE
CID_BUNDLE_TEMPLATES
CID_CAMERAPATH
CID_CAMERAPATHSOURCE
CID_CAMERASET
CID_CELLINFO
CID_CELLOVERLAP
CID_CELLRESOURCE
CID_CHARACTER
CID_CHARACTERCLASS
CID_CHARACTERSCRIPT
CID_CINEMATIC
CID_CINEMATICSCRIPT
CID_CINEMATIC_LIGHT_SETTINGS
CID_CINEMATIC_LINE
CID_CLIFFEDGE
CID_COLLAPSEDLODMESH
CID_COLLECTIBLE
CID_COLORCORRECTION
CID_COMBAT_DIALOGUE_DB
CID_CONSTRAINTBONE
CID_CONTEXTUAL_ANIMATION
CID_CONTROL_POINT
CID_COVER
CID_COVERPOINTS
CID_CRAFTING_RECIPE
CID_CURVE
CID_CURVEPOINT
CID_CUSTOM_TAG
CID_DAMAGEOBJECT
CID_DAMAGEPROFILE
CID_DAMAGESET
CID_DAMAGE_TRANSLATION
CID_DBAIDEFINITION
CID_DBDECAL
CID_DBFACEFXANIMSET
CID_DBPARTICLESYSTEM
CID_DEBUGENTITY
CID_DEBUGENTITYSCRIPT
CID_DECAL
CID_DIALOGUE_ACTION
CID_DIALOGUE_CHARACTER_TYPE
CID_DIALOGUE_CONDITION
CID_DIALOGUE_EVENT
CID_DIALOGUE_EVENT_HANDLER
CID_DIALOGUE_EVENT_SYSTEM
CID_DIALOGUE_LINE
CID_DIALOGUE_SET
CID_DIALOGUE_SET_DEFINITION
CID_DIALOGUE_SET_PLAYLIST_ITEM
CID_DIALOGUE_STRING
CID_DIALOGUE_TYPE
CID_DIALOGUE_VARIABLE
CID_DIALOGUE_VOICE_PROFILE
CID_DLC
CID_DROP_CONTEXT
CID_DROP_ENTITY
CID_DYNAMICOBJECT
CID_DYNAMICOBJECTSCRIPT
CID_EFFECT
CID_ENERGY_DROP_PRESET
CID_ENTITYBATCH
CID_ENTITY_ARCHETYPE
CID_ENUM_TABLE
CID_EPISODE
CID_EPISODEPLAYAREA
CID_EXCLUDEDMESH
CID_FLOATINGSCRIPT
CID_FOLIAGEDATA
CID_GAME_EVENT
CID_GAME_EVENT_HANDLER
CID_GENERATED_NAME_PRESET
CID_GENERICCOMPONENT
CID_GENERICENTITY
CID_GLOBALVARIABLES
CID_GLOBALVERSION
CID_GUIDANCE_OBJECTIVE
CID_GWNPATHFINDINGBLOCK
CID_HIGHDETAILCELLINFO
CID_HUDGUIDANCELAYOUT
CID_INTEL
CID_INTERIORDEFINITION
CID_ITEM
CID_ITEMSCRIPT
CID_ITEM_CATEGORY
CID_ITEM_TYPE
CID_JUNCTION
CID_KEYFRAME
CID_KEYFRAMEANIMATION
CID_KEYFRAMEDOBJECT
CID_KEYFRAMEDOBJECTSCRIPT
CID_KEYFRAMER
CID_KEYFRAMERSCRIPT
CID_KILL_CAMERA
CID_LENSFLARE
CID_LENSFLARESCRIPT
CID_LIGHTPROBEBLOCK
CID_LIGHTSOURCE
CID_LIGHTSOURCEITEM
CID_LOADINGSCREENHINT
CID_LOCATION
CID_LOGIC_ANIMATION
CID_LOOT_DROP_ITEM
CID_LOOT_DROP_PRESET
CID_LOOT_DROP_QUEUE
CID_LOOT_DROP_USER_FLAG
CID_LOWDETAILCELLINFO
CID_LV3
CID_MAPAREA
CID_MAP_BOUNDS_POLYGON_DEFINITION
CID_MAP_OVERLAY_DEFINITION
CID_MAP_ROOM_DEFINITION
CID_MATDEPENDENTSIMSOUND
CID_MATDEPENDENTSOUND
CID_MATERIAL
CID_MISSION
CID_MISSION_STEP
CID_MOVEMENT_MODELS
CID_NARRATIVE_OBJ
CID_NARRATIVE_OBJ_CHAIN
CID_NOTEBOOK_PAGE
CID_OCCLUSIONVOLUME
CID_PARTICLEKILLBOX
CID_PARTICLESYSTEM
CID_PARTICLESYSTEMSCRIPT
CID_PARTICLESYSTEMSTATE
CID_PATHFINDINGMESH
CID_PERSISTENTEPISODEBLOCK
CID_PERSISTENTLEVELBLOCK
CID_PERSISTENTRESOURCE
CID_PHYSICSMATERIAL
CID_PLAYERSKILL
CID_PLAYER_LEVELS
CID_POINTLIGHT
CID_POINTLIGHTSCRIPT
CID_PORTAL
CID_PORTALSCRIPT
CID_PROJECTILE
CID_PUBLICSCRIPTVARIABLE
CID_PVSBOUND
CID_QUANTUM_RIPPLE
CID_QUEST
CID_RADIO_SHOW
CID_RESTSTOP
CID_REVERBPRESET
CID_ROADMAP
CID_ROOM
CID_SCRIPTINSTANCE
CID_SCRIPTINSTANCESCRIPT
CID_SECTOR
CID_SIMULATEDSOUND
CID_SIMULATEDSOUNDCONTENT
CID_SIMULATEDSOUNDCONTROL
CID_SIMULATEDSOUNDINSTANCE
CID_SIMULATEDSOUNDSCRIPT
CID_SKELETON
CID_SKELETONSETUP
CID_SKINITEM
CID_SKINITEMINSTANCE
CID_SOLIDBSP
CID_SOUND
CID_SOUNDENVIRONMENT
CID_SOUNDINSTANCE
CID_SOUNDPRESET
CID_SOUNDSCRIPT
CID_SOUNDVOLUME
CID_SOUND_AMBIENCE
CID_SOUND_EVENT
CID_SOUND_EXTERNAL_SOURCE
CID_SOUND_MATERIAL_DB
CID_SPATIALTEXTUREINFO
CID_SPAWNPOINT
CID_SPAWNPOINTSCRIPT
CID_SPAWNPOSITION
CID_SPAWNPOSITIONSCRIPT
CID_SPOTLIGHT
CID_SPOTLIGHTSCRIPT
CID_SPRINGBONE
CID_SPYBIRD
CID_SPYBIRDSCRIPT
CID_STATICLEVELGEOMETRY
CID_STATICOBJECT
CID_STREAMEDCLOTH
CID_STREAMEDCOLLISIONPACKAGE
CID_STREAMEDFACEFXACTOR
CID_STREAMEDFACEFXANIMSET
CID_STREAMEDFOLIAGEMESH
CID_STREAMEDHAVOKANIMATION
CID_STREAMEDMESH
CID_STREAMEDPARTICLESYSTEM
CID_STREAMEDSOUND
CID_STREAMEDTEXTURE
CID_STREAMING_STATE
CID_STREAMING_STATE_NODE
CID_STREAMING_UNIT
CID_SWARM
CID_SWARMSCRIPT
CID_TASKCONTENT
CID_TASKDEFINITION
CID_TASKSCRIPT
CID_TERRAIN
CID_TERRAINCOLLISION
CID_TERRAINDATA
CID_TERRAINMATERIAL
CID_THRESHOLDEVENT
CID_THROWABLE
CID_THROWABLEITEM
CID_TIMEBLAST
CID_TIMEDODGE
CID_TIMEJUICE
CID_TIMEJUICEITEM
CID_TIMELINE
CID_TIMELINEEVENT
CID_TIMELINETRACK
CID_TIMEPOWERREWARDS
CID_TIMEPOWERS
CID_TIMERUSH
CID_TIMESHIELD
CID_TIMESTOP
CID_TORNADO
CID_TORNADOSCRIPT
CID_TRACKABLE
CID_TRIAL
CID_TRIGGER
CID_TRIGGERSCRIPT
CID_TUTORIAL
CID_TV_SHOW_OVERLAY
CID_UMBRATILEBLOCK
CID_UMBRAVALIDIDS
CID_UPGRADE
CID_VEHICLE
CID_VEHICLESCRIPT
CID_VEHICLESOUND
CID_VEHICLE_PRESET
CID_VIDEO
CID_VIDEO_DIARY
CID_VOLUME
CID_VOLUMEMAPID
CID_VOLUMEMAPPLANE
CID_VOLUMEMAPPORTAL
CID_VOLUMEMAPVOLUME
CID_VOLUMETRICOCCLUSIONDATA
CID_WAYPOINT
CID_WAYPOINTSCRIPT
CID_WEAPON
CID_WEAPONITEM
CID_WEAPON_DAMAGE_TRANSLATION
CID_WORLDVERSION
"""



class ObjectBinaryReadStream_v1[DT: BinFileDP | None]:
	stream: Stream
	dpfile: DT
	
	def __init__(self, stream: Stream, dpfile: DT = None):
		self.stream = stream
		self.dpfile = dpfile
	
	def object(self, objectType: str, version: int = 0):
		logger.info(f"Getting object {objectType}, v{version}")
		match objectType.lower():
			case 'rid':                     return RID(self.stream)
			case 'aabb':                    return BoundBox(self.stream)

			case 'taskcontent':             return TaskContent(self.stream, extra=self.dpfile)
			
			case 'ambientlightinstance':    return AmbientLightInstance(self.stream)
			case 'animationparameters':     return AnimationParameters(self.stream)

			case 'script':                  return Script(self.stream)
			case 'spotlightscript':         return Script(self.stream)
			case 'particlesystemscript':    return Script(self.stream)
			case 'soundscript':             return Script(self.stream)
			case 'spybirdscript':           return Script(self.stream)
			case 'scriptinstancescript':    return Script(self.stream)
			case 'ambientlightscript':      return Script(self.stream)
			case 'pointlightscript':        return Script(self.stream)
			case 'tornadoscript':           return Script(self.stream)
			case 'triggerscript':           return Script(self.stream)
			case 'areatriggerscript':       return Script(self.stream)
			case 'taskscript':              return Script(self.stream)
			case 'waypointscript':          return Script(self.stream)
			case 'keyframerscript':         return Script(self.stream)
			case 'keyframedobjectscript':   return Script(self.stream)
			case 'spawnpositionscript':     return Script(self.stream)
			case 'itemscript':              return Script(self.stream)
			case 'portalscript':            return Script(self.stream)
			case 'simulatedsoundscript':    return Script(self.stream)
		
		match objectType.lower(), version:
			case 'attachmentcontainer', 7:      return AttachmentContainer_v7(self.stream,  extra=self.dpfile)
			case 'gameevent', 5:                return GameEvent_v5(self.stream,            extra=self.dpfile)
			case 'keyframeanimation', 5:        return KeyFrameAnimation_v5(self.stream,    extra=self.dpfile)
			case 'keyframer', 3:                return KeyFramer_v3(self.stream,            extra=self.dpfile)
			case 'notebookpage', 2:             return NotebookPage_v2(self.stream,         extra=self.dpfile)
			case 'characterclass', 38:          return CharacterClass_v38(self.stream,      extra=self.dpfile)
			case 'characterclass', 42:          return CharacterClass_v42(self.stream,      extra=self.dpfile)
			case 'keyframedobject', 4:          return KeyFramedObject_v4(self.stream,      extra=self.dpfile)
			case 'keyframedobject', 5:          return KeyFramedObject_v5(self.stream,      extra=self.dpfile)
			case 'trigger', 18:                 return Trigger_v18(self.stream,             extra=self.dpfile)
			case 'trigger', 20:                 return Trigger_v20(self.stream,             extra=self.dpfile)
			case 'skeleton', 25:                return Skeleton_v25(self.stream,            extra=self.dpfile)
			case 'skeletonsetup', 1:            return SkeletonSetup_v1(self.stream,        extra=self.dpfile)
			case 'areatrigger', 3:              return AreaTrigger_v3(self.stream,          extra=self.dpfile)
			case 'animation', 17:               return Animation_v17(self.stream,           extra=self.dpfile)
			case 'animation', 19:               return Animation_v19(self.stream,           extra=self.dpfile)
			case 'weapon', 33:                  return Weapon_v33(self.stream,              extra=self.dpfile)
			case 'weapon', 39:                  return Weapon_v39(self.stream,              extra=self.dpfile)
			case 'dynamicobject', 11:           return DynamicObject_v11(self.stream,       extra=self.dpfile)
			case 'dynamicobject', 13:           return DynamicObject_v13(self.stream,       extra=self.dpfile)
			case 'taskdefinition', 11:          return TaskDefinition_v11(self.stream,      extra=self.dpfile)
			case 'taskdefinition', 15:          return TaskDefinition_v15(self.stream,      extra=self.dpfile)
			
			case 'meshmetadata', 1:             return Metadata.MeshMetadata_v1(self.stream)
			case 'texturemetadata', 1:          return Metadata.TextureMetadata_v1(self.stream)
			case 'fileinfometadata', 1:         return Metadata.FileInfoMetadata_v1(self.stream)
			case 'foliagemeshmetadata', 1:      return Metadata.FoliageMeshMetadata_v1(self.stream)
			case 'particlesystemmetadata', 1:   return Metadata.ParticleSystemMetadata_v1(self.stream)
			case 'havokanimationmetadata', 1:   return Metadata.HavokAnimationMetadata_v1(self.stream)
			
			case 'attachmentresources', 3:      return AttachmentResources_v3(self.stream)
			case 'dynamicobjectscript', 3:      return DynamicObjectScript_v3(self.stream)
			case 'characterscript', 3:          return CharacterScript_v3(self.stream)
			case 'scriptinstance', 1:           return ScriptInstance_v1(self.stream)
			case 'waypoint', 1:                 return Waypoint_v1(self.stream)
			case 'spotlight', 20:               return SpotLight_v20(self.stream)
			case 'physicsmaterial', 2:          return PhysicsMaterial_v2(self.stream)
			case 'scriptvariables', 1:          return ScriptVariables_v1(self.stream)
			case 'scriptvariables', 2:          return ScriptVariables_v2(self.stream)
			case 'floatingscript', 2:           return FloatingScript_v2(self.stream)
			case 'keyframe', 1:                 return KeyFrame_v1(self.stream)
			case 'staticobject', 10:            return StaticObject_v10(self.stream)
			case 'sound', 21:                   return Sound_v21(self.stream)
			case 'cellinfo', 1:                 return CellInfo_v1(self.stream)
			case 'character', 13:               return Character_v13(self.stream)
			case 'character', 17:               return Character_v17(self.stream)
			case 'pointlight', 11:              return PointLight_v11(self.stream)
			case 'pointlight', 13:              return PointLight_v13(self.stream)
			case 'battery', 3:                  return Battery_v3(self.stream)
			case 'battery', 4:                  return Battery_v4(self.stream)
			case 'ambientlight', 2:             return AmbientLight_v2(self.stream)
			case 'ammo', 4:                     return Ammo_v4(self.stream)
			case 'ammoitem', 3:                 return AmmoItem_v3(self.stream)
			case 'animationattimehandler', 1:   return AnimationAtTimeHandler_v1(self.stream)
			case 'batteryitem', 3:              return BatteryItem_v3(self.stream)
			case 'birdswarm', 1:                return BirdSwarm_v1(self.stream)
			case 'blocker', 2:                  return Blocker_v2(self.stream)
			case 'camerapath', 2:               return CameraPath_v2(self.stream)
			case 'cameraset', 7:                return CameraSet_v7(self.stream)
			case 'cinematic', 5:                return Cinematic_v5(self.stream)
			case 'cinematicline', 2:            return CinematicLine_v2(self.stream)
			case 'collectible', 2:              return Collectible_v2(self.stream)
			case 'constraintbone', 3:           return ConstraintBone_v3(self.stream)
			case 'dbdecal', 1:                  return DBDecal_v1(self.stream)
			case 'dbparticlesystem', 1:         return DBParticleSystem_v1(self.stream)
			case 'debugentity', 1:              return DebugEntity_v1(self.stream)
			case 'dialogueline', 4:             return DialogueLine_v4(self.stream)
			case 'effect', 3:                   return Effect_v3(self.stream)
			case 'gameeventhandler', 1:         return GameEventHandler_v1(self.stream)
			case 'interiordefinition', 4:       return InteriorDefinition_v4(self.stream)
			case 'lightsource', 10:             return LightSource_v10(self.stream)
			case 'lightsourceitem', 3:          return LightSourceItem_v3(self.stream)
			case 'loadingscreenhint', 1:        return LoadingScreenHint_v1(self.stream)
			case 'matdependentsimsound', 1:     return MatDependentSimSound_v1(self.stream)
			case 'particlekillbox', 2:          return ParticleKillBox_v2(self.stream)
			case 'particlesystem', 3:           return ParticleSystem_v3(self.stream)
			case 'persistentresource', 1:       return PersistentResource_v1(self.stream)
			case 'portal', 2:                   return Portal_v2(self.stream)
			case 'radioshow', 2:                return RadioShow_v2(self.stream)
			case 'reststop', 1:                 return RestStop_v1(self.stream)
			case 'reverbpreset', 1:             return ReverbPreset_v1(self.stream)
			case 'room', 4:                     return Room_v4(self.stream)
			case 'simulatedsound', 5:           return SimulatedSound_v5(self.stream)
			case 'simulatedsoundcontent', 6:    return SimulatedSoundContent_v6(self.stream)
			case 'simulatedsoundcontrol', 3:    return SimulatedSoundControl_v3(self.stream)
			case 'simulatedsoundinstance', 4:   return SimulatedSoundInstance_v4(self.stream)
			case 'skinitem', 1:                 return SkinItem_v1(self.stream)
			case 'soundinstance', 5:            return SoundInstance_v5(self.stream)
			case 'soundpreset', 2:              return SoundPreset_v2(self.stream)
			case 'spawnpoint', 6:               return SpawnPoint_v6(self.stream)
			case 'spawnpointscript', 3:         return SpawnPointScript_v3(self.stream)
			case 'spawnposition', 1:            return SpawnPosition_v1(self.stream)
			case 'springbone', 3:               return SpringBone_v3(self.stream)
			case 'spybird', 2:                  return SpyBird_v2(self.stream)
			case 'thresholdevent', 1:           return ThresholdEvent_v1(self.stream)
			case 'throwable', 6:                return Throwable_v6(self.stream)
			case 'throwableitem', 3:            return ThrowableItem_v3(self.stream)
			case 'tornado', 1:                  return Tornado_v1(self.stream)
			case 'vehicle', 5:                  return Vehicle_v5(self.stream)
			case 'vehiclescript', 3:            return VehicleScript_v3(self.stream)
			case 'vehiclesound', 10:            return VehicleSound_v10(self.stream)
			case 'volume', 1:                   return Volume_v1(self.stream)
			case 'weaponitem', 3:               return WeaponItem_v3(self.stream)
			
		logger.error(f'Unaccounted obrs.object type {objectType} (v{version})')
		return f'unaccounted type {objectType}'
