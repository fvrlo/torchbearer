import sys
from loguru import logger
from PySide6 import QtWidgets, QtGui

from torchbearer.gui.tool import MainWindow

__module__ = "torchbearer"
__author__ = "fvrlo"
__version__ = "0.1.2"

if __name__ == '__main__':
	logger.remove()  # Remove the default handler.
	logger.add(sys.stdout, format="[<e>{time:hh:mm:ss.SSS}</>] [<lvl>{level}</>] {message}")  # Log to console with custom format.
	
	app = QtWidgets.QApplication(sys.argv)
	app.windowIcon = QtGui.QIcon('./torchbearer/style/tbr.svg')
	window = MainWindow(__version__)
	window.show()
	
	x = app.exec()
	sys.exit(x)