import sys
sys.path.insert(0, r"C:\RoboMaster-SDK-master\RoboMaster-SDK-master\src")

import time
import math
import random
import csv
import json
import threading
from datetime import datetime

from robomaster import robot
from robomaster import config
from vicon_dssdk import ViconDataStream as vds

config.LOCAL_IP_STR = "192.168.2.34"
config.ROBOT_IP_STR = "192.168.2.1"

VICON_HOST = "localhost:801"
VICON_SUBJECT = "Zacarias"
VICON_SEGMENT = "Zacarias"
VICON_FREQ = 100

FASES = ["calibracion", "claqueta_ini", "asterisco", "espiral", "ruido",
         "claqueta_fin"]

CAL_RPM     = 80
CAL_DUR     = 2.0
CAL_PAUSA   = 2.0
PATRONES    = [(+1, +1, +1, +1), (+1, -1, -1, +1), (+1, -1, +1, -1)]

CLAQ_RPM    = 110
CLAQ_DUR    = 1.0

R_ASTERISCO = 1.2
N_RAYOS     = 8

R_ESP_INI   = 0.3
R_ESP_FIN   = 1.5
VUELTAS_ESP = 3
PTS_ESPIRAL = 36

RUIDO_TIME  = 90
NOISE_ALPHA = 0.02
RPM_STD     = 45

RPM_LIMIT   = 120
RPM_MIN     = 25
R_MAX       = 2.5

KP_POS      = 180.0
KP_YAW      = 2.0
WP_TOL      = 0.12
WP_TOL_ESP  = 0.18
WP_TIMEOUT  = 10.0
WP_SETTLE   = 0.4

LOOP_DT     = 0.05
CMD_TIMEOUT = 0.5
SUB_FREQ    = 20
FINAL_HOLD  = 3.0

Y_SIGN      = +1

vicon_lock = threading.Lock()
vicon_activo = True
vicon_estado = {"x": None, "y": None, "z": None,
                "roll": None, "pitch": None, "yaw": None}
vicon_fallos = 0


