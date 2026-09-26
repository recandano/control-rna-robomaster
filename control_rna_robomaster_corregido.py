from __future__ import annotations

import argparse
import json
import math
import random
import time
from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from scipy.signal import savgol_filter
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset


# Configuración
 

@dataclass
class Config:
    dt_control: float = 0.05
    rpm_limit: float = 120.0

    savgol_window: int = 7
    savgol_polyorder: int = 2

    max_vx_mps: float = 1.5
    max_vy_mps: float = 1.5
    max_omega_radps: float = 4.0

    train_fraction: float = 0.80
    val_fraction: float = 0.10
    max_response_lag_steps: int = 4

    hidden_direct: Tuple[int, ...] = (64, 64, 32)
    hidden_inverse: Tuple[int, ...] = (64, 64, 32)
    batch_size: int = 128
    epochs: int = 700
    patience: int = 70
    learning_rate: float = 1e-3
    weight_decay: float = 1e-5
    cycle_consistency_weight: float = 0.40

    kp_xy: float = 3.5
    ki_xy: float = 0.4
    kp_yaw: float = 2.0
    integral_xy_limit: float = 0.15
    feedforward_gain: float = 1.0
    lookahead_steps: int = 0
    max_v_body_mps: float = 0.80
    max_omega_cmd_radps: float = 1.80
    rpm_slew_per_step: float = 120.0

    simulation_duration_s: float = 12.0
    trajectory_yaw_mode: str = "hold"
    seed: int = 42
    exclude_inverse_labels: Tuple[str, ...] = ("geofence",)


REQUIRED_COLUMNS = [
    "t_s", "etiqueta",
    "w1_cmd", "w2_cmd", "w3_cmd", "w4_cmd",
    "w1_esc", "w2_esc", "w3_esc", "w4_esc",
    "x_vicon", "y_vicon", "yaw",
]


# Utilidades
 

def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def wrap_to_pi(angle):
    return np.arctan2(np.sin(angle), np.cos(angle))


def global_to_body(vx_g: float, vy_g: float, yaw: float) -> Tuple[float, float]:
    c, s = math.cos(yaw), math.sin(yaw)
    return c * vx_g + s * vy_g, -s * vx_g + c * vy_g


def body_to_global(vx_b: float, vy_b: float, yaw: float) -> Tuple[float, float]:
    c, s = math.cos(yaw), math.sin(yaw)
    return c * vx_b - s * vy_b, s * vx_b + c * vy_b


def clip_vector_norm(v: np.ndarray, max_norm: float) -> np.ndarray:
    norm = float(np.linalg.norm(v))
    if norm == 0.0 or norm <= max_norm:
        return v
    return v * (max_norm / norm)


def safe_savgol(values: np.ndarray, window: int, polyorder: int) -> np.ndarray:
    n = len(values)
    if n < 5:
        return values.copy()

    window = min(window, n if n % 2 else n - 1)
    window = max(window, polyorder + 2)
    if window % 2 == 0:
        window -= 1

    if window <= polyorder or window < 3:
        return values.copy()

    return savgol_filter(values, window_length=window, polyorder=polyorder, mode="interp")


# Fase 1 - Preprocesamiento
 

@dataclass
class TemporalSplit:
    train: np.ndarray
    val: np.ndarray
    test: np.ndarray
    split_id: np.ndarray


def make_temporal_split(n: int, guard: int, cfg: Config) -> TemporalSplit:
    if n < 100:
        raise ValueError("El dataset es demasiado pequeño.")

    i_train = int(cfg.train_fraction * n)
    i_val = int((cfg.train_fraction + cfg.val_fraction) * n)

    train = np.arange(0, max(0, i_train - guard))
    val = np.arange(min(n, i_train + guard), max(i_train + guard, i_val - guard))
    test = np.arange(min(n, i_val + guard), n)

    if min(len(train), len(val), len(test)) == 0:
        raise ValueError("Algún subconjunto quedó vacío.")

    split_id = np.full(n, -1, dtype=int)
    split_id[train] = 0
    split_id[val] = 1
    split_id[test] = 2
    return TemporalSplit(train, val, test, split_id)


