
# Imports
from src import *
from .params import *
from .spm import SPM
from .srf import SRF
from .vwr import VWR

class CGRA:
    def __init__(self):
        self.lcus = [LCU() for _ in range(CGRA_COLS)]
        self.lsus = [LSU() for _ in range(CGRA_COLS)]
        self.rcs = [[] for _ in range(CGRA_COLS)]
        for col in range(CGRA_COLS):
            for _ in range(CGRA_ROWS):
                self.rcs[col].append(RC())
        # Fill RC neighbours info (RCT, RCB, RCL, RCR)
        for col in range(CGRA_COLS):
            for row in range(CGRA_ROWS):
                # RCT
                rct_row = row-1
                if rct_row < 0: rct_row = CGRA_ROWS-1
                self.rcs[col][row].neighbours.append(self.rcs[col][rct_row])
                # RCB
                rcb_row = row+1
                if rcb_row >= CGRA_ROWS: rcb_row = 0
                self.rcs[col][row].neighbours.append(self.rcs[col][rcb_row])
                # RCL
                rcl_col = col-1
                if rcl_col < 0: rcl_col = CGRA_COLS-1
                self.rcs[col][row].neighbours.append(self.rcs[rcl_col][row])
                # RCR
                rcr_col = col+1
                if rcr_col >= CGRA_COLS: rcr_col = 0
                self.rcs[col][row].neighbours.append(self.rcs[rcr_col][row])

        self.mxcus = [MXCU() for _ in range(CGRA_COLS)]
        self.spm = SPM()
        self.kmem = KMEM()
        self.imem = IMEM()
        self.srfs = [SRF() for _ in range(CGRA_COLS)]
        self.vwrs = [[] for _ in range(CGRA_COLS)]
        for col in range(CGRA_COLS):
            for _ in range(N_VWR_PER_COL):
                self.vwrs[col].append(VWR())

    def setSPMLine(self, nline, vector):
        self.spm.setLine(nline, vector)
    
    def loadSPMData(self, data):
        nline = 0
        for vector in data:
            self.spm.setLine(nline, vector)
            nline+=1
    
    def kernel_config(self, col_one_hot, num_instructions_per_col, imem_add_start, srf_spm_addres, kernel_number):
        self.kmem.addKernel(num_instructions_per_col=num_instructions_per_col, imem_add_start=imem_add_start, col_one_hot=col_one_hot, srf_spm_addres=srf_spm_addres, nKernel=kernel_number)
        
    def updateSharedValues(self):
        # ALUs
        for col in range(CGRA_COLS):
            self.lcus[col].alu.updateALUValues()
            self.lsus[col].alu.updateALUValues()
            self.mxcus[col].alu.updateALUValues()
            for col in range(CGRA_COLS):
                for row in range(CGRA_ROWS):
                    self.rcs[col][row].alu.updateALUValues()       
        
        
        
