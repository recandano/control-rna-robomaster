---
layout: default
title: Modelos neuronales
parent: Evaluación 1 - Control por RNA
nav_order: 2
permalink: /control-rna-modelos/
---

# Modelos neuronales

## Arquitectura general

Se entrenaron dos redes neuronales con PyTorch: una **directa**, que aprende el comportamiento del robot, y una **inversa**, que aprende los comandos necesarios para producir un movimiento deseado.

![Arquitecturas]({{ site.baseurl }}/assets/img/control-rna/arquitecturas_rna.png)

## RNA directa

La red directa utiliza una MLP con arquitectura:

`4 -> 64 -> 64 -> 32 -> 3`

Entradas: velocidades de las cuatro ruedas.  
Salidas: `vx_body`, `vy_body`, `omega`.

Las capas ocultas utilizan activación **SiLU** y la salida es lineal. El entrenamiento se realiza con pérdida MSE normalizada, optimizador AdamW, early stopping y gradient clipping.

![Pérdida de la red directa]({{ site.baseurl }}/assets/img/control-rna/loss_directo_esc.png)

### Resultados de identificación

| Modelo | RMSE vx [m/s] | RMSE vy [m/s] | RMSE omega [rad/s] | R² global |
|---|---:|---:|---:|---:|
| Directo ESC | 0.0525 | 0.0739 | 0.2844 | 0.8793 |
| Planta CMD | 0.0554 | 0.0898 | 0.2709 | 0.8856 |

La caracterización logra un R² global cercano a **0.88**, suficiente para usarla como modelo auxiliar de la planta en simulación y como restricción física del controlador inverso.

## RNA inversa

La red inversa tiene arquitectura:

`3 -> 64 -> 64 -> 32 -> 4`

Entrada: cambio de pose local deseado en un paso de control: `dx_body`, `dy_body`, `dyaw`.  
Salida: comandos `w1_cmd ... w4_cmd`.

![Pérdida del controlador inverso]({{ site.baseurl }}/assets/img/control-rna/loss_controlador_inverso.png)

La función de pérdida combina dos objetivos:

1. reproducir los comandos de rueda observados en el dataset;
2. asegurar que los RPM predichos, al pasar por la planta directa, produzcan el movimiento solicitado.

Aunque el R² individual de algunas ruedas es moderado, la **consistencia física inversa + planta** alcanza un **R² global de 0.971**, que es una métrica más relacionada con el objetivo de control.

| Salida | RMSE [RPM] | R² |
|---|---:|---:|
| w1 | 22.95 | 0.731 |
| w2 | 28.77 | 0.383 |
| w3 | 27.13 | 0.342 |
| w4 | 20.03 | 0.598 |
