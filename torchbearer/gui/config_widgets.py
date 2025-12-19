from __future__ import annotations

from pathlib import Path

from loguru import logger
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import QObject
from __feature__ import true_property #type: ignore

from torchbearer.mulch import PassingException
from torchbearer.mulch_qt import qBox, qGrid, Quick, qTabs
from torchbearer.mulch_qt.paths import PathLineEdit
from torchbearer.northlight_engine.configs import AppConfig, InstanceConfig


class WatcherCSS(QtCore.QFileSystemWatcher):
	def __init__(self, *paths: Path):
		super().__init__()
		for path in paths:
			self.addPath(str(path.resolve()))
		self.fileChanged.connect(self.load_css)
		
	def toggle_auto_reload_css(self, boolean: bool, /):
		if boolean:
			self.fileChanged.connect(self.load_css)
		else:
			self.fileChanged.disconnect(self.load_css)

	@QtCore.Slot()
	def load_css(self):
		for path in self.files():
			if '.qss' in path:
				stylesheet = Path(path).read_text()
				instance = QtWidgets.QApplication.instance()
				if instance is not None:
					if len(stylesheet) != 0 and instance.styleSheet != stylesheet:
						len_old = str(instance.styleSheet).count('\n')
						len_new = stylesheet.count('\n')
						instance.styleSheet = stylesheet
						diff = len_new-len_old
						logger.opt(colors=True).info(f'Stylesheet reloaded. [{f"<r>-{abs(diff)}</r>" if diff < 0 else f"<g>+{diff}</g>"}]')


class SquareHandler(QtCore.QObject):
	"""this is kinda busted"""
	
	scaleFactor: int | float
	
	def __init__(self, parent: QtCore.QObject, scaleFactor: int | float = 1):
		super().__init__(parent)
		self.scaleFactor = scaleFactor
	
	def eventFilter(self, watched, event, /):
		if isinstance(watched, QtWidgets.QWidget):
			if isinstance(event, QtGui.QResizeEvent):
				minsize = int(min(watched.width, watched.height) * self.scaleFactor)
				watched.geometry = QtCore.QRect(watched.pos.x(), watched.pos.y(), minsize, minsize)  # noqa
		return super().eventFilter(watched, event)
	
	@classmethod
	def install[T: QObject](cls, target: T, scaleFactor: int | float = 1) -> T:
		target.installEventFilter(cls(target, scaleFactor))
		return target


class ScaledLabel(QtWidgets.QLabel):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._pixmap = self.pixmap
	
	def resizeEvent(self, event):
		self.setPixmap(self._pixmap)
		super().resizeEvent(event)
	
	def setPixmap(self, pixmap):
		if not pixmap:
			return
		self._pixmap = pixmap
		self.pixmap = self._pixmap.scaled(self.frameSize, QtCore.Qt.AspectRatioMode.KeepAspectRatio)


