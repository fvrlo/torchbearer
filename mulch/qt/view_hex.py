from __future__ import annotations

from collections import defaultdict
from enum import IntEnum

from PySide6 import QtCore, QtGui, QtWidgets
from __feature__ import true_property #type: ignore

from mulch import asciichart
from .custom_roles import UserRoles



__all__ = [
	'HexRole',
	'HexViewer',
	'HexTableView'
]

class HexRole(IntEnum):
	Raw = 0
	Int = 1
	Str = 2
	
	@classmethod
	def __len__(cls):
		return len([x for x in cls])
	
	def get_next(self):
		return type(self)((self.value + 1) % len(self))


class HexViewer(QtCore.QAbstractTableModel):
	bytedata: bytes
	_row_cnt: int
	_datamode_dict: defaultdict[int, HexRole]
	
	font: QtGui.QFont
	
	fg_dict: dict[HexRole, QtGui.QBrush]
	
	def __init__(self, value: bytes = b'', font: str = 'Lucida Console'):
		super().__init__()
		self.bytedata = value
		self.font = QtGui.QFont(font)
		self._datamode_dict = defaultdict(lambda: HexRole.Raw)
		self.fg_dict = {
			HexRole.Raw: QtGui.QBrush(QtGui.QColor(0, 0, 0)),
			HexRole.Int: QtGui.QBrush(QtGui.QColor(0, 0, 180)),
			HexRole.Str: QtGui.QBrush(QtGui.QColor(0, 180, 0)),
		}
	
	def load(self, value: bytes):
		self.beginResetModel()
		self.bytedata = value
		self._datamode_dict = defaultdict(lambda: HexRole.Raw)
		self.endResetModel()
	
	def columnCount(self, parent=None):
		return 8
	
	def rowCount(self, parent=None):
		return len(self.bytedata) // self.columnCount() + (len(self.bytedata) % self.columnCount() != 0)

	def next_datamode(self, index: QtCore.QModelIndex | list[QtCore.QModelIndex]):
		for x in (index if isinstance(index, list) else [index]):
			data_index = self.data_index(x)
			self._datamode_dict[data_index] = self._datamode_dict[data_index].get_next()
	
	def data_index(self, index: QtCore.QModelIndex) -> int | None:
		data_index = (index.row() * self.columnCount()) + index.column()
		if data_index >= len(self.bytedata):
			return None
		else:
			return data_index
	
	def data(self, index: QtCore.QModelIndex, role: UserRoles | HexRole | QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole):
		data_index = self.data_index(index)
		if data_index is None:
			return None
		
		match role:
			case UserRoles.Hex:
				return self._datamode_dict[data_index]
			case QtCore.Qt.ItemDataRole.DisplayRole:
				match self._datamode_dict[data_index]:
					case HexRole.Raw:
						return f'{self.bytedata[data_index]:02X}'
					case HexRole.Int:
						return f'{self.bytedata[data_index]}'
					case HexRole.Str:
						x = self.bytedata[data_index]
						if x in asciichart.keys():
							return asciichart[x]
						elif 32 < x <= 0x7E:
							return chr(x)
						else:
							return f'??'
			case QtCore.Qt.ItemDataRole.ForegroundRole:
				return self.fg_dict[self._datamode_dict[data_index]]
			case QtCore.Qt.ItemDataRole.ToolTipRole:
				return f"Offset {data_index} ({hex(data_index)})"
			case QtCore.Qt.ItemDataRole.TextAlignmentRole:
				return QtCore.Qt.AlignmentFlag.AlignCenter
			case QtCore.Qt.ItemDataRole.FontRole:
				return self.font
			case _:
				return None


class HexTableView(QtWidgets.QTableView):
	mdl: HexViewer
	
	def __init__(self, mdl: HexViewer):
		super().__init__(showGrid=False, gridStyle=QtCore.Qt.PenStyle.NoPen, sortingEnabled=False, wordWrap=False)
		self.mdl = mdl
		self.mdl.dataChanged.connect(self.updateEditorData)
		self.setModel(mdl)
		self.alternatingRowColors = True
		self.selectionMode = QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection
		self.verticalHeader().defaultSectionSize = 20
		self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
		self.verticalHeader().hide()
		self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
		self.horizontalHeader().hide()
	
	def mouseDoubleClickEvent(self, event):
		index = self.indexAt(event.pos())
		self.mdl.next_datamode(index)
		self.mdl.dataChanged.emit(index, index, QtCore.Qt.ItemDataRole.DisplayRole)
	
	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key.Key_Space:
			self.mdl.next_datamode(self.selectedIndexes())
			self.mdl.dataChanged.emit(self.selectedIndexes()[0], self.selectedIndexes()[-1], QtCore.Qt.ItemDataRole.DisplayRole)
			return True
		return super().keyPressEvent(event)

