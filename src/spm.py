from .params import *
class SPM:
    def __init__(self):
        self.lines = [[0 for _ in range(SPM_NWORDS)] for _ in range(SPM_NLINES)]
    
    def setLine(self, nline, vec):
        assert(nline >= 0 & nline < SPM_NLINES), "SPM: Number of SPM line out of bounds. It should be >= 0 and < " + str(SPM_NLINES) + "."
        assert(len(vec) == SPM_NWORDS), "SPM: Vector should have " + str(SPM_NWORDS) + " elements."
        self.lines[nline] = vec
    
    def getLine(self, nline):
        if nline < 0 or nline >= SPM_NLINES:
            raise Exception("SPM: Number of SPM line " + str(nline) + " out of bounds. It should be >= 0 and < " + str(SPM_NLINES) + ".")
        return self.lines[nline]