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

## Inicialización y conexiones
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
```

## Carga de modelos y preprocesamiento
Antes de iniciar el ciclo, el script instancia la RNA inversa utilizando PyTorch. Los pesos preentrenados se cargan en memoria para asegurar que la inferencia (el cálculo de las RPM a partir del error) sea lo más rápida posible y no retrase el tiempo de muestreo.
```python
# Carga de los pesos del controlador neuronal
inverse_path = args.output_dir / "controlador_inverso.pt"
inverse = RegressionBundle.load(inverse_path)

# Inicialización del controlador integrando el modelo neuronal y la configuración
controller = PositionController(inverse, cfg)
```

## Lazo de control en tiempo real (20 Hz)
El corazón del sistema es un bucle iterativo restringido a ejecutarse cada 0.05 segundos. La secuencia de operaciones es estricta:
1. Retroalimentación espacial: Se solicita la pose absoluta [x, y, yaw] a VICON. Si el sistema reporta oclusión (Occluded=True), el comando espera por seguridad.
2. Cálculo del error: Se compara la medición con la referencia paramétrica de la trayectoria.
3. Dinámica de control: El bloque controlador transforma el error en un diferencial de pose local y la RNA inversa calcula los comandos ideales de rueda.
```python
while True:
    elapsed = time.perf_counter() - t0
    if elapsed >= duration_s:
        break

    # 1. Retroalimentación de VICON
    pose = pose_provider.read_pose()
    
    # 2. Generación de referencia y feedforward
    t_ctrl = elapsed + cfg.lookahead_steps * cfg.dt_control
    ref, v_ff, omega_ff = trajectory_reference(
        t_ctrl, cfg.trajectory_yaw_mode, yaw_hold
    )

    # 3. Cálculo de error e inferencia de la RNA
    rpm = controller.controlador_trayectoria(
        pose, ref, v_ff, omega_ff
    )
    
    # 4. Envío de comandos físicos
    send_rpm(chassis, rpm, swap_w3_w4)

    # Mantenimiento estricto de la frecuencia a 20 Hz
    next_tick += cfg.dt_control
    sleep = next_tick - time.perf_counter()
    if sleep > 0:
        time.sleep(sleep)
    else:
        next_tick = time.perf_counter()
```

## Protección de hardware y Slew Rate
Las redes neuronales pueden generar comandos matemáticamente correctos pero físicamente inviables (como aceleraciones instantáneas). Para proteger el hardware, el código implementa dos filtros antes de transmitir los comandos finales:
- Saturación: Limita las salidas a la capacidad máxima de los motores (±120 RPM).
-Filtro Slew Rate: Restringe la tasa máxima de cambio de velocidad entre ciclos consecutivos. Esto evita picos altos de corriente en la batería y previene que los rodillos Mecanum patinen por pérdida de tracción.
```python
# Predicción de la RNA con primera saturación a ±120 RPM
rpm = np.clip(
    self.inverse.predict(delta),
    -self.cfg.rpm_limit,
    self.cfg.rpm_limit,
)

# Filtro Slew Rate: Restricción del cambio máximo permitido por ciclo
step = np.clip(
    rpm - self.previous_rpm,
    -self.cfg.rpm_slew_per_step,
    self.cfg.rpm_slew_per_step,
)

# Actualización del comando protegido
rpm = np.clip(
    self.previous_rpm + step,
    -self.cfg.rpm_limit,
    self.cfg.rpm_limit,
)
self.previous_rpm = rpm.copy()
```