def load_and_preprocess(csv_path: Path, cfg: Config) -> Tuple[pd.DataFrame, TemporalSplit, Dict]:
    df = pd.read_csv(csv_path)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")

    numeric_cols = [col for col in REQUIRED_COLUMNS if col != "etiqueta"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    original_rows = len(df)
    duplicate_times = int(df["t_s"].duplicated().sum())

    essential = [
        "t_s",
        "w1_cmd", "w2_cmd", "w3_cmd", "w4_cmd",
        "w1_esc", "w2_esc", "w3_esc", "w4_esc",
        "x_vicon", "y_vicon", "yaw",
    ]
    df = (
        df.dropna(subset=essential)
        .sort_values("t_s")
        .drop_duplicates(subset="t_s", keep="last")
        .reset_index(drop=True)
    )

    if len(df) < 100:
        raise ValueError("Quedaron menos de 100 muestras válidas.")

    t = df["t_s"].to_numpy(dtype=float)
    if np.any(np.diff(t) <= 0):
        raise ValueError("t_s no es estrictamente creciente.")

    x_raw = df["x_vicon"].to_numpy(dtype=float) / 1000.0
    y_raw = df["y_vicon"].to_numpy(dtype=float) / 1000.0
    yaw_raw = np.unwrap(wrap_to_pi(df["yaw"].to_numpy(dtype=float)))

    x_m = safe_savgol(x_raw, cfg.savgol_window, cfg.savgol_polyorder)
    y_m = safe_savgol(y_raw, cfg.savgol_window, cfg.savgol_polyorder)
    yaw_unwrapped = safe_savgol(yaw_raw, cfg.savgol_window, cfg.savgol_polyorder)

    vx_global = np.gradient(x_m, t, edge_order=2)
    vy_global = np.gradient(y_m, t, edge_order=2)
    omega = np.gradient(yaw_unwrapped, t, edge_order=2)

    c, s = np.cos(yaw_unwrapped), np.sin(yaw_unwrapped)
    vx_body = c * vx_global + s * vy_global
    vy_body = -s * vx_global + c * vy_global

    df["x_m"] = x_m
    df["y_m"] = y_m
    df["yaw_wrapped"] = wrap_to_pi(yaw_unwrapped)
    df["yaw_unwrapped"] = yaw_unwrapped
    df["vx_body"] = vx_body
    df["vy_body"] = vy_body
    df["w_body"] = omega
    df["dx_step_body"] = vx_body * cfg.dt_control
    df["dy_step_body"] = vy_body * cfg.dt_control
    df["dyaw_step"] = omega * cfg.dt_control

    finite = np.isfinite(df[["vx_body", "vy_body", "w_body"]].to_numpy()).all(axis=1)
    physical = (
        (np.abs(vx_body) <= cfg.max_vx_mps)
        & (np.abs(vy_body) <= cfg.max_vy_mps)
        & (np.abs(omega) <= cfg.max_omega_radps)
    )
    df["valid_dyn"] = finite & physical

    guard = cfg.savgol_window // 2
    split = make_temporal_split(len(df), guard, cfg)

    info = {
        "rows_original": int(original_rows),
        "rows_after_cleaning": int(len(df)),
        "duplicate_timestamps_removed": int(duplicate_times),
        "dt_mean_s": float(np.mean(np.diff(t))),
        "dt_median_s": float(np.median(np.diff(t))),
        "train_samples": int(len(split.train)),
        "val_samples": int(len(split.val)),
        "test_samples": int(len(split.test)),
        "valid_dynamic_samples": int(df["valid_dyn"].sum()),
    }
    return df, split, info


# Modelos
 

class MLP(nn.Module):
    def __init__(self, n_in: int, n_out: int, hidden: Sequence[int]) -> None:
        super().__init__()
        layers: List[nn.Module] = []
        prev = n_in
        for width in hidden:
            layers += [nn.Linear(prev, int(width)), nn.SiLU()]
            prev = int(width)
        layers.append(nn.Linear(prev, n_out))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


@dataclass
class ScalerParams:
    mean: np.ndarray
    scale: np.ndarray

    @classmethod
    def from_sklearn(cls, scaler: StandardScaler) -> "ScalerParams":
        return cls(
            np.asarray(scaler.mean_, dtype=np.float32),
            np.asarray(scaler.scale_, dtype=np.float32),
        )

    def transform(self, x: np.ndarray) -> np.ndarray:
        return (x - self.mean) / self.scale

    def inverse_transform(self, x: np.ndarray) -> np.ndarray:
        return x * self.scale + self.mean


class RegressionBundle:
    def __init__(
        self,
        model: MLP,
        x_scaler: ScalerParams,
        y_scaler: ScalerParams,
        input_names: Sequence[str],
        output_names: Sequence[str],
        hidden: Sequence[int],
        lag_steps: int = 0,
        metadata: Optional[Dict] = None,
    ) -> None:
        self.model = model.eval()
        self.x_scaler = x_scaler
        self.y_scaler = y_scaler
        self.input_names = list(input_names)
        self.output_names = list(output_names)
        self.hidden = tuple(hidden)
        self.lag_steps = int(lag_steps)
        self.metadata = metadata or {}

    def predict(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=np.float32)
        one_row = x.ndim == 1
        if one_row:
            x = x.reshape(1, -1)

        x_n = self.x_scaler.transform(x)
        with torch.no_grad():
            y_n = self.model(torch.tensor(x_n, dtype=torch.float32)).cpu().numpy()

        y = self.y_scaler.inverse_transform(y_n)
        return y[0] if one_row else y

    def save(self, path: Path) -> None:
        torch.save({
            "state_dict": self.model.state_dict(),
            "n_in": len(self.input_names),
            "n_out": len(self.output_names),
            "hidden": list(self.hidden),
            "x_mean": torch.tensor(self.x_scaler.mean),
            "x_scale": torch.tensor(self.x_scaler.scale),
            "y_mean": torch.tensor(self.y_scaler.mean),
            "y_scale": torch.tensor(self.y_scaler.scale),
            "input_names": self.input_names,
            "output_names": self.output_names,
            "lag_steps": self.lag_steps,
            "metadata": self.metadata,
        }, path)

    @classmethod
    def load(cls, path: Path) -> "RegressionBundle":
        try:
            payload = torch.load(path, map_location="cpu", weights_only=True)
        except TypeError:
            payload = torch.load(path, map_location="cpu")

        model = MLP(payload["n_in"], payload["n_out"], payload["hidden"])
        model.load_state_dict(payload["state_dict"])

        return cls(
            model=model,
            x_scaler=ScalerParams(payload["x_mean"].numpy(), payload["x_scale"].numpy()),
            y_scaler=ScalerParams(payload["y_mean"].numpy(), payload["y_scale"].numpy()),
            input_names=payload["input_names"],
            output_names=payload["output_names"],
            hidden=payload["hidden"],
            lag_steps=payload.get("lag_steps", 0),
            metadata=payload.get("metadata", {}),
        )


def metric_table(y_true: np.ndarray, y_pred: np.ndarray, names: Sequence[str]) -> Dict:
    out: Dict = {}
    for i, name in enumerate(names):
        mse = float(mean_squared_error(y_true[:, i], y_pred[:, i]))
        out[name] = {
            "MSE": mse,
            "RMSE": float(math.sqrt(mse)),
            "R2": float(r2_score(y_true[:, i], y_pred[:, i])),
        }

    mse = float(mean_squared_error(y_true, y_pred))
    out["overall"] = {
        "MSE": mse,
        "RMSE": float(math.sqrt(mse)),
        "R2_variance_weighted": float(
            r2_score(y_true, y_pred, multioutput="variance_weighted")
        ),
    }
    return out


def print_metrics(title: str, metrics: Dict) -> None:
    print(f"\n{title}\n" + "-" * len(title))
    for name, values in metrics.items():
        r2 = values.get("R2", values.get("R2_variance_weighted"))
        print(f"{name:>12s}: RMSE={values['RMSE']:.6f}  R2={r2:.4f}")


def plot_loss(train_loss: Sequence[float], val_loss: Sequence[float], title: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(train_loss, label="Train")
    ax.plot(val_loss, label="Val")
    ax.set(xlabel="Época", ylabel="MSE normalizado", title=title)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def train_regressor(
    x: np.ndarray,
    y: np.ndarray,
    train_idx: np.ndarray,
    val_idx: np.ndarray,
    input_names: Sequence[str],
    output_names: Sequence[str],
    hidden: Sequence[int],
    lag_steps: int,
    cfg: Config,
    metadata: Optional[Dict] = None,
) -> Tuple[RegressionBundle, List[float], List[float]]:
    sx = StandardScaler().fit(x[train_idx])
    sy = StandardScaler().fit(y[train_idx])

    x_n = sx.transform(x).astype(np.float32)
    y_n = sy.transform(y).astype(np.float32)

    model = MLP(x.shape[1], y.shape[1], hidden)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay
    )
    criterion = nn.MSELoss()

    loader = DataLoader(
        TensorDataset(
            torch.tensor(x_n[train_idx]),
            torch.tensor(y_n[train_idx]),
        ),
        batch_size=cfg.batch_size,
        shuffle=True,
    )

    x_val = torch.tensor(x_n[val_idx])
    y_val = torch.tensor(y_n[val_idx])

    best_val = float("inf")
    best_state = None
    patience = 0
    hist_train: List[float] = []
    hist_val: List[float] = []

    for _ in range(cfg.epochs):
        model.train()
        losses = []

        for xb, yb in loader:
            optimizer.zero_grad(set_to_none=True)
            loss = criterion(model(xb), yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()
            losses.append(float(loss.detach()))

        model.eval()
        with torch.no_grad():
            val_loss = float(criterion(model(x_val), y_val))

        train_loss = float(np.mean(losses))
        hist_train.append(train_loss)
        hist_val.append(val_loss)

        if val_loss < best_val - 1e-6:
            best_val = val_loss
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            patience = 0
        else:
            patience += 1

        if patience >= cfg.patience:
            break

    if best_state is None:
        raise RuntimeError("El entrenamiento no produjo un modelo válido.")

    model.load_state_dict(best_state)
    bundle = RegressionBundle(
        model,
        ScalerParams.from_sklearn(sx),
        ScalerParams.from_sklearn(sy),
        input_names,
        output_names,
        hidden,
        lag_steps,
        metadata,
    )
    return bundle, hist_train, hist_val


# Retardo y pares temporales
 

def estimate_response_lag(
    wheels: np.ndarray,
    body_velocity: np.ndarray,
    split: TemporalSplit,
    valid_dyn: np.ndarray,
    cfg: Config,
) -> Tuple[int, Dict[int, float]]:
    scores: Dict[int, float] = {}

    for lag in range(cfg.max_response_lag_steps + 1):
        n = len(wheels) - lag
        if n <= 10:
            continue

        x = wheels[:n]
        y = body_velocity[lag:lag + n]
        same_split = split.split_id[:n] == split.split_id[lag:lag + n]
        valid = (
            valid_dyn[lag:lag + n]
            & np.isfinite(x).all(axis=1)
            & np.isfinite(y).all(axis=1)
            & same_split
        )

        train = np.where(valid & (split.split_id[:n] == 0))[0]
        val = np.where(valid & (split.split_id[:n] == 1))[0]
        if len(train) < 50 or len(val) < 20:
            continue

        sx = StandardScaler().fit(x[train])
        sy = StandardScaler().fit(y[train])
        model = Ridge(alpha=1.0).fit(sx.transform(x[train]), sy.transform(y[train]))
        pred = sy.inverse_transform(model.predict(sx.transform(x[val])))

        scores[lag] = float(
            r2_score(y[val], pred, multioutput="variance_weighted")
        )

    if not scores:
        raise RuntimeError("No se pudo estimar el retardo comando-respuesta.")

    best = max(scores, key=scores.get)
    return int(best), scores


def make_lagged_pairs(
    x_source: np.ndarray,
    y_response: np.ndarray,
    lag: int,
    split: TemporalSplit,
    valid_response: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, np.ndarray], np.ndarray]:
    n = len(x_source) - lag
    if n <= 0:
        raise ValueError("El retardo es demasiado grande.")

    x = x_source[:n]
    y = y_response[lag:lag + n]
    same_split = split.split_id[:n] == split.split_id[lag:lag + n]

    valid = (
        valid_response[lag:lag + n]
        & np.isfinite(x).all(axis=1)
        & np.isfinite(y).all(axis=1)
        & same_split
    )

    ids = split.split_id[:n]
    idx = {
        "train": np.where(valid & (ids == 0))[0],
        "val": np.where(valid & (ids == 1))[0],
        "test": np.where(valid & (ids == 2))[0],
    }
    response_indices = np.arange(n) + lag
    return x, y, idx, response_indices


# Fase 2 - Modelos directos
 

def integrate_body_velocity(
    t: np.ndarray,
    initial_pose: Sequence[float],
    body_velocity: np.ndarray,
) -> np.ndarray:
    pose = np.zeros((len(body_velocity), 3), dtype=float)
    pose[0] = np.asarray(initial_pose, dtype=float)

    for k in range(len(body_velocity) - 1):
        dt = float(t[k + 1] - t[k])
        vx_b, vy_b, omega = body_velocity[k]
        vx_g, vy_g = body_to_global(vx_b, vy_b, pose[k, 2])
        pose[k + 1] = [
            pose[k, 0] + vx_g * dt,
            pose[k, 1] + vy_g * dt,
            pose[k, 2] + omega * dt,
        ]
    return pose


def plot_direct_trajectory(
    df: pd.DataFrame,
    target_indices: np.ndarray,
    predicted_velocity: np.ndarray,
    path: Path,
    title: str,
) -> None:
    if len(target_indices) < 2:
        return

    t = df.loc[target_indices, "t_s"].to_numpy(dtype=float)
    real = df.loc[target_indices, ["x_m", "y_m", "yaw_unwrapped"]].to_numpy(dtype=float)
    pred = integrate_body_velocity(t, real[0], predicted_velocity)

    fig, ax = plt.subplots(figsize=(6.5, 6))
    ax.plot(real[:, 0], real[:, 1], label="VICON")
    ax.plot(pred[:, 0], pred[:, 1], label="RNA integrada")
    ax.set(xlabel="x [m]", ylabel="y [m]", title=title)
    ax.axis("equal")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)


