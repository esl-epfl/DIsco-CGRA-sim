# Load-Store Unit

The Load-Store Unit (LSU) is responsible for generating the bank of the SPM to write into a very wide register (VWR), or to write from a VWR back to the SPM. It also takes care of shuffling the values in VWRs A and B and storing the result into VWR C. It has 8 local registers, of which register 7 holds the number of the line of the SPM for LOAD and STORE operations. `R7` is initialized with the SPM line that contains the SRF data.

## Instruction format

The instructions for the LSU have a size of 20 bits with the following structure.

|MEM_OP|VWR_SEL/SHUF_OP|MUXA_SEL|MUXB_SEL|ALU_OP|RF_WE|RF_WSEL|
|---|---|---|---|---|---|---|
|19:18|17:15|14:11|10:7|6:4|3|2:0|

- MEM_OP (2 bits): Choose the memory operation to be done.
    
    |Code|Operation|Description|
    |---|---|---|
    |0|NOP|No operation|
    |1|LOAD|Load line from SPM to VWR|
    |2|STORE|Store VWR to SPM line|
    |3|SHUFFLE|Shuffle data from VWR A and B and store the result in C|
    
- VWR_SEL/SHUF_OP (3 bits): Depending on the input `MEM_OP`, either choose a VWR/SRF to write to/from, or select a shuffle operation.
    - In the case of VWR LOAD/STORE:
        
        |Code|Register|
        |---|---|
        |0|VWR A|
        |1|VWR B|
        |2|VWR C|
        |3|SRF|
        
        Be aware taht the SRF has 8 registers, so if the `SRF` option is chosen only the first 8 elements of the SPM line will be loaded/stored.
        
    - In the case of shuffling:
        
        |Code|Operation|
        |---|---|
        |0|VWRA and VWRB interleaving upper part|
        |1|VWRA and VWRB interleaving lower part|
        |2|VWRA and VWRB even indexes|
        |3|VWRA and VWRB odd indexes|
        |4|VWRA and VWRB concatenated bit reversal upper part|
        |5|VWRA and VWRB concatenated bit reversal lower part|
        |6|VWRA and VWRB concatenated slice circular shift up upper part|
        |7|VWRA and VWRB concatenated slice circular shift up lower part|
        
- MUX{A/B}_SEL (4 bits) : select inputs to ALU.
    
    |MUX{A/B}_SEL|MUXA/MUXB|
    |---|---|
    |0-7|R0-R7|
    |8|SRF|
    |9|0|
    |10|1|
    |11|2|
    |12-15|0|
    
- ALU_OP (3 bits): ALU operation to perform between `MUXA` and `MUXB` results.
    
    |Code|Operation|Description|
    |---|---|---|
    |0|LAND|Logical AND|
    |1|LOR|Logical OR|
    |2|LXOR|Logical XOR|
    |3|SADD|Signed addition|
    |4|SSUB|Signed substraction|
    |5|SLL|Shift left logical|
    |6|SRL|Shift right logical|
    |7|BITREV|Bit reversal operation|
    
    The bit reversal operation reverses the bit order of operand a and shifts it by the amount indicated in operand b.
    
- RF_WE (1 bit): Enable writing to LSU registers.
- RF_WSEL (3 bits): One of the 8 LSU registers to write ALU result to.