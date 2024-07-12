"""lcu.py: Data structures and objects emulating the Loop Control Unit of the VWR2A architecture"""
__author__      = "Lara Orlandic"
__email__       = "lara.orlandic@epfl.ch"

import numpy as np
from enum import Enum
from ctypes import c_int32
import re
from .alu import *
from .srf import SRF_N_REGS

# Local data register (DREG) sizes of specialized slots
LCU_NUM_DREG = 4 

# Configuration register (CREG) / instruction memory sizes of specialized slots
LCU_NUM_CREG = 64

# Widths of instructions of each specialized slot in bits
LCU_IMEM_WIDTH = 20

# LCU IMEM word decoding
class LCU_ALU_OPS(int, Enum):
    '''LCU ALU operation codes'''
    NOP = 0
    SADD = 1
    SSUB = 2
    SLL = 3
    SRL = 4
    SRA = 5
    LAND = 6
    LOR = 7
    LXOR = 8
    BEQ = 9
    BNE = 10
    BGEPD = 11
    BLT = 12
    JUMP = 13
    EXIT = 14

class LCU_DEST_REGS(int, Enum):
    '''Available ALU registers to store ALU result'''
    R0 = 0
    R1 = 1
    R2 = 2
    R3 = 3
    SRF = 4

class LCU_MUXA_SEL(int, Enum):
    '''Input A to LCU ALU'''
    R0 = 0
    R1 = 1
    R2 = 2
    R3 = 3
    SRF = 4
    LAST = 5
    ZERO = 6
    IMM = 7

class LCU_MUXB_SEL(int, Enum):
    '''Input B to LCU ALU'''
    R0 = 0
    R1 = 1
    R2 = 2
    R3 = 3
    SRF = 4
    LAST = 5
    ZERO = 6
    ONE = 7
    
# LOOP CONTROL UNIT (LCU) #

class LCU_IMEM:
    '''Instruction memory of the Loop Control Unit'''
    def __init__(self):
        self.IMEM = np.zeros(LCU_NUM_CREG,dtype="S{0}".format(LCU_IMEM_WIDTH))
        # Initialize memory with default instruction
        default_word = LCU_IMEM_WORD()
        for i in range(LCU_NUM_CREG):
            self.IMEM[i] = default_word.get_word()
    
    def set_word(self, kmem_word, pos):
        '''Set the IMEM index at integer pos to the binary imem word'''
        self.IMEM[pos] = np.binary_repr(kmem_word,width=LCU_IMEM_WIDTH)
    
    def set_params(self, imm=0, rf_wsel=0, rf_we=0, alu_op=LCU_ALU_OPS.NOP, br_mode=0, muxb_sel=LCU_MUXB_SEL.R0, muxa_sel=LCU_MUXA_SEL.R0, pos=0):
        '''Set the IMEM index at integer pos to the configuration parameters.
        See LCU_IMEM_WORD initializer for implementation details.
        '''
        imem_word = LCU_IMEM_WORD(imm=imm, rf_wsel=rf_wsel, rf_we=rf_we, alu_op=alu_op, br_mode=br_mode, muxb_sel=muxb_sel, muxa_sel=muxa_sel)
        self.IMEM[pos] = imem_word.get_word()
    
    def get_instruction_asm(self, pos, srf_sel, srf_we, alu_srf_write):
        '''Print the human-readable instructions of the instruction at position pos in the instruction memory'''
        imem_word = LCU_IMEM_WORD()
        imem_word.set_word(self.IMEM[pos])
        return imem_word.get_word_in_asm(srf_sel, srf_we, alu_srf_write)
    
    def get_instr_pseudo_asm(self, pos):
        imem_word = LCU_IMEM_WORD()
        imem_word.set_word(self.IMEM[pos])
        return imem_word.get_word_pseudo_asm()
    
    def get_instruction_info(self, pos):
        '''Print the human-readable instructions of the instruction at position pos in the instruction memory'''
        imem_word = LCU_IMEM_WORD()
        imem_word.set_word(self.IMEM[pos])
        imm, rf_wsel, rf_we, alu_op, br_mode, muxb_sel, muxa_sel = imem_word.decode_word()
        
        print("Immediate value: {0}".format(imm))
        
        if br_mode == 1:
            print ("LCU is in RC data control mode")
        else: 
            print ("LCU is in loop control mode")

        if alu_op == 15: # Duplicated
            alu_op = 0 # NOP
        for op in LCU_ALU_OPS:
            if op.value == alu_op:
                alu_opcode = op.name
        for sel in LCU_MUXA_SEL:
            if sel.value == muxa_sel:
                muxa_res = sel.name
        for sel in LCU_MUXB_SEL:
            if sel.value == muxb_sel:
                muxb_res = sel.name
        if alu_op == 0: #NOP
            print("No LCU ALU Operation is performed")
        elif alu_op == 9: #BEQ
            print("If {0} and {1} are equal, branch to the immediate value {2}".format(muxa_res, muxb_res, imm))
        elif alu_op == 10: #BNE
            print("If {0} and {1} are NOT equal, branch to the immediate value {2}".format(muxa_res, muxb_res, imm))
        elif alu_op == 11: #BGEPD
            print("If {0}-1 is greater than or equal to {1}, branch to the immediate value {2}".format(muxa_res, muxb_res, imm))
        elif alu_op == 12: #BLT
            print("If {0} is less than {1}, branch to the immediate value {2}".format(muxa_res, muxb_res, imm))
        elif alu_op == 13: #JUMP
            print("Jump to address {0} + {1}".format(muxa_res, muxb_res))
        elif alu_op == 14: #EXIT
            print("Exiting out of kernel")
        else:
            print("Performing ALU operation {0} between operands {1} and {2}".format(alu_opcode, muxa_res, muxb_res))
        
        if rf_we == 1:
            print("Writing ALU result to LCU register {0}".format(rf_wsel))
        else:
            print("No LCU registers are being written")
            
    def get_word_in_hex(self, pos):
        '''Get the hexadecimal representation of the word at index pos in the LCU config IMEM'''
        return(hex(int(self.IMEM[pos],2)))
        
    
        
