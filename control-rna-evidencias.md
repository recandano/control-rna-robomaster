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

## Comparación entre simulación y prueba física

Para validar el controlador, se compararon los resultados obtenidos mediante la planta neuronal con las trayectorias registradas posteriormente durante las pruebas físicas con VICON.

### Control de posición

<div class="comparison-grid">

  <div class="comparison-card">
    <div class="comparison-title">Simulación</div>

    <img src="{{ site.baseurl }}/assets/img/control-rna/fase3_punto_simulacion.png"
         alt="Control de posición en simulación">

    <div class="comparison-caption">
      Resultado obtenido utilizando la RNA inversa y la planta neuronal.
    </div>
  </div>

  <div class="comparison-card">
    <div class="comparison-title">Prueba física</div>

    <img src="{{ site.baseurl }}/assets/img/control-rna/comparativa_trayectoria.png"
         alt="Control de posición físico">

    <div class="comparison-caption">
      Trayectoria real registrada por VICON durante la prueba con el RoboMaster.
    </div>
  </div>

</div>

<div class="result-highlight">
  <span class="result-number">1.18 cm</span>
  <span class="result-description">Error final de posición</span>
</div>


### Seguimiento de trayectoria circular

<div class="comparison-grid">

  <div class="comparison-card">
    <div class="comparison-title">Simulación</div>

    <img src="{{ site.baseurl }}/assets/img/control-rna/fase4_trayectoria.png"
         alt="Seguimiento circular en simulación">

    <div class="comparison-caption">
      Trayectoria de referencia y trayectoria obtenida mediante la simulación del controlador.
    </div>
  </div>

  <div class="comparison-card">
    <div class="comparison-title">Prueba física</div>

    <img src="{{ site.baseurl }}/assets/img/control-rna/comparativa_circulo.png"
         alt="Seguimiento circular físico">

    <div class="comparison-caption">
      Comparación entre el círculo de referencia y la trayectoria registrada por VICON.
    </div>
  </div>

</div>

<div class="result-highlight">
  <span class="result-number">2.25 cm</span>
  <span class="result-description">Error radial medio absoluto</span>
</div>

<div class="result-highlight">
  <span class="result-number">3.06 cm</span>
  <span class="result-description">RMSE radial</span>
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
