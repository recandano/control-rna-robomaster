---
layout: default
title: Control de orientación
parent: Reporte del proyecto
nav_order: 7
permalink: /control-orientacion/
---

# Control de orientación

## Posición y ángulo de la base

En este proyecto, el RoboMaster S1 se controla a partir de su **pose**: la posición que ocupa en el laboratorio y la orientación de su base. VICON mide estas variables y permite corregir el movimiento mediante un lazo de control que utiliza la red neuronal artificial (RNA) inversa.

`pose = [x, y, yaw]`

Las coordenadas `x` y `y` indican dónde está el robot. El ángulo `yaw` indica hacia dónde apunta su chasis alrededor del eje vertical. Así, una referencia puede pedir tanto **llegar a un punto** como **adoptar un ángulo determinado**.

<div class="system-grid">
  <div class="system-card">
    <div class="system-label">Variable de orientación</div>
    <div class="system-value">Yaw de la base</div>
  </div>
  <div class="system-card">
    <div class="system-label">Retroalimentación</div>
    <div class="system-value">Pose medida por VICON</div>
  </div>
  <div class="system-card">
    <div class="system-label">Periodo de control</div>
    <div class="system-value">0.05 s · 20 Hz</div>
  </div>
  <div class="system-card">
    <div class="system-label">Comandos al robot</div>
    <div class="system-value">RPM de las cuatro ruedas</div>
  </div>
</div>

## Cómo se calcula el giro

En cada periodo de control se compara la orientación deseada, `yaw_d`, con la orientación actual, `yaw`. El código calcula la diferencia angular mediante:

`e_yaw = atan2(sin(yaw_d - yaw), cos(yaw_d - yaw))`

Esta operación, implementada en `wrap_to_pi()`, expresa el error entre −π y π radianes para corregir por el giro más corto. Por ejemplo, si el robot está en **179°** y debe orientarse a **−179°**, el error es **+2°**.

La velocidad angular deseada se obtiene con una acción proporcional:

`omega_des = omega_ff + 2.0 * e_yaw`

Para una orientación fija, `omega_ff = 0`. Cuando el error angular disminuye, también disminuye la corrección solicitada. El control de posición en `x` y `y` combina acciones proporcional e integral; la corrección de orientación utiliza la acción proporcional indicada arriba.

| Parámetro del código | Valor | Función |
|---|---:|---|
| Ganancia de orientación `kp_yaw` | 2.0 s⁻¹ | Convierte el error angular en una corrección de velocidad angular |
| Límite de velocidad angular | ±1.80 rad/s | Limita el giro solicitado antes de entrar a la RNA inversa |
| Límite de comandos de rueda | ±120 RPM | Limita las salidas enviadas al robot |

La RNA inversa recibe el movimiento deseado durante un periodo de control:

`[dx_body, dy_body, dyaw] = [vx_des, vy_des, omega_des] * 0.05`

A partir de estas tres entradas calcula las RPM de las cuatro ruedas. VICON vuelve a medir la pose del robot y el proceso se repite.

## Video: control de posición y orientación

El video **ControlPosicion** muestra la respuesta del robot al solicitar un punto y un ángulo deseado de la base. El controlador corrige la posición y el giro del chasis a partir de la pose medida.

<figure style="margin: 1.5rem 0;">
  <video controls playsinline preload="metadata"
         aria-label="Demostración del control de posición y orientación de la base del RoboMaster S1"
         poster="{{ '/assets/img/control-orientacion/control-posicion.jpg' | relative_url }}"
         style="display: block; width: 100%; max-width: 848px; height: auto; margin: 0 auto; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
    <source src="{{ '/assets/videos/control-orientacion/ControlPosicion.mp4' | relative_url }}" type="video/mp4">
    Tu navegador no soporta la reproducción de video.
    <a href="{{ '/assets/videos/control-orientacion/ControlPosicion.mp4' | relative_url }}">Abrir el video de control de posición y orientación.</a>
  </video>
  <figcaption style="margin-top: 12px; text-align: center; color: #6e858a; font-size: 0.95rem;">
    Prueba física del control de posición y del ángulo de la base.
  </figcaption>
</figure>