class LCU_IMEM_WORD:      

    def __init__(self, hex_word=None, imm=0, rf_wsel=0, rf_we=0, alu_op=LCU_ALU_OPS.NOP, br_mode=0, muxb_sel=LCU_MUXB_SEL.R0, muxa_sel=LCU_MUXA_SEL.R0):
        '''Generate a binary lcu instruction word from its configuration paramerers or from a given hex word:
        
           -   imm: Immediate value to use for ALU operations or address to branch to
           -   rf_wsel: Select one of four LCU registers to write to
           -   rf_we: Enable writing to aforementioned register
           -   alu_op: Perform one of the ALU operations listed in the LCU_ALU_OPS enum
           -   br_mode: Control program counter (0) or RC datapath (1)
           -   muxb_sel: Select input B to ALU (see LCU_MUXB_SEL enum for options)
           -   muxa_sel: Select input A to ALU (see LCU_MUXA_SEL enum for options)
        
        '''
        if hex_word == None:
            self.imm = np.binary_repr(imm, width=6)
            self.rf_wsel = np.binary_repr(rf_wsel, width=2)
            self.rf_we = np.binary_repr(rf_we,width=1)
            self.alu_op = np.binary_repr(alu_op,4)
            self.br_mode = np.binary_repr(br_mode,1)
            self.muxb_sel = np.binary_repr(muxb_sel,3)
            self.muxa_sel = np.binary_repr(muxa_sel,3)
            self.word = "".join((self.muxa_sel,self.muxb_sel,self.br_mode,self.alu_op,self.rf_we,self.rf_wsel,self.imm))
        else:
            decimal_int = int(hex_word, 16)
            binary_number = bin(decimal_int)[2:]  # Removing the '0b' prefix
            # Extend binary number to LCU_IMEM_WIDTH bits
            extended_binary = binary_number.zfill(LCU_IMEM_WIDTH)

            self.imm = extended_binary[14:20] # 6 bits
            self.rf_wsel = extended_binary[12:14] # 2 bits
            self.rf_we = extended_binary[11:12] # 1 bit
            self.alu_op = extended_binary[7:11] # 4 bits
            self.br_mode = extended_binary[6:7] # 1 bit
            self.muxb_sel = extended_binary[3:6] # 3 bits
            self.muxa_sel = extended_binary[:3] # 3 bits
            self.word = extended_binary
    
    def get_word(self):
        return self.word      
        
    def get_word_in_hex(self):
        '''Get the hexadecimal representation of the word at index pos in the LCU config IMEM'''
        return(hex(int(self.word, 2)))
    
    def get_word_in_asm(self, srf_sel, srf_we, alu_srf_write):
        imm, rf_wsel, rf_we, alu_op, br_mode, muxb_sel, muxa_sel = self.decode_word()
                
        # ALU op
        if alu_op == 15: # Duplicated
            alu_op = 0 # NOP
        for op in LCU_ALU_OPS:
            if op.value == alu_op:
                alu_asm = op.name

        # Branch mode
        if br_mode == 1:
            return alu_asm + "R " + str(imm)

        # NOP or EXIT
        if alu_asm in {"NOP", "EXIT"}:
            return alu_asm

        # Muxb
        muxb_asm = ""
        for sel in LCU_MUXB_SEL:
            if sel.value == muxb_sel:
                muxb_asm = sel.name
        assert(muxb_asm != ""), self.__class__.__name__ + ": MuxB opcode not found. Incorrect instruction parsing to asm."
        
        if muxb_asm == "SRF":
            muxb_asm = "SRF(" + str(srf_sel) + ")"

        # Muxa
        muxa_asm = ""
        for sel in LCU_MUXA_SEL:
            if sel.value == muxa_sel:
                muxa_asm = sel.name
        assert(muxa_asm != ""), self.__class__.__name__ + ": MuxA opcode not found. Incorrect instruction parsing to asm."
        
        if muxa_asm == "IMM":
            muxa_asm = str(imm)
        
        if muxa_asm == "SRF":
            muxa_asm = "SRF(" + str(srf_sel) + ")"

        # Dest
        if alu_asm == "BGEPD":
            dest = ""
            if rf_we == 1:
                for sel in LCU_DEST_REGS:
                    if sel.value == rf_wsel and muxa_asm != sel.name:
                        if dest != "":
                            dest += ", "
                        dest += sel.name
            
            if srf_we == 1 and alu_srf_write == 0 and muxa_asm != "SRF(" + str(srf_sel) + ")": 
                if dest != "":
                    dest += ", "
                dest += "SRF(" + str(srf_sel) + ")"
        else:
            dest = ""
            if rf_we == 1:
                for sel in LCU_DEST_REGS:
                    if sel.value == rf_wsel:
                        if dest != "":
                            dest += ", "
                        dest += sel.name
            
            if srf_we == 1 and alu_srf_write == 0: 
                if dest != "":
                    dest += ", "
                dest += "SRF(" + str(srf_sel) + ")"
        
        if dest != "":
            asm_word = alu_asm + " " + dest + ", " + muxa_asm + ", " + muxb_asm
        else:
            asm_word = alu_asm + " " + muxa_asm + ", " + muxb_asm

        # If branches (except JUMP)
        if alu_asm in {"BEQ", "BNE", "BLT", "BGEPD"}:
            asm_word += ", " + str(imm)
        
        return asm_word
    
    def get_word_pseudo_asm(self):
        asm = self.get_word_in_asm(0,0,0)
        # Replace SRF number
        asm = re.sub(r'SRF\(\d+\)', 'SRF(X)', asm)
        return asm
    
    def set_word(self, word):
        '''Set the binary configuration word of the kernel memory'''
        self.word = word
        self.imm = word[14:]
        self.rf_wsel = word[12:14]
        self.rf_we = word[11:12]
        self.alu_op = word[7:11]
        self.br_mode = word[6:7]
        self.muxb_sel = word[3:6]
        self.muxa_sel = word[0:3]
        
    def decode_word(self):
        '''Get the configuration word parameters from the binary word'''
        imm = int(self.imm,2)
        rf_wsel = int(self.rf_wsel,2)
        rf_we = int(self.rf_we,2)
        alu_op = int(self.alu_op,2)
        br_mode = int(self.br_mode,2)
        muxb_sel = int(self.muxb_sel,2)
        muxa_sel = int(self.muxa_sel,2)
        
        return imm, rf_wsel, rf_we, alu_op, br_mode, muxb_sel, muxa_sel


