---
layout: default
title: Reporte del proyecto
nav_order: 2
has_children: true
permalink: /control-rna/
---

# Control por RNA

**DJI RoboMaster S1 + VICON + PyTorch**

-Control Inteligente - Universidad Iberoamericana - Otoño 2026  

**Integrantes:**
- Regina Cándano
- Valerie Santos
- Diego Bravo
- Omar Rodríguez
- Joel Rio Valle

---

## Descripción general

El control de un robot omnidireccional con ruedas Mecanum presenta retos que no siempre pueden representarse correctamente con un modelo ideal. En el sistema real aparecen deslizamiento, fricción, diferencias entre motores, saturación de actuadores y retrasos entre el comando enviado y el movimiento observado.

Por esta razón, el proyecto se desarrolló con un enfoque basado en datos. A partir de registros experimentales del RoboMaster S1 y mediciones de VICON se entrenaron dos redes neuronales:

- Una red neuronal artificial (RNA) directa, que aprende cómo responde el robot ante las velocidades de sus cuatro ruedas;
- Una red neuronal artificial(RNA) inversa, que estima qué comandos deben enviarse para producir un movimiento deseado.

La idea general puede resumirse así:

`RPM de ruedas → RNA directa → movimiento del robot`

y para el control:

`Movimiento deseado → RNA inversa → RPM de ruedas`

Durante la ejecución física, VICON cierra el lazo:

`VICON → error de pose → controlador → RNA inversa → RoboMaster → VICON`

## Resumen del sistema

| Elemento | Configuración |
|---|---|
| Plataforma | DJI RoboMaster S1 |
| Localización | VICON |
| Frecuencia de control | 20 Hz |
| RNA directa | 4 → 64 → 64 → 32 → 3 |
| RNA inversa | 3 → 64 → 64 → 32 → 4 |
| Dataset | 4,344 muestras válidas |
| Retardo identificado | 0.10 s |
| Límite de ruedas | ±120 RPM |
| Error final de punto | 1.18 cm |
| Error radial medio | 2.25 cm |
## Objetivo general

Desarrollar e implementar un sistema de identificación y control basado en redes neuronales artificiales para un DJI RoboMaster S1, utilizando VICON para validar su comportamiento en simulación y en pruebas físicas.

## Objetivos específicos

- Obtener un dataset experimental que relacione los comandos de las ruedas con el movimiento real del robot.
- Procesar y sincronizar la información registrada.
- Entrenar una RNA directa para aproximar la dinámica del chasis.
- Entrenar una RNA inversa para generar comandos de rueda.
- Implementar control de posición en lazo cerrado.
- Llevar al robot a coordenadas globales de VICON.
- Implementar seguimiento de trayectoria circular.
- Comparar cuantitativamente la trayectoria esperada y la obtenida.

## Navegación del reporte

Las secciones del proyecto se encuentran separadas en las siguientes páginas:

- **Metodología y datos:** adquisición, limpieza y preprocesamiento.
- **Modelos neuronales:** RNA directa, RNA inversa y métricas.
- **Control en lazo cerrado:** VICON, control de posición y seguimiento.
- **Resultados:** simulación, prueba de punto, círculo y análisis de errores.
- **Ejecución física:** conexiones, comandos, seguridad y procedimiento experimental.