def train_direct_model(
    df: pd.DataFrame,
    split: TemporalSplit,
    wheel_source: str,
    lag_steps: int,
    cfg: Config,
    output_dir: Path,
) -> Tuple[RegressionBundle, Dict]:
    if wheel_source not in ("cmd", "esc"):
        raise ValueError("wheel_source debe ser 'cmd' o 'esc'.")

    wheel_cols = [f"w{i}_{wheel_source}" for i in range(1, 5)]
    output_cols = ["vx_body", "vy_body", "w_body"]

    x_source = df[wheel_cols].to_numpy(dtype=float)
    y_response = df[output_cols].to_numpy(dtype=float)
    valid_dyn = df["valid_dyn"].to_numpy(dtype=bool)

    x, y, idx, response_idx = make_lagged_pairs(
        x_source, y_response, lag_steps, split, valid_dyn
    )

    bundle, hist_train, hist_val = train_regressor(
        x, y,
        idx["train"], idx["val"],
        wheel_cols, output_cols,
        cfg.hidden_direct, lag_steps, cfg,
        metadata={"type": "direct", "wheel_source": wheel_source},
    )

    pred = bundle.predict(x[idx["test"]])
    metrics = metric_table(y[idx["test"]], pred, output_cols)

    bundle.save(output_dir / f"modelo_directo_{wheel_source}.pt")
    plot_loss(
        hist_train, hist_val,
        f"Entrenamiento red directa ({wheel_source})",
        output_dir / f"loss_directo_{wheel_source}.png",
    )
    plot_direct_trajectory(
        df,
        response_idx[idx["test"]],
        pred,
        output_dir / f"trayectoria_directa_{wheel_source}.png",
        f"VICON vs RNA integrada ({wheel_source})",
    )
    return bundle, metrics


