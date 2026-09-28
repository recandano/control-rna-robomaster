---
layout: default
title: Control en lazo cerrado
parent: Reporte del proyecto
nav_order: 3
permalink: /control-rna/control/
---

# Control en lazo cerrado

## Idea general

Después de entrenar las redes, el objetivo fue utilizar la RNA inversa como parte de un controlador físico.

El ciclo implementado es:

`VICON → pose actual → error → controlador → RNA inversa → RPM → RoboMaster`

y nuevamente:

`RoboMaster → VICON`

Este lazo se ejecuta aproximadamente cada 0.05 s, es decir, a 20 Hz.
```mermaid
flowchart LR
    A[Referencia x, y, yaw] --> B[Error de pose]
    B --> C[PI + Feedforward]
    C --> D[RNA inversa]
    D --> E[RPM w1 w2 w3 w4]
    E --> F[RoboMaster S1]
    F --> G[VICON]
    G --> B
```
## Control de posición

En cada iteración se obtiene:

`pose_actual = [x, y, yaw]`

y se compara con:

`pose_deseada = [x_d, y_d, yaw_d]`

Se calcula el error global de posición y orientación. Después, el error en X/Y se transforma al marco local del robot.

El controlador utiliza el error entre la posición actual y la posición deseada para calcular el movimiento que debe realizar el robot. La ley de control PI (Proporcional-Integral) con *feedforward* implementada en el sistema de referencia del chasis es:

`vx_des = 1.0 * vx_ff + 3.5 * ex + 0.4 * integral(ex)`

`vy_des = 1.0 * vy_ff + 3.5 * ey + 0.4 * integral(ey)`

`omega_des = omega_ff + 2.0 * e_yaw`

Donde la acción integral se limitó a un máximo de `±0.15` para evitar el fenómeno de saturación (*anti-windup*). Finalmente, esta velocidad deseada (delimitada por seguridad a 0.80 m/s y 1.80 rad/s) se transforma en los comandos de las cuatro ruedas mediante la RNA inversa.

## Seguimiento de trayectoria

Durante el seguimiento, el controlador combina la velocidad de referencia de la trayectoria con la corrección basada en el error de posición:

`referencia de movimiento + corrección del error → RNA inversa → RPM de las ruedas`

Antes de enviar los comandos al RoboMaster, las RPM generadas por la red pasan por dos filtros de seguridad en el código:
1. Saturación absoluta: Se limitan al rango físico permitido de ±120 RPM.
2. Filtro de tasa de cambio (*Slew rate*): Se restringe el cambio máximo a 120 RPM por cada paso de control (0.05 s) para evitar picos de corriente y respuestas erráticas.

Finalmente, los valores filtrados se envían a las cuatro ruedas mediante `chassis.drive_wheels(...)`.
## Integración con VICON

Durante las primeras pruebas apareció un problema importante: VICON puede devolver una traslación [0, 0, 0] cuando el segmento se encuentra marcado como: Occluded = True

Si estos ceros se utilizaran como una pose real, el controlador asumiría incorrectamente que el robot está en el origen.

Por esta razón se modificó la lectura para:

1. Solicitar un nuevo frame.
2. Comprobar los indicadores de oclusión de posición y orientación.
3. Utilizar únicamente una pose con Occluded = False.
4. Reintentar la lectura (con pausas de 10 ms), abortando la ejecución por seguridad si después de 50 intentos continuos el sistema sigue sin entregar una pose válida.

Esta corrección fue necesaria antes de realizar las pruebas físicas finales.

## Referencia circular

La referencia original planteada fue:

`x(t) = 0.15 + 0.30 sin(2t)`

`y(t) = -0.20 + 0.30 cos(2t)`

Durante las primeras pruebas se observó que la velocidad exigida provocaba saturación frecuente de los comandos en ±120 RPM.

Para la validación física se utilizó una referencia con la misma estructura, pero más adecuada para observar el comportamiento real:

- Centro:(0.15, -0.20) m.
- Radio: 0.40 m.
- Velocidad angular reducida: aproximadamente 1.3 rad/s.

La referencia experimental fue:

`x(t) = 0.15 + 0.40 sin(1.3t)`

`y(t) = -0.20 + 0.40 cos(1.3t)`

Su punto inicial es: (0.15, 0.20) m.

Por ello, antes de ejecutar el círculo el robot se llevó a esa coordenada mediante el modo de generación de trayectorias.
