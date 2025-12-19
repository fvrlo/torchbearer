from __future__ import annotations

import sys
from pathlib import Path

import qtawesome as qta

from PySide6 import QtGui, QtWidgets, QtCore
from __feature__ import true_property #type: ignore

from loguru import logger

from torchbearer.gui.config_widgets import ConfigWindow
from torchbearer.mulch import PathPlus, byter, PassingException, yamldump, TimerLog, Dictable
from torchbearer.mulch_qt import TexViewerWidget, UserRoles, HexViewer, HexTableView, TexViewer, qGrid, qBox, Quick

from torchbearer.northlight_engine.northlight import Northlight, Reader, ReaderNLEv10
from torchbearer.northlight_engine.configs import AppConfig, InstanceConfig
from torchbearer.northlight_internal.textures.decider_tex import tex_handler
from torchbearer.northlight_internal.packmeta import PackMeta
from torchbearer.northlight_internal.binfile import bin_explorer

from torchbearer.northlight_internal.textures.nletex_pil import register
register()


# TODO: document everything (it's a mess)


extension_icons = {
	'bin'           : 'fa6s.file-zipper',
	'binfnt'        : 'fa6s.font',
	'ttf'           : 'fa6s.font',
	'otf'           : 'fa6s.font',
	'wem'           : 'fa6s.file-audio',
	'bnk'           : 'fa6s.file-video',
	'tex'           : 'fa6s.file-image',
	'flare'         : 'fa6s.fire',
	'bintimeline'   : 'fa6s.file-invoice',
	'binanimclip'   : 'fa6s.file-invoice',
	'binanimgraph'  : 'fa6s.file-invoice',
	'binclothprof'  : 'fa6s.file-invoice',
	'bineqs'        : 'fa6s.file-invoice',
	'binfbx'        : 'fa6s.file-invoice',
	'binlua'        : 'fa6s.file-invoice',
	'binmotiondb'   : 'fa6s.file-invoice',
	'binnav'        : 'fa6s.file-invoice',
	'binragdollprof': 'fa6s.file-invoice',
	'binshader'     : 'fa6s.file-invoice',
	'binskeleton'   : 'fa6s.file-invoice',
	'xml'           : 'fa6s.file-lines',
	'json'          : 'fa6s.file-lines',
	'md'            : 'fa6s.file-lines',
	'xsl'           : 'fa6s.file-lines',
	'yaml'          : 'fa6s.file-lines',
	'asset'         : 'fa6s.file-lines',
	'txt'           : 'fa6s.file-pen',
	'ui'            : 'fa6s.file-code',
	'raw'           : 'fa6s.file-circle-xmark',
	'info'          : 'fa6s.file-contract',
	'chroma'        : 'fa6s.file-circle-question',
	'chunk'         : 'fa6s.file-circle-question',
	'gfxgraph'      : 'fa6s.file-circle-question',
	'heightfield'   : 'fa6s.file-circle-question',
	'ivtree'        : 'fa6s.file-circle-question',
	'material'      : 'fa6s.file-circle-question',
	'particle'      : 'fa6s.file-circle-question',
}