# Fase 3 - Red inversa y controlador
 

def train_inverse_controller(
    df: pd.DataFrame,
    split: TemporalSplit,
    plant_cmd: RegressionBundle,
    lag: int,
    cfg: Config,
    output_dir: Path,
) -> Tuple[RegressionBundle, Dict]:
    command_cols = ["w1_cmd", "w2_cmd", "w3_cmd", "w4_cmd"]
    input_names = ["dx_step_body", "dy_step_body", "dyaw_step"]

    commands = df[command_cols].to_numpy(dtype=float)
    velocity = df[["vx_body", "vy_body", "w_body"]].to_numpy(dtype=float)
    valid_dyn = df["valid_dyn"].to_numpy(dtype=bool)

    n = len(df) - lag
    y_cmd = commands[:n]
    x_delta = velocity[lag:lag + n] * cfg.dt_control

    same_split = split.split_id[:n] == split.split_id[lag:lag + n]
    valid = (
        valid_dyn[lag:lag + n]
        & np.isfinite(y_cmd).all(axis=1)
        & np.isfinite(x_delta).all(axis=1)
        & same_split
    )

    if cfg.exclude_inverse_labels:
        labels = df["etiqueta"].astype(str).to_numpy()[:n]
        for label in cfg.exclude_inverse_labels:
            valid &= labels != label

    ids = split.split_id[:n]
    train_idx = np.where(valid & (ids == 0))[0]
    val_idx = np.where(valid & (ids == 1))[0]
    test_idx = np.where(valid & (ids == 2))[0]

    if min(len(train_idx), len(val_idx), len(test_idx)) < 20:
        raise RuntimeError("Muy pocas muestras para la red inversa.")

    sx = StandardScaler().fit(x_delta[train_idx])
    sy = StandardScaler().fit(y_cmd[train_idx])

    x_n = sx.transform(x_delta).astype(np.float32)
    y_n = sy.transform(y_cmd).astype(np.float32)

    inverse = MLP(3, 4, cfg.hidden_inverse)
    optimizer = torch.optim.AdamW(
        inverse.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay
    )
    criterion = nn.MSELoss()

    loader = DataLoader(
        TensorDataset(torch.tensor(x_n[train_idx]), torch.tensor(y_n[train_idx])),
        batch_size=cfg.batch_size,
        shuffle=True,
    )

    x_val = torch.tensor(x_n[val_idx])
    y_val = torch.tensor(y_n[val_idx])

    plant = plant_cmd.model.eval()
    for p in plant.parameters():
        p.requires_grad_(False)

    inv_x_mean = torch.tensor(sx.mean_, dtype=torch.float32)
    inv_x_scale = torch.tensor(sx.scale_, dtype=torch.float32)
    inv_y_mean = torch.tensor(sy.mean_, dtype=torch.float32)
    inv_y_scale = torch.tensor(sy.scale_, dtype=torch.float32)

    plant_x_mean = torch.tensor(plant_cmd.x_scaler.mean, dtype=torch.float32)
    plant_x_scale = torch.tensor(plant_cmd.x_scaler.scale, dtype=torch.float32)
    plant_y_mean = torch.tensor(plant_cmd.y_scaler.mean, dtype=torch.float32)
    plant_y_scale = torch.tensor(plant_cmd.y_scaler.scale, dtype=torch.float32)

    def loss_total(xb: torch.Tensor, yb: torch.Tensor) -> torch.Tensor:
        pred_cmd_n = inverse(xb)
        supervised = criterion(pred_cmd_n, yb)

        pred_cmd = pred_cmd_n * inv_y_scale + inv_y_mean
        pred_vel_n = plant((pred_cmd - plant_x_mean) / plant_x_scale)

        desired_delta = xb * inv_x_scale + inv_x_mean
        desired_vel = desired_delta / cfg.dt_control
        desired_vel_n = (desired_vel - plant_y_mean) / plant_y_scale

        consistency = criterion(pred_vel_n, desired_vel_n)
        return supervised + cfg.cycle_consistency_weight * consistency

    best_val = float("inf")
    best_state = None
    patience = 0
    hist_train: List[float] = []
    hist_val: List[float] = []

    for _ in range(cfg.epochs):
        inverse.train()
        losses = []

        for xb, yb in loader:
            optimizer.zero_grad(set_to_none=True)
            loss = loss_total(xb, yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(inverse.parameters(), 5.0)
            optimizer.step()
            losses.append(float(loss.detach()))

        inverse.eval()
        with torch.no_grad():
            val_loss = float(loss_total(x_val, y_val))

        hist_train.append(float(np.mean(losses)))
        hist_val.append(val_loss)

        if val_loss < best_val - 1e-6:
            best_val = val_loss
            best_state = {k: v.detach().clone() for k, v in inverse.state_dict().items()}
            patience = 0
        else:
            patience += 1

        if patience >= cfg.patience:
            break

    if best_state is None:
        raise RuntimeError("El entrenamiento inverso no produjo un modelo válido.")

    inverse.load_state_dict(best_state)
    bundle = RegressionBundle(
        inverse,
        ScalerParams.from_sklearn(sx),
        ScalerParams.from_sklearn(sy),
        input_names,
        command_cols,
        cfg.hidden_inverse,
        lag,
        {
            "type": "inverse_controller",
            "dt_control": cfg.dt_control,
            "rpm_limit": cfg.rpm_limit,
            "cycle_consistency_weight": cfg.cycle_consistency_weight,
        },
    )

    pred_cmd = bundle.predict(x_delta[test_idx])
    metrics = metric_table(y_cmd[test_idx], pred_cmd, command_cols)

    cycle_vel = plant_cmd.predict(pred_cmd)
    desired_vel = x_delta[test_idx] / cfg.dt_control
    metrics["forward_consistency"] = metric_table(
        desired_vel, cycle_vel, ["vx_body", "vy_body", "w_body"]
    )

    bundle.save(output_dir / "controlador_inverso.pt")
    plot_loss(
        hist_train, hist_val,
        "Entrenamiento controlador neuronal inverso",
        output_dir / "loss_controlador_inverso.png",
    )
    return bundle, metrics


class PositionController:
    def __init__(self, inverse: RegressionBundle, cfg: Config) -> None:
        self.inverse = inverse
        self.cfg = cfg
        self.previous_rpm = np.zeros(4, dtype=float)
        self.integral_error_global = np.zeros(2, dtype=float)

    def reset(self) -> None:
        self.previous_rpm[:] = 0.0
        self.integral_error_global[:] = 0.0

    def _rpm_from_velocity(
        self,
        vx_body: float,
        vy_body: float,
        omega: float,
    ) -> np.ndarray:
        vxy = clip_vector_norm(
            np.array([vx_body, vy_body], dtype=float),
            self.cfg.max_v_body_mps,
        )
        omega = float(np.clip(
            omega,
            -self.cfg.max_omega_cmd_radps,
            self.cfg.max_omega_cmd_radps,
        ))

        delta = np.array([
            vxy[0] * self.cfg.dt_control,
            vxy[1] * self.cfg.dt_control,
            omega * self.cfg.dt_control,
        ])
        rpm = np.clip(
            self.inverse.predict(delta),
            -self.cfg.rpm_limit,
            self.cfg.rpm_limit,
        )

        step = np.clip(
            rpm - self.previous_rpm,
            -self.cfg.rpm_slew_per_step,
            self.cfg.rpm_slew_per_step,
        )
        rpm = np.clip(
            self.previous_rpm + step,
            -self.cfg.rpm_limit,
            self.cfg.rpm_limit,
        )
        self.previous_rpm = rpm.copy()
        return rpm

    def controlador_trayectoria(
        self,
        pose_actual: Sequence[float],
        pose_deseada: Sequence[float],
        v_ff_global: Sequence[float] = (0.0, 0.0),
        omega_ff: float = 0.0,
    ) -> np.ndarray:
        pose_actual = np.asarray(pose_actual, dtype=float)
        pose_deseada = np.asarray(pose_deseada, dtype=float)

        error_g = pose_deseada[:2] - pose_actual[:2]
        e_yaw = float(wrap_to_pi(pose_deseada[2] - pose_actual[2]))

        self.integral_error_global += error_g * self.cfg.dt_control
        self.integral_error_global = np.clip(
            self.integral_error_global,
            -self.cfg.integral_xy_limit,
            self.cfg.integral_xy_limit,
        )

        ex_b, ey_b = global_to_body(error_g[0], error_g[1], pose_actual[2])
        ei_x_b, ei_y_b = global_to_body(
            self.integral_error_global[0],
            self.integral_error_global[1],
            pose_actual[2],
        )
        vx_ff_b, vy_ff_b = global_to_body(
            float(v_ff_global[0]),
            float(v_ff_global[1]),
            pose_actual[2],
        )

        vx_des = (
            self.cfg.feedforward_gain * vx_ff_b
            + self.cfg.kp_xy * ex_b
            + self.cfg.ki_xy * ei_x_b
        )
        vy_des = (
            self.cfg.feedforward_gain * vy_ff_b
            + self.cfg.kp_xy * ey_b
            + self.cfg.ki_xy * ei_y_b
        )
        omega_des = float(omega_ff) + self.cfg.kp_yaw * e_yaw

        return self._rpm_from_velocity(vx_des, vy_des, omega_des)

    def controlador_posicion(
        self,
        pose_actual: Sequence[float],
        pose_deseada: Sequence[float],
    ) -> np.ndarray:
        return self.controlador_trayectoria(
            pose_actual,
            pose_deseada,
            v_ff_global=(0.0, 0.0),
            omega_ff=0.0,
        )


# Fase 4 - Trayectoria y simulación
 

def trajectory_reference(
    t: float,
    yaw_mode: str,
    yaw_hold: float,
) -> Tuple[np.ndarray, np.ndarray, float]:
    xc, yc = 0.15, -0.20
    radius = 0.40
    omega_tray = 1.30

    x = xc + radius * math.sin(omega_tray * t)
    y = yc + radius * math.cos(omega_tray * t)

    vx = radius * omega_tray * math.cos(omega_tray * t)
    vy = -radius * omega_tray * math.sin(omega_tray * t)

    if yaw_mode == "hold":
        yaw, omega = yaw_hold, 0.0
    elif yaw_mode == "tangent":
        yaw = math.atan2(vy, vx)
        omega = -omega_tray
    else:
        raise ValueError("trajectory_yaw_mode debe ser 'hold' o 'tangent'.")

    return np.array([x, y, yaw]), np.array([vx, vy]), float(omega)


def simulate_closed_loop(
    plant: RegressionBundle,
    inverse: RegressionBundle,
    cfg: Config,
    output_dir: Path,
) -> Dict:
    controller = PositionController(inverse, cfg)
    dt = cfg.dt_control
    t = np.arange(0.0, cfg.simulation_duration_s + 0.5 * dt, dt)

    pose = np.zeros((len(t), 3))
    desired = np.zeros((len(t), 3))
    commands = np.zeros((len(t) - 1, 4))

    p0, _, _ = trajectory_reference(0.0, cfg.trajectory_yaw_mode, 0.0)
    pose[0] = p0
    yaw_hold = float(p0[2])

    lag = int(plant.lag_steps)
    delay = deque([np.zeros(4) for _ in range(lag)])

    for k in range(len(t) - 1):
        t_ctrl = t[k] + cfg.lookahead_steps * dt
        ref, v_ff, omega_ff = trajectory_reference(
            t_ctrl, cfg.trajectory_yaw_mode, yaw_hold
        )
        rpm = controller.controlador_trayectoria(pose[k], ref, v_ff, omega_ff)
        commands[k] = rpm

        if lag:
            delay.append(rpm.copy())
            effective_rpm = delay.popleft()
        else:
            effective_rpm = rpm

        vx_b, vy_b, omega = plant.predict(effective_rpm)
        vx_g, vy_g = body_to_global(vx_b, vy_b, pose[k, 2])

        pose[k + 1] = [
            pose[k, 0] + vx_g * dt,
            pose[k, 1] + vy_g * dt,
            pose[k, 2] + omega * dt,
        ]

    for k, tk in enumerate(t):
        desired[k], _, _ = trajectory_reference(
            float(tk), cfg.trajectory_yaw_mode, yaw_hold
        )

    ex = desired[:, 0] - pose[:, 0]
    ey = desired[:, 1] - pose[:, 1]
    e_pos = np.hypot(ex, ey)
    e_yaw = wrap_to_pi(desired[:, 2] - pose[:, 2])

    result = pd.DataFrame({
        "t_s": t,
        "x_des": desired[:, 0],
        "y_des": desired[:, 1],
        "yaw_des": desired[:, 2],
        "x_sim": pose[:, 0],
        "y_sim": pose[:, 1],
        "yaw_sim": pose[:, 2],
        "e_pos_m": e_pos,
        "e_yaw_rad": e_yaw,
    })
    for i in range(4):
        values = np.full(len(t), np.nan)
        values[:-1] = commands[:, i]
        result[f"w{i + 1}_cmd"] = values
    result.to_csv(output_dir / "simulacion_seguimiento.csv", index=False)

    fig, ax = plt.subplots(figsize=(6.6, 6))
    ax.plot(desired[:, 0], desired[:, 1], label="Deseada")
    ax.plot(pose[:, 0], pose[:, 1], label="Seguida por RNA")
    ax.set(xlabel="x [m]", ylabel="y [m]", title="Seguimiento de trayectoria")
    ax.axis("equal")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "fase4_trayectoria.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.plot(t, e_pos, label="Error posición [m]")
    ax.plot(t, np.abs(e_yaw), label="|Error yaw| [rad]")
    ax.set(xlabel="Tiempo [s]", ylabel="Error", title="Evolución del error")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "fase4_error.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    for i in range(4):
        ax.plot(t[:-1], commands[:, i], label=f"w{i + 1}")
    ax.axhline(cfg.rpm_limit, linestyle="--", linewidth=1)
    ax.axhline(-cfg.rpm_limit, linestyle="--", linewidth=1)
    ax.set(xlabel="Tiempo [s]", ylabel="RPM", title="Comandos de control")
    ax.grid(True, alpha=0.3)
    ax.legend(ncol=4)
    fig.tight_layout()
    fig.savefig(output_dir / "fase4_comandos.png", dpi=180)
    plt.close(fig)

    return {
        "position_rmse_m": float(np.sqrt(np.mean(e_pos ** 2))),
        "position_mae_m": float(np.mean(e_pos)),
        "position_max_error_m": float(np.max(e_pos)),
        "yaw_rmse_rad": float(np.sqrt(np.mean(e_yaw ** 2))),
        "max_abs_rpm": float(np.max(np.abs(commands))),
        "plant_delay_steps": lag,
        "plant_delay_s": lag * dt,
    }


def simulate_point_control(
    plant: RegressionBundle,
    inverse: RegressionBundle,
    cfg: Config,
    output_dir: Path,
    target_pose: Sequence[float],
    initial_pose: Sequence[float],
    pos_tol_m: float,
    yaw_tol_rad: float,
    settle_cycles: int = 10,
) -> Dict:
    controller = PositionController(inverse, cfg)
    dt = cfg.dt_control
    n_steps = int(round(cfg.simulation_duration_s / dt)) + 1
    t = np.arange(n_steps) * dt

    target = np.asarray(target_pose, dtype=float)
    pose = np.zeros((n_steps, 3))
    pose[0] = np.asarray(initial_pose, dtype=float)
    commands = np.zeros((n_steps - 1, 4))

    lag = int(plant.lag_steps)
    delay = deque([np.zeros(4) for _ in range(lag)])

    reached = None
    inside = 0

    for k in range(n_steps - 1):
        e_pos = float(np.linalg.norm(target[:2] - pose[k, :2]))
        e_yaw = abs(float(wrap_to_pi(target[2] - pose[k, 2])))

        inside = inside + 1 if e_pos <= pos_tol_m and e_yaw <= yaw_tol_rad else 0
        if inside >= settle_cycles:
            reached = k
            pose[k + 1:] = pose[k]
            break

        rpm = controller.controlador_posicion(pose[k], target)
        commands[k] = rpm

        if lag:
            delay.append(rpm.copy())
            effective_rpm = delay.popleft()
        else:
            effective_rpm = rpm

        vx_b, vy_b, omega = plant.predict(effective_rpm)
        vx_g, vy_g = body_to_global(vx_b, vy_b, pose[k, 2])
        pose[k + 1] = [
            pose[k, 0] + vx_g * dt,
            pose[k, 1] + vy_g * dt,
            pose[k, 2] + omega * dt,
        ]

    e_pos = np.hypot(target[0] - pose[:, 0], target[1] - pose[:, 1])
    e_yaw = wrap_to_pi(target[2] - pose[:, 2])
    final_idx = reached if reached is not None else n_steps - 1

    result = pd.DataFrame({
        "t_s": t,
        "x_obj": target[0],
        "y_obj": target[1],
        "yaw_obj": target[2],
        "x_sim": pose[:, 0],
        "y_sim": pose[:, 1],
        "yaw_sim": pose[:, 2],
        "e_pos_m": e_pos,
        "e_yaw_rad": e_yaw,
    })
    for i in range(4):
        values = np.full(n_steps, np.nan)
        values[:-1] = commands[:, i]
        result[f"w{i + 1}_cmd"] = values
    result.to_csv(output_dir / "simulacion_punto.csv", index=False)

    fig, ax = plt.subplots(figsize=(6.6, 6))
    ax.plot(pose[:, 0], pose[:, 1], label="Trayectoria")
    ax.scatter([pose[0, 0]], [pose[0, 1]], label="Inicio")
    ax.scatter([target[0]], [target[1]], marker="x", s=100, label="Objetivo")
    ax.set(xlabel="x [m]", ylabel="y [m]", title="Control de posición")
    ax.axis("equal")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "fase3_punto_trayectoria.png", dpi=180)
    plt.close(fig)

    metrics = {
        "reached": reached is not None,
        "time_to_target_s": None if reached is None else float(t[reached]),
        "final_position_error_m": float(e_pos[final_idx]),
        "final_yaw_error_deg": float(math.degrees(abs(e_yaw[final_idx]))),
        "max_abs_rpm": float(np.max(np.abs(commands))),
    }
    with open(output_dir / "metricas_simulacion_punto.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    return metrics


# Ejecución física
 

class ViconPoseProvider:
    def __init__(self, host: str, subject: str, segment: str) -> None:
        try:
            from vicon_dssdk import ViconDataStream as vds
        except ImportError as exc:
            raise RuntimeError("No está disponible vicon_dssdk.") from exc

        self.client = vds.Client()
        self.client.Connect(host)
        self.client.EnableSegmentData()
        self.subject = subject
        self.segment = segment

    def read_pose(self) -> np.ndarray:
        for _ in range(50):
            self.client.GetFrame()

            xyz_result = self.client.GetSegmentGlobalTranslation(
                self.subject, self.segment
            )
            rpy_result = self.client.GetSegmentGlobalRotationEulerXYZ(
                self.subject, self.segment
            )

            xyz, xyz_occluded = xyz_result[0], bool(xyz_result[1])
            rpy, rpy_occluded = rpy_result[0], bool(rpy_result[1])

            if not xyz_occluded and not rpy_occluded:
                pose = np.array([
                    float(xyz[0]) / 1000.0,
                    float(xyz[1]) / 1000.0,
                    float(rpy[2]),
                ])
                if np.isfinite(pose).all():
                    return pose

            time.sleep(0.01)

        raise RuntimeError("VICON no entregó una pose válida después de 50 frames.")

    def close(self) -> None:
        try:
            self.client.Disconnect()
        except Exception:
            pass


def connect_robomaster(local_ip: Optional[str]):
    try:
        import robomaster
        from robomaster import robot
    except ImportError as exc:
        raise RuntimeError("No está instalado el SDK oficial de DJI RoboMaster.") from exc

    if local_ip:
        robomaster.config.LOCAL_IP_STR = local_ip

    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap", proto_type="udp")
    return ep_robot, ep_robot.chassis


def send_rpm(chassis, rpm: np.ndarray, swap_w3_w4: bool) -> None:
    rpm_sdk = np.asarray(rpm, dtype=float).copy()
    if swap_w3_w4:
        rpm_sdk[[2, 3]] = rpm_sdk[[3, 2]]

    chassis.drive_wheels(
        w1=int(round(rpm_sdk[0])),
        w2=int(round(rpm_sdk[1])),
        w3=int(round(rpm_sdk[2])),
        w4=int(round(rpm_sdk[3])),
        timeout=0.15,
    )


def stop_robot(chassis) -> None:
    try:
        chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0, timeout=0.15)
    except Exception:
        pass


