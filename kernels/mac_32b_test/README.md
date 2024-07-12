# Add Vectors Kernel

## Kernel description

Perform element-wise multiplication and accumulation operation of three vectors. The first and second vectors are the input for the multiplication adn the thrid is the accumulator.

## Kernal usage

Inputs:
* Three 128-element vectors

SRF Initialization:
* None

Outputs:
* One 128-element vector (the same as the third input)


## Implementation details

The first input vector is loaded into SPM bank 1, the second in SPM bank 2 and the third in SPM bank 3. These are loaded from the host processor to VWR2A through DMA write requests. The vectors are then loaded into VWRs A, B and C respectively, and the mac is performed by the RCs. The accumulator is fixed to VWR C, which can be read by the host processor through a DMA read request.

## Examples of applications using this kernel

* [HEEP-Alive mac test](https://github.com/esl-epfl/heepalive-imec/blob/master/sw/applications/add_vectors/dsip_add_vectors.c)

