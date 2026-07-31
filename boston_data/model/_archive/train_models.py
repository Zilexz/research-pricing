# -*- coding: utf-8 -*-
"""
Cau phan (ii) — Train model du bao GIA + HE SO NHAN cua doi thu.
Theo docs/MODEL_DESIGN.md. Chay 1 lan, luu model + metric + in bang ket qua.

  python model/train_models.py
"""
from pathlib import Path
import sys, time, json
import numpy as np, pandas as pd
import joblib
from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score,
                             roc_auc_score, average_precision_score, brier_score_loss)

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
OUT  = HERE          # luu model + metric vao model/

# ---------------- feature sets (theo MODEL_DESIGN.md) ----------------
PRICE_CAT = ["name", "source", "destination", "observation_age_bucket"]
PRICE_NUM = ["distance_median", "lag1_price", "lag2_price", "lag3_price",
             "roll_mean6_price", "roll_std3_price", "observation_age_minutes",
             "hour_local", "weekday_local", "is_weekend"]
SURGE_CAT = ["source", "destination", "short_summary"]
SURGE_NUM = ["hour_local", "weekday_local", "is_weekend",
             "lag1_surge", "lag2_surge", "roll_mean6_surge", "roll_surge_rate6",
             "observation_age_minutes"]


def metrics_reg(y, p):
    return dict(MAE=mean_absolute_error(y, p),
                RMSE=mean_squared_error(y, p) ** .5,
                R2=r2_score(y, p),
                MAPE=float(np.mean(np.abs((y - p) / y)) * 100))


def prep(df, cat):
    X = df.copy()
    for c in cat:
        X[c] = X[c].astype("category")
    return X


def train_price(g, hang):
    """1 model gia cho 1 hang. Log-target. Tra ve dict ket qua + model."""
    d = g[g.cab_type == hang].copy()
    tr = d[d.data_split == "train"]
    te = d[d.data_split == "test"]
    feats = PRICE_CAT + PRICE_NUM
    m = HistGradientBoostingRegressor(
        max_iter=500, learning_rate=0.05, l2_regularization=1.0,
        early_stopping=True, validation_fraction=0.1,
        categorical_features=PRICE_CAT, random_state=42)
    m.fit(prep(tr, PRICE_CAT)[feats], np.log(tr.target_price))
    pred = np.exp(m.predict(prep(te, PRICE_CAT)[feats]))

    # baseline
    bl = te.lag1_price.notna()
    persistence = mean_absolute_error(te.target_price[bl], te.lag1_price[bl])
    hr = te.roll_mean6_price.notna()
    histavg = mean_absolute_error(te.target_price[hr], te.roll_mean6_price[hr])

    mk = metrics_reg(te.target_price.values, pred)
    res = {"hang": hang, "n_test": len(te), **mk,
           "MAE_persistence": persistence, "MAE_histavg": histavg,
           "cai_thien_vs_persistence_%": (1 - mk["MAE"] / persistence) * 100,
           "cai_thien_vs_histavg_%": (1 - mk["MAE"] / histavg) * 100}
    # do tre
    te = te.assign(pred=pred)
    delay = (te.groupby("observation_age_bucket", observed=True)
               .apply(lambda x: pd.Series({
                   "n": len(x),
                   "MAE_model": mean_absolute_error(x.target_price, x.pred),
                   "MAE_persist": mean_absolute_error(
                       x.target_price[x.lag1_price.notna()],
                       x.lag1_price[x.lag1_price.notna()]) if x.lag1_price.notna().any() else np.nan}),
                      include_groups=False))
    return res, m, delay, feats