def inv3(M):
    a, b, c = M[0]
    d, e, f = M[1]
    g, h, i = M[2]
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    if abs(det) < 1e-9:
        raise ValueError("matriz singular")
    return [
        [(e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det],
        [(f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det],
        [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det],
    ]


def matvec3(M, v):
    return [sum(M[r][k] * v[k] for k in range(3)) for r in range(3)]


def clip(v, lim):
    return max(-lim, min(lim, v))


def wrap180(a):
    return (a + 180.0) % 360.0 - 180.0


def global_to_body(dx, dy, yaw_deg):
    a = math.radians(yaw_deg or 0.0)
    ca, sa = math.cos(a), math.sin(a)
    return ca * dx + sa * dy, -sa * dx + ca * dy


def escalar_a_limite(w, lim):
    pico = max(abs(v) for v in w)
    if pico > lim:
        f = lim / pico
        return tuple(v * f for v in w)
    return tuple(w)


def ruedas_a_amplitudes(w):
    return [sum(w[j] * patron[j] for j in range(4)) / (4.0 * CAL_RPM)
            for patron in PATRONES]


def lector_vicon(cli):
    global vicon_fallos
    periodo = 1.0 / VICON_FREQ
    while vicon_activo:
        try:
            cli.GetFrame()
            xyz = cli.GetSegmentGlobalTranslation(VICON_SUBJECT, VICON_SEGMENT)[0]
            rpy = cli.GetSegmentGlobalRotationEulerXYZ(VICON_SUBJECT, VICON_SEGMENT)[0]
            with vicon_lock:
                if xyz is None or rpy is None:
                    vicon_fallos += 1
                else:
                    vicon_estado["x"], vicon_estado["y"], vicon_estado["z"] = xyz
                    vicon_estado["roll"], vicon_estado["pitch"], vicon_estado["yaw"] = rpy
        except Exception:
            with vicon_lock:
                vicon_fallos += 1
        time.sleep(periodo)


class RuidoFiltrado:
    def __init__(self, alpha=0.02, seed=None):
        self.alpha = alpha
        self.rng = random.Random(seed)
        self.state = 0.0
        self.gain = math.sqrt(3.0 * (2 - alpha) / alpha)

    def next(self):
        white = self.rng.uniform(-1, 1)
        self.state = self.alpha * white + (1 - self.alpha) * self.state
        return self.state * self.gain


def main():
    global vicon_activo

    print("Conectando con VICON...")
    cli = vds.Client()
    cli.Connect(VICON_HOST)
    cli.EnableSegmentData()
    cli.SetStreamMode(vds.Client.StreamMode.EClientPull)
    cli.GetFrame()

    sujetos = cli.GetSubjectNames()
    print(f"Sujetos: {sujetos}")
    if VICON_SUBJECT not in sujetos:
        raise SystemExit(f"'{VICON_SUBJECT}' no esta activo en Nexus.")

    threading.Thread(target=lector_vicon, args=(cli,), daemon=True).start()
    time.sleep(1.0)

    with vicon_lock:
        if vicon_estado["x"] is None:
            raise SystemExit("VICON no entrega pose. Revisa marcadores y Live.")
        print(f"Pose inicial VICON: x={vicon_estado['x']:.1f} "
              f"y={vicon_estado['y']:.1f} mm")

    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    chassis = ep_robot.chassis

    log = []
    pos = {"x": None, "y": None, "z": None}
    att = {"yaw": None, "pitch": None, "roll": None}
    esc = {"w1": None, "w2": None, "w3": None, "w4": None}

    def on_position(p):
        pos["x"], pos["y"], pos["z"] = p[0], p[1], p[2]

    def on_attitude(a):
        att["yaw"], att["pitch"], att["roll"] = a

    def on_esc(e):
        speed, angle, ts, state = e
        esc["w1"] = speed[0]
        esc["w2"] = -speed[1]
        esc["w3"] = -speed[2]
        esc["w4"] = speed[3]

    chassis.sub_position(freq=SUB_FREQ, callback=on_position)
    chassis.sub_attitude(freq=SUB_FREQ, callback=on_attitude)
    chassis.sub_esc(freq=SUB_FREQ, callback=on_esc)

    t0 = time.time()
    while pos["x"] is None and time.time() - t0 < 5:
        time.sleep(0.1)
    if pos["x"] is None:
        vicon_activo = False
        chassis.unsub_position()
        chassis.unsub_attitude()
        chassis.unsub_esc()
        ep_robot.close()
        raise SystemExit("No llega odometria. Revisa la conexion.")

    ORIG_X = pos["x"]
    ORIG_Y = Y_SIGN * pos["y"]
    ORIG_YAW = att["yaw"] or 0.0

    t_start = time.time()
    next_tick = t_start

    def pose_rel():
        if pos["x"] is None:
            return None, None, None
        return (pos["x"] - ORIG_X,
                Y_SIGN * pos["y"] - ORIG_Y,
                wrap180((att["yaw"] or 0.0) - ORIG_YAW))

    def tick():
        nonlocal next_tick
        next_tick += LOOP_DT
        s = next_tick - time.time()
        if s > 0:
            time.sleep(s)
        else:
            next_tick = time.time()

    def grabar(fase, etiqueta, w, extra=None):
        px, py, yaw = pose_rel()
        a = ruedas_a_amplitudes(w)

        with vicon_lock:
            vx = vicon_estado["x"]
            vy = vicon_estado["y"]
            vz = vicon_estado["z"]
            vroll = vicon_estado["roll"]
            vpitch = vicon_estado["pitch"]
            vyaw = vicon_estado["yaw"]

        row = {
            "t_s": round(time.time() - t_start, 3),
            "fase": fase,
            "etiqueta": etiqueta,
            "ax_cmd": round(a[0], 4),
            "ay_cmd": round(a[1], 4),
            "aw_cmd": round(a[2], 4),
            "w1_cmd": round(w[0], 2), "w2_cmd": round(w[1], 2),
            "w3_cmd": round(w[2], 2), "w4_cmd": round(w[3], 2),
            "w1_esc": esc["w1"], "w2_esc": esc["w2"],
            "w3_esc": esc["w3"], "w4_esc": esc["w4"],
            "x_vicon": None if vx is None else round(vx, 2),
            "y_vicon": None if vy is None else round(vy, 2),
            "z_vicon": None if vz is None else round(vz, 2),
            "roll": None if vroll is None else round(vroll, 5),
            "pitch": None if vpitch is None else round(vpitch, 5),
            "yaw": None if vyaw is None else round(vyaw, 5),
            "x_rel_mm": None if px is None else round(px * 1000, 1),
            "y_rel_mm": None if py is None else round(py * 1000, 1),
            "yaw_rel": None if yaw is None else round(yaw, 3),
            "yaw_odom": att["yaw"], "pitch_odom": att["pitch"],
            "roll_odom": att["roll"],
            "tgt_x": None, "tgt_y": None,
        }
        if extra:
            row.update(extra)
        log.append(row)

    def mandar(w, fase, etiqueta, extra=None):
        w = escalar_a_limite(w, RPM_LIMIT)
        chassis.drive_wheels(w1=w[0], w2=w[1], w3=w[2], w4=w[3],
                             timeout=CMD_TIMEOUT)
        grabar(fase, etiqueta, w, extra)
        tick()

    def parar(pausa=0.0):
        chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
        if pausa > 0:
            t_p = time.time()
            while time.time() - t_p < pausa:
                grabar("pausa", "quieto", (0, 0, 0, 0))
                tick()

    M = None
    M_inv = None
    cal_medido = []

    def calibrar():
        nonlocal M, M_inv
        print("FASE 0: autocalibracion")
        cols = []

        for idx, patron in enumerate(PATRONES):
            parar(CAL_PAUSA)
            px0, py0, yaw0 = pose_rel()
            t_ini = time.time()

            while time.time() - t_ini < CAL_DUR:
                mandar([s * CAL_RPM for s in patron],
                       "calibracion", f"patron{idx}")

            parar(1.0)
            px1, py1, yaw1 = pose_rel()

            dx, dy = px1 - px0, py1 - py0
            dyaw = wrap180(yaw1 - yaw0)
            yaw_med = yaw0 + dyaw / 2.0
            bx, by = global_to_body(dx, dy, yaw_med)

            vx, vy, w_ = bx / CAL_DUR, by / CAL_DUR, dyaw / CAL_DUR
            cols.append((vx, vy, w_))
            cal_medido.append({
                "patron": patron, "dx": round(dx, 3), "dy": round(dy, 3),
                "dyaw": round(dyaw, 1), "vx": round(vx, 3),
                "vy": round(vy, 3), "w": round(w_, 2),
            })
            print(f"  patron {patron}: vx={vx:+.3f} m/s  vy={vy:+.3f} m/s  "
                  f"w={w_:+.1f} deg/s")

        M = [[cols[c][r] for c in range(3)] for r in range(3)]
        try:
            M_inv = inv3(M)
            print("  matriz cinematica identificada\n")
        except ValueError:
            M_inv = None
            print("  ! matriz singular, se omiten asterisco y espiral\n")

    def mov_a_ruedas(vx_des, vy_des, w_des):
        if M_inv is None:
            return None
        a = matvec3(M_inv, [vx_des, vy_des, w_des])
        w = [0.0, 0.0, 0.0, 0.0]
        for k, patron in enumerate(PATRONES):
            for j in range(4):
                w[j] += a[k] * patron[j] * CAL_RPM
        return w

    def claqueta(nombre):
        print(f"FASE: {nombre}")
        parar(1.0)
        t_ini = time.time()
        while time.time() - t_ini < CLAQ_DUR:
            w = mov_a_ruedas(0.0, 0.0, 60.0)
            if w is None:
                w = [CLAQ_RPM] * 4
            mandar(w, nombre, "giro_sync")
        parar(1.0)

    def ir_a(tx, ty, fase, tol):
        t_wp = time.time()
        while time.time() - t_wp < WP_TIMEOUT:
            px, py, yaw = pose_rel()
            if px is None:
                mandar((0, 0, 0, 0), fase, "sin_odom")
                continue

            ex, ey = tx - px, ty - py
            err = math.hypot(ex, ey)
            if err <= tol:
                return True

            bx, by = global_to_body(ex, ey, yaw)
            mag = math.hypot(bx, by)
            vel = clip(KP_POS * mag, RPM_LIMIT) / KP_POS
            if vel * KP_POS < RPM_MIN:
                vel = RPM_MIN / KP_POS

            vx_des = bx / mag * vel
            vy_des = by / mag * vel
            w_des = clip(-KP_YAW * (yaw or 0.0), 30) / KP_POS

            w = mov_a_ruedas(vx_des, vy_des, w_des)
            if w is None:
                return False
            mandar(w, fase, "hacia_wp",
                   {"tgt_x": round(tx, 3), "tgt_y": round(ty, 3)})

        return False

    def asterisco():
        if M_inv is None:
            return
        print(f"FASE: asterisco - {N_RAYOS} rayos de {R_ASTERISCO} m")
        for k in range(N_RAYOS):
            ang = 2 * math.pi * k / N_RAYOS
            px, py = R_ASTERISCO * math.cos(ang), R_ASTERISCO * math.sin(ang)
            ok1 = ir_a(px, py, "asterisco", WP_TOL)
            parar(WP_SETTLE)
            ok2 = ir_a(0.0, 0.0, "asterisco", WP_TOL)
            parar(WP_SETTLE)
            print(f"  rayo {k}: {'ok' if ok1 and ok2 else 'timeout'}")
        print()

    def espiral():
        if M_inv is None:
            return
        print(f"FASE: espiral - {R_ESP_INI} a {R_ESP_FIN} m, "
              f"{VUELTAS_ESP} vueltas")
        fallos = 0
        for i in range(1, PTS_ESPIRAL + 1):
            f = i / PTS_ESPIRAL
            ang = 2 * math.pi * VUELTAS_ESP * f
            rad = R_ESP_INI + (R_ESP_FIN - R_ESP_INI) * f
            if not ir_a(rad * math.cos(ang), rad * math.sin(ang),
                        "espiral", WP_TOL_ESP):
                fallos += 1
        parar(WP_SETTLE)
        ir_a(0.0, 0.0, "espiral", WP_TOL)
        parar(WP_SETTLE)
        print(f"  {PTS_ESPIRAL - fallos}/{PTS_ESPIRAL} puntos alcanzados\n")

    def ruido(duracion):
        print(f"FASE: ruido blanco - {duracion} s")
        gens = [RuidoFiltrado(NOISE_ALPHA, seed=s) for s in (11, 22, 33, 44)]
        t_ph = time.time()
        aviso = False
        n_geo = 0

        while time.time() - t_ph < duracion:
            px, py, yaw = pose_rel()
            fuera = px is not None and math.hypot(px, py) > R_MAX

            if fuera:
                if not aviso:
                    n_geo += 1
                    aviso = True
                bx, by = global_to_body(-px, -py, yaw)
                mag = math.hypot(bx, by) or 1.0
                w = mov_a_ruedas(bx / mag * 0.4, by / mag * 0.4, 0.0)
                if w is None:
                    w = [0, 0, 0, 0]
                mandar(w, "ruido", "geofence")
            else:
                aviso = False
                mandar([g.next() * RPM_STD for g in gens], "ruido", "ruido")

        parar(0.5)
        print(f"  geofence activado {n_geo} veces\n")

    print("\nVICON y robot conectados. La grabacion es interna,")
    print("no necesitas arrancar el Tracker por separado.")
    print("Deja ~3 m libres alrededor del robot.\n")
    time.sleep(2.0)

    try:
        for fase in FASES:
            if fase == "calibracion":
                calibrar()
            elif fase in ("claqueta_ini", "claqueta_fin"):
                claqueta(fase)
            elif fase == "asterisco":
                asterisco()
            elif fase == "espiral":
                espiral()
            elif fase == "ruido":
                ruido(RUIDO_TIME)

        parar(FINAL_HOLD)
        print("Rutina terminada.\n")

    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")

    finally:
        vicon_activo = False
        chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
        time.sleep(0.3)
        chassis.unsub_position()
        chassis.unsub_attitude()
        chassis.unsub_esc()
        ep_robot.close()

        if log:
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"robomaster_dataset_{stamp}.csv"

            con_vicon = sum(1 for r in log if r["x_vicon"] is not None)

            meta = {
                "fases": ",".join(FASES),
                "loop_dt": LOOP_DT, "sub_freq": SUB_FREQ,
                "vicon_host": VICON_HOST, "vicon_subject": VICON_SUBJECT,
                "vicon_freq": VICON_FREQ, "vicon_fallos": vicon_fallos,
                "cal_rpm": CAL_RPM, "cal_dur": CAL_DUR,
                "patrones": [list(p) for p in PATRONES],
                "cal_medido": cal_medido,
                "matriz_M": M, "matriz_M_inv": M_inv,
                "claq_rpm": CLAQ_RPM, "claq_dur": CLAQ_DUR,
                "r_asterisco_m": R_ASTERISCO, "n_rayos": N_RAYOS,
                "r_esp_ini_m": R_ESP_INI, "r_esp_fin_m": R_ESP_FIN,
                "vueltas_esp": VUELTAS_ESP, "pts_espiral": PTS_ESPIRAL,
                "ruido_time_s": RUIDO_TIME, "noise_alpha": NOISE_ALPHA,
                "rpm_std": RPM_STD, "rpm_limit": RPM_LIMIT,
                "rpm_min": RPM_MIN, "r_max_m": R_MAX,
                "kp_pos": KP_POS, "kp_yaw": KP_YAW, "y_sign": Y_SIGN,
                "origen_odom": [round(ORIG_X, 4), round(ORIG_Y, 4),
                                round(ORIG_YAW, 2)],
                "samples": len(log), "duration_s": log[-1]["t_s"],
                "samples_con_vicon": con_vicon,
            }

            with open(filename, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=log[0].keys())
                writer.writeheader()
                writer.writerows(log)

            with open(filename.replace(".csv", "_meta.json"), "w") as f:
                json.dump(meta, f, indent=2)

            print(f"Datos guardados en {filename} "
                  f"({len(log)} muestras, {log[-1]['t_s']:.1f} s)")
            print(f"Muestras con pose VICON: {con_vicon} "
                  f"({100.0 * con_vicon / len(log):.1f} %)")
            if vicon_fallos > 0:
                print(f"Fallos de lectura VICON: {vicon_fallos}")

            fases_cuenta = {}
            for r in log:
                fases_cuenta[r["fase"]] = fases_cuenta.get(r["fase"], 0) + 1
            print("\nMuestras por fase:")
            for nombre, cuenta in fases_cuenta.items():
                print(f"  {nombre:14s} {cuenta:6d}  ({cuenta * LOOP_DT:6.1f} s)")


if __name__ == '__main__':
    main()
