# Inicio Rápido

## Flujo recomendado

El camino principal actual es:

`RISCV_Core` + `vga_debug_monitor` + `font128.hex`

No necesitas `VGA_Controller` para ver `PC`, `INST` y `X10` en pantalla.

## Archivos mínimos

Ten disponibles estos archivos:

- `modulosveri.sv`
- `vga_debug_monitor.sv`
- `font128.hex`

Opcionales:

- `riscv_vga_top.sv`
- `vga_controller.sv`
- `tb_vga_controller.sv`

## Paso 1: Agrega archivos al proyecto

En Quartus agrega:

- `modulosveri.sv`
- `vga_debug_monitor.sv`

Y asegúrate de que `font128.hex` quede en el directorio del proyecto.

## Paso 2: Elige el top

Si usas el proyecto actual `modulosveri.qsf`, el top es:

- `RISCV_Core`

Si quieres un top alternativo, puedes usar:

- `RISCV_VGA_Top`

## Paso 3: Asigna pines VGA

Debes mapear manualmente:

- `vga_hsync`
- `vga_vsync`
- `vga_r[3:0]`
- `vga_g[3:0]`
- `vga_b[3:0]`

Nota: esos pines VGA todavía no están cargados en el `.qsf`.

## Paso 4: Compila

```bash
vlog vga_debug_monitor.sv
vlog modulosveri.sv
vlog riscv_vga_top.sv
```

En Quartus compila normalmente después de agregar archivos y pines.

## Paso 5: Programa la FPGA

Después de compilar:

1. abre `Programmer`
2. carga el `.sof`
3. programa la placa

## Qué deberías ver

En el monitor VGA:

- `DEBUG VGA`
- `PC:`
- `INST:`
- `X10:`

En los displays `HEX`:

- `SW[2]=1` muestra instrucción
- `SW[1]=1` muestra `a0`
- sin esos switches muestra `PC`

## Prueba rápida de sintaxis

Para validar sin entrar todavía a Quartus:

```bash
vlog vga_debug_monitor.sv modulosveri.sv riscv_vga_top.sv
```

## Si no aparece imagen

Revisa:

1. pines VGA
2. presencia de `font128.hex`
3. top-level correcto
4. monitor conectado a VGA real

## Sobre los archivos legados

Estos archivos siguen en el repositorio pero ya no son el flujo principal:

- `vga_controller.sv`
- `tb_vga_controller.sv`

Úsalos solo si quieres comparar con el diseño anterior o hacer pruebas aisladas.
