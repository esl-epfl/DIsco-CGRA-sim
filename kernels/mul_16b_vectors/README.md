# Add Vectors Kernel

## Kernel description

Perform element-wise multiplication of two vectors of 16-bit elements

## Kernal usage

Inputs:
* Two 256 16-bit integers vectors

SRF Initialization:
* None

Outputs:
* One 256 16-bit integers vector


## Implementation details

The first input vector is loaded into SPM bank 1, and the second in SPM bank 2. These are loaded from the host processor to VWR2A through DMA write requests. The vectors are then loaded into VWRs A and B respectively, and the sum is performed by the RCs. The result is stored in VWR C, which is then loaded into SPM bank 3, where it can be read by the host processor through a DMA read request.

## Examples of applications using this kernel

* [HEEP-Alive mul vectors test](https://github.com/esl-epfl/heepalive-imec/blob/master/sw/applications/add_vectors/dsip_add_vectors.c)

