"""mxcu.py: Data structures and objects emulating the Multiplexer Control Unit of the VWR2A architecture"""
__author__      = "Lara Orlandic"
__email__       = "lara.orlandic@epfl.ch"

import numpy as np
from enum import Enum
from ctypes import c_int32
import re
from .alu import *

from .srf import SRF_N_REGS

# Local data register (DREG) sizes of specialized slots
MXCU_NUM_DREG = 8

# Configuration register (CREG) / instruction memory sizes of specialized slots
MXCU_NUM_CREG = 64

# Widths of instructions of each specialized slot in bits
MXCU_IMEM_WIDTH = 27

# MXCU IMEM word decoding
class MXCU_ALU_OPS(int, Enum):
    '''MXCU ALU operation codes'''
    NOP = 0
    SADD = 1
    SSUB = 2
    SLL = 3
    SRL = 4
    LAND = 5
    LOR = 6
    LXOR = 7

class MXCU_MUX_SEL(int, Enum):
    '''Input A to MXCU ALU'''
    R0 = 0
    R1 = 1
    R2 = 2
    R3 = 3
    R4 = 4
    R5 = 5
    R6 = 6
    R7 = 7
    SRF = 8
    ZERO = 9
    ONE = 10
    TWO = 11
    HALF = 12
    LAST = 13

class MXCU_DEST_REGS(int, Enum):
    '''Destination registers'''
    R0 = 0
    R1 = 1
    R2 = 2
    R3 = 3
    R4 = 4
    R5 = 5
    R6 = 6
    R7 = 7
    SRF = 8

class ALU_SRF_WRITE(int, Enum):
    '''Select which specialized slot's ALU output gets written to the chosen SRF register'''
    LCU = 0
    RC0 = 1
    MXCU = 2
    LSU = 3

class MXCU_VWR_SEL(int, Enum):
    '''Choose which VWR to write to'''
    VWR_A = 0
    VWR_B = 1
    VWR_C = 2
    
    
# MULTIPLEXER CONTROL UNIT (MXCU) #

