---
layout: default
title: Metodología y preprocesamiento
parent: Evaluación 1 - Control por RNA
nav_order: 1
permalink: /control-rna-metodologia/
---

# Metodología y preprocesamiento

## Plataforma experimental

La plataforma está formada por un RoboMaster S1 con ruedas Mecanum y un sistema VICON para medir la pose global. Durante la adquisición se registraron en un mismo dataset los comandos de rueda, velocidades medidas por ESC y posición/orientación del robot.

El dataset original contiene **4,345 registros**. Se eliminó un timestamp duplicado, quedando **4,344 muestras**. El periodo de control nominal fue de **0.05 s (20 Hz)**.

## Variables utilizadas

| Grupo | Variables | Uso |
|---|---|---|
| Comandos | `w1_cmd ... w4_cmd` | Entrenamiento de la planta CMD y del controlador inverso |
| ESC | `w1_esc ... w4_esc` | Identificación directa del comportamiento real de las ruedas |
| VICON | `x_vicon`, `y_vicon`, `yaw` | Pose global y cálculo de velocidades del cuerpo |
| Etiquetas | `fase`, `etiqueta` | Filtrado de segmentos y exclusión de eventos no deseados |

## Preprocesamiento

El pipeline realiza los siguientes pasos:

- conversión de posición VICON de milímetros a metros;
- tratamiento de yaw con `unwrap` antes de derivar;
- filtrado Savitzky-Golay para reducir ruido;
- derivación con respecto al tiempo real del registro;
- transformación de velocidades globales al marco local del robot;
- división temporal **80/10/10** en train, validation y test;
- estandarización con `StandardScaler` ajustado únicamente con Train;
- estimación del retardo comando-respuesta usando Train/Validation.

El retardo identificado entre comandos de rueda y respuesta fue de aproximadamente **0.10 s**, equivalente a **2 pasos** de control.

## Por qué se usa el marco local

El movimiento que producen las ruedas depende de la orientación instantánea del robot. Por eso, antes de aprender la dinámica, las velocidades globales de VICON se transforman al marco del cuerpo del RoboMaster. Esto permite que la RNA relacione las RPM con `vx`, `vy` y `omega` de forma consistente independientemente de la orientación global.
