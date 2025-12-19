from __future__ import annotations

from pathlib import Path

from loguru import logger

from torchbearer.northlight_internal.textures.directx.DXGI import DXGI_FORMAT
from PIL import ImageQt
from PySide6 import QtCore, QtGui, QtWidgets
from __feature__ import true_property #type: ignore

__all__ = [
	'TexViewer',
	'TexViewerWidget'
]





class TexViewerWidget(QtWidgets.QScrollArea):
	img_sca: float
	img_lbl: QtWidgets.QLabel
	empty: bool
	mousepos: QtCore.QPoint
	
	rst = QtCore.Signal()
	upd = QtCore.Signal(Path)
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.img_sca = 1.0
		self.img_lbl = QtWidgets.QLabel(scaledContents=True)
		self.img_lbl.sizePolicy.setVerticalPolicy(QtWidgets.QSizePolicy.Policy.Ignored)
		self.img_lbl.sizePolicy.setHorizontalPolicy(QtWidgets.QSizePolicy.Policy.Ignored)
		
		self.setWidget(self.img_lbl)
		
		self.zoom_i = self.addAction("Zoom &In", QtGui.QKeySequence.StandardKey.ZoomIn, lambda: self.scaleImage(1.25))
		self.zoom_o = self.addAction("Zoom &Out", QtGui.QKeySequence.StandardKey.ZoomOut, lambda: self.scaleImage(0.8))
		self.zoom_r = self.addAction("&Reset Size", "Ctrl+S", self.rst)
		
		self.zoom_i.enabled = False
		self.zoom_o.enabled = False
		self.zoom_r.enabled = False
		self.mousepos = QtCore.QPoint(0, 0)
		self.mouseTracking = True
		self.reset()
		
		self.acceptDrops = True
		self.contextMenuPolicy = QtCore.Qt.ContextMenuPolicy.ActionsContextMenu
		self.rst.connect(self.resetSize)
		self.upd.connect(self.updateImage)
	
	def reset(self):
		self.img_lbl.pixmap = QtGui.QPixmap()
		self.empty = True
	
	@QtCore.Slot(Path)
	def updateImage(self, file: Path):
		try:
			self.img_lbl.pixmap = QtGui.QPixmap.fromImage(ImageQt.ImageQt(str(file)))
		except NotImplementedError as err:
			self.reset()
			logger.error(f"Can't show image preview: {err.args[0]} ({DXGI_FORMAT(int(err.args[-1][26:])).name})")
			return False
		self.empty = False
		self.img_sca = 1.0
		self.img_lbl.adjustSize()
		return True
	
	def mousePressEvent(self, event):
		if event.button() == QtCore.Qt.MouseButton.LeftButton:
			self.cursor = QtCore.Qt.CursorShape.OpenHandCursor
			self.mousepos = event.localPos()
		super().mousePressEvent(event)
	
	def mouseMoveEvent(self, event):
		delta = event.localPos() - self.mousepos
		if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
			self.horizontalScrollBar().value = int(self.horizontalScrollBar().value - delta.x())
			self.verticalScrollBar().value = int(self.verticalScrollBar().value - delta.y())
		self.mousepos = event.localPos()
		super().mouseMoveEvent(event)
	
	def mouseReleaseEvent(self, event):
		self.unsetCursor()
		self.mousepos = event.localPos()
		super().mouseReleaseEvent(event)
	
	def keyPressEvent(self, event: QtGui.QKeyEvent):
		if event.key() == QtCore.Qt.Key.Key_Delete:
			event.accept()
			self.reset()
		else:
			event.ignore()
	
	def wheelEvent(self, event: QtGui.QWheelEvent):
		if QtCore.Qt.KeyboardModifier.ControlModifier in event.modifiers():
			event.accept()
			clicks = event.angleDelta.y() // 120
			if clicks > 0:
				for _ in range(clicks):
					self.scaleImage(1.25)
			elif clicks < 0:
				for _ in range(abs(clicks)):
					self.scaleImage(0.8)
		else:
			super().wheelEvent(event)
	
	def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
		event.accept() if event.mimeData().hasUrls else event.ignore()
	
	def dragMoveEvent(self, event: QtGui.QDragMoveEvent):
		event.accept() if event.mimeData().hasUrls else event.ignore()
	
	def dropEvent(self, event: QtGui.QDropEvent):
		if event.mimeData().hasUrls:
			event.accept()
			event.setDropAction(QtCore.Qt.DropAction.CopyAction)
			self.upd.emit(Path(event.mimeData().urls()[0].toLocalFile()))
		else:
			event.ignore()
	
	@QtCore.Slot()
	def resetSize(self):
		self.img_lbl.adjustSize()
		self.img_sca = 1.0
	
	def scaleImage(self, factor):
		self.img_sca *= factor
		self.img_lbl.resize(self.img_lbl.pixmap.size() * self.img_sca)
		for scrollBar in [self.horizontalScrollBar(), self.verticalScrollBar()]:
			scrollBar.value = int(factor * scrollBar.value + ((factor - 1) * scrollBar.pageStep / 2))
		self.zoom_i.enabled = self.img_sca < 3
		self.zoom_o.enabled = self.img_sca > 1 / 3

class TexViewer(QtWidgets.QMainWindow):
	viewer: TexViewerWidget
	
	def __init__(self, w: int | None = None, h: int | None = None):
		super().__init__()
		self.windowTitle = "TexViewer"
		self.viewer = TexViewerWidget()
		self.setCentralWidget(self.viewer)
		self.viewer.rst.connect(self.reset)
		self.viewer.upd.connect(self.updateImage)
		self.viewer.frameShape = QtWidgets.QFrame.Shape.NoFrame
		if w is not None and h is not None:
			self.resize(w, h)
		
	def reset(self):
		_instance = QtGui.QGuiApplication.instance()
		self.viewer.resize((QtGui.QGuiApplication() if _instance is None else _instance).primaryScreen.availableSize * (3 / 5))
		self.windowTitle = "TexViewer"
	
	@QtCore.Slot(Path)
	def updateImage(self, file: Path):
		self.windowTitle = f"TexViewer | {file.name}"
	