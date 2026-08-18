# -*- coding: utf-8 -*-
"""Trực quan hoá khoảng bất định — theo mức giá, khung giờ và thời tiết.

Chạy:  py -3.11 ve_uq_truc_quan.py
Xuất:  docs/hinh_anh/PR1_khoang_theo_muc_gia.png
       docs/hinh_anh/PR2_uq_theo_boi_canh.png

Vì sao cần: bảng số trả lời được "coverage bao nhiêu" nhưng không cho thấy
**một khoảng ±30% trông như thế nào** ở chuyến 50k so với chuyến 300k — đúng
điều mentor nêu (*"range 280k–320k cho 1 cuốc 300k khác nhiều so với range
30–70k cho 1 cuốc 50k"*).
"""
import warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
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
EVAL = HERE / "../model/evaluation"
HINH = (HERE / "../docs/hinh_anh").resolve()

MUC  = 0.90
CAT  = [0, 50e3, 100e3, 150e3, 200e3, 300e3, np.inf]
NHAN = ["<50k", "50–100k", "100–150k", "150–200k", "200–300k", ">300k"]
MUA  = ["Rain", "Drizzle", "Thunderstorm"]

uq_c = pd.read_parquet(EVAL / "uq_pred_calibration.parquet")
uq_t = pd.read_parquet(EVAL / "uq_pred_test.parquet")
qr_c = pd.read_parquet(EVAL / "qr_pred_calibration.parquet")
qr_t = pd.read_parquet(EVAL / "qr_pred_test.parquet")

mc, mt = uq_c.requested_lag_minutes.values == 5, uq_t.requested_lag_minutes.values == 5
uc, ut = uq_c[mc].reset_index(drop=True), uq_t[mt].reset_index(drop=True)
qc, qt = qr_c[mc].reset_index(drop=True), qr_t[mt].reset_index(drop=True)

ut["band"] = pd.cut(ut.hybrid_pred, CAT, labels=NHAN)
uc["band"] = pd.cut(uc.hybrid_pred, CAT, labels=NHAN)
uc["res"]  = (uc.hybrid_pred - uc.gia_that).abs() / uc.hybrid_pred
y, pred = ut.gia_that.values, ut.hybrid_pred.values

q_g  = uc.res.quantile(MUC)
q_bd = uc.groupby("band", observed=True).res.quantile(MUC)
q_i  = ut.band.map(q_bd).astype(float).fillna(q_g).values

def do(lo, hi):
    return dict(lo=lo, hi=hi, trong=(y >= lo) & (y <= hi),
                rong=hi - lo, rong_td=(hi - lo) / pred)

PP = {
    "Conformal toàn cục": do(pred*(1-q_g), pred*(1+q_g)),
    "Mondrian theo band": do(pred*(1-q_i), pred*(1+q_i)),
    "QR thô":             do(qt.q05.values, qt.q95.values),
}
e = np.maximum(qc.q05.values - qc.gia_that.values, qc.gia_that.values - qc.q95.values)
k = np.quantile(e, MUC)
PP["CQR"] = do(qt.q05.values - k, qt.q95.values + k)

# ══════════════════════════════════════════════════════════════════════════
# HINH PR1 — khoang bat dinh theo muc gia
# ══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(1, 3, figsize=(17.5, 5.4))

# ① Khoang THAT trong ra sao o tung band (thanh ngang tu lo den hi)
a = ax[0]
g = PP["Conformal toàn cục"]
tb = pd.DataFrame({"band": ut.band, "pred": pred, "lo": g["lo"], "hi": g["hi"]})
m = tb.groupby("band", observed=True).median().reindex(NHAN)
ypos = np.arange(len(NHAN))
for i, r in enumerate(m.itertuples()):
    a.plot([r.lo/1000, r.hi/1000], [i, i], color=BASE, lw=9, alpha=.35,
           solid_capstyle="butt")
    a.plot(r.pred/1000, i, "o", color=INK, ms=9, zorder=3)
    a.text(r.hi/1000 + 8, i, f"{r.lo/1000:.0f}–{r.hi/1000:.0f}k",
           va="center", fontsize=10.5, fontweight="bold", color=INK)
