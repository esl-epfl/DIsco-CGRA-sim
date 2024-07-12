# Kernel Memory (KMEM)

VWR2A can have multiple kernels loaded into its instruction memory (IMEM). To keep track of which kernel instructions start at which IMEM address location, we use a kernel memory that lists up to 15 possible kernels to execute (keep in mind that kernel memory position 0 is reserved and KMEM words should not be stored here).

## Instruction format

Each kernel is set up with a configuration word of 21 bits with the following structure.

|SRF ADDRESS|N_COLUMNS (one-hot encoding)|KERNEL START ADDRESS|RCs/CCs/MXCU/LSU N_INSTR|
|---|---|---|---|
|20:17|16:15|14:6|5:0|

- SRF ADDRESS (4 bits): Line (0 to 15) of the SPM that the SRF of the kernel occupies.
- N_COLUMNS (2 bits): One-hot encoding of the columns that the kernel runs on.
	
	| Encoding | Description |
	| ---- | ---- |
	| 01 | Running on column 0 |
	| 10 | Running on column 1 |
	| 11 | Running on both columns |
	
- KERNEL START ADDRESS (9 bits): Start address of the kernel in the IMEM. Ranges from 0 to 511.
- RCs/CCs/MXCU/LSU N_INSTR (6 bits): Number of instructions the kernel takes in the IMEM of each specialized slot minus one. It is 63 since that is the maximum number of words that fit in the local IMEMs of the specialized slots.

## Example

If we consider that the SRF is stored on the first slot of the SPM when configuring the VWR2A, the kernel is going to be runned only in column 0, the instructions of the kernel are stored starting from the address 15 on the IMEM and this kernel has 43 instructions, the hexadecimal KMEM instruction would be `0x83EB`.

|SRF ADDRESS|N_COLUMNS (one-hot encoding)|KERNEL START ADDRESS|RCs/CCs/MXCU/LSU N_INSTR|
|---|---|---|---|
|0000|01|000001111|101011|