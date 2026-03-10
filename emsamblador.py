# Mapeo de instrucciones Tipo R (funct7, funct3)
# El opcode para todas las Tipo R en RV32I es siempre 0110011 (0x33)
OPCODE_R = 0x33 

TABLE_R = {
    "add":  {"f7": 0x00, "f3": 0x00},
    "sub":  {"f7": 0x20, "f3": 0x00},
    "sll":  {"f7": 0x00, "f3": 0x01},
    "slt":  {"f7": 0x00, "f3": 0x02},
    "sltu": {"f7": 0x00, "f3": 0x03},
    "xor":  {"f7": 0x00, "f3": 0x04},
    "srl":  {"f7": 0x00, "f3": 0x05},
    "sra":  {"f7": 0x20, "f3": 0x05},
    "or":   {"f7": 0x00, "f3": 0x06},
    "and":  {"f7": 0x00, "f3": 0x07},
}


def assemble_r(mnemonic, rd_idx, rs1_idx, rs2_idx):
    """
    Empaqueta una instrucción Tipo R en un entero de 32 bits.
    Formato: [f7(7) | rs2(5) | rs1(5) | f3(3) | rd(5) | opcode(7)]
    """
    data = TABLE_R[mnemonic]
    
    f7 = data["f7"]
    f3 = data["f3"]
    
    # Construcción bit a bit
    inst = (f7 << 25)      # Mueve funct7 al tope (bits 31-25)
    inst |= (rs2_idx << 20) # Mueve rs2 a los bits 24-20
    inst |= (rs1_idx << 15) # Mueve rs1 a los bits 19-15
    inst |= (f3 << 12)      # Mueve funct3 a los bits 14-12
    inst |= (rd_idx << 7)   # Mueve rd a los bits 11-7
    inst |= OPCODE_R        # Opcode en los bits 6-0
    
    return inst


# Supongamos que ya limpiaste el string y tienes los índices:
# rd=3, rs1=1, rs2=2
codigo_binario = assemble_r("sub", 3, 1, 2)

# Convertir a hexadecimal de 8 dígitos para Verilog
print(f"Hexadecimal para Verilog: {codigo_binario:08X}")
# Salida esperada: 002081B3