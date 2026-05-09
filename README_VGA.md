# VGA + RISC-V: Estado Actual

## Resumen

El flujo activo del proyecto ya no usa `VGA_Controller` como camino principal. Ahora la salida VGA real sale desde `RISCV_Core` por medio de `vga_debug_monitor`, y muestra en pantalla:

- `PC`
- `INST`
- `X10` o `a0`

La fuente se carga desde `font128.hex`.

## Flujo vigente

La arquitectura actual es:

`RISCV_Core` -> `vga_debug_monitor` -> señales VGA

En esta versión:

- `modulosveri.sv` contiene el `RISCV_Core` con salidas VGA integradas.
- `vga_debug_monitor.sv` genera `hsync`, `vsync` y `RGB`.
- `font128.hex` contiene la fuente de 8x16 usada para dibujar texto.
- `riscv_vga_top.sv` ofrece tops opcionales de integración y prueba.

## Archivos importantes

- `modulosveri.sv`: flujo principal del CPU con VGA integrado.
- `vga_debug_monitor.sv`: monitor VGA de debug que dibuja `PC`, `INST` y `X10`.
- `riscv_vga_top.sv`: tops opcionales para integrar CPU + VGA o probar VGA sin CPU.
- `font128.hex`: ROM de fuente para los caracteres.
- `vga_controller.sv`: módulo legado, conservado como referencia.
- `tb_vga_controller.sv`: testbench legado del flujo anterior.

## Qué muestra la pantalla

El monitor VGA dibuja tres filas de debug:

- `PC: XXXXXXXX`
- `INST: XXXXXXXX`
- `X10: XXXXXXXX`

Cada `X` es un dígito hexadecimal generado directamente desde las señales internas del core.

## Cómo usarlo hoy

### Opción 1: Proyecto actual de Quartus

Si trabajas con el proyecto `modulosveri.qsf`, el `TOP_LEVEL_ENTITY` actual es `RISCV_Core`.

Necesitas tener en el proyecto:

- `modulosveri.sv`
- `vga_debug_monitor.sv`
- `font128.hex`

Además debes asignar manualmente en el `.qsf` los pines de:

- `vga_hsync`
- `vga_vsync`
- `vga_r[3:0]`
- `vga_g[3:0]`
- `vga_b[3:0]`

Nota: esas asignaciones VGA todavía no están cargadas en el `.qsf`.

### Opción 2: Top alternativo

También puedes usar `RISCV_VGA_Top` de `riscv_vga_top.sv` si prefieres un top con `KEY[]` y `SW[]` agrupados.

## Comandos de compilación

Para comprobar sintaxis con Questa:

```bash
vlog vga_debug_monitor.sv
vlog modulosveri.sv
vlog riscv_vga_top.sv
```

## Comportamiento de debug

- La VGA siempre muestra los tres campos al mismo tiempo.
- Los `HEX` siguen usando `SW[2:1]` para seleccionar qué valor ver en 7 segmentos.
- El registro mostrado en VGA está fijado hoy a `X10/a0`.
- `vga_cpu_ready` cambia con cada instrucción ejecutada con el reloj manual del botón.

## Si quieres cambiar el registro mostrado

Hoy el monitor usa:

- `reg_value(a0_val)`
- `reg_index(5'd10)`

Eso se conecta en `modulosveri.sv`. Si quieres mostrar otro registro, hay que cambiar esa conexión o exponer otra señal desde el banco de registros.

## Estado de `VGA_Controller`

`vga_controller.sv` no se usa en el camino principal actual del CPU. Se conserva para:

- referencia
- pruebas aisladas
- comparación con el flujo anterior

## Estado de simulación

- `vga_debug_monitor.sv`, `modulosveri.sv` y `riscv_vga_top.sv` compilan correctamente con `vlog`.
- `tb_vga_controller.sv` corresponde al flujo legado basado en `VGA_Controller`, no al monitor VGA actual.