class InstanceManager(QtWidgets.QWidget):
	cfg_window: ConfigWindow
	cfg: AppConfig
	listo: QtWidgets.QListWidget
	
	cfgChanged = QtCore.Signal()
	
	def __init__(self, cfg_window: ConfigWindow):
		super().__init__()
		
		self.cfg_window = cfg_window
		self.cfg = cfg_window.cfg
		self.listo = QtWidgets.QListWidget()
		self.listo.selectionMode = QtWidgets.QListWidget.SelectionMode.SingleSelection
		self.field_name = QtWidgets.QLineEdit('')
		self.field_vrsn = QtWidgets.QLineEdit('')
		self.field_path = PathLineEdit(Path(), select=True)
		self.populate()
		self.listo.itemSelectionChanged.connect(self.update_txts)

		self.hasIcon = ScaledLabel()
		
		self.setLayout(
			qBox(
				self.listo,
				qBox(
					qGrid(cs=[1, 5], rs=[1, 1, 1, 1, -1])
					 .add('Name', 0, 0).add(self.field_name, 0, 1)
					 .add('Version', 1, 0).add(self.field_vrsn, 1, 1)
					 .add('Path', 2, 0).add(self.field_path, 2, 1)
					 .add('Icon', 3, 0).add(self.hasIcon, 3, 1, align=QtCore.Qt.AlignmentFlag.AlignCenter)
					 .add(QtWidgets.QWidget(), 4, 0, rs=-1, cs=-1)
					 , d='v'
				).addStr(), stretch=[1, 4]
			)
		)
		
		self.field_name.editingFinished.connect(self.setValue_name)
		self.field_vrsn.editingFinished.connect(self.setValue_vrsn)
		self.field_path.pathChanged.connect(self.setValue_path)
		
		#self.cfg_window.dirwatch.directoryChanged.connect(self.populate)
	
	def dicto(self):
		return {z.text(): z for z in [self.listo.item(x) for x in range(self.listo.count)]}
	
	def selection(self) -> InstanceConfig | None:
		selected = self.listo.selectedItems()
		if len(selected) != 1:
			logger.error(len(selected))
			raise PassingException('selection', 'pass')
		else:
			return self.cfg.instances[selected[0].text()]
	
	@QtCore.Slot()
	def populate(self):
		self.listo.clear()
		self.listo.addItems([instance.key.lower() for instance in self.cfg.instances.values()])
	
	@QtCore.Slot()
	def update_txts(self):
		instance = self.selection()
		self.field_name.text = instance.name
		self.field_vrsn.text = instance.version
		self.field_path.text = str(instance.path)
		icopath = Path(f"./torchbearer/style/{instance.tomlpath.stem}.svg").resolve()
		if icopath.is_file():
			self.hasIcon.pixmap = QtGui.QPixmap(str(icopath))
		else:
			self.hasIcon.pixmap = QtGui.QPixmap()
		
	@QtCore.Slot()
	def setValue_name(self):
		self.selection().name = self.field_name.text
		self.cfgChanged.emit()
		
	@QtCore.Slot()
	def setValue_vrsn(self):
		self.selection().version = self.field_vrsn.text
		self.cfgChanged.emit()
	
	@QtCore.Slot()
	def setValue_path(self):
		self.selection().path = self.field_path.path
		self.cfgChanged.emit()


# TODO: hot reload instances
# TODO: add new configurations from GUI
# TODO: remove configurations from GUI
# TODO: add icons from GUI
# TODO: custom icon library for games/instances






class ConfigWindow(QtWidgets.QDialog):
	cfg: AppConfig
	watcher: WatcherCSS
	
	def __init__(self, cfg: AppConfig):
		self.cfg = cfg
		super().__init__(sizeGripEnabled=False)
		self.windowTitle = f"Preferences"
		self.watcher = WatcherCSS((Path.cwd() / 'style.qss'))
		
		self.field_cach = PathLineEdit(self.cfg.cach, select=True, empty=True)
		self.field_expo = PathLineEdit(self.cfg.expo, select=True, empty=True)
		self.field_conf = PathLineEdit(self.cfg.conf, select=True)
		
		toggle_button = Quick.checkbox('Auto Reload CSS', lambda: self.watcher.toggle_auto_reload_css(toggle_button.checked), True)

		self.field_cach.textChanged.connect(self.updateCach)
		self.field_expo.textChanged.connect(self.updateExpo)
		self.field_conf.textChanged.connect(self.updateConf)

		self.dirwatch = QtCore.QFileSystemWatcher(self)
		self.dirwatch.addPath(str(self.cfg.conf))
		self.dirwatch.directoryChanged.connect(self.cfg.load_instances)
		
		self.instance_manager = InstanceManager(self)
		
		self.setLayout(
			qGrid(margins=6).add(
				qTabs(
					self,
					Global=qBox(
						Quick.groupbox('Directories', qGrid().gen('Cache', self.field_cach, 'Exports', self.field_expo, 'Configs', self.field_conf, r=3, c=2)),
						Quick.groupbox('Style', qBox(Quick.pushbutton("Reload CSS", self.watcher.load_css, fixedWidth=80), toggle_button, d='v')),
						d='v', margins=3).addStr(),
					Instances=self.instance_manager
				), 0, 0, 1, 2
			).add(Quick.pushbutton("OK", lambda: self.accept(), default=True, fixedWidth=80), 1, 1)
		)
		self.resize(500, 400)
		
	@QtCore.Slot()
	def updateCach(self):
		self.cfg.cach = self.field_cach.path
	
	@QtCore.Slot()
	def updateExpo(self):
		self.cfg.expo = self.field_expo.path
	
	@QtCore.Slot()
	def updateConf(self):
		self.cfg.conf = self.field_conf.path
	
	def regen_configs(self):
		dir_steam = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Steam /steamapps/common directory", options=QtWidgets.QFileDialog.Option.ShowDirsOnly)
		dir_epic = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Epic Games library directory", options=QtWidgets.QFileDialog.Option.ShowDirsOnly)
		self.cfg.regen_configs(dir_steam, dir_epic)