[Abrir video de posición y orientación]({{ '/assets/videos/control-orientacion/ControlPosicion.mp4' | relative_url }}){: .btn }

Para solicitar una pose, el programa permite especificar `--target-x`, `--target-y` y `--target-yaw-deg`. El ángulo se introduce en grados y se convierte a radianes dentro del código. Si se omite el ángulo objetivo en el modo físico de punto, se conserva la orientación inicial.

Para solicitar un giro sobre el mismo punto se mantienen como referencia las coordenadas actuales `x_d` y `y_d`, y se cambia `yaw_d`. La retroalimentación también corrige los desplazamientos que puedan aparecer durante el giro.

El criterio de llegada del código considera conjuntamente una tolerancia de posición de **3 cm** y una tolerancia angular de **5°**, durante **10 ciclos consecutivos**. Estos valores son condiciones de parada configuradas; no son errores medidos del video.

## Video: seguimiento de una trayectoria circular

El video **trayectoriaCirculo** muestra al robot siguiendo una trayectoria deseada definida mediante ecuaciones. A diferencia de una referencia de punto fijo, aquí las coordenadas objetivo cambian con el tiempo.

<figure style="margin: 1.5rem 0;">
  <video controls playsinline preload="metadata"
         aria-label="Demostración del RoboMaster S1 siguiendo una trayectoria circular"
         poster="{{ '/assets/img/control-orientacion/trayectoria-circulo.jpg' | relative_url }}"
         style="display: block; width: 100%; max-width: 848px; height: auto; margin: 0 auto; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
    <source src="{{ '/assets/videos/control-orientacion/trayectoriaCirculo.mp4' | relative_url }}" type="video/mp4">
    Tu navegador no soporta la reproducción de video.
    <a href="{{ '/assets/videos/control-orientacion/trayectoriaCirculo.mp4' | relative_url }}">Abrir el video de la trayectoria circular.</a>
  </video>
  <figcaption style="margin-top: 12px; text-align: center; color: #6e858a; font-size: 0.95rem;">
    Prueba física del seguimiento de una referencia circular.
  </figcaption>
</figure>

[Abrir video de trayectoria circular]({{ '/assets/videos/control-orientacion/trayectoriaCirculo.mp4' | relative_url }}){: .btn }

La referencia experimental documentada en el código del proyecto es:

`x_d(t) = 0.15 + 0.40 * sin(1.3 * t)`

`y_d(t) = -0.20 + 0.40 * cos(1.3 * t)`

Estas ecuaciones describen un círculo con centro en **(0.15, −0.20) m**, radio de **0.40 m** y velocidad angular de recorrido de **1.3 rad/s**. Las derivadas de la referencia proporcionan las velocidades de anticipación (*feedforward*), mientras el error medido permite corregir desviaciones.

### Orientación durante el recorrido

El código ofrece dos formas de definir el ángulo de la base durante una trayectoria:

| Modo `trajectory_yaw_mode` | Orientación solicitada |
|---|---|
| `hold` | Mantener el ángulo inicial de la base durante el recorrido |
| `tangent` | Orientar la base en la dirección tangente a la trayectoria |

En el archivo entregado, el modo predeterminado es **`hold`**. Gracias a sus ruedas Mecanum, el robot puede desplazarse lateralmente y recorrer el círculo mientras mantiene una orientación de referencia. En el modo `tangent`, el ángulo se calcula a partir de la dirección de la velocidad y cambia durante el recorrido.

La velocidad angular de recorrido del círculo describe cómo avanza la referencia alrededor de su centro. La velocidad angular de la base describe cómo gira el chasis sobre sí mismo. Son variables distintas y su relación depende del modo de orientación elegido.

## Relación con el proyecto completo

Estas demostraciones forman parte del sistema **RoboMaster S1 + VICON + RNA inversa**: las referencias definen la pose deseada, el controlador calcula las correcciones y la red neuronal genera los comandos de rueda.

[Consultar el reporte del proyecto]({{ '/control-rna/' | relative_url }}){: .btn }

[Ver el control en lazo cerrado]({{ '/control-rna/control/' | relative_url }}){: .btn }

[Consultar los resultados experimentales]({{ '/control-rna/resultados/' | relative_url }}){: .btn }
