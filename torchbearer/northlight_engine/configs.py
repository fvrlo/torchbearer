from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from mulch.toml import ConfigTOML, field

if TYPE_CHECKING:
	from torchbearer.northlight_engine.northlight import Northlight


__all__ = [
	"AppConfig",
	"InstanceConfig"
]


class AppConfig(ConfigTOML):
	cach: Path  = field(Path, to_str=lambda x: f"\"{str(x.absolute()).replace('\\', '/')}\"")
	conf: Path  = field(Path, to_str=lambda x: f"\"{str(x.absolute()).replace('\\', '/')}\"")
	expo: Path  = field(Path, to_str=lambda x: f"\"{str(x.absolute()).replace('\\', '/')}\"")
	
	instances: dict[str, InstanceConfig]
	
	def __init__(self):
		self.instances = dict()
		cfgpath = Path.cwd() / 'config.toml'
		if not cfgpath.is_file():
			ConfigTOML.writetoml(cfgpath, cach="./cache", conf="./config", expo="./export")
		super().__init__(cfgpath)
		for k in self.conf.glob('*.toml'):
			InstanceConfig(self, k)
	
	def load_instances(self):
		self.instances = dict()
		for k in self.conf.glob('*.toml'):
			InstanceConfig(self, k)
	
	def new_instance_config(self, *, key: str, name: str, folder: str, dir_s: Path, dir_e: Path, version: str = 'latest'):
		if (self.conf / f"{key.lower()}.toml").is_file():
			raise FileExistsError
		theoretical_s = dir_s / folder
		theoretical_e = dir_e / folder
		if theoretical_s.is_dir():
			path = theoretical_s
		elif theoretical_e.is_dir():
			path = theoretical_e
		else:
			return
		InstanceConfig.new(self, key=key, name=name, version=version, path=path)
	
	def regen_configs(self, dir_steam: str, dir_epic: str):
		if dir_steam == '' or dir_epic == '':
			return
		
		dir_s = Path(dir_steam).resolve()
		dir_e = Path(dir_epic).resolve()
		for file in self.conf.iterdir():
			if file.is_file() and file.suffix == '.toml':
				file.unlink()
		self.instances = dict()
		self.new_instance_config(key="AW1", name="Alan Wake", folder="Alan Wake", dir_s=dir_s, dir_e=dir_e)
		self.new_instance_config(key="AWN", name="Alan Wake's American Nightmare", folder="alan wakes american nightmare", dir_s=dir_s, dir_e=dir_e)
		self.new_instance_config(key="CTL", name="Control", folder="Control", dir_s=dir_s, dir_e=dir_e)
		self.new_instance_config(key="FBR", name="FBC: Firebreak", folder="FBCFirebreak", dir_s=dir_s, dir_e=dir_e)
		self.new_instance_config(key="QBR", name="Quantum Break", folder="QuantumBreak", dir_s=dir_s, dir_e=dir_e)
		self.new_instance_config(key="AWR", name="Alan Wake Remastered", folder="AlanWakeRemastered", dir_s=dir_s, dir_e=dir_e)
		self.new_instance_config(key="AW2", name="Alan Wake II", folder="AlanWake2", dir_s=dir_s, dir_e=dir_e)


class InstanceConfig(ConfigTOML):
	path:       Path    = field(Path, to_str=lambda x: f"\"{str(x.absolute()).replace('\\', '/')}\"")
	name:       str     = field()
	key:        str     = field()
	version:    str     = field()
	
	app: AppConfig
	admindict: dict[Path, Northlight.Admin]
	
	@classmethod
	def new(cls, app: AppConfig, *, key: str, name: str, version: str, path: Path):
		return InstanceConfig(app, InstanceConfig.writetoml(app.conf / f"{key.lower()}.toml", key=key, name=name, version=version, path=path))
	
	def __init__(self, app: AppConfig, tomlpath: Path):
		super().__init__(tomlpath)
		self.app = app
		self.admindict = dict()
		self.app.instances[tomlpath.stem] = self

	@cached_property
	def files(self) -> list[Path]:
		return [z for z in self.path.rglob("**/*.*") if z.is_file()]
	
	@cached_property
	def dir_size(self) -> int:
		return sum([x.stat().st_size for x in self.files])
	
	@property
	def keys(self):
		return [zz for zz in [z for z in self.files if z.suffix[1:] in ['rmdp', 'rmdtoc']] if zz.stat().st_size != 0]
	
	def __len__(self):
		return self.dir_size
