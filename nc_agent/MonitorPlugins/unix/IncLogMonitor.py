
# REQUIRES Python 2.0 or greater for md5.hexdigest()

import os,sys,string, time
import re
import md5

class IncLogMonitor:
    def __init__(self,ncc):
        self.ncc = ncc
        self.restart = None
        self.datafile = "/tmp/netcon/log_monitor.data"

    def __del__ (self):
        self.save_restart()

    def load_restart(self):
        self.restart = {}
        if os.path.exists(self.datafile):
            lines = open(self.datafile).readlines()
            for line in lines:
                parts = string.split(line, ':')
                if len(parts) != 3: 
                    print "Invalid data line in %s" % self.datafile
                    continue
                self.restart[parts[0]] = (int(parts[1]), parts[2])

    def save_restart(self):
        output = []
        paths = self.restart.keys()
        paths.sort
        for path in paths:
            (ofs, digest) = self.restart[path]
            output.append("%s:%d:%s" % (path, ofs, digest))
        try:
            os.makedirs(os.path.dirname(self.datafile))
        except OSError:
            pass
        open(self.datafile, 'w').write(string.join(output, '\n'))

    def reopen_file(self, path):
        self.load_restart()

        filesize = os.path.getsize(path)
        fp = open(path)

        if self.restart.has_key(path):
            (ofs, comp_digest) = self.restart[path]
            if ofs < 4096:
                m = md5.md5(fp.read(ofs))
            else:
                m = md5.md5(fp.read(4096))
            digest = m.hexdigest()
            if comp_digest == digest:
                fp.seek(ofs)
            else:
                fp.seek(0)
        return fp

    def close_file(self, path, fp):
        ofs = fp.tell()
        fp.seek(0)
        if ofs < 4096:
            m = md5.md5(fp.read(ofs))
        else:
            m = md5.md5(fp.read(4096))
        digest = m.hexdigest()
        self.restart[path] = (ofs, digest)
        self.save_restart()

def makeMonitor(ncc):
    raise "Subclass Only"

