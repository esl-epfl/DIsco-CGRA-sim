from .params import *

class VWR():
    def __init__(self):
        self.values = [0 for _ in range(N_ELEMS_PER_VWR)]
    
    def getIdx(self, idx):
        if idx < 0 or idx >= N_ELEMS_PER_VWR:
            raise Exception("The indexed accesed " + str(idx) + " should be >= 0 and < " + str(N_ELEMS_PER_VWR) + ".")
        return self.values[idx]