
import urllib

class NCServerRpc:
    def __init__(self,urlpath):
        self._urlpath = urlpath

        # make sure we can resolve the server hostname!

    def checkIn(self):
        fp = urllib.urlopen(self._urlpath)
        print fp.read()
        
                          
        
        
        