class TreePTI(QtWidgets.QTreeWidget):
	menu_ctx: QtWidgets.QMenu
	
	action_exportf: QtGui.QAction
	action_showexp: QtGui.QAction
	action_preview: QtGui.QAction
	action_clrtree: QtGui.QAction
	action_cllapse: QtGui.QAction
	
	def __init__(self, headers: list[str], /, *, parent: QtWidgets.QWidget | None = None,):
		super().__init__(parent, columnCount=len(headers))
		self.indentation = 10
		self.uniformRowHeights = True
		self.selectionMode = QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
		self.sizeAdjustPolicy = QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
		for i, x in enumerate(headers):
			self.model().setHeaderData(i, QtCore.Qt.Orientation.Horizontal, x)
			self.header().setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
		self.model().headerDataChanged.emit(QtCore.Qt.Orientation.Horizontal, 0, len(headers) - 1)
		self.menu_ctx = QtWidgets.QMenu(self)
		self.contextMenuPolicy = QtCore.Qt.ContextMenuPolicy.DefaultContextMenu
		
		self.action_exportf = Quick.action(self, self.menu_ctx, 'Export', self.export_file, icon=qta.icon('fa6s.download'))
		self.action_showexp = Quick.action(self, self.menu_ctx, 'Show in Explorer', self.open_folder)
		self.action_preview = Quick.action(self, self.menu_ctx, 'Preview', self.load_image_preview)
		self.menu_ctx.addSeparator()
		self.action_clrtree = Quick.action(self, self.menu_ctx, 'Clear Tree', self.tree_clear, icon=qta.icon('fa6s.eraser'))
		self.action_cllapse = Quick.action(self, self.menu_ctx, 'Collapse', lambda: self.selection().setExpanded(False))
		
	def contextMenuEvent(self, event: QtGui.QContextMenuEvent):
		subitem = self.ptisel()
		if isinstance(subitem, Northlight.File):
			self.action_exportf.enabled = True
			self.action_showexp.enabled = True
			self.action_preview.enabled = subitem.extension in ['dds', 'tex']
			self.action_clrtree.enabled = False
			self.action_cllapse.enabled = True
			self.menu_ctx.popup(QtGui.QCursor.pos())
			event.accept()
			return True
		elif isinstance(subitem, Northlight.Admin):
			self.action_exportf.enabled = False
			self.action_showexp.enabled = False
			self.action_preview.enabled = False
			self.action_clrtree.enabled = True
			self.action_cllapse.enabled = True
			self.menu_ctx.popup(QtGui.QCursor.pos())
			event.accept()
			return True

		event.ignore()
		return False
	
	def selection(self) -> QtWidgets.QTreeWidgetItem:
		selected = self.selectedItems()
		if not len(selected) == 1:
			raise PassingException("contextMenuEvent", f"A single item is not selected (selections: {len(selected)}).")
		return selected[0]
	
	def ptisel(self):
		return self.selection().data(0, UserRoles.PTI)
	
	def nested_children(self, item: QtWidgets.QTreeWidgetItem):
		for ci in range(item.childCount()):
			child = item.child(ci)
			yield from self.nested_children(child)
			yield child
	
	@QtCore.Slot()
	def tree_clear(self) -> None:
		item = self.selection()
		for x in list(self.nested_children(item)):
			x.parent().removeChild(x)
		subitem = item.data(0, UserRoles.PTI)
		if isinstance(subitem, Northlight.Admin):
			subitem.clear()
	
	@QtCore.Slot()
	def load_image_preview(self):
		subitem = self.ptisel()
		if isinstance(subitem, Northlight.File):
			if not subitem.is_exported:
				subitem.export()
			popup = TexViewer()
			popup.updateImage(subitem.export_path)
			popup.show()
	
	@QtCore.Slot()
	def export_file(self) -> None:
		subitem = self.ptisel()
		if isinstance(subitem, Northlight.File):
			subitem.export_path.write_bytes(subitem.data)
			logger.info(f"File {subitem.name} exported to {subitem.export_path}")
	
	@QtCore.Slot()
	def open_folder(self) -> None:
		subitem = self.ptisel()
		if isinstance(subitem, Northlight.File):
			if subitem.is_exported:
				PathPlus.open_in_explorer(subitem.export_path.parent)




