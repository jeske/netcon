
# This just returns the full list of paths to append...
import os

def paths(root_dir):
    p = []
    cwd = os.getcwd()
    if cwd.find('blong') != -1:
      p.append("/home/blong/neotonic/python/examples/base") # base
      p.append("/home/blong/neotonic/python/") # neo_cgi.so
    else:
      p.append("/home/jeske/neotonic/python/examples/base") # base
      p.append("/home/jeske/neotonic/python/") # neo_cgi.so
    p.append("%s" % root_dir)
    p.append("%s/math" % root_dir)
    return p

