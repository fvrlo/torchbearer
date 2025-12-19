# Northlight and Remedy

---

- Articles
	- [Northlight](https://www.remedygames.com/article/about-game-engines)
	- [AW2 and Northlight](https://www.remedygames.com/article/how-northlight-makes-alan-wake-2-shine)
- Repos
	- [Animation Compression Library](https://github.com/Remedy-Entertainment/acl)
- [Universal Scene Descriptor](https://en.wikipedia.org/wiki/Universal_Scene_Description)
	- [Northlight and USD](https://www.remedygames.com/article/developing-northlight-openusd-content-workflows)
    - Repos
      - [USDBook](https://remedy-entertainment.github.io/USDBook/)
      - [USD](https://github.com/Remedy-Entertainment/USD)
      - [usdFBX](https://github.com/Remedy-Entertainment/usdFBX)
      - [USDBook](https://github.com/Remedy-Entertainment/USDBook)
- Licensed Tech
  - Bink Video (RAD Game Tools Inc. (lka. Epic Games Tools))
  - Umbra (umbra3d.com)
  - Wwse (Audiokinetic Inc.)
  - Coerent Labs User Interface Technology (Coherent Labs)
  - mopheme (NaturalMotion)
  - Auodesk Gameware Navigation software (Autodesk Inc.)
  - FaeFX (OC3 Entertainment Inc.)
  - FMD EX Sound System (Firelight Technologies)


# Extension Parsing

---

| Real Format | Description                                                            |
|-------------|------------------------------------------------------------------------|
| wem         | Wwise Encoded Media (Audio)                                            |
| ttf         | font (TrueType Font)                                                   |
| otf         | font (OpenType Font)                                                   |
| binfnt      | font (Binned, can be extracted)                                        |
| bnk         | Bink video file, signature: "KB2"                                      |
| tex         | image, signature: "DDS"                                                |
| xml         | XML, readable as raw text.                                             |
| txt         | TXT, readable as raw text.                                             |
| json        | JSON, readable as raw text.                                            |
| ui          | Renamed .bin files, packaged HTML, CSS, and JS from Coherence GameFace |


| Extension      | Count  |
|----------------|--------|
| aaa            | 6965   |
| aap            | 1      |
| animset        | 1427   |
| asset          | 21     |
| atm            | 57     |
| audioenv       | 1      |
| bin            | 50802  |
| binanim        | 62     |
| binanimclip    | 21073  |
| binanimgraph   | 807    |
| binanimmixer   | 131    |
| binapx         | 347    |
| binblendspace  | 4      |
| binbt          | 463    |
| bincloth       | 10     |
| binclothprof   | 8      |
| bineqs         | 368    |
| binfbx         | 28807  |
| binfnt         | 141    |
| binfol         | 131    |
| binfsm         | 5      |
| bingrs         | 4      |
| binhkt         | 275    |
| binhkx         | 4260   |
| binhvk         | 12304  |
| binlua         | 1986   |
| binmotiondb    | 1397   |
| binmsh         | 9318   |
| binnav         | 40     |
| binpx          | 17688  |
| binragdollprof | 36     |
| binrfx         | 148    |
| binshader      | 59     |
| binskeleton    | 1209   |
| bintimeline    | 4148   |
| binwps         | 3377   |
| bnk            | 10558  |
| chroma         | 156    |
| chunk          | 4982   |
| collisions     | 11355  |
| css            | 30     |
| dat            | 846    |
| dds            | 2      |
| dll            | 30     |
| facefx         | 29     |
| flare          | 109    |
| fsb            | 45392  |
| fxa            | 36     |
| fxe            | 2056   |
| gfxgraph       | 97     |
| heightfield    | 122    |
| info           | 76     |
| ivgidata       | 3111   |
| ivtree         | 3111   |
| json           | 372    |
| lua            | 11     |
| matdef         | 16     |
| material       | 20569  |
| meta           | 132386 |
| nmb            | 4055   |
| otf            | 24     |
| packmeta       | 20     |
| particle       | 2107   |
| pdb            | 30     |
| plugin         | 5      |
| prof           | 15     |
| raw            | 728    |
| rawbin         | 303    |
| rbf            | 523    |
| resources      | 36634  |
| sdf            | 1669   |
| skel           | 129    |
| srt            | 66     |
| tex            | 115481 |
| tex_lo         | 10626  |
| ttf            | 32     |
| txt            | 5128   |
| ui             | 41     |
| vmap           | 1      |
| wav            | 51     |
| wedmsh         | 8678   |
| wem            | 201525 |
| xml            | 1118   |
| xsl            | 5      |

# Structure Investigating

---

```
Bin handler:
	archetype.bin:  "cid_entity_archetype.bin, dp_archetype.bin" (363 occurences)

	def ep:
		episode.bin         "cid_streaming_state.bin, cid_streaming_state_node.bin, cid_taskdefinition.bin, cid_persistentepisodeblock.bin, dp_episode.bin"
		tasks.bin           "cid_genericcomponent.bin, cid_genericentity.bin, cid_entitybatch.bin, cid_archetype_reference.bin, cid_taskcontent.bin, dp_task.bin"
		GIDRegistry.txt
		JumpPoints.json
		JumpPoints.txt
	
	def layer:
		entities.bin        "cid_genericcomponent.bin, cid_genericentity.bin, cid_entitybatch.bin, cid_archetype_reference.bin, dp_episode.bin"
		quest.bin           "cid_streaming_state_node.bin, cid_quest.bin, dp_episode.bin"
		GIDRegistry.txt
		JumpPoints.json
	
	def world:
		cid_worldversion.bin
		episodes/
			$(location)/
				ep()
		layers/
			$(layer)/
				layer()
	
	def world_no_version:
		episodes/
			$(location)/
				ep()
		layers/
			$(layer)/
				layer()
	
	
	
	base-generic.rmdtoc/
		data/
			worlds/
				runtimedata.bin
				gameworld/
					world()
				global/
					layers/
						global/
							layer()
	
	stream0-generic.rmdtoc/
		data/
			worlds/
				gameworld/
					world_no_version()
				gameworld_lakehouse/
					world()
				gameworld_nightsprings/
					world()

	/data/dialouge/:
		One folder is cid_dialogue_string (usually in the language rmdtoc), the other is the same name (minus strings at end of name) in other toc. seperated for easy translation?
		
		type/line folder:       base-generic.rmdtoc/data/dialouge/lines/$(name).bin         (cid_dialogue_type.bin, cid_dialogue_line.bin: 588)
		cid_dialogue_string:    base-en.rmdtoc/data/dialouge/locale/en/$(name)strings.bin   (cid_dialogue_string.bin: 588)
		
		
		
	base-generic.rmdtoc/data/dialogue/lines/dialoguetypes.bin:
		cid_dialogue_type.bin, cid_dialogue_line.bin: 1
	
	base-generic.rmdtoc/data/dialogue/systemic/systemicdialogue.bin:
		cid_dialogue_voice_profile.bin, cid_dialogue_set_definition.bin, cid_dialogue_set_playlist_item.bin, cid_dialogue_set.bin, cid_dialogue_condition.bin, cid_dialogue_variable.bin, cid_dialogue_action.bin, cid_dialogue_event_handler.bin, cid_dialogue_event.bin, cid_dialogue_event_system.bin: 1
```