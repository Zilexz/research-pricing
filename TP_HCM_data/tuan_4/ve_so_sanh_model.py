# -*- coding: utf-8 -*-
"""So sánh 9 model: sai ở đâu, sai bao nhiêu, và chỗ nào rơi ra ngoài khoảng.

Chạy:  py -3.11 ve_so_sanh_model.py
Xuất:  docs/hinh_anh/MS1_sai_so_theo_chieu.png
       docs/hinh_anh/MS2_ra_ngoai_khoang.png

Mọi model đánh giá trên CÙNG tập test (lag 5 phút, 216.090 chuyến) và các file
dự đoán đã được kiểm căn hàng theo `gia_that`.
"""
import warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE, MULT, GREEN, RED, PURPLE, MUT = ("#0072B2", "#E69F00", "#009E73",
                                       "#D55E00", "#CC79A7", "#666666")
INK = "#222222"
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": .25,
    "savefig.dpi": 150, "savefig.bbox": "tight",
    "font.size": 11.5, "axes.titlesize": 12.5, "axes.labelsize": 11.5,
    "xtick.labelsize": 10, "ytick.labelsize": 10, "legend.fontsize": 10.5,
})
HERE = Path(__file__).resolve().parent
E    = HERE / "../model/evaluation"
HINH = (HERE / "../docs/hinh_anh").resolve()

MUC  = 0.90
CAT  = [0, 50e3, 100e3, 150e3, 200e3, 300e3, np.inf]
NHAN = ["<50k", "50–100k", "100–150k", "150–200k", "200–300k", ">300k"]
KMC  = [0, 2, 4, 6, 8, 10, 15, np.inf]
KMN  = ["<2", "2–4", "4–6", "6–8", "8–10", "10–15", ">15"]

# ── gom du doan cua moi model ───────────────────────────────────────────
uq = pd.read_parquet(E / "uq_pred_test.parquet")
gm = pd.read_parquet(E / "pred_gam.parquet")
hy = pd.read_parquet(E / "pred_hybrid_cu.parquet")
tt = pd.read_parquet(E / "pred_gia.parquet")

d = pd.DataFrame({
    "y":    uq.gia_that.values,
    "km":   uq.quote_distance.values,
    "gio":  uq.gio_vn.values,
    "tiet": uq.weather_main.values,
    "lag":  uq.requested_lag_minutes.values,
    "Hybrid (production)": uq.hybrid_pred.values,
    "Persistence":         uq.persistence.values,
    "GAM hybrid":          gm.hybrid_pred.values,
    "GAM trực tiếp":       gm.truc_tiep_pred.values,
})
for a in ["HistGB", "LightGBM", "XGBoost"]:
    d[f"Hybrid {a}"]    = hy[hy.algo == a].hybrid_pred.values
    d[f"Trực tiếp {a}"] = tt[tt.algo == a].pred.values

d = d[d.lag == 5].reset_index(drop=True)
MODEL = [c for c in d.columns if c not in ("y", "km", "gio", "tiet", "lag")]

d["band"] = pd.cut(d["Hybrid (production)"], CAT, labels=NHAN)
d["kmb"]  = pd.cut(d.km, KMC, labels=KMN)
for m in MODEL:
    d[f"sai_{m}"] = (d[m] - d.y).abs() / d.y

print(f"{len(d):,} chuyến · {len(MODEL)} model")
print("\n=== MAPE tổng ===")
tong = pd.Series({m: d[f"sai_{m}"].mean() for m in MODEL}).sort_values()
for m, v in tong.items():
    print(f"  {m:22} {v:.2%}")

# ══════════════════════════════════════════════════════════════════════════
# HINH MS1 — sai so tung model theo bon chieu
# ══════════════════════════════════════════════════════════════════════════
# Bo Persistence khoi hinh: no o muc 26–53% nen keo truc, lam 5 model kia
# (14–19%) dồn thành một cục sát đáy. Mức của nó nêu trong bảng kèm theo.
VE = ["Hybrid (production)", "Hybrid XGBoost", "Trực tiếp XGBoost",
      "GAM hybrid", "GAM trực tiếp"]
MAU = [BASE, GREEN, MULT, PURPLE, RED]
KIEU = ["o-", "s-", "^-", "D--", "v--"]

fig, ax = plt.subplots(1, 4, figsize=(19, 4.8))

