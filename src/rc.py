"""rc.py: Data structures and objects emulating a Reconfigurable Cell of the VWR2A architecture"""
__author__      = "Lara Orlandic"
__email__       = "lara.orlandic@epfl.ch"

import numpy as np
from enum import Enum
from ctypes import c_int32
import re
from .params import *
from .alu import *
from .srf import SRF_N_REGS

# Local data register (DREG) sizes of specialized slots
RC_NUM_DREG = 2

# Configuration register (CREG) / instruction memory sizes of specialized slots
RC_NUM_CREG = 64

# Widths of instructions of each specialized slot in bits
RC_IMEM_WIDTH = 18

# RC IMEM word decoding
class RC_ALU_OPS(int, Enum):
    '''RC ALU operation codes'''
    NOP = 0
    SADD = 1
    SSUB = 2
    SMUL = 3
    SDIV = 4
    SLL = 5
    SRL = 6
    SRA = 7
    LAND = 8
    LOR = 9
    LXOR = 10
    INB_SF_INA = 11
    INB_ZF_INA = 12
    FXP_MUL = 13
    FXP_DIV = 14
    MAC = 15

class RC_MUX_SEL(int, Enum):
    '''Input A and B to RC ALU'''
    VWR_A = 0
    VWR_B = 1
    VWR_C = 2
    SRF = 3
    R0 = 4
    R1 = 5
    RCT = 6
    RCB = 7
    RCL = 8
    RCR = 9
    ZERO = 10
    ONE = 11
    MAX_INT = 12
    MIN_INT = 13

class RC_MUXF_SEL(int, Enum):
    '''Select the ALU origin of the data on which to compute flags for SF and ZF operations'''
    OWN = 0
    RCT = 1
    RCB = 2
    RCL = 3
    RCR = 4

class RC_DEST_REGS(int, Enum):
    '''Available registers to store ALU result'''
    R0 = 0
    R1 = 1
    SRF = 2
    VWR = 3

# RECONFIGURABLE CELL (RC) #

