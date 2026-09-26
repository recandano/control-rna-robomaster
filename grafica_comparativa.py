from pathlib import Path
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

CIRCULO_CSV = Path("trayectoria_punto_vicon.csv")
TRAYECTORIA_CSV = Path("trayectoria_circulo_vicon.csv")

# Parámetros de la prueba
XC = 0.15
YC = -0.20
RADIO = 0.40

def cargar_vicon(path):
    # Exportación VICON:
    # línea 1 Objects
    # línea 2 frecuencia
    # línea 3 descripción
    # línea 4 encabezados
    # línea 5 unidades
    df = pd.read_csv(
        path,
        skiprows=[0, 1, 2, 4],
        encoding="utf-8-sig"
    )

    for col in ["Frame", "RX", "RY", "RZ", "TX", "TY", "TZ"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Frame", "TX", "TY"]).reset_index(drop=True)

    # VICON está a 100 Hz.
    df["t_s"] = (df["Frame"] - df["Frame"].iloc[0]) / 100.0

    # VICON exporta TX/TY en mm; convertimos a metros.
    df["x_m"] = df["TX"] / 1000.0
    df["y_m"] = df["TY"] / 1000.0

    return df

circulo = cargar_vicon(CIRCULO_CSV)
trayectoria = cargar_vicon(TRAYECTORIA_CSV)

 
# 1. CÍRCULO: esperado vs obtenido
 
theta = np.linspace(0, 2 * np.pi, 500)

x_ref = XC + RADIO * np.sin(theta)
y_ref = YC + RADIO * np.cos(theta)

x_inicio = XC
y_inicio = YC + RADIO

plt.figure(figsize=(7, 7))
plt.plot(x_ref, y_ref, linewidth=2, label="Esperado")
plt.plot(
    circulo["x_m"],
    circulo["y_m"],
    linewidth=1.5,
    label="Obtenido (VICON)"
)
plt.scatter(
    [x_inicio],
    [y_inicio],
    s=70,
    marker="o",
    label="Inicio esperado"
)
plt.scatter(
    [XC],
    [YC],
    s=70,
    marker="x",
    label="Centro"
)

plt.xlabel("x [m]")
plt.ylabel("y [m]")
plt.title("Círculo: trayectoria esperada vs obtenida")
plt.axis("equal")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig("comparativa_circulo.png", dpi=180)
plt.show()

distancia_centro = np.sqrt(
    (circulo["x_m"] - XC)**2 +
    (circulo["y_m"] - YC)**2
)

error_radial = distancia_centro - RADIO

mae_circulo = np.mean(np.abs(error_radial))
rmse_circulo = np.sqrt(np.mean(error_radial**2))
max_circulo = np.max(np.abs(error_radial))

print("\nCIRCULO")
print("-------")
print(f"Error radial medio absoluto: {mae_circulo*100:.2f} cm")
print(f"RMSE radial: {rmse_circulo*100:.2f} cm")
print(f"Error radial máximo: {max_circulo*100:.2f} cm")

 
# 2. LLEGADA AL PUNTO INICIAL DEL CÍRCULO
 
x0 = trayectoria["x_m"].iloc[0]
y0 = trayectoria["y_m"].iloc[0]

# Para un círculo con centro (0.15, -0.20) y radio 0.40,
# la referencia en t=0 es (0.15, 0.20).
x_obj = XC
y_obj = YC + RADIO

x_recta = np.linspace(x0, x_obj, 200)
y_recta = np.linspace(y0, y_obj, 200)

plt.figure(figsize=(7, 6))
plt.plot(x_recta, y_recta, linewidth=2, label="Esperado")
plt.plot(
    trayectoria["x_m"],
    trayectoria["y_m"],
    linewidth=1.5,
    label="Obtenido (VICON)"
)
plt.scatter([x0], [y0], s=70, marker="o", label="Inicio")
plt.scatter([x_obj], [y_obj], s=90, marker="x", label="Objetivo")

plt.xlabel("x [m]")
plt.ylabel("y [m]")
plt.title("Llegada al inicio del círculo: esperado vs obtenido")
plt.axis("equal")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig("comparativa_trayectoria.png", dpi=180)
plt.show()

xf = trayectoria["x_m"].iloc[-1]
yf = trayectoria["y_m"].iloc[-1]

error_final = math.hypot(
    xf - x_obj,
    yf - y_obj
)

print("\nTRAYECTORIA AL PUNTO")
print("--------------------")
print(f"Inicio: ({x0:.3f}, {y0:.3f}) m")
print(f"Objetivo: ({x_obj:.3f}, {y_obj:.3f}) m")
print(f"Final VICON: ({xf:.3f}, {yf:.3f}) m")
print(f"Error final: {error_final*100:.2f} cm")