for a, (cot, nhan, ten) in zip(ax, [("band", NHAN, "Band giá dự đoán"),
                                    ("kmb", KMN, "Quãng đường (km)"),
                                    ("gio", sorted(d.gio.unique()), "Giờ trong ngày"),
                                    ("tiet", None, "Thời tiết")]):
    if nhan is None:
        nhan = d.tiet.value_counts()
        nhan = nhan[nhan >= 1000].index.tolist()
    x = np.arange(len(nhan))
    for m, mau, k in zip(VE, MAU, KIEU):
        g = d.groupby(cot, observed=True)[f"sai_{m}"].mean().reindex(nhan)
        a.plot(x, g*100, k, color=mau, lw=2.2, ms=6, label=m, alpha=.9)
    a.set_xticks(x)
    a.set_xticklabels(nhan, rotation=25 if cot in ("band", "kmb", "tiet") else 0,
                      ha="right" if cot in ("band", "kmb", "tiet") else "center",
                      fontsize=9)
    a.set_xlabel(ten); a.set_ylabel("MAPE (%)" if a is ax[0] else "")
    a.set_ylim(8.5, 19.5)
    a.set_title(ten, fontweight="bold")
ax[0].legend(frameon=True, framealpha=.95, edgecolor=MUT, fontsize=8.5, loc="upper left")

fig.suptitle("MS1 — Mọi model bung sai số ở cùng hai chiều: quãng đường và band giá\n"
             "Gần như phẳng theo giờ và thời tiết. Ở hai đầu dải, GAM và GBM đổi ngôi (xem MS3). "
             "Persistence để ngoài hình vì ở mức 26–53%",
             fontweight="bold", fontsize=13.5, y=1.05)
fig.tight_layout()
fig.savefig(HINH / "MS1_sai_so_theo_chieu.png")
plt.show()

# ══════════════════════════════════════════════════════════════════════════
# HINH MS2 — khoang tin cay: dao dong va cho nao roi ra ngoai
# ══════════════════════════════════════════════════════════════════════════
uc = pd.read_parquet(E / "uq_pred_calibration.parquet")
uc = uc[uc.requested_lag_minutes == 5].copy()
uc["res"] = (uc.hybrid_pred - uc.gia_that).abs() / uc.hybrid_pred
q = uc.res.quantile(MUC)
p = d["Hybrid (production)"].values
d["lo"], d["hi"] = p*(1-q), p*(1+q)
d["tren"] = d.y > d.hi
d["duoi"] = d.y < d.lo
d["rong"] = d.hi - d.lo

fig, ax = plt.subplots(1, 4, figsize=(19, 4.8))

for a, (cot, nhan, ten) in zip(ax, [("band", NHAN, "Band giá dự đoán"),
                                    ("kmb", KMN, "Quãng đường (km)"),
                                    ("gio", sorted(d.gio.unique()), "Giờ trong ngày"),
                                    ("tiet", None, "Thời tiết")]):
    if nhan is None:
        nhan = d.tiet.value_counts()
        nhan = nhan[nhan >= 1000].index.tolist()
    g = d.groupby(cot, observed=True)[["tren", "duoi"]].mean().reindex(nhan)
    x = np.arange(len(nhan))
    a.bar(x, g.tren*100, color=RED,  alpha=.9, label="Vượt cận trên")
    a.bar(x, -g.duoi*100, color=BASE, alpha=.9, label="Thủng cận dưới")
    a.axhline(0, color=INK, lw=1)
    a.axhline(10, color=MUT, lw=1.4, ls="--")
    a.text(len(nhan)-.4, 10.4, "tổng sai 10% = mức cam kết", ha="right",
           fontsize=8.5, color=MUT)
    buoc = 3 if cot == "gio" else 1          # panel giờ có 24 cột, nhãn thưa ra
    for i in x[::buoc]:
        t = g.tren.iloc[i]*100
        if not np.isnan(t):
            a.text(i, t + .4, f"{t:.1f}", ha="center", fontsize=8.5, fontweight="bold")
    a.set_xticks(x)
    a.set_xticklabels(nhan, rotation=25 if cot in ("band", "kmb", "tiet") else 0,
                      ha="right" if cot in ("band", "kmb", "tiet") else "center",
                      fontsize=9)
    a.set_xlabel(ten); a.set_ylim(-8, 15)
    a.set_ylabel("Tỷ lệ rơi ngoài khoảng (%)" if a is ax[0] else "")
    a.set_title(ten, fontweight="bold")
ax[0].legend(frameon=False, fontsize=9, loc="lower left")

