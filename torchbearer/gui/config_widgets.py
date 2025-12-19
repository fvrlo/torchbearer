from __future__ import annotations

from pathlib import Path

from loguru import logger
from PySide6 import QtCore, QtWidgets, QtGui
from __feature__ import true_property #type: ignore

from mulch import PassingException, qBox, qGrid, qTabs, PathLineEdit, Quick
from torchbearer.northlight_engine.configs import AppConfig, InstanceConfig


class AspectRatioLabel(QtWidgets.QLabel):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._pixmap = self.pixmap
	
	def resizeEvent(self, event):
		self.setPixmap(self._pixmap)
		super().resizeEvent(event)
	
	def setPixmap(self, new_pixmap: QtGui.QPixmap):
		if not new_pixmap:
			return
		self._pixmap = new_pixmap
		self.pixmap = self._pixmap.scaled(self.frameSize, QtCore.Qt.AspectRatioMode.KeepAspectRatio)


# some todos:
# hot reload instances
# add new configurations from GUI
# remove configurations from GUI
# add icons from GUI
# custom icon library for games/instances


def reloadCSS(path: Path, force: bool = False):
	stylesheet = path.read_text()
	instance = QtWidgets.QApplication.instance()
	if instance is not None:
		if force or (len(stylesheet) != 0 and instance.styleSheet != stylesheet):
			len_old = str(instance.styleSheet).count('\n')
			len_new = stylesheet.count('\n')
			instance.styleSheet = stylesheet
			diff = len_new - len_old
			logger.opt(colors=True).info(f'Stylesheet reloaded. [{f"<r>-{abs(diff)}</r>" if diff < 0 else f"<g>+{diff}</g>"}]')


class ConfigWindow(QtWidgets.QDialog):
	cfg: AppConfig
	listo: QtWidgets.QListWidget
	
	field_cach: PathLineEdit
	field_expo: PathLineEdit
	field_conf: PathLineEdit
	
	field_name: QtWidgets.QLineEdit
	field_vrsn: QtWidgets.QLineEdit
	field_path: PathLineEdit
	field_icon: AspectRatioLabel
	
	cfgChanged = QtCore.Signal()
	
	def __init__(self, cfg: AppConfig):
		self.cfg = cfg
		super().__init__(sizeGripEnabled=False)
		self.windowTitle = f"Preferences"
		
		self.field_cach = PathLineEdit(self.cfg.cach, select=True, empty=True)
		self.field_expo = PathLineEdit(self.cfg.expo, select=True, empty=True)
		self.field_conf = PathLineEdit(self.cfg.conf, select=True)

		reloadCSS((Path.cwd() / 'style.qss'), True)

		self.listo = QtWidgets.QListWidget()
		self.listo.selectionMode = QtWidgets.QListWidget.SelectionMode.SingleSelection
		self.field_name = QtWidgets.QLineEdit('')
		self.field_vrsn = QtWidgets.QLineEdit('')
		self.field_path = PathLineEdit(Path(), select=True)
		self.field_icon = AspectRatioLabel()
		self.populateInstances()
		
		self.setLayout(
			qGrid(margins=6).add(
				qTabs(
					self,
					Global=qBox(
						Quick.groupbox('Directories', qGrid().gen('Cache', self.field_cach, 'Exports', self.field_expo, 'Configs', self.field_conf, r=3, c=2)),
						Quick.groupbox('Style', qBox(Quick.pushbutton("Reload CSS", lambda: reloadCSS(Path.cwd() / 'style.qss'), fixedWidth=80), d='v')),
						d='v', margins=3
					).addStr(),
					Instances=qBox(
						self.listo,
						qBox(
							qGrid(cs=[1, 5], rs=[1, 1, 1, 1, -1])
							 .add('Name', 0, 0).add(self.field_name, 0, 1)
							 .add('Version', 1, 0).add(self.field_vrsn, 1, 1)
							 .add('Path', 2, 0).add(self.field_path, 2, 1)
							 .add('Icon', 3, 0).add(self.field_icon, 3, 1, align=QtCore.Qt.AlignmentFlag.AlignCenter)
							 .add(QtWidgets.QWidget(), 4, 0, rs=-1, cs=-1)
							 , d='v'
						).addStr(), stretch=[1, 4]
					)
				), r=0, c=0, rs=1, cs=2
			).add(Quick.pushbutton("OK", self.accept, default=True, fixedWidth=80), r=1, c=1)
		)
		self.resize(500, 400)

		self.listo.itemSelectionChanged.connect(self.update_txts)

		self.field_cach.pathChanged.connect(self.updateApp)
		self.field_expo.pathChanged.connect(self.updateApp)
		self.field_conf.pathChanged.connect(self.updateApp)
		self.field_path.pathChanged.connect(self.updateInstance)
		self.field_name.editingFinished.connect(self.updateInstance)
		self.field_vrsn.editingFinished.connect(self.updateInstance)
	
		# self.dirwatch = QtCore.QFileSystemWatcher(self)
		# self.dirwatch.addPath(str(self.cfg.conf))
		# self.dirwatch.directoryChanged.connect(self.cfg.load_instances)
	
	@QtCore.Slot()
	def updateApp(self):
		self.cfg.cach = self.field_cach.path
		self.cfg.expo = self.field_expo.path
		self.cfg.conf = self.field_conf.path
		
	@QtCore.Slot()
	def updateInstance(self):
		instance = self.instance()
		instance.name = self.field_name.text
		instance.version = self.field_vrsn.text
		instance.path = self.field_path.path
		self.cfgChanged.emit()
	
	@QtCore.Slot()
	def populateInstances(self):
		self.listo.clear()
		self.listo.addItems([instance.key.lower() for instance in self.cfg.instances.values()])
	
	@QtCore.Slot()
	def update_txts(self):
		instance = self.instance()
		self.field_name.text = instance.name
		self.field_vrsn.text = instance.version
		self.field_path.path = instance.path
		icopath = Path(f"./torchbearer/style/{instance.key.lower()}.svg").resolve()
		if icopath.is_file():
			self.field_icon.pixmap = QtGui.QPixmap(str(icopath))
		else:
			self.field_icon.pixmap = QtGui.QPixmap()
	
	def regen_configs(self):
		dir_steam = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Steam /steamapps/common directory", options=QtWidgets.QFileDialog.Option.ShowDirsOnly)
		dir_epic = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Epic Games library directory", options=QtWidgets.QFileDialog.Option.ShowDirsOnly)
		self.cfg.regen_configs(dir_steam, dir_epic)
		
	def dicto(self) -> dict[str, QtWidgets.QListWidgetItem]:
		return {z.text(): z for z in [self.listo.item(x) for x in range(self.listo.count)]}
	
	def instance(self) -> InstanceConfig | None:
		selected = self.listo.selectedItems()
		if len(selected) != 1:
			logger.error(len(selected))
			raise PassingException('selection', 'pass')
		else:
			return self.cfg.instances[selected[0].text()]

	