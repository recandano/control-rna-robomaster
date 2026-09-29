---
layout: default
title: Resultados y análisis
parent: Reporte del proyecto
nav_order: 4
permalink: /control-rna/resultados/
---

# Resultados y análisis

## Simulación

Antes de realizar pruebas con el robot físico, el controlador se evaluó utilizando la planta neuronal CMD.

Los resultados obtenidos fueron:

<div class="system-grid">
  <div class="system-card">
    <div class="system-label">RMSE de posición</div>
    <div class="system-value">9.26 cm</div>
  </div>
  <div class="system-card">
    <div class="system-label">MAE de posición</div>
    <div class="system-value">8.32 cm</div>
  </div>
  <div class="system-card">
    <div class="system-label">Error máximo</div>
    <div class="system-value">15.18 cm</div>
  </div>
  <div class="system-card">
    <div class="system-label">RMSE de yaw</div>
    <div class="system-value">0.098 rad</div>
  </div>
  <div class="system-card">
    <div class="system-label">Comando máximo</div>
    <div class="system-value">120 RPM</div>
  </div>
</div>

<p align="center">
  <img src="{{ site.baseurl }}/assets/img/control-rna/fase4_trayectoria.png"
       alt="Seguimiento de trayectoria en simulación"
       width="700">
  <br>
  <em>Seguimiento de trayectoria utilizando la planta neuronal.</em>
</p>

La simulación permitió verificar la lógica del controlador y detectar la saturación de los comandos antes de realizar la prueba física.

---

## Prueba física de posicionamiento

Para colocar el robot en el inicio del círculo se utilizó el objetivo:
x_d = 0.15 m y y_d = 0.20 m.

La prueba comenzó aproximadamente en: (-0.008, -0.007) m y terminó en: (0.160, 0.206) m.

<div class="result-highlight">
  <span class="result-number">1.18 cm</span>
  <span class="result-description">Error final de posicionamiento</span>
</div>

Este valor quedó dentro de la tolerancia aproximada de 3 cm utilizada durante la prueba.

El objetivo del modo de posición es converger a la coordenada solicitada; no se impone una trayectoria recta entre el inicio y el final.

<p align="center">
  <img src="{{ site.baseurl }}/assets/img/control-rna/comparativa_trayectoria.png"
       alt="Prueba física de posicionamiento"
       width="700">
  <br>
  <em>Trayectoria medida con VICON durante la llegada al punto de inicio del círculo.</em>
</p>

---

## Seguimiento circular físico

La validación física final se realizó con:

- Centro:(0.15, -0.20) m.
- Radio: 0.40 m.

La trayectoria medida por VICON se comparó con el círculo geométrico esperado.

<p align="center">
  <img src="{{ site.baseurl }}/assets/img/control-rna/comparativa_circulo.png"
       alt="Círculo esperado frente a trayectoria medida por VICON"
       width="700">
  <br>
  <em>Comparación entre la referencia circular y el movimiento obtenido.</em>
</p>

### Métricas

| Métrica | Resultado |
|---|---:|
| Radio de referencia | 40 cm |
| Error radial medio absoluto | **2.25 cm** |
| RMSE radial | **3.06 cm** |
| Error radial máximo | **8.11 cm** |
| Error medio / radio | **5.6 %** |

La trayectoria obtenida mantiene en general la forma circular esperada. Las mayores diferencias aparecen principalmente durante los cambios de movimiento y al inicio del seguimiento, mientras que durante la mayor parte del recorrido el error se mantiene considerablemente menor.

## Análisis de errores

### Deslizamiento de las ruedas Mecanum

El movimiento del RoboMaster depende del contacto de los rodillos de las ruedas Mecanum con el piso. Debido a esto, pueden presentarse pequeños deslizamientos tanto hacia adelante como de forma lateral, provocando que el movimiento real no coincida exactamente con el predicho por el modelo.

### Comando frente a velocidad real
Las RPM que se envían como comando a las ruedas no siempre son exactamente iguales a las velocidades que realmente alcanzan los motores. Por esta razón se utilizaron dos modelos directos: uno basado en los comandos enviados y otro basado en las velocidades medidas por los ESC.

### Retardo en la respuesta
También se observó un retraso aproximado de 0.10 s entre el momento en que se envía un comando y el instante en que se observa su efecto en el movimiento del robot. Este retardo puede afectar principalmente el seguimiento de trayectorias cuando la referencia cambia rápidamente

### Saturación de los motores 

Para mantener una operación segura, los comandos de las ruedas se limitaron a: ±120 RPM.

Cuando el controlador calcula una velocidad superior a este límite, el comando se satura. Como consecuencia, el robot no puede reproducir exactamente el movimiento solicitado en esos instantes.

### Ruido en las mediciones de VICON

Aunque VICON permite medir la posición del robot con buena precisión, al calcular las velocidades a partir de estas posiciones también se amplifican pequeñas variaciones de las mediciones. Para disminuir este efecto se utilizó un filtro Savitzky-Golay antes de realizar la derivación.

<p align="center">
  <img src="{{ site.baseurl }}/assets/img/control-rna/s_g_filtro.jpg"
       alt="Filtro"
       width="400">
  <br>
   <em>Figura 4. Filtro Savitzky-Golay durante respuesta al impulso.</em>
</p>

### Comportamiento de la red inversa
En el RoboMaster, un mismo movimiento puede obtenerse con combinaciones de RPM ligeramente diferentes. Por esta razón, la red inversa no necesariamente reproduce exactamente los comandos registrados durante las pruebas. Sin embargo, al evaluar el movimiento generado por estos comandos mediante la planta directa se obtuvo una consistencia considerablemente mayor.

## Interpretación general

Los resultados de las pruebas físicas muestran que el controlador fue capaz de cumplir los dos objetivos principales del proyecto. En la prueba de posicionamiento, el RoboMaster logró llegar al punto solicitado con un error final del orden de centímetros. Por otro lado, durante el seguimiento de trayectoria, el robot consiguió conservar la forma circular de referencia con un error relativamente pequeño respecto al radio utilizado.
Estos resultados muestran que las redes neuronales no se utilizaron únicamente para representar el comportamiento del RoboMaster en simulación, sino que también formaron parte del controlador utilizado directamente sobre el robot físico.

## Conclusiones

El proyecto permitió desarrollar y probar un sistema completo de identificación y control para el RoboMaster S1 utilizando datos experimentales y redes neuronales.

La RNA directa logró representar de manera satisfactoria el comportamiento del robot a partir de las velocidades de sus ruedas, obteniendo un R² global cercano a 0.88.

Por otro lado, la RNA inversa fue capaz de generar comandos de rueda a partir del movimiento deseado. Al evaluarla junto con la planta neuronal se obtuvo una consistencia global de aproximadamente: R² = 0.971.

Las pruebas con el robot físico también mostraron buenos resultados. En el control de posición se alcanzó el punto objetivo con un error final de 1.18 cm mientras que en el seguimiento circular de radio 40 cm se obtuvo un error radial medio de 2.25 cm.

Las principales diferencias entre el comportamiento esperado y el observado se deben a factores propios del sistema real, como el deslizamiento de las ruedas Mecanum, la saturación de los motores, el retardo entre los comandos y la respuesta del robot, y las variaciones que no quedan completamente representadas por el modelo.

Como mejora futura, podría incorporarse información de instantes anteriores, como comandos y velocidades previas, para que la red tenga en cuenta la evolución temporal del movimiento. También podrían probarse arquitecturas recurrentes para mejorar la respuesta durante los transitorios.
