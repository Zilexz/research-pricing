# -*- coding: utf-8 -*-
"""
XU LY DU LIEU TRUOC KHI TRAIN (Buoc 2+3 cua pipeline)
=====================================================
Input :  data/dataset_clean.parquet        (637.322 chuyen da lam sach)
Output:  data/snapshot_price_{15,60}min.parquet
         data/snapshot_surge_{15,60}min.parquet

Lam 3 viec:
  1. GOP SNAPSHOT theo 2 do phan giai khac nhau cho 2 target
       price : series = source x destination x name  (cap cuoc, tach tung hang)
       surge : series = source x destination         (cap thi truong, chi Lyft, bo Shared)
  2. FEATURE ENGINEERING chi tu QUA KHU (chong ro ri)
       lag1/2/3, roll_mean3/6, roll_std3, delta_1_2, observation_age_minutes
  3. GAN DATA_SPLIT theo THOI GIAN (khong bao gio chia ngau nhien)
       train <= 10/12  |  calibration 13-15/12  |  test >= 16/12

Chay:  python model/data_preparation.py
Sau do:  mo model/model_train.ipynb de huan luyen
"""
from pathlib import Path
import sys, time
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
IN   = DATA / "dataset_clean.parquet"

# --- Chia theo THOI GIAN (khong bao gio chia ngau nhien) ---
TRAIN_END   = "2018-12-10"
CALIB_START, CALIB_END = "2018-12-13", "2018-12-15"
TEST_START             = "2018-12-16"

# Thoi tiet giu lai (bo cac cot proxy ngay: moonPhase, pressure, ozone)
WEATHER = ["temperature", "precipIntensity", "precipProbability",
           "humidity", "windSpeed", "visibility", "cloudCover"]


def gan_split(ngay: pd.Series) -> pd.Series:
    s = pd.Series("drop", index=ngay.index, dtype=object)
    s[ngay <= TRAIN_END] = "train"
    s[(ngay >= CALIB_START) & (ngay <= CALIB_END)] = "calibration"
    s[ngay >= TEST_START] = "test"
    return s


def them_thoi_gian(g: pd.DataFrame) -> pd.DataFrame:
    """Cot thoi gian suy tu moc snapshot."""
    t = g["snapshot"]
    g["hour_local"]    = t.dt.hour
    g["weekday_local"] = t.dt.weekday
    g["is_weekend"]    = (t.dt.weekday >= 5).astype(int)
    g["hour_sin"]      = np.sin(2 * np.pi * g.hour_local / 24)
    g["hour_cos"]      = np.cos(2 * np.pi * g.hour_local / 24)
    return g


def them_lag(g: pd.DataFrame, keys: list, cot_dich: str, tien_to: str) -> pd.DataFrame:
    """Lag + rolling + do tre quan sat. CHI dung qua khu -> khong ro ri."""
    g = g.sort_values(keys + ["snapshot"]).reset_index(drop=True)
    gr = g.groupby(keys, observed=True)

    for k in (1, 2, 3):
        g[f"lag{k}_{tien_to}"] = gr[cot_dich].shift(k)
    g[f"delta_{tien_to}_1_2"] = g[f"lag1_{tien_to}"] - g[f"lag2_{tien_to}"]

    truoc = gr[cot_dich].shift(1)
    idx = [g[k] for k in keys]
    for w in (3, 6):
        g[f"roll_mean{w}_{tien_to}"] = (truoc.groupby(idx)
                                        .rolling(w, min_periods=1).mean()
                                        .reset_index(drop=True))
    g[f"roll_std3_{tien_to}"] = (truoc.groupby(idx)
                                 .rolling(3, min_periods=2).std()
                                 .reset_index(drop=True))

    g["lag1_quote_count"] = gr["quote_count"].shift(1)
    g["so_quan_sat_truoc"] = gr.cumcount()

    # Do tre: snapshot nay cach snapshot truoc bao nhieu phut (= observation age)
    truoc_t = gr["snapshot"].shift(1)
    g["observation_age_minutes"] = (g["snapshot"] - truoc_t).dt.total_seconds() / 60
    # Bucket min hon de phuc vu phan tich suy giam theo do tre tau
    g["observation_age_bucket"] = pd.cut(
        g["observation_age_minutes"], [-1, 15, 30, 60, 180, 1e9],
        labels=["<=15p", "15-30p", "30-60p", "1-3h", ">3h"]).astype(str)
    return g