def train_surge(s):
    """Model 2 tang cho Lyft (bang cap thi truong)."""
    tr = s[s.data_split == "train"]
    te = s[s.data_split == "test"]
    feats = SURGE_CAT + SURGE_NUM

    # Tang 1: phan loai co surge
    clf = HistGradientBoostingClassifier(
        max_iter=400, learning_rate=0.05, l2_regularization=1.0,
        categorical_features=SURGE_CAT, random_state=42)
    clf.fit(prep(tr, SURGE_CAT)[feats], tr.target_is_surge)
    p_surge = clf.predict_proba(prep(te, SURGE_CAT)[feats])[:, 1]

    # Tang 2: do lon khi co surge
    trs = tr[tr.target_is_surge == 1]
    reg = HistGradientBoostingRegressor(
        max_iter=300, learning_rate=0.05, categorical_features=SURGE_CAT,
        random_state=42)
    reg.fit(prep(trs, SURGE_CAT)[feats], trs.target_surge)
    mag = reg.predict(prep(te, SURGE_CAT)[feats])

    # ket hop E[multiplier]
    e_mult = p_surge * mag + (1 - p_surge) * 1.0

    y_is = te.target_is_surge.values
    res = {
        "n_test": len(te), "ty_le_surge_%": y_is.mean() * 100,
        "ROC_AUC": roc_auc_score(y_is, p_surge),
        "PR_AUC": average_precision_score(y_is, p_surge),
        "Brier": brier_score_loss(y_is, p_surge),
        "AUC_persistence": roc_auc_score(
            y_is, (te.lag1_surge.fillna(1) - 1).clip(0)),
        "MAE_Emult": mean_absolute_error(te.target_surge, e_mult),
        "MAE_luon_1": mean_absolute_error(te.target_surge, np.ones(len(te))),
        "accuracy_doan_khong": 1 - y_is.mean(),
    }
    return res, (clf, reg), feats


def main():
    t0 = time.time()
    fp = DATA / "snapshot_price_15min.parquet"
    fs = DATA / "snapshot_surge_15min.parquet"
    if not fp.exists():
        sys.exit("Chua co snapshot_price_15min.parquet. Chay model/build_snapshots.py truoc.")
    gp = pd.read_parquet(fp)
    gs = pd.read_parquet(fs)
    print(f"Nap price {len(gp):,} | surge {len(gs):,}  ({time.time()-t0:.1f}s)\n")

    # ---------- MODEL GIA ----------
    print("=" * 66); print("MODEL GIA (per hang, log-target)"); print("=" * 66)
    price_res, delays = [], {}
    for hang in ["Uber", "Lyft"]:
        r, m, delay, feats = train_price(gp, hang)
        price_res.append(r); delays[hang] = delay
        joblib.dump(m, OUT / f"model_price_{hang.lower()}.joblib")
        print(f"\n[{hang}]  n_test={r['n_test']:,}")
        print(f"  MAE={r['MAE']:.3f}  RMSE={r['RMSE']:.3f}  R2={r['R2']:.4f}  MAPE={r['MAPE']:.2f}%")
        print(f"  Baseline: persistence={r['MAE_persistence']:.3f}  histavg={r['MAE_histavg']:.3f}")
        print(f"  Cai thien: vs persistence {r['cai_thien_vs_persistence_%']:+.1f}%  "
              f"vs histavg {r['cai_thien_vs_histavg_%']:+.1f}%")

    # ---------- MODEL SURGE ----------
    print("\n" + "=" * 66); print("MODEL HE SO NHAN (Lyft, 2 tang)"); print("=" * 66)
    sr, models, sfeats = train_surge(gs)
    joblib.dump(models, OUT / "model_surge_lyft.joblib")
    print(f"  n_test={sr['n_test']:,}  ty le surge={sr['ty_le_surge_%']:.1f}%")
    print(f"  ROC-AUC={sr['ROC_AUC']:.4f}  (persistence {sr['AUC_persistence']:.4f})")
    print(f"  PR-AUC ={sr['PR_AUC']:.4f}  (nen {sr['ty_le_surge_%']/100:.4f})")
    print(f"  Brier  ={sr['Brier']:.4f}")
    print(f"  MAE E[mult]={sr['MAE_Emult']:.4f}  (luon-1.0 {sr['MAE_luon_1']:.4f})")
    print(f"  !! Accuracy doan 'khong surge' = {sr['accuracy_doan_khong']:.4f} -> KHONG dung accuracy")

    # ---------- SUY GIAM THEO DO TRE ----------
    print("\n" + "=" * 66); print("SUY GIAM THEO DO TRE (price)"); print("=" * 66)
    order = ["<=15p", "15-30p", "30-60p", "1-3h", ">3h"]
    for hang in ["Uber", "Lyft"]:
        print(f"\n[{hang}]")
        d = delays[hang].reindex([o for o in order if o in delays[hang].index])
        print(d.round(3).to_string())

    # ---------- LUU METRIC ----------
    allm = {"price": price_res, "surge": sr,
            "delay": {h: delays[h].reset_index().to_dict("records") for h in delays},
            "price_features": PRICE_CAT + PRICE_NUM,
            "surge_features": SURGE_CAT + SURGE_NUM}
    json.dump(allm, open(OUT / "model_results.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2, default=float)
    print(f"\nDa luu: model_price_uber/lyft.joblib, model_surge_lyft.joblib, model_results.json")
    print(f"Tong thoi gian: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
