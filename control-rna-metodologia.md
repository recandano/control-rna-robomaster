---
layout: default
title: Metodología y datos
parent: Reporte del proyecto
nav_order: 1
permalink: /control-rna/metodologia/
---

# Metodología y datos

## Adquisición experimental

Para aprender cómo responde el RoboMaster S1 ante distintos comandos de rueda, se realizaron pruebas experimentales utilizando el robot y el sistema VICON.

Durante estas pruebas se aplicaron distintas señales de excitación a las ruedas para  observar el comportamiento del chasis con  movimientos hacia adelante, hacia los lados y de rotación. En cada instante se registraron tanto los comandos enviados al robot como la respuesta real medida por VICON.


El CSV utilizado para entrenamiento contenía, entre otras variables:

- Tiempo de adquisición.
- Fase o tipo de excitación.
- Comandos de movimiento.
- Velocidades comandadas de las cuatro ruedas.
- Velocidades reportadas por los ESC.
- Posición global de VICON.
- Orientación del robot.

El archivo original contenía 4,345 registros. Durante la limpieza se eliminó un timestamp duplicado, por lo que el conjunto final quedó en 4,344 muestras.

La frecuencia de trabajo para el procesamiento y el control se estableció aproximadamente en 20 Hz, equivalente a:dt = 0.05 s

## Preprocesamiento

### Conversión de unidades

VICON reporta las posiciones en milímetros. Para trabajar de forma consistente con el controlador se realizó:

`x [m] = TX / 1000`

`y [m] = TY / 1000`

### Tratamiento de yaw
Como el ángulo yaw cambia de π a -π, pueden aparecer saltos artificiales en la señal. Por eso se utilizó unwrap antes de derivar la orientación y obtener la velocidad angular. Después, al calcular el error de orientación, se aplicó wrap_to_pi para evitar que una diferencia pequeña se interpretara como un giro casi completo.

### Filtrado

La diferenciación amplifica el ruido de las mediciones. Para reducir este efecto se utilizó un filtro Savitzky-Golay, con ventana de 7 muestras y polinomio de segundo orden.

### Obtención de velocidades
A partir de las posiciones registradas por VICON y del tiempo transcurrido se calcularon las velocidades del robot en los ejes globales X y Y, así como su velocidad angular.

Después, estas velocidades se transformaron al sistema de referencia del propio RoboMaster utilizando su orientación yaw.
De esta forma, la red neuronal aprende el movimiento desde la perspectiva del robot sin depender de la dirección en la que esté orientado dentro del laboratorio.

## División de datos

El dataset se dividió temporalmente de la siguiente forma:

| Conjunto | Porcentaje |
|---|---:|
| Train | 80 % |
| Validation | 10 % |
| Test | 10 % |

La división temporal evita que muestras casi idénticas y consecutivas aparezcan simultáneamente en entrenamiento y prueba.

Los objetos StandardScaler se ajustaron únicamente con el conjunto de entrenamiento.

## Retardo comando-respuesta
Durante las pruebas se observó que el RoboMaster no respondía de forma instantánea a los comandos enviados a las ruedas. Para estimar este retraso se analizaron los datos de entrenamiento y validación, comparando el momento en que se aplicaba un comando con el instante en que comenzaba a observarse su efecto en el movimiento del robot.

El retardo estimado fue de aproximadamente 0.10 s, equivalente a dos periodos de control de 0.05 s.

Este retardo se consideró tanto en el entrenamiento del modelo basado en comandos como en el análisis del seguimiento de trayectoria, ya que el movimiento del robot ocurre unos instantes después de enviar cada comando.
