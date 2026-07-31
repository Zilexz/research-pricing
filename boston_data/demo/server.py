# -*- coding: utf-8 -*-
"""
APP MO PHONG DAT XE — chay local, khong can Flask/FastAPI.

  1. python demo/prepare.py     (chay 1 lan)
  2. python demo/server.py      (mo http://localhost:8000)
"""
import json, warnings
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import numpy as np, pandas as pd, joblib
warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
PORT = 8000

PC = ["name","source","destination","observation_age_bucket"]
PN = ["distance_median","lag1_price","lag2_price","lag3_price","roll_mean6_price",
      "roll_std3_price","observation_age_minutes","hour_local","weekday_local","is_weekend"]
SC = ["source","destination","short_summary"]
SN = ["hour_local","weekday_local","is_weekend","lag1_surge","lag2_surge",
      "roll_mean6_surge","roll_surge_rate6","observation_age_minutes"]
PF, SF = PC+PN, SC+SN

print("Nap model + bang tra cuu...")
M = joblib.load(HERE/"models.joblib")
LOOK = pd.read_json(HERE/"route_lookup.json")
SLOOK = pd.read_json(HERE/"surge_lookup.json")
META = json.load(open(HERE/"meta.json", encoding="utf-8"))
print("San sang.")

def prep(df, cat):
    X = df.copy()
    for c in cat: X[c] = X[c].astype("category")
    return X

def bucket(age):
    return "<=15p" if age<=15 else "15-30p" if age<=30 else "30-60p" if age<=60 else "1-3h" if age<=180 else ">3h"

PRICE_NUM_LOOK = ["distance_median","lag1_price","lag2_price","lag3_price","roll_mean6_price","roll_std3_price"]
SURGE_NUM_LOOK = ["lag1_surge","lag2_surge","roll_mean6_surge","roll_surge_rate6"]

DOICHIEU = ["gia_thuc_median","gia_thuc_p25","gia_thuc_p75","so_quan_sat","distance_median"]

def tra_gia(hang, source, dest, name):
    """Tra feature dien hinh + GIA THUC de doi chieu. Co FALLBACK de khong thieu."""
    exact = LOOK[(LOOK.cab_type==hang)&(LOOK.source==source)&(LOOK.destination==dest)&(LOOK.name==name)]
    if len(exact):
        r = exact.iloc[0]
        return r[PRICE_NUM_LOOK].to_dict(), r[DOICHIEU].to_dict(), "tuyen chinh xac"
    same = LOOK[(LOOK.cab_type==hang)&(LOOK.source==source)&(LOOK.name==name)]   # trung binh theo diem den
    if len(same):
        return same[PRICE_NUM_LOOK].mean().to_dict(), same[DOICHIEU].mean().to_dict(), "uoc luong tu khu don"
    anyname = LOOK[(LOOK.cab_type==hang)&(LOOK.name==name)]                       # trung binh toan hang
    if len(anyname):
        return anyname[PRICE_NUM_LOOK].mean().to_dict(), anyname[DOICHIEU].mean().to_dict(), "uoc luong toan hang"
    return None, None, None

def tra_surge(source, dest):
    exact = SLOOK[(SLOOK.source==source)&(SLOOK.destination==dest)]
    if len(exact):
        s = exact.iloc[0]
        return {**{k: float(s[k]) for k in SURGE_NUM_LOOK}, "short_summary": s.short_summary}
    same = SLOOK[SLOOK.source==source]
    if len(same):
        return {**{k: float(same[k].mean()) for k in SURGE_NUM_LOOK}, "short_summary": same.short_summary.mode().iat[0]}
    return {**{k: 0.0 for k in SURGE_NUM_LOOK}, "short_summary": "clear"}

