from .params import *
from ctypes import *
class ALU():
    def __init__(self):
        self.res = 0
        self.zero_flag = 0
        self.sign_flag = 0
        self.newRes = 0
    
    def updateALUValues(self):
        self.res = self.newRes
        if self.newRes == 0:
            self.zero_flag = 1
        else: self.zero_flag = 0
        if self.newRes < 0:
            self.sign_flag = 1
        else: self.sign_flag = 0

    def nop(self):
        pass # Intentional

    def sadd(self, val1, val2 ):
        self.newRes = c_int32( val1 + val2 ).value

    def ssub(self,  val1, val2 ):
        self.newRes = c_int32( val1 - val2 ).value

    def sll(self,  val1, val2 ):
        mask = (1 << 3) - 1 # Get the three last bits of val2 for the shift
        shift_n = val2 & mask
        self.newRes = c_int32(val1 << shift_n).value

    def srl(self,  val1, val2 ):
        # Python shifts are always arithmetic so...
        mask = (1 << 3) - 1 # Get the three last bits of val2 for the shift
        shift_n = val2 & mask
        if val1 >= 0:
            interm_result = (c_int32(val1).value & MAX_32b)
            self.newRes = c_int32(interm_result >> shift_n).value
        else:
            res_pos = c_int32((-val1) >> shift_n).value
            self.newRes = - res_pos
        

    def sra(self,  val1, val2 ):
        mask = (1 << 3) - 1 # Get the three last bits of val2 for the shift
        shift_n = val2 & mask
        self.newRes = c_int32(val1 >> shift_n).value

    def lor(self,  val1, val2 ):
        self.newRes = c_int32( val1 | val2).value

    def land(self,  val1, val2 ):
        self.newRes = c_int32( val1 & val2).value

    def lxor(self,  val1, val2 ):
        self.newRes = c_int32( val1 ^ val2).value
    
    def smul(self,  val1, val2):
        self.newRes = c_int32(val1 * val2).value & MAX_32b

    def sdiv(self,  val1, val2):
        self.newRes = c_int32(val1 / val2).value
    
    def saddh(self,  val1, val2 ):
        val1_high = (val1 >> 16) & 0xFFFF  
        val1_low = val1 & 0xFFFF           
        val2_high = (val2 >> 16) & 0xFFFF  
        val2_low = val2 & 0xFFFF           

        high_res = (val1_high + val2_high) & 0xFFFF
        low_res = (val1_low + val2_low) & 0xFFFF

        self.newRes = (high_res << 16) | low_res

    def ssubh(self,  val1, val2 ):
        val1_high = (val1 >> 16) & 0xFFFF  
        val1_low = val1 & 0xFFFF           
        val2_high = (val2 >> 16) & 0xFFFF  
        val2_low = val2 & 0xFFFF           

        high_res = (val1_high - val2_high) & 0xFFFF
        low_res = (val1_low - val2_low) & 0xFFFF

        res = (high_res << 16) | low_res

        #print("SUB.H: " + str(val1) + " , " + str(val2) + " = " + str(res))

        self.newRes = res

    def sllh(self,  val1, val2 ):
        raise Exception("Half precision sll not supported.")

    def srlh(self,  val1, val2 ):
        raise Exception("Half precision srl not supported.")
    
    def srah(self,  val1, val2 ):
        raise Exception("Half precision sra not supported.")

    def lorh(self,  val1, val2 ):
        raise Exception("Half precision lor not supported.")

    def landh(self,  val1, val2 ):
        raise Exception("Half precision land not supported.")

    def lxorh(self,  val1, val2 ):
        raise Exception("Half precision lxor not supported.")

    def smulh(self, val1, val2):
        val1_high = (val1 >> 16) & 0xFFFF  
        val1_low = val1 & 0xFFFF           
        val2_high = (val2 >> 16) & 0xFFFF  
        val2_low = val2 & 0xFFFF           

        high_res = (val1_high * val2_high) & 0xFFFF
        low_res = (val1_low * val2_low) & 0xFFFF

        self.newRes = (high_res << 16) | low_res

    def sdivh(self, val1, val2):
        raise Exception("Half precision div not supported.")

    def mul_fp(self, val1, val2):
        print("Fixed point mul to be done.")
        self.newRes = 0

    def div_fp(self, val1, val2):
        raise Exception("Fixed point div not supported.")

    def sfga(self, val1, val2, sign_flag):
        if sign_flag : self.newRes = val1
        else: self.newRes = val2

    def zfga(self, val1, val2, zero_flag):
        if zero_flag : self.newRes = val1
        else: self.newRes = val2

    def bitrev(self, val1, val2):
        # Reverse bit order of val1
        val1 = (( val1 & 0x55555555) << 1) | (( val1 & 0xAAAAAAAA) >> 1)
        val1 = (( val1 & 0x33333333) << 2) | (( val1 & 0xCCCCCCCC) >> 2)
        val1 = (( val1 & 0x0F0F0F0F) << 4) | (( val1 & 0xF0F0F0F0) >> 4)
        val1 = (( val1 & 0x00FF00FF) << 8) | (( val1 & 0xFF00FF00) >> 8)
        val1 = (( val1 & 0x0000FFFF) << 16) | (( val1 & 0xFFFF0000) >> 16)
        # Then shift it right 
        mask = (1 << 3) - 1 # Get the three last bits of val2 for the shift
        shift_n = val2 & mask
        interm_result = (c_int32(val1).value & MAX_32b)
        self.newRes = c_int32(interm_result >> shift_n).value
    
    def mac(self, val1, val2, val3):
        self.newRes = c_int32(val1 * val2).value & MAX_32b + val3

    def mach(self, val1, val2, val3):
        val1_high = (val1 >> 16) & 0xFFFF  
        val1_low = val1 & 0xFFFF           
        val2_high = (val2 >> 16) & 0xFFFF  
        val2_low = val2 & 0xFFFF
        val3_high = (val3 >> 16) & 0xFFFF  
        val3_low = val3 & 0xFFFF             

        high_res = (val1_high * val2_high) & 0xFFFF
        low_res = (val1_low * val2_low) & 0xFFFF

        high_res = (high_res + val3_high) & 0xFFFF
        low_res = (low_res + val3_low) & 0xFFFF

        self.newRes = (high_res << 16) | low_res