class MXCU_IMEM:
    '''Instruction memory of the Multiplexer control unit'''
    def __init__(self):
        self.IMEM = np.zeros(MXCU_NUM_CREG,dtype="S{0}".format(MXCU_IMEM_WIDTH))
        # Initialize kernel memory with default word
        default_word = MXCU_IMEM_WORD()
        for i, instruction in enumerate(self.IMEM):
            self.IMEM[i] = default_word.get_word()
    
    def set_word(self, kmem_word, pos):
        '''Set the IMEM index at integer pos to the binary imem word'''
        self.IMEM[pos] = np.binary_repr(kmem_word,width=MXCU_IMEM_WIDTH)
    
    def set_params(self, vwr_row_we=[0,0,0,0], vwr_sel=MXCU_VWR_SEL.VWR_A, srf_sel=0, alu_srf_write=ALU_SRF_WRITE.LCU, srf_we=0, rf_wsel=0, rf_we=0, alu_op=MXCU_ALU_OPS.NOP, muxb_sel=MXCU_MUX_SEL.R0, muxa_sel=MXCU_MUX_SEL.R0, pos=0):
        '''Set the IMEM index at integer pos to the configuration parameters.
        See MXCU_IMEM_WORD initializer for implementation details.
        NOTE: vwr_row_we should be an 4-element array of bool/int values representing a one-hot vector of row write enable bits
        '''
        #Convert one-hot array of int/bool to binary
        imem_word = MXCU_IMEM_WORD(vwr_row_we=vwr_row_we, vwr_sel=vwr_sel, srf_sel=srf_sel, alu_srf_write=alu_srf_write, srf_we=srf_we, rf_wsel=rf_wsel, rf_we=rf_we, alu_op=alu_op, muxb_sel=muxb_sel, muxa_sel=muxa_sel)
        self.IMEM[pos] = imem_word.get_word()
    
    def get_instruction_asm(self, pos):
        '''Print the human-readable instructions of the instruction at position pos in the instruction memory'''
        imem_word = MXCU_IMEM_WORD()
        imem_word.set_word(self.IMEM[pos])
        mxcu_asm, selected_vwr, srf_sel, alu_srf_write, srf_we, vwr_row_we = imem_word.get_word_in_asm()
        return mxcu_asm, selected_vwr, srf_sel, alu_srf_write, srf_we, vwr_row_we

    def get_instr_pseudo_asm(self, pos):
        mxcu_asm, selected_vwr, srf_sel, alu_srf_write, srf_we, vwr_row_we = self.get_instruction_asm(pos)
        return mxcu_asm
        
    def get_word_in_hex(self, pos):
        '''Get the hexadecimal representation of the word at index pos in the MXCU config IMEM'''
        return(hex(int(self.IMEM[pos],2)))
        
    def get_instruction_info(self, pos):
        '''Print the human-readable instructions of the instruction at position pos in the instruction memory'''
        imem_word = MXCU_IMEM_WORD()
        imem_word.set_word(self.IMEM[pos])
        vwr_row_we, vwr_sel, srf_sel, alu_srf_write, srf_we, rf_wsel, rf_we, alu_op, muxb_sel, muxa_sel = imem_word.decode_word()
        for vwr in MXCU_VWR_SEL:
            if vwr.value == vwr_sel:
                selected_vwr = vwr.name
        
        indices_of_written_rows = np.where(vwr_row_we)[0]
        if len(indices_of_written_rows)>0:
            print("Writing to VWR rows {0} of {1}".format(indices_of_written_rows, selected_vwr))
        else:
            print("Not writing to VWRs")
        
        if srf_we == 1:
            for alu_res in ALU_SRF_WRITE:
                if alu_res.value == alu_srf_write:
                    spec_slot = alu_res.name
            print("Writing from {0} ALU to SRF register {1}".format(spec_slot, srf_sel))
        else:
            print("Reading from SRF index {0}".format(srf_sel))
        
        for op in MXCU_ALU_OPS:
            if op.value == alu_op:
                alu_opcode = op.name
        if muxa_sel > 13: # Duplicated
            muxa_sel = 9 # ZERO      
        for sel in MXCU_MUX_SEL:
            if sel.value == muxa_sel:
                muxa_res = sel.name
        if muxb_sel > 13: # Duplicated
            muxb_sel = 9 # ZERO
        for sel in MXCU_MUX_SEL:
            if sel.value == muxb_sel:
                muxb_res = sel.name
        if alu_opcode == MXCU_ALU_OPS.NOP:
            print("No ALU operation")
        else:
            print("Performing ALU operation {0} between operands {1} and {2}".format(alu_opcode, muxa_res, muxb_res))
        if rf_we == 1:
            print("Writing ALU result to MXCU register {0}".format(rf_wsel))
        else:
            print("No MXCU registers are being written")
        
