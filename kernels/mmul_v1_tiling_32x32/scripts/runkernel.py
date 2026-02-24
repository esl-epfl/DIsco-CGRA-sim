# Imports
import sys
import os
import pandas as pd
from random import randint
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src import *
from src.simulator import SIMULATOR


# --------------------------------------------
#               INIT & CONFIG
# --------------------------------------------
sim = SIMULATOR()

DEBUG = 1
MAX_ITER = 300000

# DISCO-CGRA Parameters
nRCs = 4
VWR_SIZE = 128
nColsCGRA = 2

# --------------------------------------------
#               KERNEL CONFIGURATION
# --------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
kernel_path = os.path.join(SCRIPT_DIR, "")

kernel_number = 1 
column_usage = [True, True] 
nInstrPerCol = 45
imem_add_start = 0 
srf_spm_addres = 0 
version="_2col"

# Block size 32x32
BLOCK_SIZE = 32

sim.kernel_config(column_usage, nInstrPerCol, imem_add_start, srf_spm_addres, kernel_number)

# --------------------------------------------
#               DATA
# --------------------------------------------
data = np.load(os.path.join(kernel_path, "data.npz"))

A = data["A"]
B = data["B"]
C = data["C"]
expected_res = data["D"]

ROWS_A = int(data["ROWS_A"])
COLS_A = int(data["COLS_A"])
COLS_B = int(data["COLS_B"])
ALPHA  = int(data["ALPHA"])
BETA   = int(data["BETA"])

B_t = (B.reshape(COLS_A, COLS_B)).T.flatten()
output = np.zeros((ROWS_A * COLS_B), dtype=np.int32)

print(f"GeMM with {ROWS_A}x{COLS_A} * {COLS_A}x{COLS_B}, ALPHA={ALPHA}, BETA={BETA}")

def printAsMatrix(array, rows, cols):
    for i in range(rows):
        print(array[i * cols:(i + 1) * cols])

        # --------------------------------------------
#              COMPILE ASM TO HEX
# --------------------------------------------
sim.compileAsmToHex(kernel_path, kernel_number, version=version)

# --------------------------------------------
#          LOAD KERNEL INSTRUCTIONS
# --------------------------------------------

# This needs the hex instructions, if you don't provide them, generate then compiling the asm
sim.kernel_load(kernel_path, version=version + "_autogen", kernel_number=kernel_number)

# --------------------------------------------
#            SIMULATION PARAMETERS
# --------------------------------------------
show_lcu = []
show_srf = []
show_lsu = []
show_rcs = [[],[],[],[]]
show_mxcu = []
display_ops = [show_lcu, show_lsu, show_mxcu, show_rcs, show_srf]
# Default SRF values
srf = [0 for i in range(N_ELEMS_PER_VWR)]


# --------------------------------------------
#             SPM LINES MAPPING
# --------------------------------------------
nLinesPerMatrix = 8

srf_spm_line = 0 # SRF 
# BUFFER 0
buff_0_spm_line_A = srf_spm_line + 1
buff_0_spm_line_B = buff_0_spm_line_A + nLinesPerMatrix
buff_0_spm_line_C = buff_0_spm_line_B + nLinesPerMatrix
#BUFFER 1
buff_1_spm_line_A = buff_0_spm_line_C + nLinesPerMatrix
buff_1_spm_line_B = buff_1_spm_line_A + nLinesPerMatrix
buff_1_spm_line_C = buff_1_spm_line_B + nLinesPerMatrix


# --------------------------------------------
#             TILING LOOPS
# --------------------------------------------

nBlocksColsA = COLS_A // BLOCK_SIZE # Assuming divisible

