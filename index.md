---
layout: home
title: Control por RNA - RoboMaster S1
nav_order: 1
---

# Control por RNA del RoboMaster S1

## Proyecto 1 - Control Inteligente

En este proyecto se desarrolló un sistema de identificación y control basado en redes neuronales artificiales para un DJI RoboMaster S1, utilizando VICON como referencia externa para medir la posición y orientación real del robot y cerrar el lazo de control.

<p align="center">
  <img src="{{ site.baseurl }}/assets/img/control-rna/Zacarias.jpg"
       alt="RoboMaster S1"
       width="400">
  <br>
   <em>Figura 1. DJI RoboMaster S1.</em>
</p>

El proyecto se desarrolló en cinco etapas:

- Adquisición y procesamiento de datos.
- Identificación neuronal del comportamiento del robot.
- Desarrollo de un controlador neuronal inverso;
- Seguimiento de trayectoria circular.
- Control de posición y seguimiento de trayectoria en el robot físico.

## Resultados principales

En la validación física el robot alcanzó la referencia con un error final de posición de
1.18 cm. 

Para el seguimiento de una trayectoria circular de radio 0.40 m se obtuvo:
- Error radial medio absoluto: 2.25 cm
- RMSE radial: 3.06 cm
- Error radial máximo: 8.11 cm


## Contenido del proyecto

El portafolio se encuentra dividido en las siguientes secciones:

- [Metodología y datos]({{ site.baseurl }}/control-rna/metodologia/)
- [Modelos neuronales]({{ site.baseurl }}/control-rna/modelos/)
- [Control en lazo cerrado]({{ site.baseurl }}/control-rna/control/)
- [Control de orientación]({{ site.baseurl }}/control-rna/orientacion/)
- [Código principal]({{ site.baseurl }}/control-rna/codigo/)
- [Resultados y análisis]({{ site.baseurl }}/control-rna/resultados/)
- [Ejecución física]({{ site.baseurl }}/control-rna/ejecucion/)
- [Evidencias]({{ site.baseurl }}/control-rna/evidencias/)
- [Códigos/Datasets]({{ site.baseurl }}/codigos/)
- [Contribuciones del equipo]({{ site.baseurl }}/contribuciones/)


