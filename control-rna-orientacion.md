---
layout: default
title: Control de orientación
parent: Reporte del proyecto
nav_order: 4
permalink: /control-rna/orientacion/
---

# Control de orientación (Yaw)

El chasis del RoboMaster S1 utiliza ruedas Mecanum, lo que le otorga capacidades de movimiento omnidireccional. Esto permite desacoplar la traslación en el plano (movimientos en X y Y) de la rotación sobre su propio eje vertical (orientación o *yaw*). 

En este proyecto, el control de la orientación no se resolvió mediante cinemática analítica, sino que se integró directamente en el aprendizaje de la Red Neuronal Artificial Inversa.

## Medición y cálculo del error

El sistema VICON captura la pose absoluta del robot en el espacio físico, entregando el vector de estado `[x, y, yaw]` a una frecuencia de 20 Hz. Para el ángulo *yaw*, los datos en bruto de VICON se procesan utilizando una función de *unwrap* (desenrollado) para evitar discontinuidades matemáticas cuando el ángulo cruza los límites de π radianes.

El error de orientación se calcula en cada instante de tiempo comparando la referencia deseada con la medición actual:

`Error_yaw = Yaw_deseado - Yaw_actual`

## Inyección del error a la RNA Inversa

El error global de orientación, junto con los errores de posición, se procesa mediante un controlador Proporcional-Integral (PI) combinado con un término de *feedforward*. Este bloque genera las velocidades espaciales deseadas que el robot debe ejecutar en el siguiente paso de tiempo dt = 0.05 s.

El control inverso recibe como entrada este diferencial de pose en el marco de referencia local del chasis (body frame):

Entrada al control inverso: `[dx_body, dy_body, dyaw]`

El término `dyaw` representa la cantidad de rotación pura requerida. 

## Generación de comandos de rueda

A partir de la entrada `[dx_body, dy_body, dyaw]`, la RNA inversa (compuesta por capas lineales con activación SiLU) computa la velocidad angular necesaria para cada uno de los cuatro motores. 

Salida de la RNA inversa: `[w1, w2, w3, w4]` expresada en RPM.

Gracias a que la red fue entrenada con datos experimentales que capturan la dinámica real del chasis, el modelo neuronal "sabe" implícitamente que para generar un movimiento de rotación pura sobre su propio eje sin traslación, debe comandar las ruedas de un lado en sentido opuesto a las del otro lado, superando la fricción estática y el deslizamiento característico de los rodillos Mecanum.

<div class="result-highlight">
  <span class="result-number">Control unificado</span>
  <span class="result-description">La orientación no requiere un lazo de control aislado; se resuelve simultáneamente con la posición X-Y dentro de la matriz de pesos de la RNA.</span>
</div>
