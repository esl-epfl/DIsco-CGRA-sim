from .rc import RC_IMEM_WORD
from .mxcu import MXCU_IMEM_WORD
from .lsu import LSU_IMEM_WORD
from .lcu import LCU_IMEM_WORD
from .params import CGRA_ROWS

# Number of lines in the instruction memory (i.e. max number of instrucitons in all kernels)
IMEM_N_LINES = 512

# GLOBAL INSTRUCTION MEMORY (IMEM) #
class IMEM:
    '''Instruction memory of the CGRA'''
    def __init__(self):
        self.lcu_imem = [LCU_IMEM_WORD() for _ in range(IMEM_N_LINES)]
        self.lsu_imem = [LSU_IMEM_WORD() for _ in range(IMEM_N_LINES)]
        self.mxcu_imem = [MXCU_IMEM_WORD() for _ in range(IMEM_N_LINES)]
        self.rcs_imem = [[RC_IMEM_WORD() for _ in range(IMEM_N_LINES)] for _ in range(CGRA_ROWS)]
