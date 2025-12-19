from __future__ import annotations

from typing import Callable, Literal, Optional, overload, Self, Union

from PySide6 import QtWidgets, QtCore, QtGui
from __feature__ import true_property # type: ignore


__all__ = [
	"Quick",
	"qGrid",
	"qBox",
	"qTabs"
]


class _QuickAnnos:
	"""Annotation type aliases for Quick methods"""
	type WLIS = Union[QtWidgets.QWidget, QtWidgets.QLayout, QtWidgets.QLayoutItem, str]
	type WIS = Union[QtWidgets.QWidget, QtWidgets.QLayoutItem, str]



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


class qGrid(QtWidgets.QGridLayout):
	def __init__(
			self,
			*,
			parent: QtWidgets.QWidget | None = None,
			rs: list[int] | None = None,
			cs: list[int] | None = None,
			spacing: Optional[int] = None,
			margins: Optional[int | tuple[int, int, int, int]] = None
	):
		super().__init__(parent)
		if rs is not None:
			for i, s in enumerate(rs):
				self.setRowStretch(i, s)
		if cs is not None:
			for i, s in enumerate(cs):
				self.setColumnStretch(i, s)
		if spacing is not None:
			self.spacing = spacing
		if isinstance(margins, int):
			self.contentsMargins = QtCore.QMargins(margins, margins, margins, margins)  # noqa
		elif isinstance(margins, tuple):
			self.contentsMargins = QtCore.QMargins(margins[0], margins[1], margins[2], margins[3])  # noqa
	
	def gen(self, *kids: _QuickAnnos.WLIS, r: int, c: int):
		items = list(kids)
		try:
			while True:
				for row in range(r):
					for col in range(c):
						self.add(items.pop(0), row, col)
		except IndexError:
			pass
		return self
	
	@overload
	def setMargins(self) -> Self:
		...
	
	@overload
	def setMargins(self, /, l: int) -> Self:
		...
	
	@overload
	def setMargins(self, /, l: int, t: int, r: int, b: int) -> Self:
		...
	
	def setMargins(self, /, l: int = 0, t: Optional[int] = None, r: Optional[int] = None, b: Optional[int] = None) -> Self:
		if t is not None:
			self.contentsMargins = QtCore.QMargins(l, t, r, b)  # noqa
		else:
			self.contentsMargins = QtCore.QMargins(l, l, l, l)  # noqa
		return self
	
	@overload
	def add(self, item: _QuickAnnos.WLIS, r: int, c: int, rs: int, cs: int, align: QtCore.Qt.AlignmentFlag) -> Self:
		...
	
	@overload
	def add(self, item: _QuickAnnos.WLIS, r: int, c: int, align: QtCore.Qt.AlignmentFlag) -> Self:
		...
	
	@overload
	def add(self, item: _QuickAnnos.WLIS, r: int, c: int, rs: int, cs: int) -> Self:
		...
	
	@overload
	def add(self, item: _QuickAnnos.WLIS, r: int, c: int) -> Self:
		...
	
	@overload
	def add(self, item: _QuickAnnos.WIS) -> Self:
		...
	
	def add(self, item: _QuickAnnos.WLIS, r: Optional[int] = None, c: Optional[int] = None, rs: Optional[int] = None, cs: Optional[int] = None, align: QtCore.Qt.AlignmentFlag | None = None) -> Self:
		if isinstance(item, str):
			item = QtWidgets.QLabel(item)
		if isinstance(item, QtWidgets.QWidget):
			if align is None:
				if rs is not None:
					self.addWidget(item, r, c, rs, cs)
				elif r is not None:
					self.addWidget(item, r, c)
				else:
					self.addWidget(item)
			else:
				if rs is not None:
					self.addWidget(item, r, c, rs, cs, alignment=align)
				elif r is not None:
					self.addWidget(item, r, c, alignment=align)
				else:
					self.addWidget(item)
		elif isinstance(item, QtWidgets.QLayoutItem):
			if align is None:
				if rs is not None:
					self.addItem(item, r, c, rs, cs)
				elif r is not None:
					self.addItem(item, r, c)
				else:
					self.addItem(item)
			else:
				if rs is not None:
					self.addItem(item, r, c, rs, cs, alignment=align)
				elif r is not None:
					self.addItem(item, r, c, alignment=align)
				else:
					self.addItem(item)
		elif isinstance(item, QtWidgets.QLayout):
			if align is None:
				if rs is not None:
					self.addLayout(item, r, c, rs, cs)
				elif r is not None:
					self.addLayout(item, r, c)
				else:
					raise ValueError(item)
			else:
				if rs is not None:
					self.addLayout(item, r, c, rs, cs, alignment=align)
				elif r is not None:
					self.addLayout(item, r, c, alignment=align)
				else:
					raise ValueError(item)
				
		return self


qBoxDirs = Literal['ltr', 'rtl', 'ttb', 'btt', 'h', 'v']