class MainTree(QtWidgets.QWidget):
	appcfg: AppConfig
	headers: list[str]
	splitter: QtWidgets.QSplitter
	desc_txt: QtWidgets.QTextEdit
	desc_oth: QtWidgets.QTextEdit
	desc_hex: HexViewer
	desc_img: TexViewerWidget
	tree_pti: TreePTI
	fltr_txt: QtWidgets.QLineEdit
	fltr_col: QtWidgets.QComboBox
	fltr_eql: QtWidgets.QToolButton
	
	l_body: qBox
	r_body: qGrid
	
	_ru_widget: QtWidgets.QWidget
	
	
	def __init__(self, appcfg: AppConfig):
		super().__init__()
		self.appcfg = appcfg
		self.headers = ["Name", "Extension", "File Size", "Type"]

		with TimerLog("MapTree - tree init"):
			self.tree_pti = TreePTI(self.headers)
			self.load_instances()
			self.tree_pti.itemSelectionChanged.connect(self.updateDesc)

		with TimerLog("MapTree - widget init"):
			self.desc_txt = Quick.txtview()
			self.desc_oth = Quick.txtview()
			self.desc_hex = HexViewer()
			self.desc_img = TexViewerWidget()
			self.fltr_txt = QtWidgets.QLineEdit(clearButtonEnabled=True, placeholderText='Search...')
			self.fltr_txt.editingFinished.connect(self.filter_items)
			self.fltr_txt.setContentsMargins(0, 0, 0, 0)
			self.fltr_col = Quick.combobox(*self.headers, indexChanged=self.filter_items)
			self.fltr_eql = Quick.toolbutton_check(self.filter_items, toolTip='Enable Strict Filtering', icon=qta.icon('fa6s.underline'))
		
		with TimerLog("MapTree - layout init"):
			self._ru_widget = self.desc_txt
			self.l_body = qBox(qBox((self.fltr_txt, 1), self.fltr_col, self.fltr_eql, spacing=0), self.tree_pti, d=qBox.TTB, spacing=4).setMargins(9, 9, 3, 9)
			self.r_body = qGrid(rs=[4, 1], cs=[1, 1], spacing=6, margins=(3, 9, 9, 9)).add(self.desc_txt, 0, 0, 1, 2).add(self.desc_oth, 1, 0).add(HexTableView(self.desc_hex), 1, 1)
			self.splitter = Quick.split(Quick.nest(self.l_body), Quick.nest(self.r_body), orientation=QtCore.Qt.Orientation.Horizontal, childrenCollapsible=False, opaqueResize=False)
			self.setLayout(qGrid(spacing=0).setMargins().add(self.splitter))
	
	@property
	def ru_widget(self):
		return self._ru_widget
	
	@ru_widget.setter
	def ru_widget(self, widget: QtWidgets.QWidget):
		self.r_body.replaceWidget(self._ru_widget, widget)
		self._ru_widget = widget
	
	def pti_factory(self, item, parent: QtWidgets.QTreeWidgetItem | None = None) -> QtWidgets.QTreeWidgetItem:
		qtwi = QtWidgets.QTreeWidgetItem(parent)
		qtwi.setData(0, UserRoles.PTI, item)

		if isinstance(item, InstanceConfig):
			qtwi.setIcon(0, QtGui.QIcon(f"./torchbearer/style/{item.tomlpath.stem}.svg"))
		elif isinstance(item, Reader):
			qtwi.setIcon(0, qta.icon('fa6s.barcode'))
		elif isinstance(item, Northlight.Admin):
			qtwi.setIcon(0, qta.icon('fa6s.box-archive'))
		elif isinstance(item, Northlight.TreeAdmin):
			qtwi.setIcon(0, qta.icon('fa6s.folder-tree'))
		elif isinstance(item, Northlight.DataAdmin):
			qtwi.setIcon(0, qta.icon('fa6s.sitemap'))
		elif isinstance(item, Northlight.MetaAdmin):
			qtwi.setIcon(0, qta.icon('fa6s.square-binary'))
		elif isinstance(item, Northlight.File):
			qtwi.setIcon(0, qta.icon(extension_icons.get(item.extension, 'fa6.file')))
		elif isinstance(item, Northlight.Folder):
			qtwi.setIcon(0, qta.icon('fa6s.folder', color=QtGui.QColor(0xFF, 0xD9, 0x60)))

		for i, key in enumerate(self.headers):
			val = None
			match key:
				case 'Name':
					if isinstance(item, (InstanceConfig, Northlight.Folder, Northlight.File, Northlight.Admin, Path)):
						val = item.name if item.name != '' else '<EmptyName>'
					elif isinstance(item, Northlight.TreeAdmin):
						val = "Filesystem"
					elif isinstance(item, Northlight.DataAdmin):
						val = "Archives"
					elif isinstance(item, Northlight.MetaAdmin):
						val = "Metadata"
					elif isinstance(item, Reader):
						val = "Reader"
				case 'Extension':
					if isinstance(item, Path):
						val = item.suffix[1:]
					elif hasattr(item, "extension"):
						val = item.extension
				case 'File Size':
					if isinstance(item, (InstanceConfig, Northlight.Admin, Northlight.File)):
						val = byter(len(item))
					elif isinstance(item, Path):
						val = byter(item.stat().st_size)
			if val is not None:
				qtwi.setData(i, QtCore.Qt.ItemDataRole.DisplayRole, val)
		return qtwi
	
	@QtCore.Slot()
	def filter_items(self) -> None:
		mdl = self.tree_pti.model()
		headerdict = {mdl.headerData(i, QtCore.Qt.Orientation.Horizontal): i for i in range(mdl.columnCount())}
		with TimerLog(f"Executing filter on tree"):
			if self.fltr_txt.text == '':
				for x in QtWidgets.QTreeWidgetItemIterator(self.tree_pti, flags=QtWidgets.QTreeWidgetItemIterator.IteratorFlag.Hidden):
					x.value().setHidden(False)
			else:
				for tli in [self.tree_pti.topLevelItem(i) for i in range(self.tree_pti.topLevelItemCount)]:
					for item in self.tree_pti.nested_children(tli):
						subitem = item.data(0, UserRoles.PTI)
						if isinstance(subitem, Northlight.File):
							if self.fltr_eql.checked:
								decision = item.text(headerdict[self.fltr_col.currentText]) != self.fltr_txt.text
							else:
								decision = self.fltr_txt.text not in item.text(headerdict[self.fltr_col.currentText])
						elif isinstance(subitem, Northlight.Folder):
							decision = True
							for kid in [item.child(ci) for ci in range(item.childCount())]:
								if not kid.isHidden():
									decision = False
									break
						if item.isHidden() != decision:
							item.setHidden(decision)
	
	@QtCore.Slot()
	def updateDesc(self) -> None:
		item = self.tree_pti.selection()
		subitem = item.data(0, UserRoles.PTI)
		
		if isinstance(subitem, Northlight.File):
			if subitem.name.split('.')[-1] in ['tex', 'dds']:
				self.ru_widget = self.desc_img
				return
		
		if self.ru_widget != self.desc_txt:
			self.ru_widget = self.desc_txt
			
		self.updateDesc_Gen(item, subitem)
		if isinstance(self.ru_widget, QtWidgets.QTextEdit):
			self.updateDesc_Text(subitem)
		elif isinstance(self.ru_widget, TexViewerWidget):
			self.updateDesc_Image(subitem)
		self.updateDesc_Other(subitem)

	def updateDesc_Text(self, subitem) -> None:
		if isinstance(subitem, Northlight.File):
			match subitem.name.split('.')[-1]:
				case 'md':
					self.desc_txt.markdown = subitem.data.decode()
				case 'bin' | 'resources' | 'ui' | 'flare' | 'gfxgraph' | 'particle' | 'rbf' | 'ivtree' | 'binbt' | 'bineqs' | 'binfsm' | 'binapx' | 'binclothprof' | 'binragdollprof' | 'bintimeline' | 'binnav':
					self.desc_txt.plainText = bin_explorer(subitem.data, subitem.name)
				case 'txt' | 'json' | 'xml' | 'xsl' | 'yaml' | 'asset' | 'meta':
					self.desc_txt.plainText = subitem.data.decode()
				case 'tex':
					hndlr = tex_handler(subitem)
					if hndlr is not None:
						self.desc_txt.plainText = yamldump(hndlr.dict())
					else:
						self.desc_txt.plainText = ''
				case _:
					self.desc_txt.plainText = ''
		elif isinstance(subitem, Northlight.MetaAdmin):
			if subitem.path is not None:
				self.desc_txt.plainText = yamldump(PackMeta(subitem.path, subitem.admin.reader.version_minor).dict())
			elif len(subitem.metadata_types) != 0:
				self.desc_txt.plainText = yamldump(subitem.metadata_types)
			else:
				self.desc_txt.plainText = "No packmeta file associated."
		elif isinstance(subitem, Northlight.Admin):
			self.desc_txt.plainText = yamldump({'Extensions'   : subitem.extensions(), 'Top-Level Folders': sorted([x.name for x in subitem.tree.fldr if x.depth == 1]),
			                             'Second Level Folders': sorted({x.name for x in subitem.tree.fldr if x.depth == 2})})
		else:
			self.desc_txt.plainText = ''
	
	def updateDesc_Image(self, subitem) -> None:
		if isinstance(subitem, Northlight.File):
			if subitem.name.split('.')[-1] in ['tex', 'dds']:
				if not subitem.is_exported:
					subitem.export()
				self.desc_img.updateImage(subitem.export_path)
		
	def updateDesc_Gen(self, item: QtWidgets.QTreeWidgetItem, subitem) -> None:
		if isinstance(subitem, Northlight.Admin):
			if not subitem.is_set:
				self.pti_factory(subitem.reader, item)
				self.pti_factory(subitem.data, item)
				self.pti_factory(subitem.meta, item)
				self.pti_factory(subitem.tree, item)
				item.setExpanded(True)
		elif isinstance(subitem, Northlight.TreeAdmin):
			if item.childCount() == 0:
				genlist_d = dict()
				dlg = QtWidgets.QProgressDialog(self, labelText=f"Loading filemap tree for {subitem.admin.path.stem}...", maximum=300, autoClose=False, value=0, autoReset=False, minimumDuration=100)
				dlg.windowTitle = "Torchbearer Tree Mapper"
				dlg.setModal(True)
				dlg.minimumWidth = 400
				dlg.open()
				dlg.show()
				for d in subitem.fldr:
					genlist_d[d.index] = self.pti_factory(d, item if d.index == 0 and d.parent_idx <= 0 else genlist_d[d.parent_idx])
				dlg.value += 100
				genlist_f = {f.index: self.pti_factory(f, genlist_d[f.parent_idx]) for f in subitem.file}
				dlg.value += 100
				for it in [*genlist_d.values(), *genlist_f.values()]:
					it.setExpanded(True)
				item.setExpanded(True)
				logger.info(f'Finished tree generation for {subitem.admin.name}, generated {len(genlist_d)} folders and {len(genlist_f)} files')
				if dlg.wasCanceled:
					logger.info('Treegen - I got cancelled! Clearing...')
					for i in genlist_d.values():
						item.removeChild(i)
				dlg.close()
		
	def updateDesc_Other(self, subitem) -> None:
		if isinstance(subitem, Northlight.File):
			self.desc_hex.load(subitem.data)
		elif isinstance(subitem, ReaderNLEv10):
			self.desc_hex.load(subitem.uhd)
		elif isinstance(subitem, Northlight.MetaAdmin):
			if subitem.path is not None:
				self.desc_hex.load(subitem.path.read_bytes())
		else:
			self.desc_hex.bytedata = b''
		
		if isinstance(subitem, Dictable):
			self.desc_oth.plainText = yamldump(subitem.dict())
		else:
			self.desc_oth.plainText = ''
	
	@QtCore.Slot()
	def load_instances(self):
		for i, item in enumerate([self.tree_pti.topLevelItem(x) for x in range(self.tree_pti.topLevelItemCount)]):
			for x in list(self.tree_pti.nested_children(item)):
				x.parent().removeChild(x)
		self.tree_pti.clear()
		for instance_name, instance_cfg in self.appcfg.instances.items():
			instance_pti = self.pti_factory(instance_cfg)
			for item in instance_cfg.keys:
				if item in instance_cfg.keys:
					if item not in instance_cfg.admindict.keys():
						instance_cfg.admindict[item] = Northlight.Admin(item, instance_cfg)
					self.pti_factory(instance_cfg.admindict[item], instance_pti)
				else:
					raise KeyError
			self.tree_pti.addTopLevelItem(instance_pti)
			logger.info(f"MapTree - manager {instance_name} finished reader init, {len(instance_cfg.files)} files in directory ({len(instance_cfg.keys)} that match filter)")