a.set_yticks(ypos); a.set_yticklabels(NHAN); a.invert_yaxis()
a.set_xlabel("Giá (nghìn đ)"); a.set_xlim(0, 480)
a.set_title("① Một khoảng ±30% trông như thế nào\nở từng mức giá", fontweight="bold")
a.legend(handles=[Line2D([], [], color=INK, marker="o", ls="", ms=8, label="Giá dự đoán"),
                  Patch(facecolor=BASE, alpha=.35, label="Khoảng 90%")],
         frameon=True, framealpha=.95, edgecolor=MUT, loc="upper right", fontsize=9.5)

# ② Coverage theo band, 4 phuong phap
a = ax[1]
w = .2
x = np.arange(len(NHAN))
for j, (ten, mau) in enumerate(zip(PP, [MUT, BASE, MULT, GREEN])):
    cv = pd.Series(PP[ten]["trong"]).groupby(ut.band, observed=True).mean().reindex(NHAN)
    a.bar(x + (j-1.5)*w, cv*100, w, color=mau, alpha=.92, label=ten)
a.axhline(MUC*100, color=RED, lw=1.8, ls="--", label="cam kết 90%")
a.set_xticks(x); a.set_xticklabels(NHAN, rotation=20, ha="right")
a.set_ylim(80, 96); a.set_ylabel("Coverage (%)")
a.set_title("② Nhóm >300k chỉ hụt ở conformal toàn cục", fontweight="bold")
a.legend(frameon=False, fontsize=9, ncol=1, loc="lower left")

# ③ Do rong tuong doi theo band, 4 phuong phap
a = ax[2]
for ten, mau, ls in zip(PP, [MUT, BASE, MULT, GREEN], ["-", "-", "--", ":"]):
    wr = pd.Series(PP[ten]["rong_td"]).groupby(ut.band, observed=True).median().reindex(NHAN)
    a.plot(x, wr*100, "o"+ls, color=mau, lw=2.4, ms=8, label=ten)
a.set_xticks(x); a.set_xticklabels(NHAN, rotation=20, ha="right")
a.set_ylabel("Độ rộng / giá dự đoán (%)")
a.set_title("③ Conformal cấp cùng độ rộng tương đối\ncho mọi mức giá", fontweight="bold")
a.legend(frameon=False, fontsize=9)

fig.suptitle("PR1 — Khoảng bất định theo mức giá\n"
             "Cùng ±30%: chuyến ~44k ra khoảng 31–58k (rộng 27k) · chuyến ~326k ra khoảng "
             "228–424k (rộng 196k)",
             fontweight="bold", fontsize=13.5, y=1.04)
fig.tight_layout()
fig.savefig(HINH / "PR1_khoang_theo_muc_gia.png")
plt.show()

# ══════════════════════════════════════════════════════════════════════════
# HINH PR2 — UQ theo khung gio va thoi tiet
# ══════════════════════════════════════════════════════════════════════════
ut["mua"] = ut.weather_main.isin(MUA)
CD = [(7, 9), (17, 19)]
ut["cao_diem"] = ut.gio_vn.apply(lambda h: any(a_ <= h <= b_ for a_, b_ in CD))

fig, ax = plt.subplots(1, 3, figsize=(17.5, 5.2))

# ① Coverage + do rong theo 24 gio
a = ax[0]
gio = sorted(ut.gio_vn.unique())
cv_h = pd.Series(PP["Conformal toàn cục"]["trong"]).groupby(ut.gio_vn).mean().reindex(gio)
cv_m = pd.Series(PP["Mondrian theo band"]["trong"]).groupby(ut.gio_vn).mean().reindex(gio)
for h1, h2 in CD:
    a.axvspan(h1, h2, color=MULT, alpha=.13, lw=0)
a.plot(gio, cv_h*100, "o-", color=MUT,  lw=2.4, ms=6, label="Conformal toàn cục")
a.plot(gio, cv_m*100, "s-", color=BASE, lw=2.4, ms=6, label="Mondrian theo band")
a.axhline(MUC*100, color=RED, lw=1.8, ls="--", label="cam kết 90%")
a.set_xticks(range(0, 24, 3)); a.set_xlabel("Giờ trong ngày (giờ VN)")
a.set_ylabel("Coverage (%)"); a.set_ylim(85, 94)
a.set_title(f"① Coverage theo giờ — biên độ chỉ "
            f"{(cv_h.max()-cv_h.min())*100:.1f} điểm", fontweight="bold")
a.legend(frameon=False, fontsize=9.5, loc="lower right")

