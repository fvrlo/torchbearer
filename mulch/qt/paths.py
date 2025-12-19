from __future__ import annotations

import os
from pathlib import Path

import qtawesome as qta

from PySide6 import QtCore, QtGui, QtWidgets
from __feature__ import true_property #type: ignore

from mulch import byter
from mulch.qt.layouts import qGrid



class PathLineEdit(QtWidgets.QLineEdit):
	_path: Path
	
	pathChanged = QtCore.Signal(Path)
	
	actnOpen: QtGui.QAction
	actnSelect: QtGui.QAction
	actnRMDIR: QtGui.QAction
	
	def __init__(self, defaultPath: Path, *, open_in_explorer: bool = False, select: bool = False, empty: bool = False):
		super().__init__(text=str(defaultPath), readOnly=True)
		self._path = defaultPath
		
		self.actnOpen = QtGui.QAction(qta.icon('fa6s.folder'), 'Open In Explorer', self)
		self.actnOpen.triggered.connect(self.open_in_explorer)
		self.actnSelect = QtGui.QAction(qta.icon('fa6s.ellipsis'), 'Select Directory...', self)
		self.actnSelect.triggered.connect(self.select)
		self.actnRMDIR = QtGui.QAction(qta.icon('fa6s.trash-can'), 'Empty Directory...', self)
		self.actnRMDIR.triggered.connect(lambda: confirmClearDirectory(self.path))
		
		if open_in_explorer:
			self.addAction(self.actnOpen, QtWidgets.QLineEdit.ActionPosition.TrailingPosition)
		if select:
			self.addAction(self.actnSelect, QtWidgets.QLineEdit.ActionPosition.TrailingPosition)
		if empty:
			self.addAction(self.actnRMDIR, QtWidgets.QLineEdit.ActionPosition.TrailingPosition)
	
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
		new_path = Path(value).resolve()
		new_path.mkdir(parents=True, exist_ok=True)
		self._path = new_path
		self.text = str(self._path)
		self.pathChanged.emit(self._path)


def confirmClearDirectory(path: Path):
	f_count = 0
	d_count = 0
	totalsize = 0
	for dirpath, dirnames, filenames in path.walk(top_down=False):
		for filename in filenames:
			f_count += 1
			totalsize += (dirpath / filename).stat().st_size
		d_count += len(dirnames)
	
	confirm_dialog = QtWidgets.QDialog()
	
	btn_y = QtWidgets.QPushButton("OK", parent=confirm_dialog)
	btn_n = QtWidgets.QPushButton("Cancel", parent=confirm_dialog, default=True)
	
	btn_y.pressed.connect(confirm_dialog.accept)
	btn_n.pressed.connect(confirm_dialog.reject)
	
	confirm_dialog.setLayout(
		qGrid(rs=[4, 1])
		 .add(f'Are you sure you want to clear {path.resolve()}?\n{f_count} files and {d_count} directories totalling {byter(totalsize)} will be removed.', 0, 0, 1, 3)
		 .add(btn_y, 1, 1)
		 .add(btn_n, 1, 2)
	)
	
	match confirm_dialog.exec():
		case QtWidgets.QDialog.DialogCode.Accepted:
			for dirpath, dirnames, filenames in path.walk(top_down=False):
				for filename in filenames:
					(dirpath / filename).unlink()
				for dirname in dirnames:
					(dirpath / dirname).rmdir()
	