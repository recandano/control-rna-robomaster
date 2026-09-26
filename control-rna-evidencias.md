---
layout: default
title: Evidencias
parent: Reporte del proyecto
nav_order: 6
permalink: /control-rna/evidencias/
---

# Evidencias experimentales

Esta sección reúne las principales evidencias utilizadas para documentar y validar el desarrollo del proyecto.

## Sistema VICON

<p align="center">
  <img src="{{ site.baseurl }}/assets/img/control-rna/vicon.jpg"
       alt="Sistema VICON"
       width="650">
  <br>
  <em>Sistema VICON utilizado para medir la pose global del robot.</em>
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

## Control de posición

<p align="center">
  <img src="{{ site.baseurl }}/assets/img/control-rna/comparativa_trayectoria.png"
       alt="Control de posición"
       width="700">
</p>

**Error final de posición: 1.18 cm**

## Seguimiento circular

<p align="center">
  <img src="{{ site.baseurl }}/assets/img/control-rna/comparativa_circulo.png"
       alt="Seguimiento circular"
       width="700">
</p>

**Error radial medio absoluto: 2.25 cm**

**RMSE radial: 3.06 cm**

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

[Ver / descargar código principal]({{ site.baseurl }}/assets/files/control-rna/control_rna_robomaster_corregido.py){: .btn .btn-blue }

### Registros de las pruebas físicas

[Prueba de posicionamiento]({{ site.baseurl }}/assets/files/control-rna/trayectoria_punto_vicon.csv){: .btn }

[Prueba circular]({{ site.baseurl }}/assets/files/control-rna/trayectoria_circulo_vicon.csv){: .btn }