class RC_IMEM:
    '''Instruction memory of the Reconfigurable Cell'''
    def __init__(self):
        self.IMEM = np.zeros(RC_NUM_CREG,dtype="S{0}".format(RC_IMEM_WIDTH))
        # Initialize kernel memory with default word
        default_word = RC_IMEM_WORD()
        for i, instruction in enumerate(self.IMEM):
            self.IMEM[i] = default_word.get_word()
    
    def set_word(self, kmem_word, pos):
        '''Set the IMEM index at integer pos to the binary imem word'''
        self.IMEM[pos] = np.binary_repr(kmem_word,width=RC_IMEM_WIDTH)
    
    def set_params(self, rf_wsel=0, rf_we=0, muxf_sel=RC_MUXF_SEL.OWN, alu_op=RC_ALU_OPS.NOP, op_mode=0, muxb_sel=RC_MUX_SEL.VWR_A, muxa_sel=RC_MUX_SEL.VWR_A, pos=0):
        '''Set the IMEM index at integer pos to the configuration parameters.
        See RC_IMEM_WORD initializer for implementation details.
        '''
        imem_word = RC_IMEM_WORD(rf_wsel=rf_wsel, rf_we=rf_we, muxf_sel=muxf_sel, alu_op=alu_op, op_mode=op_mode, muxb_sel=muxb_sel, muxa_sel=muxa_sel)
        self.IMEM[pos] = imem_word.get_word()
    
    def get_instruction_asm(self, pos, srf_sel, selected_vwr, vwr_re, srf_we, srf_wd, row):
        '''Print the human-readable instructions of the instruction at position pos in the instruction memory'''
        imem_word = RC_IMEM_WORD()
        imem_word.set_word(self.IMEM[pos])
        return imem_word.get_word_in_asm(srf_sel, selected_vwr, vwr_re, srf_we, srf_wd, row)   
    
    def get_instr_pseudo_asm(self, pos):
        imem_word = RC_IMEM_WORD()
        imem_word.set_word(self.IMEM[pos])
        return imem_word.get_word_pseudo_asm()   
        
    def get_word_in_hex(self, pos):
        '''Get the hexadecimal representation of the word at index pos in the RC config IMEM'''
        return(hex(int(self.IMEM[pos],2)))
        
    def get_instruction_info(self, pos):
        '''Print the human-readable instructions of the instruction at position pos in the instruction memory'''
        imem_word = RC_IMEM_WORD()
        imem_word.set_word(self.IMEM[pos])
        rf_wsel, rf_we, muxf_sel, alu_op, op_mode, muxb_sel, muxa_sel = imem_word.decode_word()
        
        
        if op_mode==0:
            precision = "32-bit"
        else:
            precision = "16-bit"
        
        if alu_op == 15: # Duplicated
            alu_op = 0 # NOP
        for op in RC_ALU_OPS:
            if op.value == alu_op:
                alu_opcode = op.name
        if muxa_sel > 13: # Duplicated
            muxa_sel = 10 # ZERO
        for sel in RC_MUX_SEL:
            if sel.value == muxa_sel:
                muxa_res = sel.name
        if muxb_sel > 13: # Duplicated
            muxb_sel = 10 # ZERO
        for sel in RC_MUX_SEL:
            if sel.value == muxb_sel:
                muxb_res = sel.name
        for sel in RC_MUXF_SEL:
            if sel.value == muxf_sel:
                muxf_res = sel.name
                
        if alu_opcode == RC_ALU_OPS.NOP.name:
            print("No ALU operation")
        elif (alu_opcode == RC_ALU_OPS.INB_SF_INA.name):
            print("Output {0} if sign flag of {1} == 1, else output {2}".format(muxa_res, muxf_res, muxb_res))
        elif (alu_opcode == RC_ALU_OPS.INB_ZF_INA.name):
            print("Output {0} if zero flag of {1} == 1, else output {2}".format(muxa_res, muxf_res, muxb_res))
        else:
            print("Performing ALU operation {0} between operands {1} and {2}".format(alu_opcode, muxa_res, muxb_res))
            print("ALU is performing operations with {0} precision".format(precision))
        
        if rf_we == 1:
            print("Writing ALU result to RC register {0}".format(rf_wsel))
        else:
            print("No RC registers are being written")
        
