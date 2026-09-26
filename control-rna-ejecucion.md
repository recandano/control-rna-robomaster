---
layout: default
title: Ejecución física
parent: Reporte del proyecto
nav_order: 5
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

`IP local Wi-Fi PC = 192.168.2.34`

`IP RoboMaster = 192.168.2.1`

`VICON = 192.168.10.1:801`

El objeto de Tracker utilizado fue:

`Subject = Zacarias`

`Segment = Zacarias`

> La IP local del Wi-Fi puede cambiar entre sesiones. Debe verificarse con `ipconfig` antes de ejecutar el robot.

## Dependencias

Para entrenamiento y simulación:

- NumPy
- Pandas
- SciPy
- scikit-learn
- Matplotlib
- PyTorch

Para ejecución física:

- SDK oficial de DJI RoboMaster;
- VICON DataStream SDK (`vicon_dssdk`).

Durante las pruebas se utilizó Python 3.8 para mantener compatibilidad con el SDK del RoboMaster.

## Modos principales

| Modo | Función |
|---|---|
| `--mode train` | Entrena las redes |
| `--mode simulate` | Simula seguimiento |
| `--mode simulate-point` | Simula llegada a un punto |
| `--mode point` | Lleva físicamente el robot a una coordenada VICON |
| `--mode live` | Ejecuta seguimiento físico de trayectoria |

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

La duración debe corresponder a la velocidad angular configurada en `trajectory_reference()`.

## Seguridad

La implementación incorpora:

- saturación a ±120 RPM;
- limitación de variación entre comandos;
- `timeout` en `drive_wheels`;
- envío de RPM cero al finalizar;
- cierre de conexiones en `finally`;
- posibilidad de detener mediante `Ctrl+C`;
- rechazo de frames VICON ocluidos.

Antes de cada prueba debe comprobarse:

- Tracker en modo LIVE;
- objeto `Zacarias` visible;
- lectura válida de `[x, y, yaw]`;
- área física despejada;
- IP correcta del Wi-Fi;
- orientación y orden de ruedas verificados.

## Orden de ruedas

El script conserva el orden de ruedas utilizado durante la adquisición del dataset.

Si la instalación física del SDK utiliza una convención diferente para las ruedas traseras, existe la opción:

`--sdk-swap-w3-w4`

Esta opción solamente intercambia las salidas `w3` y `w4` antes de transmitirlas al robot. No modifica ni reentrena las redes neuronales.

