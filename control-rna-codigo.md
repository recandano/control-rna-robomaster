---
layout: default
title: Código principal
parent: Reporte del proyecto
nav_order: 5
permalink: /control-rna/codigo/
---

# Código principal y arquitectura de software

El script `control_rna_robomaster_corregido.py` es el núcleo de ejecución del proyecto. Su función es orquestar la comunicación entre el sistema de captura de movimiento (VICON), los modelos neuronales preentrenados (PyTorch) y el hardware del robot (SDK del RoboMaster S1).

A continuación, se desglosan los bloques lógicos fundamentales que componen el algoritmo de control físico.

## 1. Inicialización y conexiones
El sistema requiere establecer dos enlaces de comunicación críticos de baja latencia antes de comenzar el movimiento: la conexión Ethernet al servidor VICON para la retroalimentación y el socket Wi-Fi local hacia el RoboMaster S1.

```python
def connect_robomaster(local_ip: Optional[str]):
    import robomaster
    from robomaster import robot
    
    # Configuración de IP y conexión vía UDP
    if local_ip:
        robomaster.config.LOCAL_IP_STR = local_ip
        
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap", proto_type="udp")
    return ep_robot, ep_robot.chassis

# Instanciación de los clientes de comunicación en la ejecución en vivo
pose_provider = ViconPoseProvider(vicon_host, vicon_subject, vicon_segment)
ep_robot, chassis = connect_robomaster(local_ip)
