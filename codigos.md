---
layout: default
title: Códigos
nav_order: 3
permalink: /codigos/
---

# Códigos y archivos del proyecto

En esta sección se encuentran los principales códigos, datasets y registros utilizados durante el desarrollo del proyecto. Estos archivos incluyen desde la adquisición de datos del RoboMaster S1 y VICON hasta el entrenamiento de las redes neuronales, la simulación y las pruebas realizadas con el robot físico.

## Archivos del proyecto

| **Archivo** | **Descripción** |
|---|---|
| Código de adquisición RoboMaster + VICON | Conecta el RoboMaster S1 con VICON, ejecuta las rutinas de movimiento y genera el dataset experimental |
| Dataset experimental | Registro utilizado para entrenar las redes neuronales |
| Código principal | Procesamiento de datos, entrenamiento, simulación y control físico |
| Prueba de posicionamiento | Registro VICON de la llegada al punto objetivo |
| Prueba circular | Registro VICON del seguimiento de trayectoria |
| Análisis experimental | Script utilizado para generar las comparativas |
| Métricas | Resultados de entrenamiento y validación |

## Código de adquisición de datos

Este programa se utilizó durante la primera etapa del proyecto para conectar simultáneamente el RoboMaster S1 y el sistema VICON.

El código envía diferentes comandos de movimiento al robot, registra las velocidades de las cuatro ruedas y almacena al mismo tiempo la posición y orientación obtenidas mediante VICON. Con esta información se genera el dataset utilizado posteriormente para la identificación neuronal del sistema.

[Descargar código de adquisición]({{ site.baseurl }}/assets/files/control-rna/adquisicion_dataset_robomaster_vicon.py){: .btn  }

## Dataset experimental

Dataset obtenido a partir de las pruebas realizadas con el RoboMaster y utilizado posteriormente para el entrenamiento de las redes neuronales.

[Descargar dataset]({{ site.baseurl }}/assets/files/control-rna/dataset_entrenamiento.csv){: .btn }

## Código principal

Este código contiene el procesamiento de los datos, entrenamiento de las redes neuronales, simulación del sistema y las rutinas utilizadas para realizar las pruebas físicas con el RoboMaster.

[Descargar código principal]({{ site.baseurl }}/assets/files/control-rna/control_rna_robomaster_corregido.py){: .btn }

## Registros de las pruebas físicas

Los siguientes archivos contienen los datos registrados mediante VICON durante las pruebas finales realizadas con el robot.

### Dataset usado para entrenar la red de sincronización de VICON

[Descargar dataset sincronización]({{ site.baseurl }}/assets/files/control-rna/robomaster_dataset_20260924_140657){: .btn }

### Control de posición

[Descargar dataset prueba de posicionamiento]({{ site.baseurl }}/assets/files/control-rna/trayectoria_punto_vicon.csv){: .btn }

### Seguimiento de trayectoria circular

[Descargar dataset prueba circular]({{ site.baseurl }}/assets/files/control-rna/trayectoria_circulo_vicon.csv){: .btn }

## Análisis experimental

Script utilizado para procesar los resultados experimentales y generar algunas de las gráficas comparativas presentadas en el portafolio.

[Descargar código de análisis]({{ site.baseurl }}/assets/files/control-rna/grafica_comparativa.py){: .btn }

## Métricas

Archivo que contiene un resumen de las métricas obtenidas durante el entrenamiento y validación de los modelos neuronales.

[Descargar métricas]({{ site.baseurl }}/assets/files/control-rna/metricas_resumen.json){: .btn }
