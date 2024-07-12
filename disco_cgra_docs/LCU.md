# Loop-Control Unit

The Loop-Control Unit (LCU) is responsible for updating the program counter of the CGRA. It has branch instructions that branch to the immediate value (except in the case of `JUMP`, that branches to the sum of the `MUXA` and `MUXB` results). It also has an ALU whose result is stored in one of the local registers (R0-R3) when `RF_WE` is enabled. It also issues the `EXIT` command at the end of every kernel to wake up the host processor and put the CGRA to sleep.

# Instruction format

The instructions for the LCU have a size of 20 bits with the following structure.

|MUXA_SEL|MUXB_SEL|BR_MODE|ALU_OP|RF_WE|RF_WSEL|INMEDIATE|
|---|---|---|---|---|---|---|
|19:17|16:14|13|12:9|8|7:6|5:0|

- MUX{A/B}_SEL (3 bits) : Select inputs to the ALU.
    
    |Value|MUXA|MUXB|
    |---|---|---|
    |0|R0|R0|
    |1|R1|R1|
    |2|R2|R2|
    |3|R3|R3|
    |4|SRF|SRF|
    |5|LAST|LAST|
    |6|ZERO|ZERO|
    |7|IMM|ONE|
    
    The `LAST` option is the maximum index to access in each RC slice of VWR. For example, for an architecture with 4 RCs per column and a VWR size of 128 elements, each RC would have access to 32 elements of the VWR. So, the `LAST` value would be 31, as it is the maximum index that can be accessed by each RC.
    
    The `SRF` option enables the access to the scalar registers that are shared by every RC in the column. To choose which register of the SRF to access (R0-R7) the MXCU unit is needed.
    
- BR_MODE (1 bit): Choose the output of the ALU from the LCU or from RCs.
    
    |Value|Description|
    |---|---|
    |0|Use the flags of the LCU ALU to know if the operands are equal, greater than, less than, etc.|
    |1|Use the result of the ALU of every RC in the column to know if the operands are equal, greater than, less than, etc. Since, if an adding or a substract has been computed on an RC’s ALU, it produces some equal and greater than bit values. This equal/greater than bits of every RC’s ALU are combined with an or operation to provide the bit value finally used to take or not the branch.|
    
- ALU_OP (4 bits): ALU operation to run.
    
    |Value|Operation|Description|
    |---|---|---|
    |0|NOP|No operation|
    |1|SADD|Signed addition|
    |2|SSUB|Signed substraction|
    |3|SLL|Shift left logical|
    |4|SRL|Shift right logical|
    |5|SRA|Shift right arithmetic|
    |6|LAND|Logical AND|
    |7|LOR|Logical OR|
    |8|LXOR|Logical XOR|
    |9|BEQ|Branch if equal (a == b)|
    |10|BNE|Branch if not equal (a ≠ b)|
    |11|BGEPD|Branch if greater or equal with pre-decrement ((--a) ≥ b)|
    |12|BLT|Branch if less than (a < b)|
    |13|JUMP|Jump to MUXA + MUXB|
    |14|EXIT|Kernel exit instruction|
    |15|NOP|No operation|
    
> [!IMPORTANT]  
> If branch request and exit same time, exit is ignored.  
    
- RF_WE (1 bit): enable writing ALU result to the chosen register.
- RF_WSEL (2 bits): One of the 4 LCU registers to write ALU result to.
- INMEDIATE (6 bits): an IMEM address to branch to in all branch operations except `JUMP`. Also can be passed into the ALU for logic operations through `MUXA`.

# Examples

## Example 1: Branch with `BGEPD`

For example, a pseudo-assembly instruction could be `BGEPD R0, R1, 7`. It decrements R0 by one and then if the new value of R0 is greater or equal to the value of R1, it takes the branch to the 7th instruction of the local instruction memory. So, we need to take into account the following:

- Set the ALU operation to`BGEPD`.
- Set the inmediate value to 7.
- Set `MUXA` to 0 to access `R0` and the `MUXB` to 1 to access `R1`.
- Set to 0 the write enable flag since we don’t want to store the ALU result in any register.
- Set the branch mode to 0 since we want to take into account the result of the LCU ALU in order to take the branch or not.

So, the final hex codification would be `0x05707`.

|MUXA_SEL|MUXB_SEL|BR_MODE|ALU_OP|RF_WE|RF_WSEL|INMEDIATE|
|---|---|---|---|---|---|---|
|000|001|0|1011|0|00|000111|

## Example 2: Use a value from the SRF

For example, a pseudo-assembly instruction could be `BLT R0, SRF[6], 11`. This compares the value on the local register `R0` and the value on the 6th register of the SRF, and if the first one is lower than the second one, it takes the branch to the 11th instruction on the imem. To execute properly this instruction we will need to use the LCU and the MXCU units.

In the LCU we need to specify the following:

- Set the ALU operation to `BLT`.
- Set the inmediate value to 11.
- Set `MUXA` to 0 to access `R0` and the `MUXB` to 4 to access a register of the SRF.
- Set to 0 the write enable flag since we don’t want to store the ALU result in any register.
- Set the branch mode to 0 since we want to take into account the result of the LCU ALU in order to take the branch or not.

So, the hex codification for the instruction of the LCU would be `0x1180B`.

|MUXA_SEL|MUXB_SEL|BR_MODE|ALU_OP|RF_WE|RF_WSEL|INMEDIATE|
|---|---|---|---|---|---|---|
|000|100|0|1100|0|00|001011|

In the MXCU we need to specify the number of the SRF register that is going to be accessed. So, the `RF_WSEL` option must have the value 6 and the rest of the options can have the value 0 to ensure we don’t write anything uncontrolled in any place and the operation on the ALU is a `NOP`. With this taken into account the hex codification for the MXCU instruction would be `0x180`.

|MUXA_SEL|MUXB_SEL|OPS|RF_WE|RF_WSEL|SRF_WE|SRF_WD|SRF_SEL|VWR_SEL|VWR_ROW_WE|
|---|---|---|---|---|---|---|---|---|---|
|0000|0000|000|0|000|0|00|110|00|0000|

## Example 3: Use the RC control mode

For example, a pseudo-assembly instruction could be `BNER 6`, where the `R` after the `BNE` is used to indicate the value of the branch control mode. So, this takes into account the equal values flag from the ALU of the RCs of the column to decide if the branch is taken or not. Therefore, we need to take into account the following:

- Set the ALU operation to `BNE`.
- Set the inmediate value to 6.
- Set the branch mode to 1.

The rest of the bits will be set to 0 to avoid uncontrolled writtings. So, the hex codification for the instruction would be `0x3406`.

|MUXA_SEL|MUXB_SEL|BR_MODE|ALU_OP|RF_WE|RF_WSEL|INMEDIATE|
|---|---|---|---|---|---|---|
|000|000|1|1010|0|00|000110|