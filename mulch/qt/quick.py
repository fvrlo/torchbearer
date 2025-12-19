from __future__ import annotations

from typing import Callable

from PySide6 import QtCore, QtGui, QtWidgets
from __feature__ import true_property # type: ignore


class Quick:
	@staticmethod
	def nest(layout: QtWidgets.QLayout, parent: QtWidgets.QWidget | None = None):
		widget = QtWidgets.QWidget(parent)
		widget.setLayout(layout)
		return widget
	
	@staticmethod
	def split(*items: QtWidgets.QWidget, orientation: QtCore.Qt.Orientation, childrenCollapsible: bool | None = None, opaqueResize: bool | None = None):
		splitter = QtWidgets.QSplitter(orientation=orientation, childrenCollapsible=childrenCollapsible)
		for item in items:
			splitter.addWidget(item)
		if opaqueResize is not None:
			splitter.opaqueResize = opaqueResize
		return splitter
	
	@staticmethod
	def toolbutton_check(*connections: QtCore.Slot | Callable, toolTip: str | None = None, icon: QtGui.QIcon | None = None):
		tbn = QtWidgets.QToolButton()
		tbn.checkable = True
		for x in connections:
			tbn.toggled.connect(x)
		if toolTip is not None:
			tbn.toolTip = toolTip
		if icon is not None:
			tbn.icon = icon
		return tbn

	@staticmethod
	def combobox(*items: str, indexChanged: QtCore.Slot | Callable | None = None):
		combobox = QtWidgets.QComboBox()
		if indexChanged is not None:
			combobox.currentIndexChanged.connect(indexChanged)
		combobox.addItems(items)
		return combobox

	@staticmethod
	def txtview():
		txt = QtWidgets.QTextEdit(readOnly=True)
		txt.textInteractionFlags |= QtCore.Qt.TextInteractionFlag.TextSelectableByMouse
		txt.tabStopDistance = QtGui.QFontMetrics("Lucida Console").size(0, '    ').width()
		return txt

	@staticmethod
	def action(parent: QtCore.QObject, menu: QtWidgets.QMenu, txt: str, caller: QtCore.Slot | Callable, *, icon: QtGui.QIcon | None = None):
		actn = QtGui.QAction(txt, parent)
		actn.triggered.connect(caller)
		menu.addAction(actn)
		if icon is not None:
			menu.icon = icon
		return actn

	@staticmethod
	def pushbutton(text: str, caller: QtCore.Slot | Callable, *, default: bool | None = None, fixedWidth: int | None = None):
		btn = QtWidgets.QPushButton(text)
		btn.pressed.connect(caller)
		if fixedWidth is not None:
			btn.setFixedWidth(fixedWidth)
		if default is not None:
			btn.default = default
		return btn

	@staticmethod
	def checkbox(text: str, caller: QtCore.Slot | Callable, defaultState: bool = False):
		btn = QtWidgets.QCheckBox(text)
		btn.pressed.connect(caller)
		btn.checkable = True
		btn.checked = defaultState
		return btn

	@staticmethod
	def hline():
		return QtWidgets.QFrame(frameShape=QtWidgets.QFrame.Shape.HLine, frameShadow=QtWidgets.QFrame.Shadow.Sunken)

	@staticmethod
	def vline():
		return QtWidgets.QFrame(frameShape=QtWidgets.QFrame.Shape.VLine, frameShadow=QtWidgets.QFrame.Shadow.Sunken)
	
	@staticmethod
	def groupbox(name: str, layout: QtWidgets.QLayout):
		x = QtWidgets.QGroupBox(name, flat=True)
		x.setLayout(layout)
		return x
