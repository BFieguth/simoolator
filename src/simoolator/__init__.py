# read version from installed package
from importlib.metadata import version
__version__ = version("simoolator")

from simoolator.cow import Cow
from simoolator.herd import Herd