class RC_IMEM_WORD:
    def __init__(self, hex_word=None, rf_wsel=0, rf_we=0, muxf_sel=RC_MUXF_SEL.OWN, alu_op=RC_ALU_OPS.NOP, op_mode=0, muxb_sel=RC_MUX_SEL.VWR_A, muxa_sel=RC_MUX_SEL.VWR_A):
        '''Generate a binary rc instruction word from its configuration paramerers:
        
           -   rf_wsel: Select one of eight RC registers to write to
           -   rf_we: Enable writing to aforementioned register
           -   muxf_sel: Select a source for the “flag” parameter that is used to compute the zero and sign flags for some ALU operations
           -   alu_op: Perform one of the ALU operations listed in the RC_ALU_OPS enum
           -   op_mode: 0 if 32-bit precision, 1 if 16-bit precision
           -   muxb_sel: Select input B to ALU (see RC_MUX_SEL enum for options)
           -   muxa_sel: Select input A to ALU (see RC_MUX_SEL enum for options)
        
        '''
        if hex_word == None:
            self.rf_wsel = np.binary_repr(rf_wsel, width=1)
            self.rf_we = np.binary_repr(rf_we,width=1)
            self.muxf_sel = np.binary_repr(muxf_sel,width=3)
            self.alu_op = np.binary_repr(alu_op,4)
            self.op_mode = np.binary_repr(op_mode,width=1)
            self.muxb_sel = np.binary_repr(muxb_sel,4)
            self.muxa_sel = np.binary_repr(muxa_sel,4)
            self.word = "".join((self.muxa_sel,self.muxb_sel,self.op_mode,self.alu_op,self.muxf_sel,self.rf_we,self.rf_wsel))
        else:
            decimal_int = int(hex_word, 16)
            binary_number = bin(decimal_int)[2:]  # Removing the '0b' prefix
            # Extend binary number to LSU_IMEM_WIDTH bits
            extended_binary = binary_number.zfill(RC_IMEM_WIDTH)
            self.rf_wsel = extended_binary[17:18] # 1 bit
            self.rf_we = extended_binary[16:17] # 1 bit
            self.muxf_sel = extended_binary[13:16] # 3 bits
            self.alu_op = extended_binary[9:13] # 4 bits
            self.op_mode = extended_binary[8:9] # 1 bit
            self.muxb_sel = extended_binary[4:8] # 4 bits
            self.muxa_sel = extended_binary[:4] # 4 bits
            self.word = extended_binary

    def get_word(self):
        return self.word
    
    def get_word_in_hex(self):
        '''Get the hexadecimal representation of the word at index pos in the RC config IMEM'''
        return(hex(int(self.word, 2)))
    
    def get_word_in_asm(self, srf_sel, selected_vwr, vwr_re, srf_we, srf_wd, row):
        rf_wsel, rf_we, muxf_sel, alu_op, op_mode, muxb_sel, muxa_sel = self.decode_word()
        
        # Half-precision
        if op_mode==0:
            precision = ""
        else:
            precision = ".H"

        # Input muxes
        if muxa_sel > 13: # Duplicated
            muxa_sel = 10 # ZERO
        for sel in RC_MUX_SEL:
            if sel.value == muxa_sel:
                muxa_asm = sel.name
        if muxa_asm == "SRF":
            muxa_asm = "SRF(" + str(srf_sel) + ")"

        if muxb_sel > 13: # Duplicated
            muxb_sel = 10 # ZERO
        for sel in RC_MUX_SEL:
            if sel.value == muxb_sel:
                muxb_asm = sel.name
        if muxb_asm == "SRF":
            muxb_asm = "SRF(" + str(srf_sel) + ")"
        
        # Destination
        dest = ""
        if vwr_re == 1:
            dest += selected_vwr
        
        if rf_we == 1:
            for sel in RC_DEST_REGS:
                if sel.value == rf_wsel:
                    if dest != "":
                        dest += ", "
                    dest += sel.name
        
        if srf_we == 1 and srf_wd == 1 and row == 0: 
            if dest != "":
                dest += ", "
            dest += "SRF(" + str(srf_sel) + ")"

        # ALU ops
        for op in RC_ALU_OPS:
            if op.value == alu_op:
                alu_asm = op.name

        if alu_asm == "INB_SF_INA" or alu_asm == "INB_ZF_INA" :
            for sel in RC_MUXF_SEL:
                if sel.value == muxf_sel:
                    flag = sel.name
            if alu_asm == "INB_SF_INA":
                alu_asm = "SFGA"
            else:
                alu_asm = "ZFGA"
            rc_asm = alu_asm + " " + dest + ", " + flag
        elif alu_asm == "NOP":
            rc_asm = alu_asm
        elif alu_asm == "FXP_MUL" or alu_asm == "FXP_DIV":
            if alu_asm == "FXP_MUL":
                alu_asm = "MUL.FXP"
            else:
                alu_asm = "DIV.FXP"
            rc_asm = alu_asm + " " + dest + ", " + muxa_asm + ", " + muxb_asm
        else:
            rc_asm = alu_asm + precision + " " + dest + ", " + muxa_asm + ", " + muxb_asm

        return rc_asm
    
    def get_word_pseudo_asm(self):
        asm = self.get_word_in_asm(0,0,0,0,0,0)
        # Replace SRF number
        asm = re.sub(r'SRF\(\d+\)', 'SRF(X)', asm)
        # Replace VWR letter
        asm = re.sub(r'VWR_\w', 'VWR_X', asm)
        return asm    

    def set_word(self, word):
        '''Set the binary configuration word of the kernel memory'''
        self.word = word
        self.rf_wsel = word[17:]
        self.rf_we = word[16:17]
        self.muxf_sel = word[13:16]
        self.alu_op = word[9:13]
        self.op_mode = word[8:9]
        self.muxb_sel = word[4:8]
        self.muxa_sel = word[0:4]
        
    def decode_word(self):
        '''Get the configuration word parameters from the binary word'''
        rf_wsel = int(self.rf_wsel,2)
        rf_we = int(self.rf_we,2)
        muxf_sel = int(self.muxf_sel,2)
        alu_op = int(self.alu_op,2)
        op_mode = int(self.op_mode,2)
        muxb_sel = int(self.muxb_sel,2)
        muxa_sel = int(self.muxa_sel,2)
        
        return rf_wsel, rf_we, muxf_sel, alu_op, op_mode, muxb_sel, muxa_sel
    
