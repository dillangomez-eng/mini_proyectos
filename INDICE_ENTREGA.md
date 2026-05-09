# Índice de Entrega

## Estado actual del proyecto

La integración principal quedó basada en:

- `RISCV_Core` como datapath principal
- `vga_debug_monitor.sv` como salida VGA activa
- `font128.hex` como fuente de caracteres

## Archivos principales

### `modulosveri.sv`

Archivo principal del CPU.

Incluye:

- lógica del `RISCV_Core`
- señales `pc`, `inst` y `a0_val`
- integración directa con `vga_debug_monitor`
- salidas VGA hacia la FPGA

### `vga_debug_monitor.sv`

Monitor VGA activo del proyecto.

Responsabilidades:

- generar video `640x480 @ 60 Hz`
- mostrar `PC`
- mostrar `INST`
- mostrar `X10/a0`
- cargar la fuente desde `font128.hex`

### `riscv_vga_top.sv`

Tops alternativos.

Incluye:

- `RISCV_VGA_Top`
- `VGA_Only_Top`

Ambos ya usan el monitor VGA nuevo.

## Archivos de apoyo

- `font128.hex`: fuente 8x16
- `README_VGA.md`: resumen actualizado
- `VGA_INTEGRACION.md`: integración técnica actual
- `INICIO_RAPIDO.md`: arranque rápido
- `ARQUITECTURA_SISTEMA.md`: arquitectura resumida

## Archivos legados

Estos ya no forman el flujo principal:

- `vga_controller.sv`
- `tb_vga_controller.sv`

Se mantienen como referencia o para pruebas separadas.

## Compilación

Archivos recomendados para compilar:

- `modulosveri.sv`
- `vga_debug_monitor.sv`
- `riscv_vga_top.sv`

## Qué falta para FPGA

Pendientes importantes:

1. asignar pines VGA en el `.qsf`
2. validar el cableado físico hacia el conector VGA
3. probar en placa con `font128.hex` presente

## Resultado esperado

La salida VGA debe mostrar:

- `PC`
- `INST`
- `X10`

Y los displays `HEX` siguen siendo útiles para debug adicional.