class LCU:
    lcu_arith_ops   = { 'SADD','SSUB','SLL','SRL','SRA','LAND','LOR','LXOR' }
    lcu_rcmode_ops  = { 'BEQR','BNER','BLTR','BGER' }
    lcu_branch_ops  = { 'BEQ','BNE','BLT' }
    lcu_bgepd_ops  = { 'BGEPD' }
    lcu_jump_ops    = { 'JUMP' }
    lcu_nop_ops     = { 'NOP' }
    lcu_exit_ops    = { 'EXIT' }
    
    def __init__(self):
        self.regs       = [0 for _ in range(LCU_NUM_DREG)]
        self.imem       = LCU_IMEM()
        self.nInstr     = 0
        self.default_word = LCU_IMEM_WORD().get_word()
        self.iregs = [self.default_word in range(LCU_NUM_CREG)]
        self.alu = ALU()
        self.exit = 0
        self.branch = 0
        self.branch_pc = 0

    def getMuxValue(self, mux, vwr2a, col, srf_sel, imm, muxA, bgepd):
        if mux <= 3 : # Rx
            muxValue = self.regs[mux]
            if bgepd and muxA:
                muxValue -= 1
        elif mux == 4: # SRF
            muxValue = vwr2a.srfs[col].regs[srf_sel]
            if bgepd and muxA:
                muxValue -= 1
        elif mux == 5: # LAST
            muxValue = int(SPM_NWORDS/CGRA_ROWS) -1 # 128/4 -1 = 31 (last index)
            if bgepd and muxA:
                muxValue -= 1
        elif mux == 6: # ZERO
            muxValue = 0
            if bgepd and muxA:
                muxValue -= 1
        elif mux == 7: # IMM or ONE
            if muxA:
                muxValue = imm
                if bgepd:
                    muxValue -= 1                    
            else:
                muxValue = 1
        else:
            raise Exception(self.__class__.__name__ + ": Mux value not recognized")
        return muxValue
    
    def runAlu(self, alu_op, muxa_val, muxb_val, imm, br_mode, vwr2a, col):
        self.branch = 0
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
        elif alu_op == 5: # SRA
            self.alu.sra(muxa_val, muxb_val)
        elif alu_op == 6: # LAND
            self.alu.land(muxa_val, muxb_val)
        elif alu_op == 7: # LOR
            self.alu.lor(muxa_val, muxb_val)
        elif alu_op == 8: # LXOR
            self.alu.lxor(muxa_val, muxb_val)
        elif alu_op >= 9 and alu_op <= 12: # Conditional branches
            if br_mode == 0:
                self.alu.ssub(muxa_val, muxb_val)
                equal = 0
                greater = 0
                if self.alu.newRes == 0:
                    equal = 1
                if self.alu.newRes > 0: 
                    greater = 1 
            else: # Get the flags from the rcs # TODO: check that this is true
                equal = 0
                greater = 0
                for row in range(CGRA_ROWS):
                    if vwr2a.rcs[col][row].alu.newRes == 0:
                        equal = 1
                    if vwr2a.rcs[col][row].alu.newRes > 0: 
                        greater = 1 
            if alu_op == 9 and equal: # BEQ
                self.branch = 1
                self.branch_pc = imm
            if alu_op == 10 and not equal: # BNE
                self.branch = 1
                self.branch_pc = imm
            if alu_op == 11 and (greater or equal): # BGEPD
                self.branch = 1
                self.branch_pc = imm
                self.alu.ssub(muxa_val, 0) # The ALU result is the decrement that it is already in muxA
            if alu_op == 12 and not (greater or equal): # BLT
                self.branch = 1
                self.branch_pc = imm
        elif alu_op == 13: # JUMP
            self.branch = 1
            self.branch_pc = muxb_val + muxa_val
        elif alu_op == 14: # EXIT
            self.exit = 1
        else:
            raise Exception(self.__class__.__name__ + ": ALU op not recognized")

    def run(self, pc, vwr2a, col):
        # MXCU info
        mxcu_asm, selected_vwr, srf_sel, alu_srf_write, srf_we, vwr_row_we = vwr2a.mxcus[col].imem.get_instruction_asm(pc)
        # This LCU instruction
        lcu_hex = self.imem.get_word_in_hex(pc)
        imm, rf_wsel, rf_we, alu_op, br_mode, muxb_sel, muxa_sel = LCU_IMEM_WORD(hex_word=lcu_hex).decode_word()
        # Get muxes value
        bgepd = False # Especial case BGEPD
        if alu_op == 11:
            bgepd = True
        muxa_val = self.getMuxValue(muxa_sel, vwr2a, col, srf_sel, imm, True, bgepd)
        muxb_val = self.getMuxValue(muxb_sel, vwr2a, col, srf_sel, imm, False, bgepd)
        # ALU op
        self.runAlu(alu_op, muxa_val, muxb_val, imm, br_mode, vwr2a, col)

        # Write result locally
        if rf_we == 1:
            self.regs[rf_wsel] = self.alu.newRes
        
        # ---------- Print something -----------
        print(self.__class__.__name__ + ": " + self.imem.get_instruction_asm(pc, srf_sel, srf_we, alu_srf_write) + " --> ALU res = " + str(self.alu.newRes))

    def parseDestArith(self, rd, instr):
        # Define the regular expression pattern
        r_pattern = re.compile(r'^R(\d+)$')
        srf_pattern = re.compile(r'^SRF\((\d+)\)$')

        # Check if the input matches the 'R' pattern
        r_match = r_pattern.match(rd)
        if r_match:
            ret = None
            try:
                ret = LCU_DEST_REGS[rd]
            except:
                raise ValueError("Instruction not valid for LCU: " + instr + ". The accessed register must be betwwen 0 and " + str(len(self.regs) -1) + ".")
            return ret, -1


        # Check if the input matches the 'SRF' pattern
        srf_match = srf_pattern.match(rd)
        if srf_match:
            return LCU_DEST_REGS["SRF"], int(srf_match.group(1))

        return None, -1

    # Returns the value for muxA and the number of the srf accessed (-1 if it isn't accessed)
    def parseMuxAArith(self, rs, instr):
        # Define the regular expression pattern
        r_pattern = re.compile(r'^R(\d+)$')
        srf_pattern = re.compile(r'^SRF\((\d+)\)$')
        zero_pattern = re.compile(r'^ZERO$')
        last_pattern = re.compile(r'^LAST$')

        # Check if the input matches the 'R' pattern
        r_match = r_pattern.match(rs)
        if r_match:
            ret = None
            try:
                ret = LCU_MUXA_SEL[rs]
            except:
                raise ValueError("Instruction not valid for LCU: " + instr + ". The accessed register must be betwwen 0 and " + str(len(self.regs) -1) + ".")
            return ret, -1

        # Check if the input matches the 'SRF' pattern
        srf_match = srf_pattern.match(rs)
        if srf_match:
            i = srf_match.group(1)
            return LCU_MUXA_SEL["SRF"], int(srf_match.group(1))
        
        # Check if the input matches the 'ZERO' pattern
        zero_match = zero_pattern.match(rs)
        if zero_match:
            return LCU_MUXA_SEL[rs], -1

        # Check if the input matches the 'LAST' pattern
        last_match = last_pattern.match(rs)
        if last_match:
            return LCU_MUXA_SEL[rs], -1

        return None, -1

    def parseMuxBArith(self, rs, instr):
        # Define the regular expression pattern
        r_pattern = re.compile(r'^R(\d+)$')
        srf_pattern = re.compile(r'^SRF\((\d+)\)$')
        zero_pattern = re.compile(r'^ZERO$')
        last_pattern = re.compile(r'^LAST$')
        one_pattern = re.compile(r'^ONE$')

        # Check if the input matches the 'R' pattern
        r_match = r_pattern.match(rs)
        if r_match:
            ret = None
            try:
                ret = LCU_MUXB_SEL[rs]
            except:
                raise ValueError("Instruction not valid for LCU: " + instr + ". The accessed register must be betwwen 0 and " + str(len(self.regs) -1) + ".")
            return ret, -1

        # Check if the input matches the 'SRF' pattern
        srf_match = srf_pattern.match(rs)
        if srf_match:
            return LCU_MUXB_SEL["SRF"], int(srf_match.group(1))
        
        # Check if the input matches the 'ZERO' pattern
        zero_match = zero_pattern.match(rs)
        if zero_match:
            return LCU_MUXB_SEL[rs], -1

        # Check if the input matches the 'LAST' pattern
        last_match = last_pattern.match(rs)
        if last_match:
            return LCU_MUXB_SEL[rs], -1
        
        # Check if the input matches the 'ONE' pattern
        one_match = one_pattern.match(rs)
        if one_match:
            return LCU_MUXB_SEL[rs], -1

        return None, -1

    def asmToHex(self, instr):
        space_instr = instr.replace(",", " ")
        split_instr = [word for word in space_instr.split(" ") if word]
        try:
            op      = split_instr[0]
        except:
            op      = split_instr

        if op in self.lcu_arith_ops:
            alu_op = LCU_ALU_OPS[op]
            # Expect 3 or more operands
            nOperands = 3
            # Check +1 because the first is the op
            assert(len(split_instr) >= nOperands+1), "Instruction not valid for " + self.__class__.__name__ + ": " + instr + ". Expected at least " + str(nOperands) + " operands."

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
            muxA, srf_muxA_index = self.parseMuxAArith(rs, instr)
            muxB, srf_muxB_index = self.parseMuxBArith(rt, instr)
            
            srf_read_index = srf_muxA_index

            if srf_read_index > SRF_N_REGS or srf_muxB_index > SRF_N_REGS or any(x >= SRF_N_REGS for x in srf_strs_idx):
                raise ValueError("Instruction not valid for LCU: " + instr + ". The accessed SRF must be between 0 and " + str(SRF_N_REGS -1) + ".")

            if any(x == None for x in dests):
                raise ValueError("Instruction not valid for LCU: " + instr + ". Expected another format for dest.")
            
            srf_str_index = -1
            for x in srf_strs_idx:
                if x != -1 and srf_str_index != -1:
                    raise Exception("Instruction not valid for RC: " + instr + ". Expected at most one writes to the SRF.")
                elif x != -1:
                    srf_str_index = x

            if muxB == None:
                raise ValueError("Instruction not valid for LCU: " + instr + ". Expected another format for muxB.")

            imm = 0
            if muxA == None:
                try:
                    imm = int(rs)
                except:
                    raise ValueError("Instruction not valid for LCU: " + instr + ". Expected another format for muxA.")
                muxA = LCU_MUXA_SEL["IMM"]
            
            if srf_muxB_index != -1:
                if srf_read_index != -1 and srf_muxB_index != srf_read_index:
                    raise ValueError("Instruction not valid for LCU: " + instr + ". Expected only reads/writes to the same reg of the SRF.") 
                srf_read_index = srf_muxB_index

            if srf_str_index != -1 and srf_read_index != -1 and srf_str_index != srf_read_index:
                raise ValueError("Instruction not valid for LCU: " + instr + ". Expected only reads/writes to the same reg of the SRF.")

            br_mode = 0

            # Check if writes to local regs
            rf_wsel = 0
            rf_we = 0
            last = -1
            for dest in dests:
                if dest < LCU_NUM_DREG:
                    if last != -1 and last != dest:
                        raise Exception("Instruction not valid for LCU: " + instr + ". Expected writes to more than one local register.")
                    last = dest
                    rf_we = 1
                    rf_wsel = dest

            # Return read and write srf indexes and the hex translation
            word = LCU_IMEM_WORD(imm=imm, rf_wsel=rf_wsel, rf_we=rf_we, alu_op=alu_op, br_mode=br_mode, muxb_sel=muxB, muxa_sel=muxA)
            return srf_read_index, srf_str_index, word

        if op in self.lcu_rcmode_ops:
            alu_op = LCU_ALU_OPS[op[:-1]]
            # Expect 1 operand: imm
            try:
                imm_str = split_instr[1]
            except:
                raise ValueError("Instruction not valid for LCU: " + instr + ". Expected 1 operand.")
            try:
                imm = int(imm_str) 
            except:
                raise ValueError("Instruction not valid for LCU: " + instr + ". Expected an inmediate as an operand.")
            
            br_mode = 1
            # Return read and write srf indexes
            word = LCU_IMEM_WORD(imm=imm, alu_op=alu_op, br_mode=br_mode)
            return -1, -1, word

        if op in self.lcu_bgepd_ops:
            alu_op = LCU_ALU_OPS[op]
            # Do not admit a destination
            assert(len(split_instr) == 4), "Instruction not valid for" + self.__class__.__name__ + ": " + instr + ". Expected 3 operands."

            rs = split_instr[1]
            rt = split_instr[2]
            imm_str = split_instr[3]

            muxA, srf_muxA_index = self.parseMuxAArith(rs, instr)
            muxB, srf_muxB_index = self.parseMuxBArith(rt, instr)
            imm = 0

            if srf_muxB_index > SRF_N_REGS or srf_muxA_index > SRF_N_REGS:
                raise ValueError("Instruction not valid for LCU: " + instr + ". The accessed SRF must be betwwen 0 and " + str(SRF_N_REGS -1) + ".")

            if muxB == None:
                raise ValueError("Instruction not valid for LCU: " + instr + ". Expected another format for muxB.")
            
            imm_rs = None
            if muxA == None:
                try:
                    imm_rs = int(rs)
                except:
                    raise ValueError("Instruction not valid for LCU: " + instr + ". Expected another format for muxA.")
                muxA = LCU_MUXA_SEL["IMM"]
            
            try:
                imm = int(imm_str) 
            except:
                raise ValueError("Instruction not valid for LCU: " + instr + ". Expected an inmediate as last operand.")
            if imm_rs != None and imm != imm_rs:
                raise ValueError("Instruction not valid for LCU: " + instr + ". Expected the same inmediate as last operand.")
            
            # Read SRF
            srf_read_index = srf_muxB_index
            if srf_muxA_index != -1 and srf_read_index != -1 and srf_muxA_index != srf_read_index:
                raise ValueError("Instruction not valid for LCU: " + instr + ". Expected only reads/writes to the same reg of the SRF.")
            srf_read_index = srf_muxA_index

            br_mode = 0
            
            # How does BGEPD really work? The result of the ALU is the first operand minus one
            # And it writes to SRF if it is the first operand
            srf_str_index = srf_muxA_index  
            
            # Check if writes to local regs
            rf_wsel = 0
            rf_we = 0
            if muxA < LCU_NUM_DREG:
                rf_we = 1
                rf_wsel = muxA
    
            # Return read and write srf indexes
            word = LCU_IMEM_WORD(imm=imm, rf_wsel=rf_wsel, rf_we=rf_we, alu_op=alu_op, br_mode=br_mode, muxb_sel=muxB, muxa_sel=muxA)
            return srf_read_index, srf_str_index, word

        if op in self.lcu_branch_ops:
            alu_op = LCU_ALU_OPS[op]

            # Check number of operands           
            assert(len(split_instr) >= 4), "Instruction not valid for" + self.__class__.__name__ + ": " + instr + ". Expected at least 3 operands."

            # Control more than one destination
            rds = []
            for i in range(1, len(split_instr) - 3):
                rds.append(split_instr[i])
            rs = split_instr[len(split_instr) -3]
            rt = split_instr[len(split_instr) -2]
            imm_str = split_instr[len(split_instr) -1]

            dests = []
            srf_strs_idx = []
            for i in range(len(rds)):
                dest, aux_srf = self.parseDestArith(rds[i], instr)
                dests.append(dest)
                srf_strs_idx.append(aux_srf)

            muxA, srf_muxA_index = self.parseMuxAArith(rs, instr)
            muxB, srf_muxB_index = self.parseMuxBArith(rt, instr)
            imm = 0

            if srf_muxB_index > SRF_N_REGS or srf_muxA_index > SRF_N_REGS or any(x >= SRF_N_REGS for x in srf_strs_idx):
                raise ValueError("Instruction not valid for LCU: " + instr + ". The accessed SRF must be betwwen 0 and " + str(SRF_N_REGS -1) + ".")

            if any(x == None for x in dests):
                raise ValueError("Instruction not valid for LCU: " + instr + ". Expected another format for dest.")
            
            srf_str_index = -1
            for x in srf_strs_idx:
                if x != -1 and srf_str_index != -1:
                    raise Exception("Instruction not valid for LCU: " + instr + ". Expected at most one write to the SRF.")
                elif x != -1:
                    srf_str_index = x

            if muxB == None:
                raise ValueError("Instruction not valid for LCU: " + instr + ". Expected another format for muxB.")
            
            imm_rs = None
            if muxA == None:
                try:
                    imm_rs = int(rs)
                except:
                    raise ValueError("Instruction not valid for LCU: " + instr + ". Expected another format for muxA.")
                muxA = LCU_MUXA_SEL["IMM"]
            
            
            try:
                imm = int(imm_str) 
            except:
                raise ValueError("Instruction not valid for LCU: " + instr + ". Expected an inmediate as last operand.")
            if imm_rs != None and imm != imm_rs:
                raise ValueError("Instruction not valid for LCU: " + instr + ". Expected the same inmediate as last operand.")
            
            srf_read_index = srf_muxB_index
            if srf_muxA_index != -1 and srf_read_index != -1 and srf_muxA_index != srf_read_index:
                raise ValueError("Instruction not valid for LCU: " + instr + ". Expected only reads/writes to the same reg of the SRF.")
            srf_read_index = srf_muxA_index

            br_mode = 0   
            
            # Check if writes to local regs
            rf_wsel = 0
            rf_we = 0
            last = -1
            for dest in dests:
                if dest < LCU_NUM_DREG:
                    if last != -1 and last != dest:
                        raise Exception("Instruction not valid for LCU: " + instr + ". Expected writes to more than one local register.")
                    last = dest
                    rf_we = 1
                    rf_wsel = dest
    
            # Return read and write srf indexes
            word = LCU_IMEM_WORD(imm=imm, rf_wsel=rf_wsel, rf_we=rf_we, alu_op=alu_op, br_mode=br_mode, muxb_sel=muxB, muxa_sel=muxA)
            return srf_read_index, srf_str_index, word

        
        if op in self.lcu_jump_ops:
            alu_op = LCU_ALU_OPS[op]

            # Check number of operands           
            assert(len(split_instr) >= 3), "Instruction not valid for" + self.__class__.__name__ + ": " + instr + ". Expected at least 2 operands."

            # Control more than one destination
            rds = []
            for i in range(1, len(split_instr) - 2):
                rds.append(split_instr[i])
            rs = split_instr[len(split_instr) -2]
            rt = split_instr[len(split_instr) -1]

            dests = []
            srf_strs_idx = []
            for i in range(len(rds)):
                dest, aux_srf = self.parseDestArith(rds[i], instr)
                dests.append(dest)
                srf_strs_idx.append(aux_srf)
            muxA, srf_read_index = self.parseMuxAArith(rs, instr)
            muxB, srf_muxB_index = self.parseMuxBArith(rt, instr)
            imm = 0

            if srf_muxB_index > SRF_N_REGS or srf_read_index > SRF_N_REGS or any(x >= SRF_N_REGS for x in srf_strs_idx):
                raise ValueError("Instruction not valid for LCU: " + instr + ". The accessed SRF must be betwwen 0 and " + str(SRF_N_REGS -1) + ".")

            if any(x == None for x in dests):
                raise ValueError("Instruction not valid for LCU: " + instr + ". Expected another format for dest.")
            
            srf_str_index = -1
            for x in srf_strs_idx:
                if x != -1 and srf_str_index != -1:
                    raise Exception("Instruction not valid for RC: " + instr + ". Expected at most one write to the SRF.")
                elif x != -1:
                    srf_str_index = x

            if muxB == None:
                raise ValueError("Instruction not valid for LCU: " + instr + ". Expected another format for the first operand (muxB).")
            
            if muxA == None:
                try:
                    imm = int(rs)
                except:
                    raise ValueError("Instruction not valid for LCU: " + instr + ". Expected another format for the second operand (muxA).")
                muxA = LCU_MUXA_SEL["IMM"]
            
            if srf_muxB_index != -1:
                if srf_read_index != -1 and srf_muxB_index != srf_read_index:
                    raise ValueError("Instruction not valid for LCU: " + instr + ". Expected only reads/writes to the same reg of the SRF.") 
                srf_read_index = srf_muxB_index

            # Check if writes to local regs
            rf_wsel = 0
            rf_we = 0
            last = -1
            for dest in dests:
                if dest < LCU_NUM_DREG:
                    if last != -1 and last != dest:
                        raise Exception("Instruction not valid for RC: " + instr + ". Expected writes to more than one local register.")
                    last = dest
                    rf_we = 1
                    rf_wsel = dest

            br_mode = 0
            # Return read and write srf indexes
            word = LCU_IMEM_WORD(imm=imm, rf_wsel=rf_wsel, rf_we=rf_we, alu_op=alu_op, br_mode=br_mode, muxb_sel=muxB, muxa_sel=muxA)
            return srf_read_index, -1, word


        if op in self.lcu_nop_ops:
            alu_op = LCU_ALU_OPS[op]
            # Expect 0 operands
            if len(split_instr) > 1:
                raise ValueError("Instruction not valid for LCU: " + instr + ". Nop does not expect operands.")

            # Return read and write srf indexes
            word = LCU_IMEM_WORD(alu_op=alu_op)
            return -1, -1, word
        
        if op in self.lcu_exit_ops:
            alu_op = LCU_ALU_OPS[op]
            # Expect 0 operands
            if len(split_instr) > 1:
                raise ValueError("Instruction not valid for LCU: " + instr + ". Exit does not expect operands.")
            
            # Return read and write srf indexes
            word = LCU_IMEM_WORD(alu_op=alu_op)
            return -1, -1, word
        
        raise ValueError("Instruction not valid for LCU: " + instr + ". Operation not recognised.")

    def hexToAsm(self, instr, srf_sel, srf_we, alu_srf_write):
        return LCU_IMEM_WORD(hex_word=instr).get_word_in_asm(srf_sel, srf_we, alu_srf_write)
    