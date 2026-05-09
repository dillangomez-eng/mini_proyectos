import re
import sys

# =========================================================
# ENSAMBLADOR RISC-V (RV32I) - VERSIÓN INTEGRADA
# =========================================================

# 1. MAPEO DE REGISTROS (Números y nombres ABI)
REG_MAP = {f"x{i}": i for i in range(32)}
ABI_NAMES = {
    "zero": 0, "ra": 1, "sp": 2, "gp": 3, "tp": 4, "t0": 5, "t1": 6, "t2": 7,
    "s0": 8, "fp": 8, "s1": 9, "a0": 10, "a1": 11, "a2": 12, "a3": 13, 
    "a4": 14, "a5": 15, "a6": 16, "a7": 17, "s2": 18, "s3": 19, "s4": 20,
    "s5": 21, "s6": 22, "s7": 23, "s8": 24, "s9": 25, "s10": 26, "s11": 27,
    "t3": 28, "t4": 29, "t5": 30, "t6": 31
}
REG_MAP.update(ABI_NAMES)

# 2. TABLAS DE REFERENCIA (Opcodes, funct3, funct7)
OPCODE_R    = 0x33
OPCODE_I    = 0x13
OPCODE_LOAD = 0x03

TABLE_R = {
    "add":  {"f7": 0x00, "f3": 0x00}, "sub":  {"f7": 0x20, "f3": 0x00},
    "sll":  {"f7": 0x00, "f3": 0x01}, "slt":  {"f7": 0x00, "f3": 0x02},
    "sltu": {"f7": 0x00, "f3": 0x03}, "xor":  {"f7": 0x00, "f3": 0x04},
    "srl":  {"f7": 0x00, "f3": 0x05}, "sra":  {"f7": 0x20, "f3": 0x05},
    "or":   {"f7": 0x00, "f3": 0x06}, "and":  {"f7": 0x00, "f3": 0x07},
}

TABLE_I = {
    "addi":  {"f3": 0x0}, "slti":  {"f3": 0x2}, "sltiu": {"f3": 0x3},
    "xori":  {"f3": 0x4}, "ori":   {"f3": 0x6}, "andi":  {"f3": 0x7},
}

TABLE_SHIFT = {
    "slli":  {"f3": 0x1, "f7": 0x00},
    "srli":  {"f3": 0x5, "f7": 0x00},
    "srai":  {"f3": 0x5, "f7": 0x20},
}

TABLE_LOAD = {
    "lb":  {"f3": 0x0}, "lh":  {"f3": 0x1}, "lw":  {"f3": 0x2},
    "lbu": {"f3": 0x4}, "lhu": {"f3": 0x5},
}

OPCODE_S = 0x23

TABLE_S = {
    "sb": {"f3": 0x0},  # Store Byte (8 bits)
    "sh": {"f3": 0x1},  # Store Halfword (16 bits)
    "sw": {"f3": 0x2},  # Store Word (32 bits)
}

OPCODE_B = 0x63

TABLE_B = {
    "beq":  {"f3": 0x0}, # Branch if Equal
    "bne":  {"f3": 0x1}, # Branch if Not Equal
    "blt":  {"f3": 0x4}, # Branch if Less Than
    "bge":  {"f3": 0x5}, # Branch if Greater or Equal
    "bltu": {"f3": 0x6}, # Branch if Less Than (Unsigned)
    "bgeu": {"f3": 0x7}, # Branch if Greater or Equal (Unsigned)
}

TABLE_U = {
    "auipc": {"op": 0x17}, # Add Upper Immediate to PC
    "lui":   {"op": 0x37}, # Load Upper Immediate
}

LABEL_DEF_RE = re.compile(r"^\s*([A-Za-z_.$][\w.$]*):\s*(.*)$")
PCREL_HI_RE = re.compile(r"(?P<label>[A-Za-z_.$][\w.$]*)\[31:12\]")
PCREL_LO_RE = re.compile(r"(?P<label>[A-Za-z_.$][\w.$]*)\[11:0\]")

