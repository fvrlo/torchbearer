![Torchbearer Logo, made by me. graphic design is not my passion.](torchbearer/style/tbr.svg)

# Torchbearer

---

Torchbearer is an attempt at a general Northlight Engine data interpreter (and maybe someday writer), built on the backbone of [OpenAWE-Project/OpenAWE](https://github.com/OpenAWE-Project/OpenAWE) and made using some rough Python and Qt.


This goes without saying, but this is Remedy data from Remedy games in Remedy formats.
Copyrighted data belongs to the respective owners.
This is for research and exploration, not copyright infringement or [AI trash](https://www.wheresyoured.at/the-haters-gui/). <Please tinker/use responsibly.> 


## How To Use

In the top directory, run `torchbearer/__init__.py` with Python `>=3.13` and the packages from requirements.txt installed. If you're just using it as a library, you can likely skip PySide6 and QtAwesome.

It should work right out of the gate. If not, it might be a configuration issue in `config.toml` or your instance configs. Or I might have not tested it on other machines.

### Development

uhhhhhhhhhhhhhhhhh this is a mess

This is a very beginner project, so I likely didn't implement something right or code something efficiently, but it "works" so whatever.
A lot is still undocumented, and a lot more error handling needs to be implemented, but that's something that can be added with time.
Expect refactors in the future but commits/pulls will be appreciated.

Versioning follows [Python syntax](https://packaging.python.org/en/latest/specifications/version-specifiers).


### Mulch

This project includes a subproject called Mulch, intended to be a stdlib for some general Python tools.
It might get spun out at some point, but for now this is the only thing I use it for.


### Supported Games

[Northlight](https://www.remedygames.com/northlight) is an in-house game engine for Remedy (developers of Alan Wake, Control, etc.) styled as a "storytelling engine".

I'm going to use TBC often to reference the games, which is just a 3-letter abbreviation.

| Game                           | TBC | Year | RMDP Version                                              | Structure            |
|--------------------------------|-----|------|-----------------------------------------------------------|----------------------|
| Alan Wake                      | AW1 | 2010 | 2                                                         | .bin/.rmdp           |
| Alan Wake's American Nightmare | AWN | 2012 | 7                                                         | .bin/.rmdp/.packmeta |
| Quantum Break                  | QBR | 2016 | 8                                                         | .bin/.rmdp/.packmeta |
| Control                        | CTL | 2019 | 9                                                         | .bin/.rmdp/.packmeta |
| Alan Wake Remastered           | AWR | 2021 | 2 (Torchbearer treats this as a 3 for processing reasons) | .bin/.rmdp           |
| Alan Wake II                   | AW2 | 2023 | N/A                                                       | .rmdtoc/.rmdblob     |
| FBC: Firebreak                 | FBR | 2025 | N/A                                                       | .rmdtoc/.rmdblob     |
| Control Resonant               | CTR | 2026 | ...                                                       | ...                  |


## Resources

Scripts, and projects that were instrumental to development. Lots of code was reworked from OpenAWE, to the point this might as well be a fork of that project if not for the goal/language change.

| Author       | Repository                                                                       | License |
|--------------|----------------------------------------------------------------------------------|---------|
| OpenAWE      | [OpenAWE-Project/OpenAWE](https://github.com/OpenAWE-Project/OpenAWE)            | GPL-3.0 |
| Nostritius   | [Nostritius/AWTools](https://github.com/Nostritius/AWTools)                      | GPL-3.0 |
| GrzybDev     | [GrzybDev/NorthlightTools](https://github.com/GrzybDev/NorthlightTools)          | GPL-3.0 |
| 987123879113 | [rmdtool](https://gist.github.com/987123879113/0d014083a61b0d1ae5894c55cc8634cb) | ...     |


### Other Tools

Here's some other useful tools/projects for anyone interested in Northlight engine stuff.

- [TomEvin/neat](https://github.com/TomEvin/neat) (AKA "The Northlight Tool")
- [louh/control-records](https://github.com/louh/control-records)
- [atrexus/unluau](https://github.com/atrexus/unluau)
- [amrshaheen61/Alan-Wake-2-RMDTOC-Tool](https://github.com/amrshaheen61/Alan-Wake-2-RMDTOC-Tool)
- [profMagija/control-unpack](https://github.com/profMagija/control-unpack)
- [eprilx/NorthlightFontMaker](https://github.com/eprilx/NorthlightFontMaker)
- [riverence/io_scene_binfbx](https://github.com/riverence/io_scene_binfbx)


#

---


Questions that don't fit as a repo issue? Reach out to me (fvrlo) on Twitter or Discord.

![trans rights](https://pride-badges.pony.workers.dev/static/v1?label=trans%20rights&stripeWidth=6&stripeColors=5BCEFA,F5A9B8,FFFFFF,F5A9B8,5BCEFA)
