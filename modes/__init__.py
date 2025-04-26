'''Contains all the chess gamemodes as well as a separate file (basic) for objects common to all of them.'''

from os.path import dirname, basename, isfile, join
import glob

hidden=True
blacklist=["__init__.py","basic.py","tests.py"]
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not any([f.endswith(blacklist[i]) for i in range(len(blacklist))])]
__all__.sort()