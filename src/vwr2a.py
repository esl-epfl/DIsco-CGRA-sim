
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
        # Fill RC neighbours info
        for col in range(CGRA_COLS):
            for row in range(CGRA_ROWS):
                # RCT
                rct_col = col-1
                if rct_col < 0: rct_col = CGRA_COLS-1
                self.rcs[col][row].neighbours[0] = self.rcs[rct_col][row].alu
                # RCB
                rcb_col = col+1
                if rcb_col >= CGRA_COLS: rcb_col = 0
                self.rcs[col][row].neighbours[1] = self.rcs[rcb_col][row].alu
                # RCL
                rcl_row = row-1
                if rcl_row < 0: rcl_row = CGRA_ROWS-1
                self.rcs[col][row].neighbours[2] = self.rcs[col][rcl_row].alu
                # RCR
                rcr_row = row+1
                if rcr_row >= CGRA_ROWS: rcr_row = 0
                self.rcs[col][row].neighbours[3] = self.rcs[col][rcr_row].alu

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
        # Write on SRF
                    
        # Write on VWRs
        
        
