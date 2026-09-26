---
layout: default
title: Resultados y análisis
parent: Evaluación 1 - Control por RNA
nav_order: 4
permalink: /control-rna-resultados/
---

# Resultados y análisis

## Simulación

La simulación cerrada utiliza la planta neuronal CMD como sustituto del robot físico y el mismo controlador inverso que posteriormente se ejecuta con VICON.

![Seguimiento en simulación]({{ site.baseurl }}/assets/img/control-rna/fase4_simulacion.png)

| Métrica | Resultado |
|---|---:|
| RMSE posición | 0.0926 m |
| MAE posición | 0.0832 m |
| Error máximo | 0.1518 m |
| RMSE yaw | 0.0983 rad |
| Máximo comando | 120 RPM |

La saturación de 120 RPM fue una de las principales limitaciones para la referencia circular rápida.

## Prueba física de posición

Para posicionar el robot en el inicio del círculo se utilizó como objetivo `(0.15, 0.20)` m.

![Prueba física de punto]({{ site.baseurl }}/assets/img/control-rna/comparativa_trayectoria.png)

| Dato | Valor |
|---|---:|
| Inicio | (-0.008, -0.007) m |
| Objetivo | (0.150, 0.200) m |
| Final VICON | (0.160, 0.206) m |
| Error final | **1.18 cm** |

El objetivo del control de punto es converger a la posición, no recorrer una línea recta. Por eso, la curva real puede ser distinta a una conexión geométrica directa entre inicio y objetivo.

![Error al objetivo]({{ site.baseurl }}/assets/img/control-rna/error_punto_fisico.png)

## Prueba física del círculo

Se evaluó un círculo de radio 0.40 m y centro `(0.15, -0.20)` m.

![Círculo esperado vs obtenido]({{ site.baseurl }}/assets/img/control-rna/comparativa_circulo.png)

| Métrica física | Resultado |
|---|---:|
| Error radial medio absoluto | **2.25 cm** |
| RMSE radial | **3.06 cm** |
| Error radial máximo | **8.11 cm** |
| Error medio relativo al radio | 5.6 % |

![Error radial físico]({{ site.baseurl }}/assets/img/control-rna/error_radial_fisico.png)

El recorrido conserva claramente la geometría circular. El error máximo ocurre de manera localizada durante transitorios; el error promedio es considerablemente menor.

## Principales fuentes de error

- deslizamiento longitudinal y lateral de las ruedas Mecanum;
- diferencia entre comando de RPM y velocidad real medida por ESC;
- retardo aproximado de 0.10 s;
- saturación de las ruedas a ±120 RPM;
- ruido introducido al derivar mediciones de VICON;
- dinámica inversa no estrictamente unívoca durante transitorios;
- errores de alineación entre el marco global VICON y el marco local del robot.

## Conclusión

Los resultados muestran que la identificación neuronal representa de forma útil el comportamiento del RoboMaster y que el controlador inverso puede emplearse en un lazo cerrado real. La prueba de punto logró un error final de 1.18 cm y el seguimiento circular presentó un error radial medio de 2.25 cm. El desempeño puede mejorar incorporando historial temporal, velocidad actual del cuerpo o modelos recurrentes.
