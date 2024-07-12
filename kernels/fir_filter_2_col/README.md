# FIR-Filter 2-Column Kernel

## Kernel description

This kernel uses both columns of VWR2A to run a Finite Impulse Response (FIR) filter on the input data.

## Kernal usage

Inputs:
* A vector of data to be filtered. Its size should be divisible by twice VWR size of the VWR2A (i.e. 2x128 = 256).
* The "taps" (i.e. filter coefficients) to convolve with the input

SRF Initialization:
* Column 0:
    * [0]: Index of the "taps" in the SPM banks
    * [1]: Index of the data in the SPM banks in which the input data is written and the output result is read
    * [2]: (Presumably) the SPM index loaded with the previous window of data to initialize the filter
    * [3]: Number of filter taps
    * [4]: Number of filtering iterations, which is the data input size divided by the VWR size divided by two (for the two columns)
    * [5]: A bit shift of 15 (assuming 16-bit input samples, since the CGRA works with 32-bit data)
* Column 1:
    * [0]: Index of the "taps" in the SPM banks
    * [1]: Index of the data in the SPM banks in which the input data is written and the output result is read
    * [2]: (Presumably) the SPM index loaded with the previous window of data to initialize the filter
    * [3]: Number of filter taps
    * [4]: Number of filtering iterations, which is the data input size divided by the VWR size divided by two (for the two columns)
    * [5]: A bit shift of 15 (assuming 16-bit input samples, since the CGRA works with 32-bit data)
    * [6]: The index of an array of zeros written into the SPM

Outputs:
* The filtered vector (same size as the input vector)

## Implementation details

First, the filter coefficients of the CGRA are written to an SPM bank, whose index is stored in SRF position 0 of both columns.The index of the data (both for reading and writing) in the SPM is stored to SFR position 1. The number of filter coefficients is stored into SRF position 3. The number of iterations of filtering, which is equal to INPUT_SIZE/CGRA_VWR_SIZE/2, is stored in SRF index 4. The output is stored to the same data index as the input.

## Examples of applications using this kernel

* [FIR filter example](https://eslgit.epfl.ch/esl/architectures-and-systems/accelerators/cgra/vwr2a_kernel_examples/-/tree/main/fir_filter/src/fir_filter.c)
* [Biosignal monitoring](https://eslgit.epfl.ch/esl/architectures-and-systems/accelerators/cgra/vwr2a_kernel_examples/-/blob/main/biosignal_monitoring_cgra/src/RSP_FIRfiltering_CMSIS.c)