def run_live_point(
    inverse: RegressionBundle,
    cfg: Config,
    local_ip: Optional[str],
    vicon_host: str,
    vicon_subject: str,
    vicon_segment: str,
    target_x: float,
    target_y: float,
    target_yaw_rad: Optional[float],
    duration_s: float,
    pos_tol_m: float,
    yaw_tol_rad: float,
    swap_w3_w4: bool,
    settle_cycles: int = 10,
) -> None:
    pose_provider = ViconPoseProvider(vicon_host, vicon_subject, vicon_segment)
    ep_robot, chassis = connect_robomaster(local_ip)
    controller = PositionController(inverse, cfg)

    initial_pose = pose_provider.read_pose()
    if target_yaw_rad is None:
        target_yaw_rad = float(initial_pose[2])

    target = np.array([target_x, target_y, target_yaw_rad], dtype=float)
    print(
        f"\nObjetivo: x={target_x:.3f} m, y={target_y:.3f} m, "
        f"yaw={math.degrees(target_yaw_rad):.1f}°"
    )

    t0 = time.perf_counter()
    next_tick = t0
    inside = 0

    try:
        while time.perf_counter() - t0 < duration_s:
            pose = pose_provider.read_pose()
            e_pos = float(np.linalg.norm(target[:2] - pose[:2]))
            e_yaw = abs(float(wrap_to_pi(target[2] - pose[2])))

            inside = inside + 1 if e_pos <= pos_tol_m and e_yaw <= yaw_tol_rad else 0
            if inside >= settle_cycles:
                print(f"Objetivo alcanzado. Error final: {e_pos * 100:.2f} cm")
                break

            rpm = controller.controlador_posicion(pose, target)
            send_rpm(chassis, rpm, swap_w3_w4)

            next_tick += cfg.dt_control
            sleep = next_tick - time.perf_counter()
            if sleep > 0:
                time.sleep(sleep)
            else:
                next_tick = time.perf_counter()

    except KeyboardInterrupt:
        print("\nInterrupción del usuario.")
    finally:
        stop_robot(chassis)
        pose_provider.close()
        ep_robot.close()