def du_doan(hang, source, dest, name, hour, weekday, age, weather=None, distance=None):
    r, dc, nguon = tra_gia(hang, source, dest, name)
    if r is None:
        return {"error": f"Khong co du lieu cho dich vu {name}"}
    dist = float(distance) if distance and float(distance) > 0 else float(r["distance_median"])
    is_we = int(weekday>=5)
    X = pd.DataFrame([{"name":name,"source":source,"destination":dest,"observation_age_bucket":bucket(age),
        "distance_median":dist,"lag1_price":r["lag1_price"],"lag2_price":r["lag2_price"],
        "lag3_price":r["lag3_price"],"roll_mean6_price":r["roll_mean6_price"],"roll_std3_price":r["roll_std3_price"],
        "observation_age_minutes":age,"hour_local":hour,"weekday_local":weekday,"is_weekend":is_we}])
    m = M["m_uber"] if hang=="Uber" else M["m_lyft"]
    gia = float(np.exp(m.predict(prep(X,PC)[PF])[0]))

    surge, p_surge = 1.0, 0.0
    if hang=="Lyft":
        s = tra_surge(source, dest)
        ss = weather if weather else s["short_summary"]
        XS = pd.DataFrame([{"source":source,"destination":dest,"short_summary":ss,
            "hour_local":hour,"weekday_local":weekday,"is_weekend":is_we,
            "lag1_surge":s["lag1_surge"],"lag2_surge":s["lag2_surge"],"roll_mean6_surge":s["roll_mean6_surge"],
            "roll_surge_rate6":s["roll_surge_rate6"],"observation_age_minutes":age}])
        p_surge = float(M["clf"].predict_proba(prep(XS,SC)[SF])[0,1])
        mag = float(M["reg"].predict(prep(XS,SC)[SF])[0])
        surge = p_surge*mag + (1-p_surge)*1.0
    # ---- DOI CHIEU voi du lieu thuc ----
    sc = tra_surge_doichieu(source, dest)
    doi_chieu = {
        "gia_thuc_median": round(float(dc["gia_thuc_median"]),2),
        "gia_thuc_p25": round(float(dc["gia_thuc_p25"]),2),
        "gia_thuc_p75": round(float(dc["gia_thuc_p75"]),2),
        "so_quan_sat": int(dc["so_quan_sat"]),
        "quang_duong_data": round(float(dc["distance_median"]),2),
        "nguon": nguon,
        "sai_lech_gia": round(gia - float(dc["gia_thuc_median"]), 2),
        "surge_thuc_median": sc["surge_thuc_median"],
        "ty_le_surge_thuc": sc["ty_le_surge_thuc"],
    }
    lag1 = r["lag1_price"]
    return {"gia_du_doan": round(gia,2), "quang_duong_dam": round(dist,2),
            "P_surge": round(p_surge,3), "he_so_nhan": round(surge,3),
            "khu_don": source, "khu_den": dest,
            "gia_truoc_lag1": round(float(lag1),2) if pd.notna(lag1) else None,
            "doi_chieu": doi_chieu}


def tra_surge_doichieu(source, dest):
    ex = SLOOK[(SLOOK.source==source)&(SLOOK.destination==dest)]
    if len(ex):
        s = ex.iloc[0]
        return {"surge_thuc_median": round(float(s.surge_thuc_median),3),
                "ty_le_surge_thuc": round(float(s.ty_le_surge_thuc)*100,1)}
    return {"surge_thuc_median": None, "ty_le_surge_thuc": None}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype+"; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body if isinstance(body, bytes) else body.encode("utf-8"))

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, (HERE/"index.html").read_text(encoding="utf-8"), "text/html")
        elif self.path == "/api/meta":
            self._send(200, json.dumps(META, ensure_ascii=False))
        else:
            self._send(404, json.dumps({"error":"not found"}))

    def do_POST(self):
        if self.path != "/api/predict":
            return self._send(404, json.dumps({"error":"not found"}))
        n = int(self.headers.get("Content-Length", 0))
        d = json.loads(self.rfile.read(n) or b"{}")
        try:
            res = du_doan(d["hang"], d["source"], d["destination"], d["name"],
                          int(d["hour"]), int(d["weekday"]), int(d.get("age",15)),
                          d.get("weather"), d.get("distance"))
            self._send(200, json.dumps(res, ensure_ascii=False))
        except Exception as e:
            self._send(400, json.dumps({"error": str(e)}, ensure_ascii=False))

    def log_message(self, *a): pass  # tat log rac


if __name__ == "__main__":
    print(f"\n>>> Mo trinh duyet: http://localhost:{PORT}\n")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
