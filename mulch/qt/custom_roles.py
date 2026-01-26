from __future__ import annotations

from enum import IntEnum

from PySide6 import QtCore

__all__ = [
	'UserRoles'
]

class UserRoles(IntEnum):
	PTI = QtCore.Qt.ItemDataRole.UserRole.value + 1100
	Hex = QtCore.Qt.ItemDataRole.UserRole.value + 1101
