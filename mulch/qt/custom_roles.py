from __future__ import annotations

from enum import IntEnum

from PySide6 import QtCore
from __feature__ import true_property #type: ignore

__all__ = [
	'UserRoles'
]

class UserRoles(IntEnum):
	PTI = QtCore.Qt.ItemDataRole.UserRole.value + 1100
	Hex = QtCore.Qt.ItemDataRole.UserRole.value + 1101
