# Integración Actual: VGA + CPU RISC-V

## Objetivo

El flujo actual está orientado a depuración por VGA. En lugar de escribir texto desde software a una RAM de caracteres, el sistema genera directamente en pantalla tres señales internas del core:

- `PC`
- `INST`
- `X10/a0`

## Módulos que participan

### `modulosveri.sv`

Contiene el `RISCV_Core` y el llamado principal al monitor VGA.

### `vga_debug_monitor.sv`

Genera:

- reloj de píxel a 25 MHz
- `hsync`
- `vsync`
- `red`, `green`, `blue`
- `frame_pulse`
- `line_pulse`

Además convierte a texto hexadecimal:

- `pc`
- `inst`
- `reg_value`

usando la fuente cargada desde `font128.hex`.

### `font128.hex`

Archivo ROM con la fuente 8x16 usada por el monitor.

## Integración dentro del core

La integración activa se hace dentro de `RISCV_Core`, no por fuera.

El monitor se conecta con estas señales:

```systemverilog
vga_debug_monitor debug_vga (
    .clk50(CLOCK_50),
    .reset(reset),
    .pc(pc),
    .inst(inst),
    .reg_value(a0_val),
    .reg_index(5'd10),
    .frame_pulse(vga_frame_pulse_int),
    .line_pulse(vga_line_pulse_int),
    .hsync(vga_hsync),
    .vsync(vga_vsync),
    .red(vga_r),
    .green(vga_g),
    .blue(vga_b)
);
```

Eso significa:

- `PC` sale de la señal `pc`
- `INST` sale de la señal `inst`
- el registro mostrado es `a0`, expuesto como `a0_val`

## Qué se ve en pantalla

El monitor dibuja:

```text
DEBUG VGA

PC:   XXXXXXXX
INST: XXXXXXXX
X10:  XXXXXXXX
```

Los valores cambian conforme avanza la CPU.

## Señales de salida del core

`RISCV_Core` exporta:

- `vga_hsync`
- `vga_vsync`
- `vga_r[3:0]`
- `vga_g[3:0]`
- `vga_b[3:0]`
- `vga_cpu_ready`
- `vga_frame_done`
- `vga_line_done`

## Sobre `cpu_ready`

En el flujo actual, `vga_cpu_ready` se usa como señal de debug y cambia con cada instrucción ejecutada por el reloj manual.

No controla la generación de video. La VGA corre continuamente con `CLOCK_50`.

## Sobre `frame_done` y `line_done`

Estas señales salen del monitor VGA:

- `vga_frame_done`: pulso al terminar un frame
- `vga_line_done`: pulso al terminar una línea

Sirven para debug o sincronización adicional.

## Fuente y caracteres

La ROM se carga con:

```systemverilog
$readmemh("font128.hex", font_rom);
```

Por eso es importante que `font128.hex` esté disponible en el proyecto o en el directorio de simulación.

## Cómo cambiar el registro mostrado

Hoy el monitor está fijo a `X10/a0`.

Si quieres mostrar otro registro:

1. expón ese valor desde `RegisterFile` o desde el datapath
2. cambia `reg_value(...)` en la instancia del monitor
3. cambia también `reg_index(...)`

Ejemplo:

```systemverilog
.reg_value(s1_val),
.reg_index(5'd9)
```

## Diferencia con el flujo antiguo

El flujo anterior usaba `VGA_Controller` y una RAM de texto escrita desde software.

Ese flujo ya no es el principal. Sigue en el repositorio como referencia en:

- `vga_controller.sv`
- `tb_vga_controller.sv`

## Compilación recomendada

```bash
vlog vga_debug_monitor.sv
vlog modulosveri.sv
vlog riscv_vga_top.sv
```

## Pendientes para FPGA

Antes de verlo en placa todavía falta:

1. asignar pines VGA en el `.qsf`
2. asegurar que `font128.hex` esté incluido en el proyecto
3. programar la FPGA con el top que elijas

## Nota sobre tops

- `RISCV_Core`: top actual del proyecto `modulosveri.qsf`
- `RISCV_VGA_Top`: top alternativo
- `VGA_Only_Top`: prueba del monitor VGA sin CPU real