def run_live_trajectory(
    inverse: RegressionBundle,
    cfg: Config,
    local_ip: Optional[str],
    vicon_host: str,
    vicon_subject: str,
    vicon_segment: str,
    duration_s: float,
    swap_w3_w4: bool,
) -> None:
    pose_provider = ViconPoseProvider(vicon_host, vicon_subject, vicon_segment)
    ep_robot, chassis = connect_robomaster(local_ip)
    controller = PositionController(inverse, cfg)

    initial_pose = pose_provider.read_pose()
    yaw_hold = float(initial_pose[2])

    t0 = time.perf_counter()
    next_tick = t0

    try:
        while True:
            elapsed = time.perf_counter() - t0
            if elapsed >= duration_s:
                break

            pose = pose_provider.read_pose()
            t_ctrl = elapsed + cfg.lookahead_steps * cfg.dt_control
            ref, v_ff, omega_ff = trajectory_reference(
                t_ctrl, cfg.trajectory_yaw_mode, yaw_hold
            )

            rpm = controller.controlador_trayectoria(
                pose, ref, v_ff, omega_ff
            )
            send_rpm(chassis, rpm, swap_w3_w4)

            next_tick += cfg.dt_control
            sleep = next_tick - time.perf_counter()
            if sleep > 0:
                time.sleep(sleep)
            else:
                next_tick = time.perf_counter()

    except KeyboardInterrupt:
        print("\nInterrupción del usuario.")
    finally:
        stop_robot(chassis)
        pose_provider.close()
        ep_robot.close()


