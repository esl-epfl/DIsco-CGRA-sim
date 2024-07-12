# RMS 64 Kernel

## Kernel description

This kernel computes the root mean squared (RMS) of 64 values of data.

## Kernal usage

Inputs:
* Presumably the SPM columns whose upper 64 values will be used to compute the RMS.

SRF Initialization:
* Whoever figures out how this kernel works, please update the README here :)

Outputs:
* SPM column to read the computed RMS from

## Implementation details

Whoever figures out how this kernel works, please update the README here :)

## Examples of applications using this kernel

* [Respiration feature extraction](https://eslgit.epfl.ch/esl/architectures-and-systems/accelerators/cgra/vwr2a_kernel_examples/-/tree/main/rsp_features_extraction/src/rsp_features.c)