class qTabs(QtWidgets.QTabWidget):
	def __init__(self, parent: QtCore.QObject | None = None, /, **kids: QtWidgets.QWidget | QtWidgets.QLayout):
		super().__init__(parent)
		for name, item in kids.items():
			if isinstance(item, QtWidgets.QLayout):
				self.addTab(Quick.nest(item), name)
			else:
				self.addTab(item, name)
	
	def add(self, item: QtWidgets.QWidget | QtWidgets.QLayout, name: str):
		if isinstance(item, QtWidgets.QLayout):
			self.addTab(Quick.nest(item), name)
		else:
			self.addTab(item, name)
		


class qBox(QtWidgets.QBoxLayout):
	LTR = QtWidgets.QBoxLayout.Direction.LeftToRight
	RTL = QtWidgets.QBoxLayout.Direction.RightToLeft
	TTB = QtWidgets.QBoxLayout.Direction.TopToBottom
	BTT = QtWidgets.QBoxLayout.Direction.BottomToTop
	
	def __init__(self,
	             *items:    QtWidgets.QWidget | QtWidgets.QLayout | str | tuple[QtWidgets.QWidget | QtWidgets.QLayout | str, int],
	             d:         QtWidgets.QBoxLayout.Direction | QtCore.Qt.Orientation | qBoxDirs = QtWidgets.QBoxLayout.Direction.LeftToRight,
	             stretch:   list[int] | None = None,
	             spacing:   Optional[int] = None,
	             margins:   Optional[int] = None,
	             name:      Optional[str] = None,
	             parent:    Optional[QtWidgets.QWidget] = None
	             ):
		
		match d:
			case 'ltr' | QtWidgets.QBoxLayout.Direction.LeftToRight:
				super().__init__(QtWidgets.QBoxLayout.Direction.LeftToRight, parent=parent)
			case 'rtl' | QtWidgets.QBoxLayout.Direction.RightToLeft:
				super().__init__(QtWidgets.QBoxLayout.Direction.RightToLeft, parent=parent)
			case 'ttb' | QtWidgets.QBoxLayout.Direction.TopToBottom:
				super().__init__(QtWidgets.QBoxLayout.Direction.TopToBottom, parent=parent)
			case 'btt' | QtWidgets.QBoxLayout.Direction.BottomToTop:
				super().__init__(QtWidgets.QBoxLayout.Direction.BottomToTop, parent=parent)
			case 'h' | QtCore.Qt.Orientation.Horizontal:
				super().__init__(QtWidgets.QBoxLayout.Direction.LeftToRight, parent=parent)
			case 'v' | QtCore.Qt.Orientation.Vertical:
				super().__init__(QtWidgets.QBoxLayout.Direction.TopToBottom, parent=parent)

		if spacing is not None:
			self.spacing = spacing
		if margins is not None:
			self.contentsMargins = QtCore.QMargins(margins, margins, margins, margins)  # noqa
		for item in items:
			if isinstance(item, tuple):
				self.add(item[0], item[1])
			else:
				self.add(item)
		if name is not None:
			self.objectName = name
		if stretch is not None:
			for i, s in enumerate(stretch):
				self.setStretch(i, s)
	
	@overload
	def setMargins(self) -> Self:
		...
	
	@overload
	def setMargins(self, /, l: int) -> Self:
		...
	
	@overload
	def setMargins(self, /, l: int, t: int, r: int, b: int) -> Self:
		...
	
	def setMargins(self, /, l: int = 0, t: Optional[int] = None, r: Optional[int] = None, b: Optional[int] = None) -> Self:
		if t is not None:
			self.contentsMargins = QtCore.QMargins(l, t, r, b)  # noqa
		else:
			self.contentsMargins = QtCore.QMargins(l, l, l, l)  # noqa
		return self
	
	@overload
	def add(self, item: QtWidgets.QWidget | QtWidgets.QLayout | str, stretch: int) -> Self:
		...
	
	@overload
	def add(self, item: QtWidgets.QWidget | QtWidgets.QLayout  | str) -> Self:
		...
	
	def add(self, item: QtWidgets.QWidget | QtWidgets.QLayout | str, stretch: Optional[int] = None) -> Self:
		if isinstance(item, str):
			item = QtWidgets.QLabel(item)
		if isinstance(item, QtWidgets.QWidget):
			if stretch is not None:
				self.addWidget(item, stretch)
			else:
				self.addWidget(item)
		elif isinstance(item, QtWidgets.QLayout):
			if stretch is not None:
				self.addLayout(item, stretch)
			else:
				self.addLayout(item)
		return self
	
	def addSep(self):
		direction = self.direction()
		if direction in [QtWidgets.QBoxLayout.Direction.LeftToRight, QtWidgets.QBoxLayout.Direction.RightToLeft]:
			self.addWidget(Quick.vline())
		elif direction in [QtWidgets.QBoxLayout.Direction.TopToBottom, QtWidgets.QBoxLayout.Direction.BottomToTop]:
			self.addWidget(Quick.vline())
		return self
	
	def addStr(self, /, stretch: int | None = None):
		if stretch is not None:
			self.addStretch(stretch)
		else:
			self.addStretch()
		return self

	def addSpa(self, spacing: int):
		self.addSpacing(spacing)
		return self


