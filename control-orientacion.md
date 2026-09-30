---
layout: default
title: Pruebas de posición, orientación y trayectoria
parent: Reporte del proyecto
nav_order: 7
permalink: /control-orientacion/
---
Pruebas de posición, orientación y trayectoria
Esta sección reúne dos demostraciones físicas del RoboMaster S1: el movimiento hacia un punto con un ángulo deseado de la base y el seguimiento de una trayectoria circular. Los videos permiten observar la respuesta del robot durante las pruebas del proyecto.
Los fundamentos del controlador se describen en [Control en lazo cerrado]({{ '/control-rna/control/' | relative_url }}) y [Control de orientación]({{ '/control-rna/orientacion/' | relative_url }}).
Prueba 1: posición y orientación de la base
Objetivo
Solicitar una posición dentro del espacio de trabajo y un ángulo deseado para la base del robot. Durante la prueba, el chasis puede desplazarse y girar para aproximarse a la pose solicitada, utilizando VICON como retroalimentación.
Video de la prueba
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
    Video 1. ControlPosicion: movimiento del robot y giro de su base durante la prueba física.
  </figcaption>
</figure>
[Abrir video de posición y orientación]({{ '/assets/videos/control-orientacion/ControlPosicion.mp4' | relative_url }}){: .btn }
Qué observar en el video
El desplazamiento del robot dentro del espacio de prueba.
Los cambios en el ángulo de la base durante el movimiento.
La respuesta del chasis al combinar desplazamiento y giro.
La posición indica dónde se encuentra el robot; la orientación indica hacia dónde apunta su base. Para solicitar únicamente un cambio de ángulo sobre el mismo punto, se mantiene la posición objetivo y se cambia la orientación deseada.
Prueba 2: seguimiento de una trayectoria circular
Objetivo
Hacer que el RoboMaster siga una trayectoria circular definida por las ecuaciones de referencia del programa. En esta prueba, el punto que debe seguir el robot cambia con el tiempo y el controlador corrige su movimiento a partir de las mediciones de VICON.
Video de la prueba
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
    Video 2. trayectoriaCirculo: seguimiento físico de una referencia circular.
  </figcaption>
</figure>
[Abrir video de trayectoria circular]({{ '/assets/videos/control-orientacion/trayectoriaCirculo.mp4' | relative_url }}){: .btn }
Qué observar en el video
La forma del recorrido realizado por el robot.
La continuidad del movimiento durante el seguimiento.
La orientación de la base mientras el chasis se desplaza por el círculo.
Recorrer un círculo y girar la base sobre sí misma son movimientos distintos. Las ruedas Mecanum permiten combinar el desplazamiento del robot con el control de su orientación.
Comparación de las pruebas
Prueba	Referencia solicitada	Qué se observa
Posición y orientación	Un punto y un ángulo deseados	Desplazamiento y giro de la base
Trayectoria circular	Una posición que cambia con el tiempo	Seguimiento de un recorrido circular
Las grabaciones complementan los registros de VICON y las gráficas del reporte. Para consultar las mediciones y el análisis de los errores de las pruebas documentadas, visita la sección de resultados.
[Consultar los resultados experimentales]({{ '/control-rna/resultados/' | relative_url }}){: .btn }
[Consultar el reporte del proyecto]({{ '/control-rna/' | relative_url }}){: .btn }