class RC:
    rc_arith_ops    = { 'MAC','SADD','SSUB','SMUL','SDIV','SLL','SRL','SRA','LAND','LOR', 'LXOR', 'SADD.H','SSUB.H','SMUL.H','SDIV.H','SLL.H','SRL.H','SRA.H','LAND.H','LOR.H','MUL.FXP','DIV.FXP', 'MAC.H' }
    rc_flag_ops     = { 'SFGA','ZFGA' }
    rc_nop_ops      = { 'NOP' }

    def __init__(self):
        self.regs       = [0 for _ in range(RC_NUM_DREG)]
        assert(CGRA_ROWS > 1 and CGRA_COLS > 1), self.__class__.__name__ + ": CGRA too small, at least 4 neighbours per RC"
        self.neighbours = [ALU() for _ in range(4)] # RCT, RCB, RCL, RCR
        self.imem       = RC_IMEM()
        self.nInstr     = 0
        self.default_word = RC_IMEM_WORD().get_word()
        self.alu = ALU()
    
    # Returns the value for mux
    def getMuxValue(self, mux, vwr2a, col, srf_sel, row):
        mxcu_r0 = vwr2a.mxcus[col].regs[0] # VWR_IDX
        vwr_offset = int(SPM_NWORDS/CGRA_ROWS)*row
        if mux == 0: # VWR_A
            mxcu_r5 = vwr2a.mxcus[col].regs[5] # MASK_VWR_A
            slice_idx = mxcu_r0 & mxcu_r5
            muxValue = vwr2a.vwrs[col][0].getIdx(slice_idx + vwr_offset)
        elif mux == 1: # VWR_B
            mxcu_r6 = vwr2a.mxcus[col].regs[6] # MASK_VWR_B
            slice_idx = mxcu_r0 & mxcu_r6
            muxValue = vwr2a.vwrs[col][1].getIdx(slice_idx + vwr_offset)
        elif mux == 2: # VWR_C
            mxcu_r7 = vwr2a.mxcus[col].regs[7] # MASK_VWR_C
            slice_idx = mxcu_r0 & mxcu_r7
            muxValue = vwr2a.vwrs[col][2].getIdx(slice_idx + vwr_offset)
        elif mux == 3: # SRF
            muxValue = vwr2a.srfs[col].regs[srf_sel]
        elif mux == 4: # R0
            muxValue = self.regs[0]
        elif mux == 5: # R1
            muxValue = self.regs[1]
        elif mux == 6: # RCT
            muxValue = self.neighbours[0].res
        elif mux == 7: # RCB
            muxValue = self.neighbours[1].res
        elif mux == 8: # RCL
            muxValue = self.neighbours[2].res
        elif mux == 9: # RCR
            muxValue = self.neighbours[3].res
        elif mux == 10: # ZERO
            muxValue = 0
        elif mux == 11: # ONE
            muxValue = 1
        elif mux == 12: # MAX_INT
            muxValue = MAX_32b
        elif mux == 13: # MIN_INT
            muxValue = MIN_32b
        else:
            raise Exception(self.__class__.__name__ + ": Mux value not recognized")
        return muxValue

    def runAlu(self, alu_op, muxa_val, muxb_val, half_precision, muxf_sel):
        if alu_op == 0: # NOP
            self.alu.nop()
        elif alu_op == 1: # SADD
            if half_precision: self.alu.saddh(muxa_val, muxb_val)
            else: self.alu.sadd(muxa_val, muxb_val)
        elif alu_op == 2: # SSUB
            if half_precision: self.alu.ssubh(muxa_val, muxb_val)
            else:  self.alu.ssub(muxa_val, muxb_val)
        elif alu_op == 3: # SMUL
            if half_precision:  self.alu.smulh(muxa_val, muxb_val)
            else:  self.alu.smul(muxa_val, muxb_val)
        elif alu_op == 4: # SDIV
            if half_precision:  self.alu.sdivh(muxa_val, muxb_val)
            else:  self.alu.sdiv(muxa_val, muxb_val)
        elif alu_op == 5: # SLL
            if half_precision:  self.alu.sllh(muxa_val, muxb_val)
            else:  self.alu.sll(muxa_val, muxb_val)
        elif alu_op == 6: # SRL
            if half_precision:  self.alu.srlh(muxa_val, muxb_val)
            else:  self.alu.srl(muxa_val, muxb_val)
        elif alu_op == 7: # SRA
            if half_precision:  self.alu.srah(muxa_val, muxb_val)
            else:  self.alu.sra(muxa_val, muxb_val)
        elif alu_op == 8: # LAND
            if half_precision:  self.alu.landh(muxa_val, muxb_val)
            else:  self.alu.land(muxa_val, muxb_val)
        elif alu_op == 9: # LOR
            if half_precision:  self.alu.lorh(muxa_val, muxb_val)
            else:  self.alu.lor(muxa_val, muxb_val)
        elif alu_op == 10: # LXOR
            if half_precision:  self.alu.lxorh(muxa_val, muxb_val)
            else:  self.alu.lxor(muxa_val, muxb_val)
        elif alu_op == 11 or alu_op == 12: # INB_SF_INA or INB_ZF_INA
            if muxf_sel == 0: # OWN
                s_flag = self.alu.sign_flag
                z_flag = self.alu.zero_flag
            else:
                s_flag = self.neighbours[muxf_sel-1].sign_flag
                z_flag = self.neighbours[muxf_sel-1].zero_flag
            if alu_op == 11:
                 self.alu.sfga(muxa_val, muxb_val, s_flag)
            else:
                 self.alu.zfga(muxa_val, muxb_val, z_flag)
        elif alu_op == 13: # FP_MUL
             self.alu.mul_fp(muxa_val, muxb_val)
        elif alu_op == 14: # FP_DIV
             self.alu.div_fp(muxa_val, muxb_val)
        elif alu_op == 15: # MAC
            if half_precision:  self.alu.mach(muxa_val, muxb_val, self.regs[0])
            else: self.alu.mac(muxa_val, muxb_val, self.regs[0])
        else:
            raise Exception(self.__class__.__name__ + ": ALU op not recognized")
                
    def run(self, pc, vwr2a, col, row):
        # MXCU info
        mxcu_asm, selected_vwr, srf_sel, alu_srf_write, srf_we, vwr_row_we = vwr2a.mxcus[col].imem.get_instruction_asm(pc)
        # This RC instruction
        rc_hex = self.imem.get_word_in_hex(pc)
        rf_wsel, rf_we, muxf_sel, alu_op, op_mode, muxb_sel, muxa_sel = RC_IMEM_WORD(hex_word=rc_hex).decode_word()
        # Get muxes value
        muxa_val = self.getMuxValue(muxa_sel, vwr2a, col, srf_sel, row)
        muxb_val = self.getMuxValue(muxb_sel, vwr2a, col, srf_sel, row)
        # ALU op
        self.runAlu(alu_op, muxa_val, muxb_val, op_mode, muxf_sel)
        # Write result locally
        if rf_we == 1:
            self.regs[rf_wsel] = self.alu.newRes

        # ---------- Print something -----------
        vwr_re = vwr_row_we[CGRA_ROWS -1 -row] # The opposite way around because its like a binary number where the last one is the least significant so RC0
        rc_asm = self.imem.get_instruction_asm(pc, srf_sel, selected_vwr, vwr_re, srf_we, alu_srf_write, row)
        print(self.__class__.__name__ + str(row) +": " + rc_asm + " --> ALU res = " + str(self.alu.newRes))
        
    def parseDestArith(self, rd, instr):
        # Define the regular expression pattern
        r_pattern = re.compile(r'^R(\d+)$')
        srf_pattern = re.compile(r'^SRF\((\d+)\)$')
        vwr_pattern = re.compile(r'^VWR_([A-Za-z])$')
        rout_pattern = re.compile(r'^ROUT$')

        # Check if the input matches the 'R' pattern
        r_match = r_pattern.match(rd)
        if r_match:
            ret = None
            try:
                ret = RC_DEST_REGS[rd]
            except:
                raise Exception("Instruction not valid for RC: " + instr + ". The accessed register must be betwwen 0 and " + str(RC_NUM_DREG -1) + ".")
            return ret, -1, -1
        
        # Check if the input matches the 'ROUT' pattern
        rout_match = rout_pattern.match(rd)
        if rout_match:
            return 4, -1, -1

        # Check if the input matches the 'SRF' pattern
        srf_match = srf_pattern.match(rd)
        if srf_match:
            return RC_DEST_REGS["SRF"], int(srf_match.group(1)), -1
        
        # Check if the input matches the 'VWR' pattern
        vwr_match = vwr_pattern.match(rd)
        if vwr_match:
            if vwr_match.group(1) == 'A':
                return RC_DEST_REGS["VWR"], -1, 0
            if vwr_match.group(1) == 'B':
                return RC_DEST_REGS["VWR"], -1, 1
            if vwr_match.group(1) == 'C':
                return RC_DEST_REGS["VWR"], -1, 2

        return None, -1, -1

    # Returns the value for muxA and the number of the srf accessed (-1 if it isn't accessed)
    def parseMuxArith(self, rs, instr):
        # Define the regular expression pattern
        r_pattern = re.compile(r'^R(\d+)$')
        srf_pattern = re.compile(r'^SRF\((\d+)\)$')
        vwr_pattern = re.compile(r'^VWR_([A-Za-z])$')
        zero_pattern = re.compile(r'^ZERO$')
        one_pattern = re.compile(r'^ONE$')
        maxInt_pattern = re.compile(r'^MAX_INT$')
        minInt_pattern = re.compile(r'^MIN_INT$')
        neigh_pattern = re.compile(r'^RC([A-Za-z])$')

        # Check if the input matches the 'R' pattern
        r_match = r_pattern.match(rs)
        if r_match:
            ret = None
            try:
                ret = RC_MUX_SEL[rs]
            except:
                raise Exception("Instruction not valid for RC: " + instr + ". The accessed register must be between 0 and " + str(RC_NUM_DREG -1) + ".")
            return ret, -1

        # Check if the input matches the 'SRF' pattern
        srf_match = srf_pattern.match(rs)
        if srf_match:
            i = srf_match.group(1)
            return RC_MUX_SEL["SRF"], int(srf_match.group(1))
        
        # Check if the input matches the 'VWR' pattern
        vwr_match = vwr_pattern.match(rs)
        if vwr_match:
            try:
                ret = RC_MUX_SEL[rs]
            except:
                raise Exception("Instruction not valid for RC: " + instr + ". The accessed VWR must be A, B or C.")
            return ret, -1
            
        # Check if the input matches the 'RCX' pattern
        neigh_match = neigh_pattern.match(rs)
        if neigh_match:
            ret = None
            try:
                ret = RC_MUX_SEL[rs]
            except:
                raise Exception("Instruction not valid for RC: " + instr + ". The accessed register is not a valid neighbour (RCT, RCB, RCR, RCL).")
            return ret, -1
        
        # Check if the input matches the 'ZERO' pattern
        zero_match = zero_pattern.match(rs)
        if zero_match:
            return RC_MUX_SEL[rs], -1

        # Check if the input matches the 'ONE' pattern
        one_match = one_pattern.match(rs)
        if one_match:
            return RC_MUX_SEL[rs], -1
        
        # Check if the input matches the 'MAX_INT' pattern
        maxInt_match = maxInt_pattern.match(rs)
        if maxInt_match:
            return RC_MUX_SEL[rs], -1
        
        # Check if the input matches the 'MIN_INT' pattern
        minInt_match = minInt_pattern.match(rs)
        if minInt_match:
            return RC_MUX_SEL[rs], -1

        return None, -1
    
    def parseFlag(self, flag, instr):
        ret = None
        try:
            ret = RC_MUXF_SEL[flag]
        except:
            raise Exception("Instruction not valid for RC: " + instr + ". The accessed ALU flags parameters is not valid (OWN, RCT, RCB, RCR, RCL).")

        return ret

    def asmToHex(self, instr):
        space_instr = instr.replace(",", " ")
        split_instr = [word for word in space_instr.split(" ") if word]
        try:
            op      = split_instr[0]
        except:
            op      = split_instr
        
        if op in self.rc_arith_ops:
            half_precision = 0
            if '.H' in op:
                half_precision = 1
                alu_op = RC_ALU_OPS[op[:-2]]
            elif '.FXP' in op:
                if op == "DIV.FXP":
                    raise Exception("Float point division not supported yet.")
                if op == "MUL.FXP":
                    alu_op = RC_ALU_OPS["FXP_MUL"]
            else:
                alu_op = RC_ALU_OPS[op]

            # Expect 3 or more operands: rd/srf, rs/srf/zero/one, rt/srf/zero/imm
            assert(len(split_instr) >= 3), "Instruction not valid for RC: " + instr + ". Expected at least 3 operands."

            # Control more than one destination
            rds = []
            for i in range(1, len(split_instr) - 2):
                rds.append(split_instr[i])
            rs = split_instr[len(split_instr) - 2]
            rt = split_instr[len(split_instr) - 1]

            dests = []
            srf_strs_idx = []
            vwr_strs = []
            for i in range(len(rds)):
                dest, aux_srf, vwr_str = self.parseDestArith(rds[i], instr)
                dests.append(dest)
                srf_strs_idx.append(aux_srf)
                vwr_strs.append(vwr_str)
            muxA, srf_read_index = self.parseMuxArith(rs, instr)
            muxB, srf_muxB_index = self.parseMuxArith(rt, instr)

            if srf_read_index >= SRF_N_REGS or srf_muxB_index >= SRF_N_REGS or any(x >= SRF_N_REGS for x in srf_strs_idx):
                raise Exception("Instruction not valid for RC: " + instr + ". The accessed SRF must be between 0 and " + str(SRF_N_REGS -1) + ".")

            srf_str_index = -1
            for x in srf_strs_idx:
                if x != -1 and srf_str_index != -1:
                    raise Exception("Instruction not valid for RC: " + instr + ". Expected at most one writes to the SRF.")
                elif x != -1:
                    srf_str_index = x

            vwr_str = -1
            for x in vwr_strs:
                if x != -1:
                    if vwr_str != -1 and x != vwr_str:
                        raise Exception("Instruction not valid for RC: " + instr + ". Expected at most one write to the VWR.")
                    else:
                        vwr_str = x

            if any(x == None for x in dests):
                raise Exception("Instruction not valid for RC: " + instr + ". Expected another format for the destination operand.")
            
            if muxA == None:
                raise Exception("Instruction not valid for RC: " + instr + ". Expected another format for muxA (" + rs +").")

            if muxB == None:
                raise Exception("Instruction not valid for RC: " + instr + ". Expected another format for muxB (" + rt +").")
            
            if srf_muxB_index != -1:
                if srf_read_index != -1 and srf_muxB_index != srf_read_index:
                    raise Exception("Instruction not valid for RC: " + instr + ". Expected only reads/writes to the same reg of the SRF.") 
                srf_read_index = srf_muxB_index
       
            # Check if writes to local regs
            rf_wsel = 0
            rf_we = 0
            last = -1
            for dest in dests:
                if dest <= 1:
                    if last != -1 and last != dest:
                        raise Exception("Instruction not valid for RC: " + instr + ". Expected writes to more than one local register.")
                    last = dest
                    rf_we = 1
                    rf_wsel = dest

            muxf_sel=RC_MUXF_SEL.OWN

            # Return read and write srf indexes and the flag to write on a vwr
            word = RC_IMEM_WORD(rf_wsel=rf_wsel, rf_we=rf_we, muxf_sel=muxf_sel, alu_op=alu_op, op_mode=half_precision, muxb_sel=muxB, muxa_sel=muxA)
            return srf_read_index, srf_str_index, vwr_str, word
        
        if op in self.rc_nop_ops:
            alu_op = RC_ALU_OPS[op]
            # Expect 0 operands
            if len(split_instr) > 1:
                raise Exception("Instruction not valid for RC: " + instr + ". Nop does not expect operands.")
            
            # Return read and write srf indexes
            word = RC_IMEM_WORD(alu_op=alu_op)
            return -1, -1, -1, word
        
        if op in self.rc_flag_ops:
            if op == "SFGA":
                alu_op = RC_ALU_OPS["INB_SF_INA"]
            if op == "ZFGA":
                alu_op = RC_ALU_OPS["INB_ZF_INA"]

            # Expect 2 or more operands: rd/srf, flag
            assert(len(split_instr) >= 2), "Instruction not valid for RC: " + instr + ". Expected at least 2 operands."

            # Control more than one destination
            rds = []
            for i in range(1, len(split_instr) - 1):
                rds.append(split_instr[i])
            flag = split_instr[len(split_instr) - 1]

            dests = []
            srf_strs_idx = []
            vwr_strs = []
            for i in range(len(rds)):
                dest, srf_str_index, vwr_str = self.parseDestArith(rds[i], instr)
                dests.append(dest)
                srf_strs_idx.append(srf_str_index)
                vwr_strs.append(vwr_str)

            muxf_sel = self.parseFlag(flag, instr)

            if any(x == None for x in dests):
                raise Exception("Instruction not valid for RC: " + instr + ". Expected another format for first operand (dest).")
            
            srf_str_index = -1
            for x in srf_strs_idx:
                if x != -1 and srf_str_index != -1:
                    raise Exception("Instruction not valid for RC: " + instr + ". Expected at most one writes to the SRF.")
                elif x != -1:
                    srf_str_index = x
            
            vwr_str = -1
            for x in vwr_strs:
                if x != -1 and vwr_str != -1:
                    raise Exception("Instruction not valid for RC: " + instr + ". Expected at most one write to the VWR.")
                elif x != -1:
                    vwr_str = x

            if muxf_sel == None:
                raise Exception("Instruction not valid for RC: " + instr + ". Expected another format for second operand (flag).")
            
            if any(x >= SRF_N_REGS for x in srf_strs_idx):
                raise Exception("Instruction not valid for RC: " + instr + ". The accessed SRF must be between 0 and " + str(SRF_N_REGS -1) + ".")

            for x in srf_strs_idx:
                if x != -1:
                    if srf_read_index == -1: 
                        srf_read_index = x
                    elif x != srf_read_index:
                        raise Exception("Instruction not valid for RC: " + instr + ". Expected only reads/writes to the same reg of the SRF.")

            # Check if writes to local regs
            rf_wsel = 0
            rf_we = 0
            last = -1
            for dest in dests:
                if dest < RC_NUM_DREG:
                    if last != -1 and last != dest:
                        raise Exception("Instruction not valid for RC: " + instr + ". Expected writes to more than one local register.")
                    last = dest
                    rf_we = 1
                    rf_wsel = dest

            # Return read and write srf indexes and the flag to write on a vwr
            word = RC_IMEM_WORD(rf_wsel=rf_wsel, rf_we=rf_we, muxf_sel=muxf_sel, alu_op=alu_op)
            return -1, srf_str_index, vwr_str, word
        
        raise Exception("Instruction not valid for RC: " + instr + ". Operation not recognised.")

    def hexToAsmRc(self, instr, srf_sel, selected_vwr, vwr_we, srf_we, srf_wd, row):
        return RC_IMEM_WORD(hex_word=instr).get_word_in_asm(srf_sel, selected_vwr, vwr_we, srf_we, srf_wd, row)