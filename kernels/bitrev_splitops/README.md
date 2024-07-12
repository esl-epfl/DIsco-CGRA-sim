# Bitrev Splitops Kernel

## Kernel description

This kernel performs bit reversal operations following the FFT kernel to output the final FFT result. It must be called directly after the FFT kernel to compute the final result.

## Kernal usage

### In the case of a complex-valued FFT:
Inputs (same as to the FFT kernel):
* Vector of data on which to compute the FFT. Its size is three times the size of the resulting FFT (FFT_SIZE), where:
    * The first FFT_SIZE values are the real part 
    * The next FFT_SIZE values are the imaginary part
    * The next FFT_SIZE/2 values are the real weights
    * The final FFT_SIZE/2 values are the imaginary weights

SRF Initialization:
* Whoever figures out how this kernel works, please update the README here :)

Outputs:
* The FFT result vector whose length is FFT_SIZE

## Implementation details

Whoever figures out how this kernel works, please update the README here :)

## Examples of applications using this kernel

* [HEEP-Alive FFT test](https://github.com/esl-epfl/heepalive-imec/blob/master/sw/applications/dsip_fft/dsip_fft.c)
* [Respiration feature extraction](https://eslgit.epfl.ch/esl/architectures-and-systems/accelerators/cgra/vwr2a_kernel_examples/-/tree/main/rsp_features_extraction/src/rsp_features.c)
* [FFT test](https://eslgit.epfl.ch/esl/architectures-and-systems/accelerators/cgra/vwr2a_kernel_examples/-/tree/main/fft/src/rsp_fft.c)
* [Biosignal monitoring](https://eslgit.epfl.ch/esl/architectures-and-systems/accelerators/cgra/vwr2a_kernel_examples/-/tree/main/biosignal_monitoring_cgra/src/rsp.c)
