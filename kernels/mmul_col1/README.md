# Add Vectors Kernel

## Kernel description

Perform multiplication of two matrices.

## Kernal usage

Inputs:
* Two matrices "A" and "B" of dimensions 4x32 and 32x32, respectively. (to be generalized)
* One matrix "C" initialized to 0 of dimension ROWS_A x COLS_B.

SRF Initialization:

| Position | Value                                       |
| -------- | ------------------------------------------- |
| 0        | Number of cols on the block of A minus 1    |
| 1        | Numbers of elements of C in each RC minus 1 |
| 2        | Line of the SPM where the block of C is     |

Outputs:
* One matrix of dims ROWS_A x COLS_B.


## Implementation details

The SRF is loaded into SPM bank 0. The matrix "B" is allocated by columns into the SPM banks 1 to 32. Each column of "B" is replicated 4 times so it generates a vector of 128 elements and this vector is loaded into the SPM. The matrix C, initalized to 0s, is loaded into SPM bank 33 and the matrix A is loaded into SPM bank 34. The MAC operation is done by the RCs while the other units control the 2 loops needed and the access to the SPM and VWR index. When a partial sum in computed in an RC, the result is stored in VWR C.

## Examples of applications using this kernel

* [HEEP-Alive mmul](https://github.com/esl-epfl/heepalive-imec/blob/master/sw/applications/mmul/dsip_mmul.c)

