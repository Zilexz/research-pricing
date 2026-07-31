# -*- coding: utf-8 -*-
"""
Ham & cau hinh dung chung cho cac notebook phan tich key feature — bo TP.HCM.

Dung trong notebook:
    import sys; sys.path.insert(0, ".")
    from _common import *
    setup(); df = load()
"""
import glob, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---- bang mau dung chung ----
BLUE, ORANGE, GREEN, RED, PURPLE, MUT = (
    "#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#666666")

BASE = Path("../data/synthetic_data/synthetic_quote_context_sandbox_20260727_024458_utc")

# Ten cot target
PRICE = "target_shown_price"
SURGE = "target_shown_multiplier"


def setup():
    """Cau hinh pandas + matplotlib."""
    warnings.filterwarnings("ignore")
    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 80)
    plt.rcParams.update({
        "figure.facecolor": "white", "axes.facecolor": "white",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": "#ECECEC", "grid.linewidth": 0.8,
        "font.size": 10,
    })


def load(frac=0.15, seed=1, verbose=True):
    """Nap bang forecasting (mau frac). Them cac bien dan xuat.

    Don vi goc: quote_distance = KM, quote_duration = GIAY.

    Bien dan xuat:
      is_surge     : co surge khong (multiplier > 1)
      speed_kmh    : toc do trung binh (km/h)  -> thap = tac duong
      dur_per_km   : phut/km                    -> cao = tac duong
      price_k      : gia (nghin VND)
    """
    parts = sorted(glob.glob(str(BASE / "hexes/*/synthetic_intern_forecasting_v1_part*.csv.gz")))
    df = pd.concat([pd.read_csv(p).sample(frac=frac, random_state=seed) if frac < 1
                    else pd.read_csv(p) for p in parts], ignore_index=True)
    df["target_timestamp"] = pd.to_datetime(df.target_timestamp)
    df["is_surge"]    = (df[SURGE] > 1).astype(int)
    # distance = km, duration = giay
    df["speed_kmh"]   = df.quote_distance / (df.quote_duration.clip(lower=1) / 3600)
    df["dur_per_km"]  = (df.quote_duration / 60) / df.quote_distance.clip(lower=0.1)
    df["price_k"]     = df[PRICE] / 1000
    # target_hour/target_day_of_week la UTC -> them gio & thu Viet Nam (UTC+7)
    df["gio_vn"]      = (df.target_hour + 7) % 24
    df["thu_vn"]      = (df.target_day_of_week + (df.target_hour + 7) // 24) % 7
    if verbose:
        print(f"Nap {len(df):,} dong (mau {int(frac*100)}%) | "
              f"gia median {df.price_k.median():.0f}k VND | surge {df.is_surge.mean()*100:.1f}%")
    return df


def eta(groups, y):
    """Correlation ratio (0-1): % phuong sai cua y giai thich boi nhom."""
    g = np.asarray(groups).astype(str)
    y = np.asarray(y, dtype=float)
    ybar = y.mean()
    sst = ((y - ybar) ** 2).sum()
    if sst == 0:
        return 0.0
    ssb = sum(len(y[g == k]) * (y[g == k].mean() - ybar) ** 2 for k in np.unique(g))
    return float(np.sqrt(ssb / sst))


def binned(s, q=8):
    """Chia bin bien so de so sanh cong bang voi bien phan loai."""
    if pd.api.types.is_numeric_dtype(s) and s.nunique() > q:
        try:
            return pd.qcut(s, q, duplicates="drop").astype(str)
        except Exception:
            return s.astype(str)
    return s.astype(str)


def control_distance_corr(df, col, target=PRICE, q=10):
    """Tuong quan cua `col` voi target TRONG tung dai quang duong (da kiem soat)."""
    dbin = binned(df.quote_distance, q)
    return df.groupby(dbin).apply(lambda x: x[col].corr(x[target])).mean()
