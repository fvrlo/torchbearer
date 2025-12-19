import sys
import warnings

from loguru import logger

# fucking shiboken... gives me weird errors in pycharm 2025.03 despite working just fine. this seems to be the easiest fix, as long as it's activated before PySide6 is imported.
warnings.filterwarnings("ignore", category=RuntimeWarning, module="shibokensupport")

from torchbearer.gui.tool import mainApp

__module__ = "torchbearer"
__author__ = "fvrlo"
__version__ = "0.1.1"



if __name__ == '__main__':
	logger.remove()  # Remove the default handler.
	logger.add(sys.stdout, format="[<e>{time:hh:mm:ss.SSS}</>] [<lvl>{level}</>] {message}")  # Log to console with custom format.
	sys.exit(mainApp(__version__).exec())