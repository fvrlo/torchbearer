import sys
from loguru import logger
import warnings



warnings.filterwarnings("ignore", category=RuntimeWarning, module="shibokensupport")

from torchbearer.gui.tool import default

if __name__ == '__main__':
	logger.remove()  # Remove the default handler.
	logger.add(sys.stdout, format="[<e>{time:hh:mm:ss.SSS}</>] [<lvl>{level}</>] {message}")  # Log to console with custom format.
	default()