---
layout: default
title: Modelos neuronales
parent: Reporte del proyecto
nav_order: 2
permalink: /control-rna/modelos/
---

# Modelos neuronales

## RNA directa: identificación de la planta

La primera red neuronal aprende el comportamiento directo del RoboMaster.

La pregunta que responde es:

> Si las cuatro ruedas giran con determinadas velocidades, ¿qué movimiento producirá el chasis?

### Arquitectura

Se utilizó una MLP con estructura feedforward:

`4 → 64 → 64 → 32 → 3`

Las entradas son las velocidades de las cuatro ruedas:

`[w1, w2, w3, w4]`

Las salidas son:

`[vx_body, vy_body, omega]`

donde vx_body y vy_body representan las velocidades longitudinal y lateral en el marco del robot (sistema de coordenadas del propio robot), y omega representa la velocidad angular.

Las capas ocultas utilizan activación SiLU y la salida es lineal.

El entrenamiento se realizó en PyTorch utilizando AdamW, pérdida cuadrática media normalizada, early stopping y gradient clipping.

## Dos variantes de planta

Se entrenaron dos versiones de la red directa.

### Modelo ESC

Entradas:

`[w1_esc, w2_esc, w3_esc, w4_esc]`

Este modelo utiliza las velocidades medidas realmente en las ruedas, por lo que refleja de manera más directa cómo respondió el robot durante las pruebas.

### Modelo CMD

Entradas:

`[w1_cmd, w2_cmd, w3_cmd, w4_cmd]`

Este modelo se utiliza principalmente en simulación, ya que recibe como entrada los mismos comandos de rueda que genera la RNA inversa.

## Resultados de identificación

| Modelo | RMSE vx [m/s] | RMSE vy [m/s] | RMSE omega [rad/s] | R² global |
|---|---:|---:|---:|---:|
| Directo ESC | 0.0525 | 0.0739 | 0.2844 | 0.8793 |
| Planta CMD | 0.0554 | 0.0898 | 0.2709 | 0.8856 |

Los valores de R² global cercanos a 0.88 muestran que las redes capturan una parte importante del comportamiento observado del sistema.

<p align="center">
  <img src="{{ site.baseurl }}/assets/img/control-rna/loss_directo_esc.png"
       alt="Pérdida de entrenamiento de la RNA directa"
       width="700">
  <br>
  <em>Curva de entrenamiento de la RNA directa basada en velocidades ESC.</em>
</p>

---

## RNA inversa: generación de comandos

Una vez aprendida la relación entre ruedas y movimiento, se resolvió el problema inverso:

> Dado un pequeño cambio de pose deseado, ¿qué RPM deben enviarse a las ruedas?

### Arquitectura

La red inversa utiliza:

`3 → 64 → 64 → 32 → 4`

Entrada:

`[dx_body, dy_body, dyaw]`

Salida:

`[w1_cmd, w2_cmd, w3_cmd, w4_cmd]`

Cada entrada representa el pequeño movimiento que se desea producir durante un periodo de control de 0.05 s.

## Función de pérdida

El entrenamiento combina dos objetivos.

El primero es supervisado: se penaliza la diferencia entre las RPM estimadas y las RPM registradas.

El segundo introduce consistencia física:

`movimiento deseado → RNA inversa → RPM → planta directa → movimiento predicho`

De esta manera, no basta con copiar exactamente los comandos del dataset; también se busca que las RPM generadas produzcan el movimiento deseado según la planta aprendida.

## Resultados de la RNA inversa

| Salida | RMSE [RPM] | R² |
|---|---:|---:|
| w1 | 22.95 | 0.731 |
| w2 | 28.77 | 0.383 |
| w3 | 27.13 | 0.342 |
| w4 | 20.03 | 0.598 |

Las métricas por rueda muestran que el problema inverso no es completamente unívoco. Sin embargo, al evaluar el movimiento producido después de pasar los comandos por la planta directa se obtiene: R² global de consistencia ≈ 0.971

Esta métrica es especialmente relevante porque evalúa si el controlador genera un movimiento correcto, aunque las RPM no coincidan exactamente con las observadas históricamente.

<p align="center">
  <img src="{{ site.baseurl }}/assets/img/control-rna/loss_controlador_inverso.png"
       alt="Pérdida de entrenamiento del controlador inverso"
       width="700">
  <br>
  <em>Curva de entrenamiento de la RNA inversa.</em>
</p>
