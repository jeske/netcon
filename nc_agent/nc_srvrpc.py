
import postdata
import time

class NCServerRpc:
    def __init__(self,myhostname):
        self._myhostname = myhostname

        # make sure we can resolve the server hostname!

    def checkIn(self,ncmgr):
        now = int(time.time())
        result = postdata.post_multipart("c1.neotonic.com","/netcon/agentCheckIn.py",
                            [('hostname',self._myhostname), ('now',str(now))],[('data','data.txt',ncmgr.postdata())])
        print result
                          
        
        
        
