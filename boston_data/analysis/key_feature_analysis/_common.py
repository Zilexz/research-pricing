# -*- coding: utf-8 -*-
"""
Ham & cau hinh dung chung cho cac notebook phan tich key feature.

Dung trong notebook:
    import sys; sys.path.insert(0, ".")
    from _common import *
    setup(); df, dfL = load()
"""
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---- bang mau dung chung ----
BLUE, ORANGE, GREEN, RED, PURPLE, MUT = (
    "#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#666666")

DATA_NAME = "dataset_clean.parquet"


def setup():
    """Cau hinh pandas + matplotlib."""
    warnings.filterwarnings("ignore")
    pd.set_option("display.max_columns", 80)
    pd.set_option("display.width", 220)
    pd.set_option("display.max_rows", 120)
    plt.rcParams.update({
        "figure.facecolor": "white", "axes.facecolor": "white",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": "#ECECEC", "grid.linewidth": 0.8,
        "font.size": 10,
    })


def _find_data():
    here = Path(__file__).resolve().parent
    for base in [here.parent.parent / "data", here.parent / "data",
                 here / "data", Path("../../data"), Path("../data"), Path("data")]:
        p = base / DATA_NAME
        if p.exists():
            return p
    raise FileNotFoundError(
        f"Khong tim thay {DATA_NAME}. Hay chay analysis/00_clean_full_dataset.ipynb truoc.")


def load(verbose=True):
    """Nap du lieu sach. Tra ve (df, dfU, dfL).

    df  : ca 2 hang  -> chi dung khi CAN SO SANH 2 hang
    dfU : chi Uber   -> phan tich gia cua Uber
    dfL : chi Lyft   -> phan tich gia + SURGE cua Lyft

    LUU Y: 2 hang co cong thuc gia KHAC NHAU (don gia/dam khac,
    danh muc dich vu khong trung nhau) nen mac dinh phai tach rieng.
    """
    p = _find_data()
    df = pd.read_parquet(p)
    dfU = df[df.cab_type == "Uber"].copy()
    dfL = df[df.cab_type == "Lyft"].copy()
    if verbose:
        print(f"Nguon: {p}")
        print(f"  df  (ca 2 hang, chi de SO SANH): {len(df):,} chuyen x {df.shape[1]} cot")
        print(f"  dfU (Uber) : {len(dfU):,} chuyen | gia TB {dfU.price.mean():.2f} USD | "
              f"surge: KHONG CO (toan bo = 1.0)")
        print(f"  dfL (Lyft) : {len(dfL):,} chuyen | gia TB {dfL.price.mean():.2f} USD | "
              f"surge {dfL.is_surge.mean()*100:.2f}% ({int(dfL.is_surge.sum()):,} cuoc)")
    return df, dfU, dfL


# Mau rieng cho tung hang (dung nhat quan o moi bieu do)
MAU_HANG = {"Uber": "#0072B2", "Lyft": "#D55E00"}


def so_sanh_hang(df, cot_nhom, gia_tri="price", aggfunc="mean"):
    """Bang so sanh mot chi so giua Uber va Lyft theo tung nhom.

    Tra ve DataFrame co cot Uber, Lyft va chenh lech %.
    """
    pv = df.pivot_table(index=cot_nhom, columns="cab_type",
                        values=gia_tri, aggfunc=aggfunc)
    if {"Uber", "Lyft"}.issubset(pv.columns):
        pv["chenh_%"] = ((pv["Uber"] / pv["Lyft"] - 1) * 100).round(2)
    return pv.round(3)


def eta(groups, y):
    """Correlation ratio (0-1): % phuong sai cua y giai thich boi nhom."""
    g = groups.astype(str)
    ybar = y.mean()
    sst = ((y - ybar) ** 2).sum()
    if sst == 0:
        return 0.0
    ssb = sum(len(s) * (s.mean() - ybar) ** 2 for _, s in y.groupby(g))
    return float(np.sqrt(ssb / sst))


def binned(s, q=10):
    """Chia bin bien so de tinh eta -> so sanh cong bang voi bien phan loai."""
    if pd.api.types.is_numeric_dtype(s) and s.nunique() > q:
        return pd.qcut(s, q, duplicates="drop").astype(str)
    return s.astype(str)


def base_price_model(df):
    """Hoc gia co so tu cac chuyen KHONG surge, tra ve (mo_hinh, ham_du_doan).

    Dung de suy nguoc he so nhan ngam:  mult = price / base_pred
    """
    from sklearn.ensemble import HistGradientBoostingRegressor
    tr = df[df.surge_multiplier == 1.0]
    X = tr[["name", "distance"]].copy()
    X["name"] = X["name"].astype("category")
    m = HistGradientBoostingRegressor(
        max_iter=300, learning_rate=.06, categorical_features=["name"],
        random_state=42).fit(X, tr.price)

    def predict(d):
        Xa = d[["name", "distance"]].copy()
        Xa["name"] = Xa["name"].astype("category")
        return m.predict(Xa)

    return m, predict


def bar_rank(ax, labels, values, color=BLUE, fmt="{:.2f}", ref=None, ref_label=None):
    """Ve bar ngang da sap xep, co ghi so o dau thanh."""
    order = np.argsort(values)
    lab = np.asarray(labels)[order]
    val = np.asarray(values)[order]
    cols = color if isinstance(color, str) else [color[i] for i in order]
    ax.barh(range(len(val)), val, color=cols, alpha=.88, zorder=3)
    ax.set_yticks(range(len(val)))
    ax.set_yticklabels(lab, fontsize=8.5)
    span = (val.max() - min(val.min(), 0)) or 1
    for i, v in enumerate(val):
        ax.text(v + span * .01, i, fmt.format(v), va="center", fontsize=7.5)
    if ref is not None:
        ax.axvline(ref, color=ORANGE, ls="--", lw=1.5, label=ref_label)
        if ref_label:
            ax.legend(fontsize=7.5, frameon=False)
    ax.grid(axis="y", visible=False)
    return ax