# Entrenamiento completo
 

def train_all(csv_path: Path, output_dir: Path, cfg: Config) -> Dict:
    set_seed(cfg.seed)
    output_dir.mkdir(parents=True, exist_ok=True)

    df, split, data_info = load_and_preprocess(csv_path, cfg)
    df.to_csv(output_dir / "dataset_preprocesado.csv", index=False)

    body_velocity = df[["vx_body", "vy_body", "w_body"]].to_numpy(dtype=float)
    valid_dyn = df["valid_dyn"].to_numpy(dtype=bool)

    cmd = df[["w1_cmd", "w2_cmd", "w3_cmd", "w4_cmd"]].to_numpy(dtype=float)
    esc = df[["w1_esc", "w2_esc", "w3_esc", "w4_esc"]].to_numpy(dtype=float)

    cmd_lag, cmd_scores = estimate_response_lag(
        cmd, body_velocity, split, valid_dyn, cfg
    )
    esc_lag, esc_scores = estimate_response_lag(
        esc, body_velocity, split, valid_dyn, cfg
    )

    _, metrics_esc = train_direct_model(
        df, split, "esc", esc_lag, cfg, output_dir
    )
    plant_cmd, metrics_cmd = train_direct_model(
        df, split, "cmd", cmd_lag, cfg, output_dir
    )
    inverse, metrics_inverse = train_inverse_controller(
        df, split, plant_cmd, cmd_lag, cfg, output_dir
    )

    print_metrics("Directo ESC", metrics_esc)
    print_metrics("Planta CMD", metrics_cmd)
    print_metrics(
        "Controlador inverso",
        {k: v for k, v in metrics_inverse.items() if k != "forward_consistency"},
    )
    print_metrics(
        "Consistencia inversa + planta",
        metrics_inverse["forward_consistency"],
    )

    simulation = simulate_closed_loop(
        plant_cmd, inverse, cfg, output_dir
    )

    summary = {
        "config": asdict(cfg),
        "dataset": data_info,
        "lag_command_response": {
            "selected_steps": cmd_lag,
            "selected_seconds": cmd_lag * cfg.dt_control,
            "validation_scores": cmd_scores,
        },
        "lag_esc_response": {
            "selected_steps": esc_lag,
            "selected_seconds": esc_lag * cfg.dt_control,
            "validation_scores": esc_scores,
        },
        "phase2_direct_esc": metrics_esc,
        "phase2_plant_cmd": metrics_cmd,
        "phase3_inverse": metrics_inverse,
        "phase4_simulation": simulation,
    }

    with open(output_dir / "metricas_resumen.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\nResultados guardados en: {output_dir.resolve()}")
    return summary


