---
layout: default
title: Metodología y datos
parent: Reporte del proyecto
nav_order: 1
permalink: /control-rna/metodologia/
---

# Metodología y datos

## Adquisición experimental

La identificación del RoboMaster S1 se realizó a partir de datos obtenidos directamente del robot y del sistema VICON.

Durante las pruebas se aplicaron diferentes señales de excitación a las ruedas con el objetivo de observar el comportamiento del chasis en movimientos longitudinales, laterales y rotacionales. Para cada muestra se registraron tanto las señales enviadas como la respuesta física medida.

El CSV utilizado para entrenamiento contenía, entre otras variables:

- Tiempo de adquisición;
- Fase o tipo de excitación;
- Comandos de movimiento;
- Velocidades comandadas de las cuatro ruedas;
- Velocidades reportadas por los ESC;
- Posición global de VICON;
- Orientación del robot.

El archivo original contenía 4,345 registros. Durante la limpieza se eliminó un timestamp duplicado, por lo que el conjunto final quedó en 4,344 muestras.

La frecuencia de trabajo para el procesamiento y el control se estableció aproximadamente en 20 Hz, equivalente a:
`dt = 0.05 s`

## Preprocesamiento

### Conversión de unidades

VICON reporta las posiciones en milímetros. Para trabajar de forma consistente con el controlador se realizó:

`x [m] = TX / 1000`

`y [m] = TY / 1000`

### Tratamiento de yaw

El ángulo `yaw` presenta una discontinuidad natural entre `-π` y `π`. Antes de derivar la orientación se utilizó `unwrap` para evitar saltos artificiales, y posteriormente se aplicó `wrap_to_pi` al calcular errores angulares.

### Filtrado

La diferenciación amplifica el ruido de las mediciones. Para reducir este efecto se utilizó un filtro **Savitzky-Golay**, con ventana de siete muestras y polinomio de segundo orden.

### Obtención de velocidades

A partir de la posición medida por VICON y del tiempo real se estimaron:

- velocidad global en X;
- velocidad global en Y;
- velocidad angular.

Después, las velocidades globales se transformaron al marco local del robot mediante la orientación `yaw`.

Esta transformación permite que las redes aprendan el movimiento desde el punto de vista del propio RoboMaster, independientemente de su orientación global dentro del laboratorio.

## División de datos

El dataset se dividió temporalmente de la siguiente forma:

| Conjunto | Porcentaje |
|---|---:|
| Train | 80 % |
| Validation | 10 % |
| Test | 10 % |

La división temporal evita que muestras casi idénticas y consecutivas aparezcan simultáneamente en entrenamiento y prueba.

Los objetos `StandardScaler` se ajustaron únicamente con el conjunto de entrenamiento.

## Retardo comando-respuesta

El comportamiento del robot mostró un retraso entre el comando enviado y la respuesta observada.

La búsqueda del retardo se realizó utilizando únicamente datos de Train/Validation. El mejor valor encontrado para la relación comando-respuesta fue de aproximadamente:

**0.10 s**

equivalente a **2 pasos** de 0.05 s.

Este retardo fue considerado al entrenar la planta basada en comandos y al analizar el seguimiento de trayectoria.
