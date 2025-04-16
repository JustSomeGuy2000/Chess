from os.path import dirname, basename, isfile, join
import glob

blacklist=["__init__.py","basic.py","tests.py"]
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3]+".Info" for f in modules if isfile(f) and not any([f.endswith(blacklist[i]) for i in range(len(blacklist))])]