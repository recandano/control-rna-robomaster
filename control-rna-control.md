---
layout: default
title: Control en lazo cerrado
parent: Evaluación 1 - Control por RNA
nav_order: 3
permalink: /control-rna-control/
---

# Control en lazo cerrado

## Estructura del controlador

En ejecución física, la RNA no trabaja sola. El controlador utiliza VICON para cerrar el lazo y corregir el error en cada instante.

![Lazo de control]({{ site.baseurl }}/assets/img/control-rna/lazo_control.png)

El proceso en cada ciclo de 0.05 s es:

1. VICON entrega la pose actual `[x, y, yaw]`.
2. Se calcula el error con respecto a la referencia.
3. El error global se transforma al marco local del robot.
4. Se aplica compensación PI y, para trayectoria, feedforward.
5. La RNA inversa convierte el movimiento deseado en RPM de las cuatro ruedas.
6. Se aplican saturación y límite de cambio de RPM.
7. Se envían los comandos al RoboMaster y se repite el ciclo.

## Seguridad de VICON

Durante las pruebas se detectó que VICON puede devolver una traslación `[0, 0, 0]` cuando el segmento está marcado como `Occluded=True`. Por ello, la versión de ejecución física debe **rechazar frames ocluidos** y esperar una pose válida antes de generar comandos. Esto evita que un cero inválido sea interpretado como una posición real.

## Control de punto

El modo `point` recibe una coordenada global de VICON. Por ejemplo:

```text
--target-x 0.15 --target-y 0.20
```

no significa "avanzar 15 cm y 20 cm", sino llegar al punto absoluto `(0.15, 0.20)` m del sistema VICON.

Si no se especifica `target-yaw-deg`, el código conserva la orientación inicial.

## Seguimiento circular

La referencia general se expresa como:

```text
x(t) = xc + R sin(omega t)
y(t) = yc + R cos(omega t)
```

En la prueba física reportada se utilizó:

- centro: `(0.15, -0.20)` m;
- radio: `0.40 m`;
- punto inicial: `(0.15, 0.20)` m;
- velocidad angular de validación: aproximadamente `1.3 rad/s`.

La reducción de velocidad respecto a la referencia rápida inicial permitió disminuir saturación y observar con mayor claridad el desempeño del controlador.