def dung_bang_price(df: pd.DataFrame) -> pd.DataFrame:
    """series = source x destination x name, tach rieng tung hang."""
    keys = ["cab_type", "source", "destination", "name"]
    agg = {"price": [("target_price", "median"),
                     ("price_min", "min"), ("price_max", "max")],
           "distance": [("distance_median", "median")],
           "id": [("quote_count", "size")]}
    gb = df.groupby(keys + ["snapshot"], observed=True)
    parts = [gb[c].agg(how).rename(name) for c, specs in agg.items() for name, how in specs]
    parts += [gb[w].median().rename(w) for w in WEATHER if w in df.columns]
    parts.append(gb["short_summary"].agg(
        lambda s: s.mode().iat[0] if len(s.mode()) else "NA").rename("short_summary"))
    g = pd.concat(parts, axis=1).reset_index()
    g["price_spread"] = g.price_max - g.price_min
    g = them_thoi_gian(g)
    g = them_lag(g, keys, "target_price", "price")
    return g


def dung_bang_surge(df: pd.DataFrame) -> pd.DataFrame:
    """series = source x destination (CAP THI TRUONG). Chi Lyft, bo Shared."""
    d = df[(df.cab_type == "Lyft") & (df.name != "Shared")]
    keys = ["source", "destination"]
    gb = d.groupby(keys + ["snapshot"], observed=True)
    # DUNG MEAN, khong dung median: trong 1 gio neu 3/11 bao gia co surge thi
    # median van = 1.0 -> mat tin hieu. Mean giu duoc cuong do.
    parts = [gb["surge_multiplier"].mean().rename("target_surge"),
             gb["is_surge"].mean().rename("target_surge_rate"),
             gb["surge_multiplier"].max().rename("surge_max"),
             gb["distance"].median().rename("distance_median"),
             gb["id"].size().rename("quote_count")]
    parts += [gb[w].median().rename(w) for w in WEATHER if w in d.columns]
    parts.append(gb["short_summary"].agg(
        lambda s: s.mode().iat[0] if len(s.mode()) else "NA").rename("short_summary"))
    g = pd.concat(parts, axis=1).reset_index()
    # Target nhi phan suy TRUC TIEP tu target_surge -> luon nhat quan
    g["target_is_surge"] = (g.target_surge > 1.0).astype(int)
    g = them_thoi_gian(g)
    g = them_lag(g, keys, "target_surge", "surge")
    truoc = g.groupby(keys, observed=True)["target_surge_rate"].shift(1)
    g["lag1_surge_rate"] = truoc
    g["roll_surge_rate6"] = (truoc.groupby([g[k] for k in keys])
                             .rolling(6, min_periods=1).mean()
                             .reset_index(drop=True))
    return g


# Cac muc phan giai can dung. "15min" la ban chinh cho muc ii (nghien cuu do tre);
# "60min" giu lam doi chung. Doi bucket -> chi doi dt.floor(freq).
BUCKETS = {"15min": "15min", "60min": "h"}


def main():
    if not IN.exists():
        sys.exit(f"Khong tim thay {IN}. Hay chay analysis/00_clean_full_dataset.ipynb truoc.")
    t0 = time.time()
    df = pd.read_parquet(IN)
    print(f"Nap {len(df):,} chuyen tu {IN.name}  ({time.time()-t0:.1f}s)\n")

    for ten_bucket, freq in BUCKETS.items():
        df["snapshot"] = df["local"].dt.floor(freq)
        print(f"############### BUCKET {ten_bucket} (floor '{freq}') ###############")
        for ten, ham, base in [("PRICE", dung_bang_price, "snapshot_price"),
                               ("SURGE", dung_bang_surge, "snapshot_surge")]:
            t = time.time()
            g = ham(df)
            g["data_split"] = gan_split(g["snapshot"].dt.normalize())
            g = g[g.data_split != "drop"].reset_index(drop=True)
            fn = f"{base}_{ten_bucket}.parquet"
            g.to_parquet(DATA / fn, index=False)

            keys = (["cab_type", "source", "destination", "name"] if ten == "PRICE"
                    else ["source", "destination"])
            age = g["observation_age_minutes"]
            print(f"=== BANG {ten} -> {fn} ===")
            print(f"  {len(g):,} snapshot x {g.shape[1]} cot  ({time.time()-t:.1f}s)")
            print(f"  So series: {g.groupby(keys, observed=True).ngroups:,}")
            print(f"  Split: {g.data_split.value_counts().to_dict()}")
            print(f"  Do tre giua 2 snapshot: median={age.median():.0f}p | "
                  f"p90={age.quantile(.9):.0f}p")
            print(f"  Phan bo do tre: {g.observation_age_bucket.value_counts().to_dict()}")
            if ten == "SURGE":
                print(f"  Ty le surge (mean>1): {g.target_is_surge.mean()*100:.2f}%")
            print(f"  Thieu lag1: {g.filter(like='lag1_').isna().mean().mean()*100:.1f}%")
            print()

    print(f"Tong thoi gian: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
