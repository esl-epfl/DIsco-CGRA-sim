# Morphological Filter Baseline Removal Kernel

## Kernel description

The baseline removal is part of a 4-kernel sequence that performs morphological filtering of an input biosignal. The kernel sequence is:
* Q64 Erosion
* Q128 Dilation
* Q128 Erosion
* Baseline removal

## Kernal usage

Inputs:

SRF Initialization:

Outputs:


## Implementation details

Whoever figures out how this kernel works, please update the README here :)

## Examples of applications using this kernel

* [Morphological Filter Baseline Removal](https://eslgit.epfl.ch/esl/architectures-and-systems/accelerators/cgra/vwr2a_kernel_examples/-/tree/main/mf_baseline_rm/src/morph_filter.c)
* [Queue Baseline Removal](https://eslgit.epfl.ch/esl/architectures-and-systems/accelerators/cgra/vwr2a_kernel_examples/-/tree/main/queue_baseline_rm/src/morph_filter.c)
* [Morphological Baseline Lowpass Filter](https://eslgit.epfl.ch/esl/architectures-and-systems/accelerators/cgra/vwr2a_kernel_examples/-/tree/main/mf_baseline_lp_filter_cgra_1l/src/morph_filter.c)