# ② Do rong TUYET DOI theo gio (vi gia thay doi theo gio)
a = ax[1]
w_h = pd.Series(PP["Conformal toàn cục"]["rong"]).groupby(ut.gio_vn).median().reindex(gio)
p_h = pd.Series(pred).groupby(ut.gio_vn).median().reindex(gio)
for h1, h2 in CD:
    a.axvspan(h1, h2, color=MULT, alpha=.13, lw=0)
a.plot(gio, w_h/1000, "o-", color=BASE, lw=2.6, ms=6, label="Độ rộng khoảng")
a.plot(gio, p_h/1000, "s:", color=MUT,  lw=2.2, ms=5, label="Giá dự đoán (trung vị)")
a.set_xticks(range(0, 24, 3)); a.set_xlabel("Giờ trong ngày (giờ VN)")
a.set_ylabel("Nghìn đ")
a.set_title(f"② Khoảng nới theo giá, không theo giờ\n"
            f"rộng {w_h.min()/1000:.0f}k → {w_h.max()/1000:.0f}k", fontweight="bold")
a.legend(frameon=False, fontsize=9.5)

# ③ Theo thoi tiet
a = ax[2]
tt = ut.weather_main.value_counts()
tt = tt[tt >= 1000].index.tolist()
x = np.arange(len(tt)); w = .38
cv_w = pd.Series(PP["Conformal toàn cục"]["trong"]).groupby(ut.weather_main).mean()
wr_w = pd.Series(PP["Conformal toàn cục"]["rong_td"]).groupby(ut.weather_main).median()
a.bar(x - w/2, [cv_w[t]*100 for t in tt], w, color=BASE, alpha=.92, label="Coverage")
a.bar(x + w/2, [wr_w[t]*100 for t in tt], w, color=MULT, alpha=.92, label="Độ rộng tương đối")
a.axhline(MUC*100, color=RED, lw=1.8, ls="--")
for i, t in enumerate(tt):
    a.text(i - w/2, cv_w[t]*100 + .8, f"{cv_w[t]:.1%}", ha="center",
           fontsize=10, fontweight="bold")
    a.text(i + w/2, wr_w[t]*100 + .8, f"{wr_w[t]:.0%}", ha="center",
           fontsize=10, fontweight="bold")
a.set_xticks(x); a.set_xticklabels([f"{t}\n(n={tt_n:,})" for t, tt_n in
                                    zip(tt, [int((ut.weather_main == t).sum()) for t in tt])],
                                   fontsize=9.5)
a.set_ylim(0, 100); a.set_ylabel("%")
a.set_title("③ Thời tiết gần như không ảnh hưởng\ncoverage lẫn độ rộng", fontweight="bold")
a.legend(frameon=False, fontsize=9.5, loc="lower left")

fig.suptitle("PR2 — Khoảng bất định theo bối cảnh: khung giờ và thời tiết\n"
             "Khoảng nới ra theo MỨC GIÁ chứ không theo bối cảnh — "
             "coverage gần như phẳng qua 24 giờ và 4 loại thời tiết",
             fontweight="bold", fontsize=13.5, y=1.04)
fig.tight_layout()
fig.savefig(HINH / "PR2_uq_theo_boi_canh.png")
plt.show()

# ── số in ra để dán vào báo cáo ─────────────────────────────────────────
print("=== Khoảng thật theo band (trung vị) ===")
for r in m.itertuples():
    print(f"  {r.Index:>9}: {r.lo/1000:6.0f}k – {r.hi/1000:6.0f}k  "
          f"(rộng {(r.hi-r.lo)/1000:5.0f}k, giá dự đoán {r.pred/1000:.0f}k)")
print(f"\n=== Theo giờ ===")
print(f"  Coverage: {cv_h.min():.2%} ({cv_h.idxmin()}h) → {cv_h.max():.2%} ({cv_h.idxmax()}h)"
      f"  · biên độ {(cv_h.max()-cv_h.min())*100:.2f} điểm")
print(f"  Độ rộng : {w_h.min()/1000:.0f}k ({w_h.idxmin()}h) → {w_h.max()/1000:.0f}k ({w_h.idxmax()}h)")
print(f"\n=== Theo thời tiết ===")
for t in tt:
    print(f"  {t:10} n={int((ut.weather_main==t).sum()):>7,}  "
          f"coverage {cv_w[t]:.2%}  · độ rộng tương đối {wr_w[t]:.1%}")
print(f"\n→ {HINH/'PR1_khoang_theo_muc_gia.png'}")
print(f"→ {HINH/'PR2_uq_theo_boi_canh.png'}")
