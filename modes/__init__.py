'''Contains all the chess gamemodes as well as a separate file (basic) for objects common to all of them.'''

from os.path import dirname, basename, isfile, join
import glob

hidden=True
blacklist=["__init__.py","basic.py","tests.py"]
namespace=''
try:
    __import__("standard")
except:
    namespace="modes."
modules = glob.glob(join(dirname(__file__), "*.py"))
original_modules=[basename(f)[:-3] for f in modules if isfile(f) and not any([f.endswith(blacklist[i]) for i in range(len(blacklist))])] #original module file names
module_list=[getattr(getattr(__import__(namespace+mdl,fromlist=[namespace]),"info"),"name") for mdl in original_modules] # sorted module proper names
module_list.sort()
module_dict={getattr(getattr(__import__(namespace+mdl,fromlist=[namespace]),"info"),"name"):mdl for mdl in original_modules}
__all__ = [module_dict[item] for item in module_list] 
# for every proper name in module_list (the sorted one), add the corresponding module name from the list of file names