# Línea de comandos
 

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Control por RNA - RoboMaster S1 + VICON"
    )
    parser.add_argument(
        "--mode",
        choices=["train", "simulate", "simulate-point", "point", "live"],
        default="train",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("robomaster_dataset_20260924_140657.csv"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("salida_control_rna"),
    )

    parser.add_argument("--local-ip", type=str, default=None)
    parser.add_argument("--vicon-host", default="192.168.10.1:801")
    parser.add_argument("--vicon-subject", default="Zacarias")
    parser.add_argument("--vicon-segment", default="Zacarias")
    parser.add_argument("--duration", type=float, default=12.0)

    parser.add_argument("--start-x", type=float, default=0.0)
    parser.add_argument("--start-y", type=float, default=0.0)
    parser.add_argument("--start-yaw-deg", type=float, default=0.0)

    parser.add_argument("--target-x", type=float)
    parser.add_argument("--target-y", type=float)
    parser.add_argument("--target-yaw-deg", type=float)

    parser.add_argument("--pos-tol-cm", type=float, default=3.0)
    parser.add_argument("--yaw-tol-deg", type=float, default=5.0)
    parser.add_argument("--sdk-swap-w3-w4", action="store_true")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = Config(simulation_duration_s=args.duration)
    set_seed(cfg.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.mode == "train":
        if not args.csv.is_file():
            raise FileNotFoundError(f"No se encontró el CSV: {args.csv.resolve()}")
        train_all(args.csv, args.output_dir, cfg)
        return

    inverse_path = args.output_dir / "controlador_inverso.pt"
    if not inverse_path.is_file():
        raise FileNotFoundError("Ejecuta primero --mode train.")

    inverse = RegressionBundle.load(inverse_path)

    if args.mode in ("simulate", "simulate-point"):
        plant_path = args.output_dir / "modelo_directo_cmd.pt"
        if not plant_path.is_file():
            raise FileNotFoundError("No existe modelo_directo_cmd.pt.")
        plant = RegressionBundle.load(plant_path)

        if args.mode == "simulate":
            metrics = simulate_closed_loop(plant, inverse, cfg, args.output_dir)
        else:
            if args.target_x is None or args.target_y is None:
                raise ValueError("Indica --target-x y --target-y.")

            initial = np.array([
                args.start_x,
                args.start_y,
                math.radians(args.start_yaw_deg),
            ])
            target_yaw = (
                math.radians(args.target_yaw_deg)
                if args.target_yaw_deg is not None
                else initial[2]
            )
            target = np.array([args.target_x, args.target_y, target_yaw])

            metrics = simulate_point_control(
                plant, inverse, cfg, args.output_dir,
                target, initial,
                args.pos_tol_cm / 100.0,
                math.radians(args.yaw_tol_deg),
            )

        print(json.dumps(metrics, indent=2, ensure_ascii=False))
        return

    if args.mode == "point":
        if args.target_x is None or args.target_y is None:
            raise ValueError("Indica --target-x y --target-y.")

        target_yaw = (
            math.radians(args.target_yaw_deg)
            if args.target_yaw_deg is not None
            else None
        )
        run_live_point(
            inverse, cfg,
            args.local_ip,
            args.vicon_host,
            args.vicon_subject,
            args.vicon_segment,
            args.target_x,
            args.target_y,
            target_yaw,
            args.duration,
            args.pos_tol_cm / 100.0,
            math.radians(args.yaw_tol_deg),
            args.sdk_swap_w3_w4,
        )
        return

    run_live_trajectory(
        inverse, cfg,
        args.local_ip,
        args.vicon_host,
        args.vicon_subject,
        args.vicon_segment,
        args.duration,
        args.sdk_swap_w3_w4,
    )


if __name__ == "__main__":
    main()
