---
layout: default
title: Evidencias
parent: Reporte del proyecto
nav_order: 6
permalink: /control-rna/evidencias/
---

# Evidencias experimentales

Esta sección enseña las principales evidencias utilizadas para documentar y validar el desarrollo del proyecto.

## Sistema VICON

<p align="center">
  <video width="750" controls>
    <source src="{{ site.baseurl }}/assets/img/control-rna/circulobien.mp4" type="video/mp4">
    Tu navegador no soporta la reproducción de video.
  </video>
</p>

<p align="center">
  <em>Seguimiento del RoboMaster S1 registrado durante la prueba con VICON.</em>
</p>

## Entrenamiento de la RNA directa

<p align="center">
  <img src="{{ site.baseurl }}/assets/img/control-rna/loss_directo_esc.png"
       alt="Entrenamiento RNA directa"
       width="700">
</p>

## Entrenamiento del controlador inverso

<p align="center">
  <img src="{{ site.baseurl }}/assets/img/control-rna/loss_controlador_inverso.png"
       alt="Entrenamiento RNA inversa"
       width="700">
</p>

## Simulación y validación física

La simulación se utilizó para comprobar el funcionamiento general del controlador antes de realizar las pruebas con el RoboMaster real. Posteriormente, el sistema se validó físicamente utilizando VICON.

Las referencias utilizadas en simulación y en las pruebas físicas no fueron exactamente las mismas. Por esta razón, los resultados se presentan como dos etapas de validación diferentes y no como una comparación directa punto por punto.

### Control de posición

#### Simulación

<p align="center">
  <img src="{{ site.baseurl }}/assets/img/control-rna/fase3_punto_trayectoria.png"
       alt="Control de posición en simulación"
       width="700">
  <br>
  <em>Prueba simulada utilizada para verificar que la RNA inversa y la planta neuronal permitieran llevar el modelo hacia un punto objetivo.</em>
</p>

#### Prueba física

<p align="center">
  <img src="{{ site.baseurl }}/assets/img/control-rna/comparativa_trayectoria.png"
       alt="Control de posición físico"
       width="700">
  <br>
  <em>Trayectoria registrada por VICON durante la prueba física. La coordenada objetivo utilizada fue distinta a la empleada en simulación.</em>
</p>

<div class="result-highlight">
  <span class="result-number">1.18 cm</span>
  <span class="result-description">Error final de posición en la prueba física</span>
</div>

---

### Seguimiento de trayectoria circular

#### Simulación

<p align="center">
  <img src="{{ site.baseurl }}/assets/img/control-rna/fase4_trayectoria.png"
       alt="Seguimiento circular en simulación"
       width="700">
  <br>
  <em>Seguimiento de la trayectoria circular utilizada durante la etapa de simulación.</em>
</p>

La simulación permitió comprobar que el controlador podía seguir una referencia circular y también ayudó a identificar problemas como la saturación de los comandos de rueda.

#### Prueba física

<p align="center">
  <img src="{{ site.baseurl }}/assets/img/control-rna/comparativa_circulo.png"
       alt="Seguimiento circular físico"
       width="700">
  <br>
  <em>Comparación entre la trayectoria de referencia utilizada en la prueba física y la trayectoria registrada por VICON.</em>
</p>

Para la prueba con el RoboMaster real se ajustaron algunos parámetros de la referencia con respecto a la simulación. En particular, se utilizó un radio de 0.40 m y una velocidad angular aproximada de 1.3 rad/s con el objetivo de obtener un movimiento más estable durante la ejecución física.

  <div class="results-row">
  <div class="result-highlight">
    <span class="result-number">2.25 cm</span>
    <span class="result-description">Error radial medio absoluto</span>
  </div>
  <div class="result-highlight">
    <span class="result-number">3.06 cm</span>
    <span class="result-description">RMSE radial</span>
  </div>
</div>

## Archivos del proyecto

Los principales archivos utilizados para desarrollar y validar el sistema se encuentran disponibles a continuación.

| Archivo | Descripción |
|---|---|
| Dataset experimental | Registro utilizado para entrenar las redes neuronales |
| Código principal | Identificación, entrenamiento, simulación y control físico |
| Prueba de posicionamiento | Registro VICON de la llegada al punto objetivo |
| Prueba circular | Registro VICON del seguimiento de trayectoria |
| Análisis experimental | Script utilizado para generar las comparativas |
| Métricas | Resultados de entrenamiento y validación |

### Dataset experimental

[Descargar dataset]({{ site.baseurl }}/assets/files/control-rna/dataset_entrenamiento.csv){: .btn .btn-blue }

### Código principal

[Descargar código principal]({{ site.baseurl }}/assets/files/control-rna/control_rna_robomaster_corregido.py){: .btn .btn-blue }

### Registros de las pruebas físicas

[Descargar dataset prueba de posicionamiento]({{ site.baseurl }}/assets/files/control-rna/trayectoria_punto_vicon.csv){: .btn }

[Descargar dataset prueba circular]({{ site.baseurl }}/assets/files/control-rna/trayectoria_circulo_vicon.csv){: .btn }
