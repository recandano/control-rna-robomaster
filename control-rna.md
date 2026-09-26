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
## Resumen del sistema

<div class="system-grid">

  <div class="system-card">
    <div class="system-label">Plataforma</div>
    <div class="system-value">DJI RoboMaster S1</div>
  </div>

  <div class="system-card">
    <div class="system-label">Localización</div>
    <div class="system-value">VICON</div>
  </div>

  <div class="system-card">
    <div class="system-label">Frecuencia de control</div>
    <div class="system-value">20 Hz</div>
  </div>

  <div class="system-card">
    <div class="system-label">Dataset</div>
    <div class="system-value">4,344 muestras</div>
  </div>

  <div class="system-card">
    <div class="system-label">RNA directa</div>
    <div class="system-value">4 → 64 → 64 → 32 → 3</div>
  </div>

  <div class="system-card">
    <div class="system-label">RNA inversa</div>
    <div class="system-value">3 → 64 → 64 → 32 → 4</div>
  </div>

  <div class="system-card">
    <div class="system-label">Retardo identificado</div>
    <div class="system-value">0.10 s</div>
  </div>

  <div class="system-card">
    <div class="system-label">Límite de ruedas</div>
    <div class="system-value">±120 RPM</div>
  </div>

  <div class="system-card result-card">
    <div class="system-label">Error final de punto</div>
    <div class="system-value result-value">1.18 cm</div>
  </div>

  <div class="system-card result-card">
    <div class="system-label">Error radial medio</div>
    <div class="system-value result-value">2.25 cm</div>
  </div>

</div>
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
