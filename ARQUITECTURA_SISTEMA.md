# Arquitectura del Sistema VGA + RISC-V

## Vista general

La arquitectura activa del proyecto es:

```text
CLOCK_50 --------------------------+
                                   |
                                   v
                             vga_debug_monitor
                                   |
                                   +--> hsync
                                   +--> vsync
                                   +--> RGB

clk_button --> clk_cpu --> RISCV_Core
                           |
                           +--> pc
                           +--> inst
                           +--> a0_val
                           |
                           +--> vga_debug_monitor
```

## Idea central

La VGA ya no depende de una RAM de texto escrita por software.

Ahora el monitor:

1. toma señales internas del core
2. las convierte a ASCII hexadecimal
3. busca los bits del carácter en `font128.hex`
4. dibuja directamente la información en pantalla

## Señales que alimentan la VGA

Desde `RISCV_Core` se conectan:

- `pc`
- `inst`
- `a0_val`

Eso permite ver el estado del procesador sin necesidad de que el programa RISC-V escriba texto en memoria VGA.

## Campos mostrados

La salida VGA presenta tres zonas:

```text
DEBUG VGA

PC:   XXXXXXXX
INST: XXXXXXXX
X10:  XXXXXXXX
```

## Fuente de caracteres

La fuente usada es `font128.hex`.

Cada carácter usa una malla `8x16`, y el monitor calcula:

- fila de carácter
- columna de carácter
- fila interna del glifo
- columna interna del glifo

## Temporización VGA

Se mantiene el esquema estándar:

- resolución visible: `640x480`
- reloj de píxel: `25 MHz`
- horizontal total: `800`
- vertical total: `525`

## Debug adicional

Además de la salida VGA:

- `HEX` sigue mostrando valores seleccionados por switches
- `vga_cpu_ready` cambia con cada instrucción ejecutada
- `vga_frame_done` y `vga_line_done` salen como pulsos auxiliares

## Tops disponibles

- `RISCV_Core`: top actual del proyecto `modulosveri.qsf`
- `RISCV_VGA_Top`: top alternativo de integración
- `VGA_Only_Top`: prueba del monitor VGA con valores sintéticos

## Módulos legados

`vga_controller.sv` pertenece al flujo anterior basado en modo texto con RAM de caracteres.

Sigue en el repositorio como referencia, pero no es la arquitectura principal actual.

## Pendiente de hardware

La arquitectura lógica ya está integrada, pero falta:

1. asignar pines VGA en el `.qsf`
2. validar la conexión física del monitor
3. probar el diseño en FPGA