buff_C = 0
buff_AB = 0
rC = 0
while rC < ROWS_A :
    cC = 0
    while cC < COLS_B :
        c_spm_line = buff_0_spm_line_C
        if buff_C: c_spm_line = buff_1_spm_line_C
        # Load C block
        realRc = rC
        aux_c_spm_line = c_spm_line
        for nLine in range(nLinesPerMatrix):
            lineC = []
            for r in range(VWR_SIZE//BLOCK_SIZE):
                lineC += C[realRc * COLS_B + cC : realRc * COLS_B + cC + BLOCK_SIZE].tolist()
                realRc += 1
            sim.setSPMLine(aux_c_spm_line, lineC)
            aux_c_spm_line +=1
            print(f"Loading C on line {aux_c_spm_line}: {lineC}")

        # Output Stationary
        blockA = 0
        while blockA < nBlocksColsA :
            a_spm_line = buff_0_spm_line_A
            b_spm_line = buff_0_spm_line_B
            if buff_AB: 
                a_spm_line = buff_1_spm_line_A
                b_spm_line = buff_1_spm_line_B
            # Load A block
            a_spm_line_aux = a_spm_line
            rA = rC
            for nLine in range(nLinesPerMatrix):
                lineA = []
                for r in range(VWR_SIZE//BLOCK_SIZE):
                    lineA += A[rA * COLS_A + blockA*BLOCK_SIZE : rA * COLS_A + blockA*BLOCK_SIZE + BLOCK_SIZE].tolist()
                    rA += 1
                sim.setSPMLine(a_spm_line_aux, lineA.copy())
                print(f"Loading A on line {a_spm_line_aux}: {lineA}")
                a_spm_line_aux +=1
            # Load B block
            b_spm_line_aux = b_spm_line
            rB = cC
            for nLine in range(nLinesPerMatrix):
                lineB = []
                for r in range(VWR_SIZE//BLOCK_SIZE):
                    lineB += B_t[rB * COLS_A + blockA*BLOCK_SIZE : rB * COLS_A + blockA*BLOCK_SIZE + BLOCK_SIZE].tolist()
                    rB += 1
                sim.setSPMLine(b_spm_line_aux, lineB.copy())
                print(f"Loading B on line {b_spm_line_aux}: {lineB}")
                b_spm_line_aux +=1
            # Load SRF
            # Col 0
            srf[0]  = a_spm_line 
            srf[1]  = b_spm_line 
            srf[2]  = c_spm_line
            srf[3]  = 3 # Share 8 lines between the 2 cols
            srf[4]  = 7 # Go through every line of B
            srf[5]  = 31 # Go through every element of B
            srf[6]  = ALPHA
            srf[7]  = BETA
            # Col 1
            srf[8]  = a_spm_line + 4 # Compute the next rows of C
            srf[9]  = b_spm_line
            srf[10] = c_spm_line + 4 # Compute the next rows of C
            srf[11] = 3 # Share 8 lines between the 2 cols
            srf[12] = 7
            srf[13] = 31
            srf[14] = ALPHA
            srf[15] = BETA
            sim.setSPMLine(srf_spm_line, srf.copy())
            print(f"Loading SRF into line {srf_spm_line}: {srf}")

            # Compute 
            print("Run kernel")
            sim.run(kernel_number, display_ops=display_ops, max_iter=MAX_ITER)
            blockA += 1
            buff_AB = (buff_AB+1)%2
        
        # Block C fully computed -> extract it
        block_out = []
        c_spm_line_aux = c_spm_line
        for i in range(nLinesPerMatrix):
            block_out.extend(c_int32(x).value for x in sim.getSPMLine(c_spm_line))
            print("Extracting C line:", c_spm_line)
            c_spm_line+=1
        # Store block in output
        for i in range(BLOCK_SIZE):
            output[(rC+i) * COLS_B + cC : (rC+i) * COLS_B + cC + BLOCK_SIZE] = block_out[i * BLOCK_SIZE:(i + 1) * BLOCK_SIZE]
                
        cC += BLOCK_SIZE
        buff_C = (buff_C+1)%2
    rC += BLOCK_SIZE

# Verify results
disco_out = output
errors = 0
for i in range(len(expected_res)):
    if expected_res[i] != disco_out[i]:
        errors+=1
    
if errors == 0:
    print("The result is correct!")
else:
    print("Oops, something went wrong. There are " + str(errors) + " errors (out of " + str(len(expected_res)) + " elements).")
    print("DISCO out:")
    printAsMatrix(disco_out, ROWS_A, COLS_B)
    print("Expected result:")
    printAsMatrix(expected_res, ROWS_A, COLS_B)
    print("A:")
    printAsMatrix(A, ROWS_A, COLS_A)
    print("B_t:")
    printAsMatrix(B_t, COLS_B, COLS_A)
    print("C:")
    printAsMatrix(C, ROWS_A, COLS_B)