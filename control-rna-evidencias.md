---
layout: default
title: Evidencias
parent: Reporte del proyecto
nav_order: 8
permalink: /control-rna/evidencias/
---

# Evidencias experimentales

Esta sección enseña las principales evidencias utilizadas para documentar y validar el desarrollo del proyecto.

## Sistema VICON

<p align="center">
  <video width="750" controls style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
    <source src="{{ site.baseurl }}/assets/img/control-rna/circulobien.mp4" type="video/mp4">
    Tu navegador no soporta la reproducción de video.
  </video>
</p>

<p align="center">
  <em>Seguimiento del RoboMaster S1 registrado durante la prueba con VICON.</em>
</p>
Interfaz del software de captura de movimiento durante la ejecución de la trayectoria. El sistema rastrea el segmento del robot utilizando el arreglo de cámaras infrarrojas (visibles en el entorno virtual) para calcular su pose absoluta [x, y, yaw]. Esta telemetría se transmite a 20 Hz hacia el script de control, sirviendo como la retroalimentación exacta e indispensable para evaluar el error de posición en cada instante.

## Ejecución física en el espacio de prueba

Prueba 1: seguimiento de una trayectoria circular.

Objetivo. Hacer que el RoboMaster siga una trayectoria circular definida por las ecuaciones de referencia del programa. En esta prueba, el punto que debe seguir el robot cambia con el tiempo y el controlador corrige su movimiento a partir de las mediciones de VICON.
<figure style="margin: 1.5rem 0;">
  <video controls playsinline preload="metadata"
         aria-label="Prueba del RoboMaster S1 siguiendo una trayectoria circular"
         poster="{{ '/assets/img/control-orientacion/trayectoria-circulo.jpg' | relative_url }}"
         style="display: block; width: 100%; max-width: 848px; height: auto; margin: 0 auto; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
    <source src="{{ '/assets/videos/control-orientacion/trayectoriaCirculo.mp4' | relative_url }}" type="video/mp4">
    Tu navegador no soporta la reproducción de video.
    <a href="{{ '/assets/videos/control-orientacion/trayectoriaCirculo.mp4' | relative_url }}">Abrir el video de la trayectoria circular.</a>
  </video>
  <figcaption style="margin-top: 12px; text-align: center; color: #6e858a; font-size: 0.95rem;">
    Trayectoria del circulo: seguimiento físico de una referencia circular.
  </figcaption>
</figure>
Qué observar en el video:
- La forma del recorrido realizado por el robot.
- La continuidad del movimiento durante el seguimiento.
- La orientación de la base mientras el chasis se desplaza por el círculo.
- Recorrer un círculo y girar la base sobre sí misma son movimientos distintos. 
- Las ruedas Mecanum permiten combinar el desplazamiento del robot con el control de su orientación.

Prueba 2: posición y orientación de la base.

Objetivo. Solicitar una posición dentro del espacio de trabajo y un ángulo deseado para la base del robot. Durante la prueba, el chasis puede desplazarse y girar para aproximarse a la pose solicitada, utilizando VICON como retroalimentación.
<figure style="margin: 1.5rem 0;">
  <video controls playsinline preload="metadata"
         aria-label="Prueba de posición y orientación de la base del RoboMaster S1"
         poster="{{ '/assets/img/control-orientacion/control-posicion.jpg' | relative_url }}"
         style="display: block; width: 100%; max-width: 848px; height: auto; margin: 0 auto; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
    <source src="{{ '/assets/videos/control-orientacion/ControlPosicion.mp4' | relative_url }}" type="video/mp4">
    Tu navegador no soporta la reproducción de video.
    <a href="{{ '/assets/videos/control-orientacion/ControlPosicion.mp4' | relative_url }}">Abrir el video de posición y orientación.</a>
  </video>
  <figcaption style="margin-top: 12px; text-align: center; color: #6e858a; font-size: 0.95rem;">
    Control Posición: movimiento del robot y giro de su base durante la prueba física.
  </figcaption>
</figure>

Qué observar en el video:
- El desplazamiento del robot dentro del espacio de prueba.
- Los cambios en el ángulo de la base durante el movimiento.
- La respuesta del chasis al combinar desplazamiento y giro.
- La posición indica dónde se encuentra el robot; la orientación indica hacia dónde apunta su base. Para solicitar únicamente un cambio de ángulo sobre el mismo punto, se mantiene la posición objetivo y se cambia la orientación deseada.

Comparación de las pruebas

| Prueba | Referencia solicitada | Qué se observa |
| :--- | :--- | :--- |
| **Posición y orientación** | Un punto y un ángulo deseados | Desplazamiento y giro de la base |
| **Trayectoria circular** | Una posición que cambia con el tiempo | Seguimiento de un recorrido circular |

## Entrenamiento de la RNA directa

<p align="center">
  <img src="{{ site.baseurl }}/assets/img/control-rna/loss_directo_esc.png"
       alt="Entrenamiento RNA directa"
       width="700">
  <br>
  <em>Evolución del Error Cuadrático Medio (MSE) normalizado durante el entrenamiento de la planta neuronal directa.</em>
</p>
La rápida convergencia y la estabilidad de la curva de validación (naranja) indican que el modelo generalizó correctamente la dinámica del chasis sin caer en sobreajuste.

## Entrenamiento del controlador inverso

<p align="center">
  <img src="{{ site.baseurl }}/assets/img/control-rna/loss_controlador_inverso.png"
       alt="Entrenamiento RNA inversa"
       width="700">
  <br>
  <em>Curva de convergencia del controlador inverso.</em>
</p>
El gráfico refleja la minimización exitosa de la función de pérdida compuesta (error supervisado + consistencia física). La detención temprana (early stopping) capturó los pesos óptimos del modelo alrededor de la época 70.

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

[Descargar dataset]({{ site.baseurl }}/assets/files/control-rna/dataset_entrenamiento.csv){: .btn }

### Código principal

[Descargar código principal]({{ site.baseurl }}/assets/files/control-rna/control_rna_robomaster_corregido.py){: .btn }

### Registros de las pruebas físicas

[Descargar dataset prueba de posicionamiento]({{ site.baseurl }}/assets/files/control-rna/trayectoria_punto_vicon.csv){: .btn }

[Descargar dataset prueba circular]({{ site.baseurl }}/assets/files/control-rna/trayectoria_circulo_vicon.csv){: .btn }