fig.suptitle("MS2 — Dự đoán rơi ra ngoài khoảng ở đâu nhiều nhất\n"
             "Chuyến đắt và chuyến dài lệch nặng nhất, và lệch chủ yếu về phía "
             "VƯỢT CẬN TRÊN — giá thật cao hơn dự đoán",
             fontweight="bold", fontsize=13.5, y=1.05)
fig.tight_layout()
fig.savefig(HINH / "MS2_ra_ngoai_khoang.png")
plt.show()

# ══════════════════════════════════════════════════════════════════════════
# HINH MS3 — GAM va GBM doi ngoi o hai dau dai
# ══════════════════════════════════════════════════════════════════════════
d["chenh"] = d["sai_Hybrid (production)"] - d["sai_GAM hybrid"]   # dương = GAM tốt hơn
rng = np.random.default_rng(0)

def khoang_tin_cay(x, n=400):
    v = x.values
    m = rng.choice(v, (n, len(v)), replace=True).mean(axis=1)
    return np.percentile(m, [2.5, 97.5])

fig, ax = plt.subplots(1, 2, figsize=(15, 5.2))

for a, (cot, nhan, ten) in zip(ax, [("band", NHAN, "Band giá dự đoán"),
                                    ("kmb", KMN, "Quãng đường (km)")]):
    tb = []
    for g in nhan:
        s = d[d[cot] == g]
        lo, hi = khoang_tin_cay(s.chenh)
        tb.append((g, len(s), s.chenh.mean()*100, lo*100, hi*100))
    x = np.arange(len(tb))
    val = [r[2] for r in tb]
    mau = [GREEN if r[3] > 0 else (RED if r[4] < 0 else MUT) for r in tb]
    a.bar(x, val, color=mau, alpha=.9, width=.62)
    a.errorbar(x, val, yerr=[[r[2]-r[3] for r in tb], [r[4]-r[2] for r in tb]],
               fmt="none", ecolor=INK, capsize=4, lw=1.4)
    for i, r in enumerate(tb):
        a.text(i, r[4] + .25, f"n={r[1]:,}", ha="center", fontsize=8.5, color=MUT)
    a.axhline(0, color=INK, lw=1.2)
    a.set_xticks(x); a.set_xticklabels(nhan, rotation=25, ha="right", fontsize=9.5)
    a.set_xlabel(ten)
    a.set_ylabel("GAM tốt hơn Hybrid (điểm %)" if a is ax[0] else "")
    a.set_title(ten, fontweight="bold")

fig.suptitle("MS3 — GAM và GBM sai ở HAI CHỖ KHÁC NHAU\n"
             "Xanh = GAM tốt hơn có ý nghĩa · đỏ = GBM tốt hơn (khoảng tin cậy bootstrap 95%). "
             "GBM thắng ở giữa dải, GAM thắng ở đuôi",
             fontweight="bold", fontsize=13.5, y=1.04)
fig.tight_layout()
fig.savefig(HINH / "MS3_gam_vs_gbm.png")
plt.show()

# ── so in ra ────────────────────────────────────────────────────────────
print("\n=== MAPE theo band (6 model) ===")
b = pd.DataFrame({m: d.groupby("band", observed=True)[f"sai_{m}"].mean() for m in VE}).reindex(NHAN)
print(b.applymap(lambda v: f"{v:.2%}").to_string())
print("\n=== MAPE theo quãng đường ===")
k = pd.DataFrame({m: d.groupby("kmb", observed=True)[f"sai_{m}"].mean() for m in VE}).reindex(KMN)
print(k.applymap(lambda v: f"{v:.2%}").to_string())
print("\n=== Biên độ MAPE của Hybrid production theo từng chiều ===")
for cot, ten in [("band", "band giá"), ("kmb", "quãng đường"), ("gio", "giờ"), ("tiet", "thời tiết")]:
    g = d.groupby(cot, observed=True)["sai_Hybrid (production)"].mean()
    print(f"  {ten:14} {g.min():.2%} → {g.max():.2%}   (biên độ {(g.max()-g.min())*100:.2f} điểm)")
print("\n=== Rơi ngoài khoảng ===")
for cot, ten, nh in [("band", "band giá", NHAN), ("kmb", "quãng đường", KMN)]:
    g = d.groupby(cot, observed=True)[["tren", "duoi"]].mean().reindex(nh)
    w = (g.tren + g.duoi)
    print(f"  {ten}: tệ nhất {w.idxmax()} ({w.max():.2%}) · tốt nhất {w.idxmin()} ({w.min():.2%})")
print(f"\n→ {HINH/'MS1_sai_so_theo_chieu.png'}")
print(f"→ {HINH/'MS2_ra_ngoai_khoang.png'}")
