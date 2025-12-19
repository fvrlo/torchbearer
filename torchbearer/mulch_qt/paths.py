from __future__ import annotations

import os
from pathlib import Path

import qtawesome as qta

from PySide6 import QtCore, QtGui, QtWidgets
from __feature__ import true_property #type: ignore

from torchbearer.mulch_qt.layouts import qGrid

class PathLineEdit(QtWidgets.QLineEdit):
	_path: Path
	
	pathChanged = QtCore.Signal(Path)
	
	def __init__(self, defaultPath: Path, *, open_in_explorer: bool = False, select: bool = False, empty: bool = False):
		super().__init__(text=str(defaultPath), readOnly=True)
		self._path = defaultPath
		if open_in_explorer:
			actn1 = QtGui.QAction(qta.icon('fa6s.folder'), 'Open In Explorer', self)
			actn1.triggered.connect(self.open_in_explorer)
			self.addAction(actn1, QtWidgets.QLineEdit.ActionPosition.TrailingPosition)
		if select:
			actn_sel = QtGui.QAction(qta.icon('fa6s.ellipsis'), 'Select Directory...', self)
			actn_sel.triggered.connect(self.select)
			self.addAction(actn_sel, QtWidgets.QLineEdit.ActionPosition.TrailingPosition)
		if empty:
			actn_trash = QtGui.QAction(qta.icon('fa6s.trash-can'), 'Empty Directory...', self)
			self.addAction(actn_trash, QtWidgets.QLineEdit.ActionPosition.TrailingPosition)
			actn_trash.triggered.connect(lambda: self.clear_directory(self.path))
	
	@QtCore.Slot()
	def open_in_explorer(self):
		os.startfile(self._path.parent)
	
	@QtCore.Slot()
	def select(self):
		self.path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", str(self._path.parent), QtWidgets.QFileDialog.Option.ShowDirsOnly)
	
	@property
	def path(self) -> Path:
		return self._path

	@path.setter
	def path(self, value: str):
		if value != '':
			self._path = Path(value).resolve()
			self.text = str(self._path)
			self.pathChanged.emit(self._path)
	
	@staticmethod
	def clear_directory(path: Path):
		f_count = 0
		d_count = 0
		totalsize = 0
		for root, dirs, files in path.walk(top_down=False):
			for name in files:
				f_count += 1
				totalsize += (root / name).stat().st_size
			for _ in dirs:
				d_count += 1
		confirm_dialog = QtWidgets.QDialog(sizeGripEnabled=False)
		
		btn_y = QtWidgets.QPushButton("OK")
		btn_y.pressed.connect(lambda: confirm_dialog.accept())
		
		btn_n = QtWidgets.QPushButton("Cancel", default=True)
		btn_n.pressed.connect(lambda: confirm_dialog.reject())
		
		diaglayout = qGrid(rs=[4, 1]).add(
			f'Are you sure you want to clear {path.resolve()}?\n{f_count} files and {d_count} directories totalling {byter(totalsize)} will be removed.', 0, 0, 1, 3)
		diaglayout.add(btn_y, 1, 1).add(btn_n, 1, 2)
		confirm_dialog.setLayout(diaglayout)
		
		match confirm_dialog.exec():
			case QtWidgets.QDialog.DialogCode.Accepted:
				for root, dirs, files in path.walk(top_down=False):
					for name in files:
						(root / name).unlink()
					for name in dirs:
						(root / name).rmdir()
			case _:
				pass