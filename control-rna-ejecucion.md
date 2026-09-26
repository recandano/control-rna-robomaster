---
layout: default
title: Ejecución y comandos
parent: Evaluación 1 - Control por RNA
nav_order: 5
permalink: /control-rna-ejecucion/
---

# Ejecución y comandos

## Entorno

Para la ejecución física se utilizó Python 3.8 en un entorno virtual. Las dependencias principales son:

```text
numpy
pandas
torch
scipy
scikit-learn
matplotlib
robomaster
vicon_dssdk
```

La computadora debe mantener dos conexiones simultáneas:

- **Wi-Fi** hacia el RoboMaster. `--local-ip` corresponde a la IPv4 de ese adaptador.
- **Ethernet** hacia VICON. El host utilizado fue `192.168.10.1:801`.

En la sesión reportada la IP local Wi-Fi fue `192.168.2.34`; puede cambiar y debe verificarse con `ipconfig`.

## Comprobar VICON antes de mover el robot

Antes de ejecutar el control, VICON debe entregar una pose válida y no ocluida. Si la lectura indica `Occluded=True`, el robot no debe recibir comandos.

## Llegar al inicio del círculo

```bash
.venv\\Scripts\\python.exe control_rna_robomaster_completo.py --mode point --output-dir salida_control_rna --local-ip 192.168.2.34 --vicon-host 192.168.10.1:801 --vicon-subject Zacarias --vicon-segment Zacarias --target-x 0.15 --target-y 0.20 --duration 15
```

## Ejecutar una vuelta

Con `omega = 1.3 rad/s`, una vuelta tarda aproximadamente `2*pi/1.3 = 4.83 s`.

```bash
.venv\\Scripts\\python.exe control_rna_robomaster_completo.py --mode live --output-dir salida_control_rna --local-ip 192.168.2.34 --vicon-host 192.168.10.1:801 --vicon-subject Zacarias --vicon-segment Zacarias --duration 4.83
```

## Modos del programa

| Modo | Función |
|---|---|
| `train` | Preprocesa datos y entrena modelos |
| `simulate` | Simula seguimiento usando la planta neuronal |
| `simulate-point` | Simula llegada a una pose fija |
| `point` | Lleva físicamente el robot a una pose VICON |
| `live` | Ejecuta seguimiento físico de trayectoria |

## Reglas de seguridad

- comprobar el espacio físico antes de ejecutar;
- verificar que VICON rastrea `Zacarias`;
- usar la IP Wi-Fi correcta de la PC;
- mantener `Ctrl+C` disponible;
- no ejecutar si VICON devuelve pose ocluida;
- realizar pruebas inicialmente con velocidades moderadas;
- comprobar físicamente el orden de ruedas antes de una trayectoria rápida.
