# this starts up the T-environment...
# 
# The root dir should point to the top of the python tree


import sys

sys.path.insert(0, "../") # pickup our application code
sys.path.insert(0, "../../../../") # pickup neo_cgi.so
sys.path.insert(0, "../../../base") # pickup base libs

# don't put anything above this because the path isn't
# extended yet...
