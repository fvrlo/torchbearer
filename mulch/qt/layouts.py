from __future__ import annotations

from typing import Literal, overload, Self

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QWidget, QGridLayout, QLayout, QLabel, QBoxLayout, QTabWidget
from PySide6.QtCore import Qt, QMargins, QObject
from __feature__ import true_property # type: ignore

from mulch.qt.quick import Quick

__all__ = [
	"qGrid",
	"qTabs",
	"qBox",
]



class qGrid(QGridLayout):
	def __init__(
			self,
			*,
			parent: QWidget | None = None,
			rs: list[int] | None = None,
			cs: list[int] | None = None,
			spacing: int | None = None,
			margins: int | None | tuple[int, int, int, int] = None
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
			self.contentsMargins = QMargins(margins, margins, margins, margins)  # noqa
		elif isinstance(margins, tuple):
			self.contentsMargins = QMargins(margins[0], margins[1], margins[2], margins[3])  # noqa
	
	def gen(self, *kids: QWidget | QLayout | str, r: int, c: int):
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
	
	def setMargins(self, /, l: int = 0, t: int | None = None, r: int | None = None, b: int | None = None) -> Self:
		if t is not None:
			self.contentsMargins = QMargins(l, t, r, b)  # noqa
		else:
			self.contentsMargins = QMargins(l, l, l, l)  # noqa
		return self
	
	@overload
	def add(self, item: QWidget | QLayout | str, r: int, c: int, rs: int, cs: int, align: Qt.AlignmentFlag) -> Self:
		...
	
	@overload
	def add(self, item: QWidget | QLayout | str, r: int, c: int, align: Qt.AlignmentFlag) -> Self:
		...
	
	@overload
	def add(self, item: QWidget | QLayout | str, r: int, c: int, rs: int, cs: int) -> Self:
		...
	
	@overload
	def add(self, item: QWidget | QLayout | str, r: int, c: int) -> Self:
		...
	
	@overload
	def add(self, item: QWidget | str) -> Self:
		...
	
	def add(self,
	            item: QWidget | QLayout | str,
	            r: int | None = None,
	            c: int | None = None,
	            rs: int | None = None,
	            cs: int | None = None,
	            align: Qt.AlignmentFlag | None = None
	        ) -> Self:
		if isinstance(item, str):
			item = QLabel(item)
		
		# here comes the overload parade
		if isinstance(item, QWidget):
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
		elif isinstance(item, QLayout):
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


class qTabs(QTabWidget):
	def __init__(self, parent: QObject | None = None, /, **kids: QWidget | QLayout):
		super().__init__(parent)
		for name, item in kids.items():
			if isinstance(item, QLayout):
				self.addTab(Quick.nest(item), name)
			else:
				self.addTab(item, name)
	
	def add(self, item: QWidget | QLayout, name: str):
		if isinstance(item, QLayout):
			self.addTab(Quick.nest(item), name)
		else:
			self.addTab(item, name)
		

class qBox(QBoxLayout):
	def __init__(self,
	             *items:    QWidget | QLayout | str | tuple[QWidget | QLayout | str, int],
	             d:         QBoxLayout.Direction | Qt.Orientation | Literal['ltr', 'rtl', 'ttb', 'btt', 'h', 'v'] = QBoxLayout.Direction.LeftToRight,
	             stretch:   list[int] | None = None,
	             spacing:   int | None = None,
	             margins:   int | None = None,
	             name:      int | None = None,
	             parent:    QWidget | None = None
	             ):
		
		match d:
			case 'ltr' | QBoxLayout.Direction.LeftToRight:
				super().__init__(QBoxLayout.Direction.LeftToRight, parent=parent)
			case 'rtl' | QBoxLayout.Direction.RightToLeft:
				super().__init__(QBoxLayout.Direction.RightToLeft, parent=parent)
			case 'ttb' | QBoxLayout.Direction.TopToBottom:
				super().__init__(QBoxLayout.Direction.TopToBottom, parent=parent)
			case 'btt' | QBoxLayout.Direction.BottomToTop:
				super().__init__(QBoxLayout.Direction.BottomToTop, parent=parent)
			case 'h' | Qt.Orientation.Horizontal:
				super().__init__(QBoxLayout.Direction.LeftToRight, parent=parent)
			case 'v' | Qt.Orientation.Vertical:
				super().__init__(QBoxLayout.Direction.TopToBottom, parent=parent)

		if spacing is not None:
			self.spacing = spacing
		if margins is not None:
			self.contentsMargins = QMargins(margins, margins, margins, margins)  # noqa
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
	
	def setMargins(self, /, l: int = 0, t: int | None = None, r: int | None = None, b: int | None = None) -> Self:
		if t is not None:
			self.contentsMargins = QMargins(l, t, r, b)  # noqa
		else:
			self.contentsMargins = QMargins(l, l, l, l)  # noqa
		return self
	
	@overload
	def add(self, item: QWidget | QLayout | str, stretch: int) -> Self:
		...
	
	@overload
	def add(self, item: QWidget | QLayout  | str) -> Self:
		...
	
	def add(self, item: QWidget | QLayout | str, stretch: int | None = None) -> Self:
		if isinstance(item, str):
			item = QLabel(item)
		if isinstance(item, QWidget):
			if stretch is not None:
				self.addWidget(item, stretch)
			else:
				self.addWidget(item)
		elif isinstance(item, QLayout):
			if stretch is not None:
				self.addLayout(item, stretch)
			else:
				self.addLayout(item)
		return self
	
	def addSep(self):
		direction = self.direction()
		if direction in [QBoxLayout.Direction.LeftToRight, QBoxLayout.Direction.RightToLeft]:
			self.addWidget(Quick.vline())
		elif direction in [QBoxLayout.Direction.TopToBottom, QBoxLayout.Direction.BottomToTop]:
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
