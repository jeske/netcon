# this starts up the T-environment...
# 
# The root dir should point to the top of the python tree


import sys

ROOT_DIR = "../"
sys.path.insert(0, ROOT_DIR)
from tpaths import paths
sys.path = paths(ROOT_DIR) + sys.path
