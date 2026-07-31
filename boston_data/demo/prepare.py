# -*- coding: utf-8 -*-
"""
CHUAN BI cho app mo phong (chay 1 lan):
  - Dung bang tra cuu feature theo tuyen + dich vu tu snapshot
  - Train 3 model (gia Uber, gia Lyft, surge Lyft) -> luu app/models.joblib
  - Luu toa do 12 khu Boston -> app/area_coords.json

  python demo/prepare.py
"""
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd, joblib
warnings.filterwarnings("ignore")
from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"

PC = ["name","source","destination","observation_age_bucket"]
PN = ["distance_median","lag1_price","lag2_price","lag3_price","roll_mean6_price",
      "roll_std3_price","observation_age_minutes","hour_local","weekday_local","is_weekend"]
SC = ["source","destination","short_summary"]
SN = ["hour_local","weekday_local","is_weekend","lag1_surge","lag2_surge",
      "roll_mean6_surge","roll_surge_rate6","observation_age_minutes"]
PF, SF = PC+PN, SC+SN

# Toa do gan dung 12 khu lõi Boston (lat, lon)
AREA_COORDS = {
    "Back Bay":               [42.3503, -71.0810],
    "Beacon Hill":            [42.3588, -71.0707],
    "Boston University":      [42.3505, -71.1054],
    "Fenway":                 [42.3429, -71.0973],
    "Financial District":     [42.3559, -71.0550],
    "Haymarket Square":       [42.3634, -71.0578],
    "North End":              [42.3647, -71.0542],
    "North Station":          [42.3663, -71.0622],
    "Northeastern University":[42.3398, -71.0892],
    "South Station":          [42.3519, -71.0552],
    "Theatre District":       [42.3519, -71.0643],
    "West End":               [42.3644, -71.0661],
}

def prep(df, cat):
    X = df.copy()
    for c in cat: X[c] = X[c].astype("category")
    return X

def main():
    print("Nap snapshot...")
    gp = pd.read_csv(DATA/"snapshot_price_15min.csv")
    gs = pd.read_csv(DATA/"snapshot_surge_15min.csv")

    # ---- Bang tra cuu GIA: (hang,source,dest,name) -> feature dien hinh + GIA THUC de doi chieu ----
    look = (gp.groupby(["cab_type","source","destination","name"])
              .agg(distance_median=("distance_median","median"),
                   lag1_price=("lag1_price","median"), lag2_price=("lag2_price","median"),
                   lag3_price=("lag3_price","median"), roll_mean6_price=("roll_mean6_price","median"),
                   roll_std3_price=("roll_std3_price","median"),
                   gia_thuc_median=("target_price","median"),
                   gia_thuc_p25=("target_price", lambda x: x.quantile(.25)),
                   gia_thuc_p75=("target_price", lambda x: x.quantile(.75)),
                   so_quan_sat=("target_price","size"))
              .reset_index())
    look = look.dropna(subset=["distance_median"])

    # ---- Bang tra cuu SURGE theo tuyen + THUC de doi chieu ----
    slook = (gs.groupby(["source","destination"])
               .agg(lag1_surge=("lag1_surge","median"), lag2_surge=("lag2_surge","median"),
                    roll_mean6_surge=("roll_mean6_surge","median"),
                    roll_surge_rate6=("roll_surge_rate6","median"),
                    short_summary=("short_summary", lambda s: s.mode().iat[0] if len(s.mode()) else "clear"),
                    surge_thuc_median=("target_surge","median"),
                    ty_le_surge_thuc=("target_is_surge","mean"),
                    so_quan_sat_surge=("target_is_surge","size"))
               .reset_index())

    # ---- Train 3 model (nhanh, du chinh xac cho demo) ----
    print("Train model gia...")
    def tp(hang):
        tr = gp[(gp.cab_type==hang)&(gp.data_split=="train")]
        return HistGradientBoostingRegressor(max_iter=300, learning_rate=0.06, l2_regularization=1.0,
            early_stopping=True, validation_fraction=0.1, n_iter_no_change=15,
            categorical_features=PC, random_state=42).fit(prep(tr,PC)[PF], np.log(tr.target_price))
    m_uber, m_lyft = tp("Uber"), tp("Lyft")

    print("Train model surge...")
    trs = gs[gs.data_split=="train"]
    clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06, l2_regularization=1.0,
        categorical_features=SC, random_state=42).fit(prep(trs,SC)[SF], trs.target_is_surge)
    tso = trs[trs.target_is_surge==1]
    reg = HistGradientBoostingRegressor(max_iter=200, learning_rate=0.06,
        categorical_features=SC, random_state=42).fit(prep(tso,SC)[SF], tso.target_surge)

    # ---- Luu ----
    joblib.dump({"m_uber":m_uber, "m_lyft":m_lyft, "clf":clf, "reg":reg}, HERE/"models.joblib")
    look.to_json(HERE/"route_lookup.json", orient="records", force_ascii=False)
    slook.to_json(HERE/"surge_lookup.json", orient="records", force_ascii=False)
    meta = {"areas": AREA_COORDS,
            "services": {"Uber": sorted(gp[gp.cab_type=="Uber"].name.unique().tolist()),
                         "Lyft": sorted(gp[gp.cab_type=="Lyft"].name.unique().tolist())},
            "weather_options": sorted(gs.short_summary.dropna().unique().tolist())}
    json.dump(meta, open(HERE/"meta.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)

    print(f"Xong. Luu vao {HERE}:")
    print("  models.joblib, route_lookup.json, surge_lookup.json, meta.json")
    print(f"  {len(look)} route-service | {len(slook)} tuyen surge")

if __name__ == "__main__":
    main()
