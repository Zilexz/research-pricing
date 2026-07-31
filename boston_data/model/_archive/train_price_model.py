# -*- coding: utf-8 -*-
"""
Chot & hoan thien model PRICE (target_price_median).
- So sanh: FULL (44 feat) vs LEAN (~7 feat) vs LEAN+log-target vs Persistence(lag1).
- Metric: MAE, RMSE, R2, MAPE tren calibration + test.
- Luu model tot nhat + feature list + bieu do.
"""
import json, numpy as np, pandas as pd, joblib
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BLUE, ORANGE, INK, MUT = "#0072B2", "#E69F00", "#222222", "#666666"
plt.rcParams.update({"figure.facecolor":"white","axes.spines.top":False,"axes.spines.right":False,
    "axes.grid":True,"grid.color":"#ECECEC","font.size":10})

from pathlib import Path
HERE = Path(__file__).resolve().parent
snap = pd.read_csv(HERE/"snapshot_table.csv")
TARGET = "target_price_median"

# ---- feature sets ----
FULL_CAT = ["cab_type","name","source","destination","short_summary","observation_age_bucket"]
FULL_NUM = ["distance_median","latitude","longitude","temperature","apparentTemperature",
    "precipIntensity","precipProbability","humidity","windSpeed","windGust","visibility",
    "dewPoint","pressure","windBearing","cloudCover","uvIndex","ozone","event_hour_local",
    "event_weekday_local","event_month_local","is_weekend","hour_sin","hour_cos","weekday_sin",
    "weekday_cos","observation_age_minutes","lag1_price_median","lag2_price_median","lag3_price_median",
    "lag1_multiplier_median","lag1_quote_count","lag1_price_spread","lag1_distance_median",
    "lag_price_delta_1_2","history_price_mean_last3","history_price_std_last3",
    "history_price_mean_last6","history_observation_count"]
LEAN_CAT = ["name","source","destination"]
LEAN_NUM = ["distance_median","history_price_mean_last6","history_price_std_last3","lag1_price_median"]

tr = snap["data_split"]=="train"; ca = snap["data_split"]=="calibration"; te = snap["data_split"]=="test"
y = snap[TARGET]

def prep(cols_cat, cols_num):
    X = snap[cols_cat+cols_num].copy()
    for c in cols_cat: X[c] = X[c].astype("category")
    return X, cols_cat

def metrics(y_true, y_pred):
    return dict(MAE=mean_absolute_error(y_true,y_pred),
                RMSE=mean_squared_error(y_true,y_pred)**0.5,
                R2=r2_score(y_true,y_pred),
                MAPE=float(np.mean(np.abs((y_true-y_pred)/y_true))*100))

def train_eval(name, cols_cat, cols_num, log_target=False):
    X, cats = prep(cols_cat, cols_num)
    ytr = np.log(y[tr]) if log_target else y[tr]
    mdl = HistGradientBoostingRegressor(max_iter=500, learning_rate=0.05, l2_regularization=1.0,
            early_stopping=True, validation_fraction=0.1, random_state=42,
            categorical_features=cats)
    mdl.fit(X[tr], ytr)
    res = {}
    for split, m in [("calib",ca),("test",te)]:
        p = mdl.predict(X[m]); p = np.exp(p) if log_target else p
        res[split] = metrics(y[m].values, p)
    return mdl, X, res

rows = []
models = {}
for name, cc, cn, logt in [
    ("FULL (44 feat)",   FULL_CAT, FULL_NUM, False),
    ("LEAN (7 feat)",    LEAN_CAT, LEAN_NUM, False),
    ("LEAN + log-target",LEAN_CAT, LEAN_NUM, True),
]:
    mdl, X, res = train_eval(name, cc, cn, logt)
    models[name] = (mdl, X, logt, cc+cn)
    for split in ("calib","test"):
        rows.append({"model":name,"split":split, **{k:round(v,4) for k,v in res[split].items()}})

# persistence baseline (predict = lag1) tren test
lag = snap.loc[te,"lag1_price_median"]; ok = lag.notna()
rows.append({"model":"Persistence(lag1)","split":"test",
             **{k:round(v,4) for k,v in metrics(y[te][ok].values, lag[ok].values).items()}})

report = pd.DataFrame(rows)
print("="*78); print("SO SANH CAC MODEL PRICE"); print("="*78)
print(report.to_string(index=False))

# ---- chon model tot nhat theo MAE test ----
test_only = report[(report.split=="test") & (report.model.str.startswith(("FULL","LEAN")))]
best_name = test_only.sort_values("MAE").iloc[0]["model"]
print(f"\n>> Model tot nhat (MAE test thap nhat): {best_name}")

best_mdl, best_X, best_log, best_feats = models[best_name]

# ---- luu model + metadata ----
joblib.dump(best_mdl, HERE/"model_price.joblib")
meta = {"target":TARGET, "model":best_name, "log_target":best_log,
        "features":best_feats,
        "categorical":[f for f in best_feats if f in (LEAN_CAT+FULL_CAT)],
        "metrics_test":report[(report.model==best_name)&(report.split=="test")].iloc[0].to_dict(),
        "note":"HistGradientBoostingRegressor; train<=2018-12-10, test 16-18/12"}
json.dump(meta, open(HERE/"model_price_meta.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
report.to_csv(HERE/"model_price_metrics.csv", index=False)

# ---- bieu do: du doan vs thuc te + residual (tren test) ----
pred = best_mdl.predict(best_X[te]); pred = np.exp(pred) if best_log else pred
yt = y[te].values
fig, axes = plt.subplots(1,2, figsize=(13,5.4))
axes[0].scatter(yt, pred, s=8, alpha=0.25, color=BLUE, edgecolors="none")
lim=[0, max(yt.max(),pred.max())*1.02]
axes[0].plot(lim,lim, color=ORANGE, lw=1.5, ls="--", label="y=x (hoan hao)")
axes[0].set_xlabel("Gia thuc te (USD)"); axes[0].set_ylabel("Gia du doan (USD)")
axes[0].set_title(f"Du doan vs Thuc te — {best_name}"); axes[0].legend(frameon=False)
resid = pred - yt
axes[1].hist(resid, bins=60, color=BLUE, alpha=0.85)
axes[1].axvline(0, color=ORANGE, lw=1.5, ls="--")
axes[1].set_xlabel("Sai so (du doan - thuc te)"); axes[1].set_ylabel("So snapshot")
axes[1].set_title(f"Phan bo sai so (MAE={metrics(yt,pred)['MAE']:.2f} USD)")
fig.tight_layout(); fig.savefig(HERE/"model_price_diagnostics.png", dpi=130); plt.close(fig)

print("\nDa luu:")
for f in ["model_price.joblib","model_price_meta.json","model_price_metrics.csv","model_price_diagnostics.png"]:
    print("  -", HERE/f)