class MXCU_IMEM_WORD:
    def __init__(self, hex_word=None, vwr_row_we=[0,0,0,0], vwr_sel=MXCU_VWR_SEL.VWR_A, srf_sel=0, alu_srf_write=ALU_SRF_WRITE.LCU, srf_we=0, rf_wsel=0, rf_we=0, alu_op=MXCU_ALU_OPS.NOP, muxb_sel=MXCU_MUX_SEL.R0, muxa_sel=MXCU_MUX_SEL.R0):
        '''Generate a binary mxcu instruction word from its configuration paramerers:
        
           -   vwr_row_we: One-hot encoded write enable to the 4 rows (also known as slices) of the VWR.
           -   vwr_sel: Select which VWR to write to (see MXCU_VWR_SEL for options)
           -   srf_sel: Select one of 8 SRF registers to read/write to
           -   alu_srf_write: Decide which specialized slot ALU result to write to selected SRF register (see ALU_SRF_WRITE enum)
           -   srf_we: Write enable to the SRF
           -   rf_wsel: Select one of 8 MXCU local registers to write to. Note that some registers have special jobs. See vwr2a_ISA doc.
           -   rf_we: Enable writing to local registers
           -   alu_op: Perform one of the ALU operations listed in the MXCU_ALU_OPS enum
           -   muxb_sel: Select input B to ALU (see MXCU_MUX_SEL enum for options)
           -   muxa_sel: Select input A to ALU (see MXCU_MUX_SEL enum for options)
        
        '''
        if hex_word == None:
            binary_vwr_row_we = ""
            for b in vwr_row_we:
                binary_vwr_row_we += (np.binary_repr(b))
            self.vwr_row_we = binary_vwr_row_we
            self.vwr_sel = np.binary_repr(vwr_sel,2)
            self.srf_sel = np.binary_repr(srf_sel,3)
            self.alu_srf_write = np.binary_repr(alu_srf_write,2)
            self.srf_we = np.binary_repr(srf_we, 1)
            self.rf_wsel = np.binary_repr(rf_wsel, width=3)
            self.rf_we = np.binary_repr(rf_we,width=1)
            self.alu_op = np.binary_repr(alu_op,3)
            self.muxb_sel = np.binary_repr(muxb_sel,4)
            self.muxa_sel = np.binary_repr(muxa_sel,4)
            self.word = "".join((self.muxa_sel, self.muxb_sel, self.alu_op, self.rf_we, self.rf_wsel, self.srf_we, self.alu_srf_write, self.srf_sel, self.vwr_sel, self.vwr_row_we))
        else:
            decimal_int = int(hex_word, 16)
            binary_number = bin(decimal_int)[2:]  # Removing the '0b' prefix
            # Extend binary number to LSU_IMEM_WIDTH bits
            extended_binary = binary_number.zfill(MXCU_IMEM_WIDTH)

            self.vwr_row_we = extended_binary[23:27] # 4 bitsa
            self.vwr_sel = extended_binary[21:23] # 2 bits
            self.srf_sel = extended_binary[18:21] # 3 bits
            self.alu_srf_write = extended_binary[16:18] # 2 bits
            self.srf_we = extended_binary[15:16] # 1 bit
            self.rf_wsel = extended_binary[12:15] # 3 bits
            self.rf_we = extended_binary[11:12] # 1 bit
            self.alu_op = extended_binary[8:11] # 3 bits
            self.muxb_sel = extended_binary[4:8] # 4 bits
            self.muxa_sel = extended_binary[:4] # 4 bits
            self.word = extended_binary

    def get_word(self):
        return self.word

    def get_word_in_hex(self):
        '''Get the hexadecimal representation of the word at index pos in the MXCU config IMEM'''
        return(hex(int(self.word, 2)))
    
    def get_word_in_asm(self):
        vwr_row_we, vwr_sel, srf_sel, alu_srf_write, srf_we, rf_wsel, rf_we, alu_op, muxb_sel, muxa_sel = self.decode_word()
        
        # Parse vwr selected
        for vwr in MXCU_VWR_SEL:
            if vwr.value == vwr_sel:
                selected_vwr = vwr.name

        # ALU
        for op in MXCU_ALU_OPS:
            if op.value == alu_op:
                alu_asm = op.name
        
        # Muxes
        if muxa_sel > 13: # Duplicated
            muxa_sel = 9 # ZERO
        for sel in MXCU_MUX_SEL:
            if sel.value == muxa_sel:
                muxa_asm = sel.name
        if muxa_asm == "SRF":
            muxa_asm = "SRF(" + str(srf_sel) + ")"
        
        if muxb_sel > 13: # Duplicated
            muxb_sel = 9 # ZERO
        for sel in MXCU_MUX_SEL:
            if sel.value == muxb_sel:
                muxb_asm = sel.name
        if muxb_asm == "SRF":
            muxb_asm = "SRF(" + str(srf_sel) + ")"

        # Destination
        dest = ""
        if rf_we == 1:
            for sel in MXCU_DEST_REGS:
                if sel.value == rf_wsel:
                    if dest != "":
                        dest += ", "
                    dest += sel.name
        
        if srf_we == 1 and alu_srf_write == 2: 
            if dest != "":
                dest += ", "
            dest += "SRF(" + str(srf_sel) + ")"

        mxcu_asm = alu_asm + " " + dest + ", " + muxa_asm + ", " + muxb_asm
        
        if alu_asm == "NOP":
            mxcu_asm = alu_asm
        
        return mxcu_asm, selected_vwr, srf_sel, alu_srf_write, srf_we, vwr_row_we
    
    def get_word_pseudo_asm(self):
        return self.get_word_in_asm()

    def set_word(self, word):
        '''Set the binary configuration word of the kernel memory'''
        self.word = word
        self.vwr_row_we = word[23:]
        self.vwr_sel = word[21:23]
        self.srf_sel = word[18:21]
        self.alu_srf_write = word[16:18]
        self.srf_we = word[15:16]
        self.rf_wsel = word[12:15]
        self.rf_we = word[11:12]
        self.alu_op = word[8:11]
        self.muxb_sel = word[4:8]
        self.muxa_sel = word[0:4]
        
    def decode_word(self):
        '''Get the configuration word parameters from the binary word'''

        vwr_sel = int(self.vwr_sel,2)
        srf_sel = int(self.srf_sel,2)
        alu_srf_write = int(self.alu_srf_write,2)
        srf_we = int(self.srf_we,2)
        rf_wsel = int(self.rf_wsel,2)
        rf_we = int(self.rf_we,2)
        alu_op = int(self.alu_op,2)
        muxb_sel = int(self.muxb_sel,2)
        muxa_sel = int(self.muxa_sel,2)
        
        # Return one-hot veectors as numpy arrays of integers or booleans
        one_hot_vwr_row_we = []
        for i in range(len(self.vwr_row_we)):
            one_hot_vwr_row_we.append(int(self.vwr_row_we[i:i+1],2))
        
        reverse = one_hot_vwr_row_we[::-1]
                
        return reverse, vwr_sel, srf_sel, alu_srf_write, srf_we, rf_wsel, rf_we, alu_op, muxb_sel, muxa_sel
    

