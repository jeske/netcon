
# This just returns the full list of paths to append...

def paths(root_dir):
    p = []
    p.append("/home/jeske/neotonic/python/examples/base") # base
    p.append("/home/jeske/neotonic/python/") # neo_cgi.so
    p.append("%s" % root_dir)
    return p

