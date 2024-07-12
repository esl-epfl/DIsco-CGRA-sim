"""srf.py: Data structures and objects emulating the Scalar Register File of the VWR2A architecture"""
__author__      = "María José Belda Beneyto"
__email__       = "mbelda@ucm.es"

import numpy as np

from .params import *

class SRF():
    def __init__(self):
        self.regs = [0 for _ in range(SRF_N_REGS)]
    
    def checkReadsWrites(self, srf_read_idx_lcu, srf_read_idx_lsu, srf_read_idx_rc, srf_str_idx_lcu, srf_str_idx_lsu, srf_str_idx_rc, cycle):
        # ---------------------- Check reads/writes to SRF/VWR ---------------------- 
        # Check: Only RC0 should be able to write to SRF
        if np.any(np.array(srf_str_idx_rc[1:]) != -1):
            raise ValueError("Instructions not valid for this cycle (" + str(cycle) + ") of the CGRA. Only the RC on row 0 can write to the SRF.")
        
        # Check: Only reads to the same SRF register can be made by every unit
        srf_sel = -1 # No one reads
        all_read_srf = srf_read_idx_rc
        all_read_srf.append(srf_read_idx_lcu)
        all_read_srf.append(srf_read_idx_lsu)
        all_read_srf = np.array(all_read_srf)
        unique_vector_read_srf = np.unique(all_read_srf)
        if -1 in unique_vector_read_srf:
            unique_vector_read_srf = unique_vector_read_srf[unique_vector_read_srf != -1]
        if len(unique_vector_read_srf) > 1:
            raise ValueError("Instructions not valid for this cycle (" + str(cycle) + ") of the CGRA. Detected reads to different registers of the SRF.")
        if np.any(all_read_srf != -1):
            srf_sel = (all_read_srf[all_read_srf != -1])[0]

        # Check: Only one write can be done to a register of the SRF
        srf_we = 0 # Default
        srf_str_idx = -1 # Default
        all_str_srf = srf_str_idx_rc
        all_str_srf.append(srf_str_idx_lcu)
        all_str_srf.append(srf_str_idx_lsu)
        all_str_srf = np.array(all_str_srf)
        
        all_str_srf = all_str_srf[all_str_srf != -1]
        if len(all_str_srf) > 1:
            raise ValueError("Instructions not valid for this cycle (" + str(cycle) + ") of the CGRA. Detected multiple writes to the SRF.")
        if len(all_str_srf) > 0:
            srf_we = 1
            srf_str_idx = all_str_srf[0]

        # Check: The reads and writes to the SRF are made to the same register
        if srf_we != 0 and srf_sel != -1 and srf_sel != srf_str_idx:
            raise ValueError("Instructions not valid for this cycle (" + str(cycle) + ") of the CGRA. Detected reads and writes to different registers of the SRF.")
        
        # Set who writes to the SRF
        alu_srf_write = 0 # Default
        if srf_str_idx_rc[0] != -1:
            alu_srf_write = 1 # RC0
        if srf_str_idx_lcu != -1:
            alu_srf_write = 0 # LCU
        if srf_str_idx_lsu != -1:
            alu_srf_write = 3 # LSU
        
        srf_wsel = srf_sel
        if srf_str_idx != -1:
            srf_wsel = srf_str_idx
                
        return srf_wsel, srf_we, alu_srf_write