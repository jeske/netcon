
import postdata

class NCServerRpc:
    def __init__(self,urlpath):
        self._urlpath = urlpath

        # make sure we can resolve the server hostname!

    def checkIn(self,ncmgr):
        result = postdata.post_multipart("c1.neotonic.com","/netcon/agentCheckIn.py",
                            [],[('data','data.txt',ncmgr.postdata())])
        print result
                          
        
        
        