class MainWindow(QtWidgets.QMainWindow):
	cfg: AppConfig
	tree: MainTree
	
	def __init__(self):
		super().__init__()
		self.cfg = AppConfig()
		self.windowTitle = f"Torchbearer | v{self.cfg.vrsn}"
		self.statusBar = QtWidgets.QStatusBar()
		self.resize(1366, 768)

		self.tree = MainTree(self.cfg)
		self.setCentralWidget(self.tree)
		menu_file = self.menuBar().addMenu('File')
		menu_file.addAction('&Preferences...', self.conf)
		menu_file.addSeparator()

		menu_debug = self.menuBar().addMenu('Debug')
		menu_debug.addAction('Empty TexViewer', self.new_texviewer)
		
		menu_about = self.menuBar().addMenu('About...')
		menu_about.addAction('About Torchbearer', self.about)
		menu_about.addAction('About QT', QtWidgets.QApplication.aboutQt)
		
		self.confwindow = ConfigWindow(self.cfg)
		self.confwindow.watcher.load_css()
		self.confwindow.instance_manager.cfgChanged.connect(self.tree.load_instances)
	
	@QtCore.Slot()
	def conf(self):
		self.confwindow.exec()

	@QtCore.Slot()
	def about(self):
		md_txt = QtWidgets.QTextEdit(markdown=Path('./readme.md').read_text(), readOnly=True)
		md_txt.setFrameStyle(QtWidgets.QFrame.Shape.NoFrame)
		md_txt.windowTitle = f"About Torchbearer v{self.cfg.vrsn}"
		md_txt.resize(600, 400)
		md_txt.show()

	@QtCore.Slot()
	def new_texviewer(self):
		texview = TexViewer(300, 300)
		texview.show()


# Want no borders? Use this where self is a QtWidgets.QMainWindow instance:
# self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
# Further reading: https://doc.qt.io/qtforpython-6/PySide6/QtCore/Qt.html#PySide6.QtCore.Qt.WindowType


def default():
	with TimerLog('Program init'):
		app = QtWidgets.QApplication(sys.argv)
		app.windowIcon = QtGui.QIcon('./torchbearer/style/tbr.svg')
		window = MainWindow()
		window.show()
	sys.exit(app.exec())
	