# ESL-DISCO-CGRA Simulator
The [DISCO-CGRA architecture](https://dl.acm.org/doi/abs/10.1145/3489517.3530980) is a powerful CGRA-like processor designed for the biomedical domain, but can be used to accelerate a multitude of edge-AI applications if programmed accordingly. This simulator repository models the different architectural components of DISCO-CGRA (RTL blocks, memories, processing elements, etc.) using Python structures. This repository serves to:
* Educate new users of the DISCO-CGRA architecutre on its full structure and funcitonality
* Enable users to deconstruct existing kernels and understand their functionality at every step
* Facilitate the development of new kernels, thus expanding the potential and impact of the DISCO-CGRA
This simulator does not include the compilation of C code into DISCO-CGRA-compatible assembly code.

# Structure
The `how_to_start.ipynb` file teaches you how to understand existing DISCO-CGRA kernels and start writing new ones.

The `disco-cgra_docs/` folder includes important information about the strucutre and function of the architecture.
It is also included a description of the assembly ISA for the DISCO-CGRA.

The `src/` folder contains Python structures modeling each architectural module of the DISCO-CGRA, functions for encoding/decoding the Assembly language of each of these blocks, and (future work) simulations of its processing and memeory elements.

The `kernels/` folder contains all existing kernels written for the DISCO-CGRA, as well as insructions for using them. It is mandatory that every new kernel written for the DISCO-CGRA contains a README describing the usage of the kernel (i.e. expected inputs/outputs, how to initialize the Scalar Register File, where to write data and read the results in memory).
