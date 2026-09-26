---
layout: default
title: Evaluación 1 - Control por RNA
nav_order: 5
has_children: true
permalink: /control-rna/
---

# Evaluación 1 - Control por RNA
{: .no_toc }

**DJI RoboMaster S1 + VICON + PyTorch**  
Curso: Control Inteligente - Otoño 2026

---

## Resumen

El objetivo de esta práctica fue identificar el comportamiento de un **DJI RoboMaster S1** mediante redes neuronales artificiales y utilizar el modelo aprendido para construir un controlador de posición y seguimiento de trayectoria.

El sistema combina dos fuentes principales de información: los comandos y velocidades de las cuatro ruedas Mecanum del RoboMaster y la pose global medida por **VICON**. El control físico se ejecuta a **20 Hz** y utiliza la pose de VICON como retroalimentación.

![Flujo general]({{ site.baseurl }}/assets/img/control-rna/flujo_general.png)

## Qué se implementó

1. Limpieza y preprocesamiento del dataset experimental.
2. RNA directa para caracterizar la dinámica del robot.
3. RNA inversa para convertir movimiento deseado en comandos de rueda.
4. Control de posición en lazo cerrado con VICON.
5. Seguimiento circular en simulación y en el RoboMaster físico.

## Resultado principal

En la validación física, el robot alcanzó el punto inicial del círculo con un **error final de 1.18 cm**. Para el círculo físico de radio **0.40 m**, se obtuvo un **error radial medio de 2.25 cm** y un **RMSE radial de 3.06 cm**.

![Comparativa física del círculo]({{ site.baseurl }}/assets/img/control-rna/comparativa_circulo.png)

## Navegación del reporte

- [Metodología y preprocesamiento]({{ site.baseurl }}/control-rna-metodologia/)
- [Modelos neuronales]({{ site.baseurl }}/control-rna-modelos/)
- [Control en lazo cerrado]({{ site.baseurl }}/control-rna-control/)
- [Resultados y análisis]({{ site.baseurl }}/control-rna-resultados/)
- [Ejecución y comandos]({{ site.baseurl }}/control-rna-ejecucion/)
