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

| Métrica | Resultado |
|---|---:|
| RMSE de posición | 0.0926 m |
| MAE de posición | 0.0832 m |
| Error máximo | 0.1518 m |
| RMSE de yaw | 0.0983 rad |
| Comando máximo | 120 RPM |

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

`x_d = 0.15 m`

`y_d = 0.20 m`

La prueba comenzó aproximadamente en:

`(-0.008, -0.007) m`

y terminó en:

`(0.160, 0.206) m`

El error final fue de:

**1.18 cm**

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

- centro: `(0.15, -0.20) m`;
- radio: `0.40 m`.

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

La forma obtenida conserva claramente la geometría circular. El error máximo aparece principalmente en regiones transitorias, mientras que el error medio es considerablemente menor.

## Análisis de errores

### Deslizamiento de las ruedas Mecanum

El movimiento depende del contacto de múltiples rodillos con el piso. Esto provoca deslizamiento longitudinal y lateral y hace que la respuesta real varíe respecto al modelo.

### Comando frente a velocidad real

Las RPM comandadas no siempre coinciden exactamente con las velocidades reportadas por los ESC. Esta diferencia motivó el uso de dos modelos directos.

### Retardo dinámico

El retardo aproximado de 0.10 s afecta el seguimiento cuando la referencia cambia rápidamente.

### Saturación

Los comandos fueron limitados a:

`±120 RPM`

Cuando la referencia exige velocidades mayores, el controlador ya no puede reproducir exactamente el movimiento solicitado.

### Ruido de VICON

La diferenciación de posición amplifica pequeñas variaciones de medición. El filtrado Savitzky-Golay reduce este efecto sin eliminar por completo la dinámica.

### Ambigüedad de la dinámica inversa

Distintas combinaciones de RPM pueden producir movimientos similares. Por ello, algunos `R²` individuales de rueda son modestos, mientras que la consistencia global del movimiento es mucho mayor.

## Interpretación general

Los resultados físicos muestran dos comportamientos importantes:

1. el controlador es capaz de llevar el robot a una posición fija con error del orden de centímetros;
2. la trayectoria circular real conserva la forma esperada y presenta un error radial medio relativamente pequeño respecto al radio de referencia.

Esto confirma que la red neuronal no se utilizó únicamente como modelo de simulación, sino como parte efectiva de un sistema de control en tiempo real.

## Conclusiones

El proyecto completó el ciclo completo de identificación y control basado en datos.

La RNA directa logró representar una parte importante de la dinámica del RoboMaster, con `R²` global cercano a 0.88.

La RNA inversa, evaluada en conjunto con la planta aprendida, alcanzó una consistencia global de aproximadamente:

**R² = 0.971**

En el robot físico se obtuvo un error final de 1.18 cm en control de posición y un error radial medio de 2.25 cm durante la trayectoria circular de radio 40 cm.

Las principales limitaciones siguen asociadas a deslizamiento, saturación, retardo y dinámica temporal no modelada explícitamente.

Como trabajo futuro sería interesante incluir historial de comandos, velocidad actual del cuerpo y arquitecturas recurrentes para representar mejor los transitorios.