# 3. FUNCIONES AUXILIARES  
def get_reg(name):
    name = str(name).lower().replace(',', '').strip()
    if name in REG_MAP: return REG_MAP[name]
    if name.startswith('x') and name[1:].isdigit(): return int(name[1:])
    raise ValueError(f"Error: Registro '{name}' no reconocido.")

def clean_imm(value, bits=12):
    """Maneja el complemento a dos para números negativos."""
    mask = (1 << bits) - 1
    return int(value) & mask

def calcular_pcrel_hi_lo(destino, pc_base):
    """
    Divide un offset relativo al PC en la pareja usada por AUIPC + instrucción tipo I.
    """
    offset = destino - pc_base
    hi20 = (offset + 0x800) >> 12
    lo12 = offset - (hi20 << 12)
    return hi20, lo12

# 4. FUNCIONES DE ENSAMBLADO (BIT-PACKING)   
def assemble_r(mnemonic, rd, rs1, rs2):      
    data = TABLE_R[mnemonic]                 
    inst = (data["f7"] << 25) | (rs2 << 20) | (rs1 << 15) | (data["f3"] << 12) | (rd << 7) | OPCODE_R
    return inst

def assemble_i(mnemonic, rd, rs1, imm, opcode):
    """Corregida para manejar jalr y cualquier otra instrucción tipo I"""
    if mnemonic in TABLE_I: f3 = TABLE_I[mnemonic]["f3"]
    elif mnemonic in TABLE_LOAD: f3 = TABLE_LOAD[mnemonic]["f3"]
    elif mnemonic == "jalr": f3 = 0x0  # El f3 de JALR siempre es 0
    else: f3 = 0x0 # Default
    
    imm_12 = clean_imm(imm, 12)
    inst = (imm_12 << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | opcode
    return inst
    
   

def assemble_shift(mnemonic, rd, rs1, shamt):
    data = TABLE_SHIFT[mnemonic]
    shamt_5 = int(shamt) & 0x1F
    inst = (data["f7"] << 25) | (shamt_5 << 20) | (rs1 << 15) | (data["f3"] << 12) | (rd << 7) | OPCODE_I
    return inst

def assemble_s(mnemonic, rs2, rs1, imm):
    """
    Empaqueta instrucciones sb, sh, sw.
    Formato: [imm[11:5] | rs2 | rs1 | f3 | imm[4:0] | op]
    """
    f3 = TABLE_S[mnemonic]["f3"]
    imm_12 = clean_imm(imm, 12)
    
    # Partimos el inmediato
    imm_4_0 = imm_12 & 0x1F          # Los 5 bits más bajos
    imm_11_5 = (imm_12 >> 5) & 0x7F  # Los 7 bits más altos
    
    # Construcción
    inst = (imm_11_5 << 25)  # Bits 31-25
    inst |= (rs2 << 20)      # Bits 24-20
    inst |= (rs1 << 15)      # Bits 19-15
    inst |= (f3 << 12)       # Bits 14-12
    inst |= (imm_4_0 << 7)   # Bits 11-7
    inst |= OPCODE_S         # Bits 6-0
    
    return inst

def assemble_b(mnemonic, rs1, rs2, imm):
    """
    Empaqueta instrucciones Tipo B.
    imm es el offset relativo (debe ser múltiplo de 2).
    """
    f3 = TABLE_B[mnemonic]["f3"]
    # El inmediato en Tipo B es de 13 bits (pero el bit 0 no se guarda)
    imm_13 = clean_imm(imm, 13)
    
    # Extracción de pedazos (bitmasking)
    i12   = (imm_13 >> 12) & 0x1    # Bit 12
    i11   = (imm_13 >> 11) & 0x1    # Bit 11
    i10_5 = (imm_13 >> 5)  & 0x3F   # Bits 10 al 5
    i4_1  = (imm_13 >> 1)  & 0xF    # Bits 4 al 1
    
    # Construcción según el estándar
    inst = (i12 << 31)     # Bit 31
    inst |= (i10_5 << 25)  # Bits 30-25
    inst |= (rs2 << 20)    # Bits 24-20
    inst |= (rs1 << 15)    # Bits 19-15
    inst |= (f3 << 12)     # Bits 14-12
    inst |= (i4_1 << 8)    # Bits 11-8
    inst |= (i11 << 7)     # Bit 7
    inst |= OPCODE_B       # Bits 6-0
    
    return inst

def assemble_u(mnemonic, rd, imm):
    """
    Empaqueta instrucciones lui y auipc.
    imm es un valor de 20 bits.
    """
    opcode = TABLE_U[mnemonic]["op"]
    
    # Limpiamos el inmediato a 20 bits (0xFFFFF)
    imm_20 = int(imm) & 0xFFFFF
    
    # Construcción: el inmediato va del bit 12 al 31
    inst = (imm_20 << 12) | (rd << 7) | opcode
    
    return inst

OPCODE_J = 0x6F
OPCODE_JALR = 0x67
def assemble_j(mnemonic, rd, imm):
    """Empaqueta la instrucción jal."""
    imm_21 = clean_imm(imm, 21)
    
    # Extracción de pedazos (¡Cuidado con el orden!)
    i20    = (imm_21 >> 20) & 0x1    # Bit 20
    i19_12 = (imm_21 >> 12) & 0xFF   # Bits 19-12
    i11    = (imm_21 >> 11) & 0x1    # Bit 11
    i10_1  = (imm_21 >> 1)  & 0x3FF  # Bits 10-1
    
    # Construcción
    inst = (i20 << 31)     # Bit 31
    inst |= (i10_1 << 21)  # Bits 30-21
    inst |= (i11 << 20)    # Bit 20
    inst |= (i19_12 << 12) # Bits 19-12
    inst |= (rd << 7)      # Bits 11-7
    inst |= OPCODE_J       # Bits 6-0
    
    return inst


def expandir_pseudo_instruccion(linea):
    """
    Toma una línea de ensamblador y devuelve una lista con las instrucciones base.
    Devuelve una lista porque algunas pseudo-instrucciones (como 'li' o 'call') 
    se expanden en 2 instrucciones separadas.
    """
    # Limpiamos la línea de comas y la dividimos en palabras
    partes = linea.replace(',', ' ').split()
    if not partes:
        return [linea]
 #  addi    sp,sp,0
    op = partes[0]
    args = partes[1:]

    # ==========================================
    # 1. Operaciones Básicas (Imagen 2)
    # ==========================================
    if op == "nop":
        return ["addi x0, x0, 0"]
    elif op == "mv":
        return [f"addi {args[0]}, {args[1]}, 0"]
    elif op == "not":
        return [f"xori {args[0]}, {args[1]}, -1"]
    elif op == "neg":
        return [f"sub {args[0]}, x0, {args[1]}"]
    
    # Manejo básico de 'li' (Load Immediate)
    elif op == "li":
        rd = args[0]
        imm = int(args[1], 0) # Acepta decimal o hexadecimal
        # Si cabe en 12 bits, usamos un addi simple
        if -2048 <= imm <= 2047:
            return [f"addi {rd}, x0, {imm}"]
        else:
            # Si es más grande, dividimos en lui (20 bits) y addi (12 bits)
            upper = (imm + 0x800) >> 12
            lower = imm & 0xFFF
            return [f"lui {rd}, {upper}", f"addi {rd}, {rd}, {lower}"]

    # ==========================================
    # 2. Comparaciones (Imagen 3)
    # ==========================================
    elif op == "seqz":
        return [f"sltiu {args[0]}, {args[1]}, 1"]
    elif op == "snez":
        return [f"sltu {args[0]}, x0, {args[1]}"]
    elif op == "sltz":
        return [f"slt {args[0]}, {args[1]}, x0"]
    elif op == "sgtz":
        return [f"slt {args[0]}, x0, {args[1]}"]

    # ==========================================
    # 3. Saltos Condicionales contra Cero (Imagen 4)
    # ==========================================
    elif op == "beqz":
        return [f"beq {args[0]}, x0, {args[1]}"]
    elif op == "bnez":
        return [f"bne {args[0]}, x0, {args[1]}"]
    elif op == "blez":
        return [f"bge x0, {args[0]}, {args[1]}"]
    elif op == "bgez":
        return [f"bge {args[0]}, x0, {args[1]}"]
    elif op == "bltz":
        return [f"blt {args[0]}, x0, {args[1]}"]
    elif op == "bgtz":
        return [f"blt x0, {args[0]}, {args[1]}"]

    # ==========================================
    # 4. Saltos Invertidos y Jumps (Imagen 5)
    # ==========================================
    elif op == "bgt":
        return [f"blt {args[1]}, {args[0]}, {args[2]}"]
    elif op == "ble":
        return [f"bge {args[1]}, {args[0]}, {args[2]}"]
    elif op == "bgtu":
        return [f"bltu {args[1]}, {args[0]}, {args[2]}"]
    elif op == "bleu":
        return [f"bgeu {args[1]}, {args[0]}, {args[2]}"]
    
    elif op == "j":
        return [f"jal x0, {args[0]}"]
    elif op == "jal" and len(args) == 1:
        return [f"jal x1, {args[0]}"]
    elif op == "jr":
        return [f"jalr x0, {args[0]}, 0"]
    elif op == "jalr" and len(args) == 1:
        return [f"jalr x1, {args[0]}, 0"]
    elif op == "ret":
        return ["jalr x0, x1, 0"]
    
    # Call y Tail (Sustitución de strings base)
    elif op == "call":
        return [f"auipc x1, {args[0]}[31:12]", f"jalr x1, x1, {args[0]}[11:0]"]
    elif op == "tail":
        return [f"auipc x6, {args[0]}[31:12]", f"jalr x0, x6, {args[0]}[11:0]"]

    
    # ==========================================
    # 5. Cargas en Memoria (Imagen 1)
    # ==========================================
    elif op == "la":
        return [f"auipc {args[0]}, {args[1]}[31:12]", f"addi {args[0]}, {args[0]}, {args[1]}[11:0]"]
    # Para Load globales (lb, lh, lw, )
    elif op in ["lb", "lh", "lw", ] and len(args) == 2 and not "(" in args[1]:
        return [f"auipc {args[0]}, {args[1]}[31:12]", f"{op} {args[0]}, {args[1]}[11:0]({args[0]})"]
    # Para Store globales (sb, sh, sw, )
    elif op in ["sb", "sh", "sw", ] and len(args) == 3 and not "(" in args[2]:
        return [f"auipc {args[2]}, {args[1]}[31:12]", f"{op} {args[0]}, {args[1]}[11:0]({args[2]})"]

    # Si no coincide con ninguna pseudo-instrucción, la devolvemos intacta
      
    return [linea]

# 5. PROCESADOR DE LÍNEAS (PARSER)
def assemble_line(line):
    line = line.split('#')[0].strip() # Quitar comentarios
    if not line: return None
    
    # Normalizar separadores: comas y paréntesis a espacios
    line_clean = line.replace(',', ' ').replace('(', ' ').replace(')', ' ').replace('[', ' ').replace(']', ' ')
    tokens = line_clean.split()
    mnemonic = tokens[0].lower()
    
    try:
        # --- TIPOS R, SHIFT, I, LOAD, S, B, U, J (Ya los tienes) ---
        if mnemonic in TABLE_R:
            return assemble_r(mnemonic, get_reg(tokens[1]), get_reg(tokens[2]), get_reg(tokens[3]))
        elif mnemonic in TABLE_SHIFT:
            return assemble_shift(mnemonic, get_reg(tokens[1]), get_reg(tokens[2]), tokens[3])
        elif mnemonic in TABLE_I:
            return assemble_i(mnemonic, get_reg(tokens[1]), get_reg(tokens[2]), tokens[3], OPCODE_I)
        elif mnemonic in TABLE_LOAD:
            return assemble_i(mnemonic, get_reg(tokens[1]), get_reg(tokens[3]), tokens[2], OPCODE_LOAD)
        elif mnemonic in TABLE_S:
            return assemble_s(mnemonic, get_reg(tokens[1]), get_reg(tokens[3]), tokens[2])
        elif mnemonic in TABLE_B:
            return assemble_b(mnemonic, get_reg(tokens[1]), get_reg(tokens[2]), int(tokens[3]))
        elif mnemonic in TABLE_U:
            return assemble_u(mnemonic, get_reg(tokens[1]), tokens[2])
        elif mnemonic == "jal":
            return assemble_j(mnemonic, get_reg(tokens[1]), int(tokens[2]))
        elif mnemonic == "jalr":
            # jalr rd, rs1, imm
            return assemble_i(mnemonic, get_reg(tokens[1]), get_reg(tokens[2]), tokens[3], OPCODE_JALR)
        elif mnemonic == "ebreak":
            return 0x00100073  # Valor hexadecimal fijo para ebreak en RV32I 
        else:
            print(f"Instrucción desconocida: {mnemonic}")
            return None
    except Exception as e:
        print(f"Error procesando línea '{line}': {e}")
        return None

# =========================================================
# 4.5. ENSAMBLADOR DE DOS PASADAS (RESOLVER ETIQUETAS)
# =========================================================
def resolver_etiquetas(instrucciones):
    """Pasa 1: Encuentra las etiquetas. Pasa 2: Calcula los saltos."""
    tabla_etiquetas = {}
    pc = 0
    lineas_limpias = []

    # --- PASADA 1: Encontrar las etiquetas y guardar su dirección ---
    for linea in instrucciones:
        linea = linea.strip()
        if not linea: continue

        # Si encontramos dos puntos, es una etiqueta (ej. ".L3:")
        etiqueta_match = LABEL_DEF_RE.match(linea)
        if etiqueta_match:
            nombre_etiqueta = etiqueta_match.group(1).strip()
            tabla_etiquetas[nombre_etiqueta] = pc
            
            # Si hay código en la misma línea (ej. ".L2: addi a0, a0, 1")
            resto = etiqueta_match.group(2).strip()
            if resto:
                lineas_limpias.append(resto)
                pc += 4 # Avanza 4 bytes
        else:
            lineas_limpias.append(linea)
            pc += 4

    # --- PASADA 2: Cambiar el nombre de la etiqueta por la distancia en bytes ---
    codigo_final = []
    pc_actual = 0
    ultimo_pcrel_hi = None
    
    for linea in lineas_limpias:
        hi_match = PCREL_HI_RE.search(linea)
        lo_match = PCREL_LO_RE.search(linea)

        if hi_match:
            etiqueta = hi_match.group("label")
            ultimo_pcrel_hi = None
            if etiqueta in tabla_etiquetas:
                hi20, _ = calcular_pcrel_hi_lo(tabla_etiquetas[etiqueta], pc_actual)
                linea = PCREL_HI_RE.sub(str(hi20), linea, count=1)
                ultimo_pcrel_hi = {"label": etiqueta, "pc": pc_actual}
        elif lo_match:
            etiqueta = lo_match.group("label")
            if etiqueta in tabla_etiquetas:
                pc_base = pc_actual
                if (
                    ultimo_pcrel_hi
                    and ultimo_pcrel_hi["label"] == etiqueta
                    and ultimo_pcrel_hi["pc"] == pc_actual - 4
                ):
                    pc_base = ultimo_pcrel_hi["pc"]
                _, lo12 = calcular_pcrel_hi_lo(tabla_etiquetas[etiqueta], pc_base)
                linea = PCREL_LO_RE.sub(str(lo12), linea, count=1)
            ultimo_pcrel_hi = None
        else:
            ultimo_pcrel_hi = None

        tokens = linea.replace(',', ' ').split()
        if not tokens: continue
        
        # Revisamos si el último argumento de la línea es una etiqueta conocida
        ultimo_arg = tokens[-1]
        if ultimo_arg in tabla_etiquetas:
            destino = tabla_etiquetas[ultimo_arg]
            
            # MAGIA: Calculamos el offset (Destino - Origen)
            offset = destino - pc_actual
            
            # Reemplazamos el nombre por el número calculado
            tokens[-1] = str(offset)
            
            # Volvemos a armar la línea
            nueva_linea = f"{tokens[0]} " + ", ".join(tokens[1:])
            codigo_final.append(nueva_linea)
        else:
            codigo_final.append(linea)
            
        pc_actual += 4
        
    return codigo_final

def generar_archivo_hex(instructions, nombre_archivo="programa.hex"):
    """Genera un archivo .hex limpio con las instrucciones en formato hexadecimal"""
    print(f"Generando archivo {nombre_archivo}...")
    
    # 1. Expandimos las pseudo-instrucciones primero
    instrucciones_expandidas = []
    for line in instructions:
        clean_line = line.split('#')[0].strip()
        if not clean_line:
            continue
        instrucciones_expandidas.extend(expandir_pseudo_instruccion(clean_line))
        
    # 2. CALCULAMOS LAS ETIQUETAS (El nuevo paso)
    instrucciones_listas = resolver_etiquetas(instrucciones_expandidas)
        
    # 3. Abrimos el archivo y guardamos los hexadecimales
    with open(nombre_archivo, "w") as f:
        for line in instrucciones_listas:
            resultado = assemble_line(line)
            if resultado is not None:
                f.write(f"{resultado:08x}\n")
                
    print(f"¡Archivo '{nombre_archivo}' generado con éxito!")


def leer_archivo_asm(ruta):
    """Abre un archivo de texto y devuelve una lista con sus líneas."""
    try:
        with open(ruta, "r") as archivo:
            # Leemos las líneas y quitamos los saltos de línea (\n)
            return [linea.strip() for linea in archivo.readlines()]
    except FileNotFoundError:
        print(f"❌ ERROR: No se pudo encontrar el archivo '{ruta}'.")
        print("Asegúrate de que exista en la misma carpeta que tu script de Python.")
        return []
# =========================================================
# PRUEBA DEL ENSAMBLADOR CON PSEUDO-INSTRUCCIONES Y SALIDA .HEX
# =========================================================
if __name__ == "__main__":
    # 1. Elegir qué archivo leer
  
    if len(sys.argv) > 1:
        archivo_entrada = sys.argv[1]
    else:
        # Si solo le das a "Run" en tu editor, buscará este archivo por defecto
        archivo_entrada = "test1.txt" 
        
    # 2. Leer el archivo
    
    mi_codigo_asm = leer_archivo_asm(archivo_entrada)
    
    # Si el archivo estaba vacío o no existe, detenemos el programa
    if not mi_codigo_asm:
        sys.exit()
        
    print(f"=== ENSAMBLANDO ARCHIVO: {archivo_entrada} ===")
    print(f"{'INSTRUCCIÓN (Expandida)':<30} | {'HEXADECIMAL'}")
    print("-" * 50)
    
    # 3. Expandir pseudo-instrucciones
    instrucciones_expandidas = []
    for linea in mi_codigo_asm:
        clean_line = linea.split('#')[0].strip()
        if clean_line:
            instrucciones_expandidas.extend(expandir_pseudo_instruccion(clean_line))
            
    # 4. Resolver Etiquetas (El paso mágico de las 2 pasadas)
    instrucciones_finales = resolver_etiquetas(instrucciones_expandidas)
    
    # 5. Ensamblar e Imprimir en consola
    for linea in instrucciones_finales:
        resultado = assemble_line(linea)
        if resultado is not None:
            print(f"{linea.strip():<30} | {resultado:08X}")
     
    print("\n--- CREACIÓN DEL ARCHIVO ---")
    generar_archivo_hex(mi_codigo_asm, "programa.hex")