class MXCU:
    mxcu_arith_ops   = { 'SADD', 'SSUB','SLL','SRL','LAND','LOR','LXOR' }
    mxcu_nop_ops     = { 'NOP' }

    def __init__(self):
        self.regs       = [0 for _ in range(MXCU_NUM_DREG)]
        self.imem       = MXCU_IMEM()
        self.nInstr     = 0
        self.default_word = MXCU_IMEM_WORD().get_word()
        self.alu = ALU()
    
    def getMuxValue(self, mux, vwr2a, col, srf_sel):
        if mux <= 7 : # Rx
            muxValue = self.regs[mux]
        elif mux == 8: # SRF
            muxValue = vwr2a.srfs[col].regs[srf_sel]
        elif mux == 9: # ZERO
            muxValue = 0
        elif mux == 10: # ONE
            muxValue = 1
        elif mux == 11: # TWO
            muxValue = 2
        elif mux == 12: # HALF
            muxValue = int(SPM_NWORDS/CGRA_ROWS/2) -1 # 128/4/2 -1 = 15 (half index)
        elif mux == 13: # LAST
            muxValue = int(SPM_NWORDS/CGRA_ROWS) -1 # 128/4 -1 = 31 (last index)
        else:
            raise Exception(self.__class__.__name__ + ": Mux value not recognized")
        return muxValue
    
    def runAlu(self, alu_op, muxa_val, muxb_val):
        if alu_op == 0: # NOP
            self.alu.nop()
        elif alu_op == 1: # SADD
            self.alu.sadd(muxa_val, muxb_val)
        elif alu_op == 2: # SSUB
            self.alu.ssub(muxa_val, muxb_val)
        elif alu_op == 3: # SLL
            self.alu.sll(muxa_val, muxb_val)
        elif alu_op == 4: # SRL
            self.alu.srl(muxa_val, muxb_val)
        elif alu_op == 5: # LAND
            self.alu.land(muxa_val, muxb_val)
        elif alu_op == 6: # LOR
            self.alu.lor(muxa_val, muxb_val)
        elif alu_op == 7: # LXOR
            self.alu.lxor(muxa_val, muxb_val)
        else:
            raise Exception(self.__class__.__name__ + ": ALU op not recognized")

        
    def run(self, pc, vwr2a, col):
        # This MXCU instruction
        mxcu_hex = self.imem.get_word_in_hex(pc)
        one_hot_vwr_row_we, vwr_sel, srf_sel, alu_srf_write, srf_we, rf_wsel, rf_we, alu_op, muxb_sel, muxa_sel = MXCU_IMEM_WORD(hex_word=mxcu_hex).decode_word()
        # Get muxes value
        muxa_val = self.getMuxValue(muxa_sel, vwr2a, col, srf_sel)
        muxb_val = self.getMuxValue(muxb_sel, vwr2a, col, srf_sel)
        # ALU op
        self.runAlu(alu_op, muxa_val, muxb_val)
        # SRF store control
        if alu_srf_write == 0: # LCU
            srf_data = vwr2a.lcus[col].alu.newRes
        elif alu_srf_write == 1: # RC0
            srf_data = vwr2a.rcs[col][0].alu.newRes
        elif alu_srf_write == 2: # MXCU
            srf_data = vwr2a.mscus[col].alu.newRes
        else: # LSU
            srf_data = vwr2a.lsus[col].alu.newRes
        if srf_we == 1:
            vwr2a.srfs[col].regs[srf_sel] = srf_data
        # VWR store control
        vwr_dest = vwr2a.vwrs[col][vwr_sel]
        mxcu_r0 = vwr2a.mxcus[col].regs[0] # VWR_IDX
        mxcu_mask = vwr2a.mxcus[col].regs[5+vwr_sel] # R5, 6 or 7 for VWR_A, B or C
        slice_idx = mxcu_r0 & mxcu_mask
        slice_size = int(SPM_NWORDS/CGRA_ROWS)
        for row in range(CGRA_ROWS):
            if one_hot_vwr_row_we[row] == 1:
                vwr_idx = slice_idx + slice_size*row
                vwr_dest.values[vwr_idx] = vwr2a.rcs[col][row].alu.newRes

        # Write result locally
        if rf_we == 1:
            self.regs[rf_wsel] = self.alu.newRes
        
        # ---------- Print something -----------
        mxcu_asm, selected_vwr, srf_sel, alu_srf_write, srf_we, vwr_row_we = self.imem.get_instruction_asm(pc)
        if srf_we == 0:
            write_srf = "not writting SRF"
        else:
            for op in ALU_SRF_WRITE:
                if op.value == alu_srf_write:
                    dest = op.name
            write_srf = "writting SRF(" + str(srf_sel) + ") from " + dest
        print(self.__class__.__name__ + ": " + mxcu_asm + " (VWR selected: " + str(vwr_sel) + ", " + write_srf + ") --> ALU res = " + str(self.alu.newRes))

    def parseDestArith(self, rd, instr):
        # Define the regular expression pattern
        r_pattern = re.compile(r'^R(\d+)$')
        srf_pattern = re.compile(r'^SRF\((\d+)\)$')

        # Check if the input matches the 'R' pattern
        r_match = r_pattern.match(rd)
        if r_match:
            ret = None
            try:
                ret = MXCU_DEST_REGS[rd]
            except:
                raise ValueError("Instruction not valid for MXCU: " + instr + ". The accessed register must be betwwen 0 and " + str(len(self.regs) -1) + ".")
            return ret, -1

        # Check if the input matches the 'SRF' pattern
        srf_match = srf_pattern.match(rd)
        if srf_match:
            return MXCU_DEST_REGS["SRF"], int(srf_match.group(1))

        return None, -1

    def parseMuxArith(self, rs, instr):
        # Define the regular expression pattern
        r_pattern = re.compile(r'^R(\d+)$')
        srf_pattern = re.compile(r'^SRF\((\d+)\)$')
        zero_pattern = re.compile(r'^ZERO$')
        one_pattern = re.compile(r'^ONE$')
        two_pattern = re.compile(r'^TWO$')
        half_pattern = re.compile(r'^HALF$')
        last_pattern = re.compile(r'^LAST$')

        # Check if the input matches the 'R' pattern
        r_match = r_pattern.match(rs)
        if r_match:
            ret = None
            try:
                ret = MXCU_MUX_SEL[rs]
            except:
                raise ValueError("Instruction not valid for MXCU: " + instr + ". The accessed register must be betwwen 0 and " + str(MXCU_NUM_DREG -1) + ".")
            return ret, -1

        # Check if the input matches the 'SRF' pattern
        srf_match = srf_pattern.match(rs)
        if srf_match:
            return MXCU_MUX_SEL["SRF"], int(srf_match.group(1))
        
        # Check if the input matches the 'ZERO' pattern
        zero_match = zero_pattern.match(rs)
        if zero_match:
            return MXCU_MUX_SEL[rs], -1
        
        # Check if the input matches the 'ONE' pattern
        one_match = one_pattern.match(rs)
        if one_match:
            return MXCU_MUX_SEL[rs], -1
        
        # Check if the input matches the 'TWO' pattern
        two_match = two_pattern.match(rs)
        if two_match:
            return MXCU_MUX_SEL[rs], -1
        
        # Check if the input matches the 'HALF' pattern
        half_match = half_pattern.match(rs)
        if half_match:
            return MXCU_MUX_SEL[rs], -1
        
        # Check if the input matches the 'LAST' pattern
        last_match = last_pattern.match(rs)
        if last_match:
            return MXCU_MUX_SEL[rs], -1

        return None, -1
    
    def asmToHex(self, instr, srf_sel, srf_we, alu_srf_write, vwr_row_we, vwr_sel):
        # Set default value for params
        rf_wsel=0
        rf_we=0
        alu_op=MXCU_ALU_OPS.NOP
        muxA=MXCU_MUX_SEL.R0
        muxB=MXCU_MUX_SEL.R0

        # Parse the MXCU instruction
        space_instr = instr.replace(",", " ")
        split_instr = [word for word in space_instr.split(" ") if word]
        try:
            op      = split_instr[0]
        except:
            op      = split_instr
        
        if op not in self.mxcu_arith_ops and op not in self.mxcu_nop_ops:
            raise ValueError("Instruction not valid for MXCU: " + instr + ". Operation not recognised.")

        if op in self.mxcu_arith_ops:
            alu_op = MXCU_ALU_OPS[op]
            # Expect 3 or more operands
            assert(len(split_instr) >= 3), "Instruction not valid for MXCU: " + instr + ". Expected at least 3 operands."

            # Control more than one destination
            rds = []
            for i in range(1, len(split_instr) - 2):
                rds.append(split_instr[i])
            rs = split_instr[len(split_instr) - 2]
            rt = split_instr[len(split_instr) - 1]

            dests = []
            srf_strs_idx = []
            for i in range(len(rds)):
                dest, aux_srf = self.parseDestArith(rds[i], instr)
                dests.append(dest)
                srf_strs_idx.append(aux_srf)
            muxA, srf_read_index = self.parseMuxArith(rs, instr)
            muxB, srf_muxB_index = self.parseMuxArith(rt, instr)


            if srf_read_index > SRF_N_REGS or srf_muxB_index > SRF_N_REGS or any(x >= SRF_N_REGS for x in srf_strs_idx):
                raise ValueError("Instruction not valid for MXCU: " + instr + ". The accessed SRF must be between 0 and " + str(SRF_N_REGS -1) + ".")

            if any(x == None for x in dests):
                raise ValueError("Instruction not valid for MXCU: " + instr + ". Expected another format for first operand (dest).")
            
            srf_str_index = -1
            for x in srf_strs_idx:
                if x != -1 and srf_str_index != -1:
                    raise Exception("Instruction not valid for RC: " + instr + ". Expected at most one writes to the SRF.")
                elif x != -1:
                    srf_str_index = x

            if muxB == None:
                raise ValueError("Instruction not valid for MXCU: " + instr + ". Expected another format for the second operand (muxB).")

            if muxA == None:
                raise ValueError("Instruction not valid for MXCU: " + instr + ". Expected another format for the third operand (muxA).")
            
            if srf_muxB_index != -1:
                if srf_read_index != -1 and srf_muxB_index != srf_read_index:
                    raise ValueError("Instruction not valid for MXCU: " + instr + ". Expected only reads/writes to the same reg of the SRF.") 
                srf_read_index = srf_muxB_index

            if srf_str_index != -1 and srf_read_index != -1 and srf_str_index != srf_read_index:
                raise ValueError("Instruction not valid for MXCU: " + instr + ". Expected only reads/writes to the same reg of the SRF.")

            # Check if writes to local regs
            rf_wsel = 0
            rf_we = 0
            last = -1
            for dest in dests:
                if dest < MXCU_NUM_DREG:
                    if last != -1 and last != dest:
                        raise Exception("Instruction not valid for RC: " + instr + ". Received writes to more than one local register.")
                    last = dest
                    rf_we = 1
                    rf_wsel = dest

            if srf_str_index != -1:
                # Check that MXCU is the only one trying to write to SRF
                if srf_we != 0:
                    raise ValueError("Instructions not valid for this cycle of the CGRA. Detected multiple writes to the SRF.")
                srf_we = 1
                # TODO: Check that the srf_sel is correct because it needs to be checked for writes and reads on the mxcu and the rest
                alu_srf_write = ALU_SRF_WRITE["MXCU"]
            
            if srf_sel != -1 and srf_str_index != -1 and srf_sel != srf_str_index:
                raise ValueError("Instruction not valid for the CGRA. Expected only writes to the same reg of the SRF.")
            if srf_sel != -1 and srf_read_index != -1 and srf_sel != srf_read_index: 
                raise ValueError("Instruction not valid for the CGRA. Expected only reads to the same reg of the SRF.")
            
            if srf_sel == -1:
                if srf_str_index != -1:
                    srf_sel = srf_str_index
                else:
                    srf_sel = srf_read_index
            
        if op in self.mxcu_nop_ops:
            alu_op = MXCU_ALU_OPS[op]
            # Expect 0 operands
            if len(split_instr) > 1:
                raise ValueError("Instruction not valid for MXCU: " + instr + ". Nop does not expect operands.")
        
        # If after everything no one writes, the value should be 0
        if srf_sel == -1:
            srf_sel = 0
        
        word = MXCU_IMEM_WORD(vwr_row_we=vwr_row_we, vwr_sel=vwr_sel, srf_sel=srf_sel, alu_srf_write=alu_srf_write, srf_we=srf_we, rf_wsel=rf_wsel, rf_we=rf_we, alu_op=alu_op, muxb_sel=muxB, muxa_sel=muxA)
        return word
        
    def hexToAsm(self, instr):
        mxcu_asm, selected_vwr, srf_sel, alu_srf_write, srf_we = MXCU_IMEM_WORD(hex_word=instr).get_word_in_asm()
        return mxcu_asm

    def hexToAsmPlus(self, instr):
        mxcu_asm, selected_vwr, srf_sel, alu_srf_write, srf_we, vwr_row_we = MXCU_IMEM_WORD(hex_word=instr).get_word_in_asm()
        return mxcu_asm, selected_vwr, srf_sel, alu_srf_write, srf_we, vwr_row_we
