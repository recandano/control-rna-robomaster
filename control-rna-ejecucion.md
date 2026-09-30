---
layout: default
title: Ejecución física
parent: Reporte del proyecto
nav_order: 7
permalink: /control-rna/ejecucion/
---

# Ejecución física

## Conexiones utilizadas

Durante la ejecución se utilizaron dos interfaces de red simultáneamente:

| Interfaz | Función |
|---|---|
| Wi-Fi | Comunicación con RoboMaster |
| Ethernet | Comunicación con VICON |

En la sesión de prueba:
<div class="system-grid">

  <div class="system-card">
    <div class="system-label">IP local Wi-Fi PC</div>
    <div class="system-value">192.168.2.34</div>
  </div>

  <div class="system-card">
    <div class="system-label">IP RoboMaster</div>
    <div class="system-value">192.168.2.1</div>
  </div>

  <div class="system-card">
    <div class="system-label">Servidor VICON</div>
    <div class="system-value">192.168.10.1:801</div>
  </div>

  <div class="system-card">
    <div class="system-label">Subject VICON</div>
    <div class="system-value">Zacarias</div>
  </div>

  <div class="system-card">
    <div class="system-label">Segment VICON</div>
    <div class="system-value">Zacarias</div>
  </div>

</div>

{: .note }
La IP local del Wi-Fi puede cambiar entre sesiones, por lo que debe verificarse con `ipconfig` antes de ejecutar el robot.

## Dependencias

### Entrenamiento y simulación

<div class="system-grid">

  <div class="system-card">
    <div class="system-label">Cálculo numérico</div>
    <div class="system-value">NumPy</div>
  </div>

  <div class="system-card">
    <div class="system-label">Manejo de datos</div>
    <div class="system-value">Pandas</div>
  </div>

  <div class="system-card">
    <div class="system-label">Procesamiento de señales</div>
    <div class="system-value">SciPy</div>
  </div>

  <div class="system-card">
    <div class="system-label">Preprocesamiento y métricas</div>
    <div class="system-value">scikit-learn</div>
  </div>

  <div class="system-card">
    <div class="system-label">Gráficas</div>
    <div class="system-value">Matplotlib</div>
  </div>

  <div class="system-card">
    <div class="system-label">Redes neuronales</div>
    <div class="system-value">PyTorch</div>
  </div>

</div>

### Ejecución física

<div class="system-grid">

  <div class="system-card">
    <div class="system-label">Control del robot</div>
    <div class="system-value">DJI RoboMaster SDK</div>
  </div>

  <div class="system-card">
    <div class="system-label">Captura de movimiento</div>
    <div class="system-value">VICON DataStream SDK</div>
  </div>

  <div class="system-card">
    <div class="system-label">Entorno de ejecución</div>
    <div class="system-value">Python 3.8</div>
  </div>

</div>

Python 3.8 se utilizó durante las pruebas físicas para mantener compatibilidad con el SDK del RoboMaster.

## Modos principales

| Modo | Función |
|---|---|
| --mode train | Entrena las redes |
| --mode simulate | Simula seguimiento |
| --mode simulate-point | Simula llegada a un punto |
| --mode point | Lleva físicamente el robot a una coordenada VICON |
| --mode live | Ejecuta seguimiento físico de trayectoria |

## Ejemplo: control hacia un punto

```bash
.venv\Scripts\python.exe control_rna_robomaster_completo.py --mode point --output-dir salida_control_rna --local-ip 192.168.2.34 --vicon-host 192.168.10.1:801 --vicon-subject Zacarias --vicon-segment Zacarias --target-x 0.15 --target-y 0.20 --duration 15
```

El objetivo corresponde a coordenadas absolutas del sistema VICON.

## Ejemplo: seguimiento del círculo

Después de colocar el robot en el punto inicial del círculo:

```bash
.venv\Scripts\python.exe control_rna_robomaster_completo.py --mode live --output-dir salida_control_rna --local-ip 192.168.2.34 --vicon-host 192.168.10.1:801 --vicon-subject Zacarias --vicon-segment Zacarias --duration 4.83
```

La duración debe corresponder a la velocidad angular configurada en trajectory_reference().
