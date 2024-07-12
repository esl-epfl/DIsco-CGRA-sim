# Multiplexer Control Unit (MXCU)

The Multiplexer Control Unit (MXCU) computes the slice of the VWR (out of 32 slices) that each RC executes at a time. It also computes which SRF line is used to load/store values on/from the RCs, the LCU or the LSU. And, it has 8 local registers.

# Instruction format

The instructions for the MXCU have a size of 27 bits with the following structure.

|MUXA_SEL|MUXB_SEL|OPS|RF_WE|RF_WSEL|SRF_WE|SRF_WD|SRF_SEL|VWR_SEL|VWR_ROW_WE|
|---|---|---|---|---|---|---|---|---|---|
|26:23|22:19|18:16|15|14:12|11|10:9|8:6|5:4|3:0|

- MUX{A/B}_SEL (4 bits) : Select inputs to the ALU.
    
    |Value|MUXA/MUXB|
    |---|---|
    |0-7|R0-R7|
    |8|SRF|
    |9|0|
    |10|1|
    |11|2|
    |12|HALF|
    |13|LAST|
    |14|0|
    |15|0|
    
    The `LAST` option is the maximum index to access in each RC slice of VWR. For example, for an architecture with 4 RCs per column and a VWR size of 128 elements, each RC would have access to 32 elements of the VWR. So, the `LAST` value would be 31, as it is the maximum index that can be accessed by each RC.
    
    Similarly, the `HALF` options is the index to access the element in the middle position of the VWR slice. So, in the same architecture example as above, this would be 32/2 -1 = 15.
    
- OPS (3 bits): ALU operations for MXCU ALU.
    
    |Value|Operation|Description|
    |---|---|---|
    |0|NOP|No operation|
    |1|SADD|Signed addition|
    |2|SSUB|Signed substraction|
    |3|SLL|Shift left logical|
    |4|SRL|Shift right logical|
    |5|LAND|Logical AND|
    |6|LOR|Logical OR|
    |7|LXOR|Logical XOR|
    
- RF_WE (1 bit): Enable writing to local registers.
- RF_WSEL (3 bits): Select one of 8 MXCU local registers to write to. These registers have special “jobs”:
    
    |Register|Description|
    |---|---|
    |R0|Index of the VWR entry passed to the RCs datapath|
    |R5|VWR_A mask (vwr_sel=R0&R5)|
    |R6|VWR_B mask (vwr_sel=R0&R6)|
    |R7|VWR_C mask (vwr_sel=R0&R7)|
    
> [!NOTE]  
> The mask registers (R5-R7) can be used to access diferent indexes of diferent VWR at the same cycle. For example, let’s consider the assembly instruction `SADD VWR_C, VWR_A, VWR_B` where i<sub>c</sub>, i<sub>a</sub> and i<sub>b</sub> are the indexes that are going to be accessed by each RC from their slice. This indexes are obtained combining the value on `R0` and the value of `R5`, `R6` and `R7` with a logical and operation to obtain  i<sub>a</sub>,  i<sub>b</sub> and  i<sub>c</sub>, respectively.
    
- SRF_WE (1 bit): Write enable to the SRF.
- SRF_WD (2 bits): Decide which ALU result to write to selected SRF register.
    
    |Value|ALU result from|
    |---|---|
    |0|LCU|
    |1|RC0|
    |2|MXCU|
    |3|LSU|
    
    Notice that only `RC0` among the RCs can write to the SRF.
    
- SRF_SEL (3 bits): Select one of 8 SRF registers to read/write to.
- VWR_SEL (2 bits): Select the VWR to write RC ALU outputs to.
    
    |Value|Destination|
    |---|---|
    |0|VWR_A|
    |1|VWR_B|
    |2|VWR_C|
    
- VWR_ROW_WE (4 bits): one-hot encoded write enable to the four rows (VWR slices).