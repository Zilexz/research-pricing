# -*- coding: utf-8 -*-
"""
Vẽ lại hình "giá theo thời gian + dải bất định" (ý 2 trong feedback mentor).

Chạy:  py -3.11 ve_chuoi_thoi_gian.py [YYYY-MM-DD]
Xuất :  docs/hinh_anh/TT0_chuoi_thoi_gian.png

Khác bản cũ ở sáu điểm — xem docs/bao_cao_uncertainty.md hoặc phần chú thích dưới:
  1. Thời tiết vẽ thành DẢI dưới trục, không phải điểm lơ lửng ở độ cao vô nghĩa.
  2. Bỏ hẳn nhóm "thời tiết chưa xác định" — thiếu dữ liệu thì không vẽ thành hạng mục.
  3. Cao điểm và mưa dùng hai kênh thị giác khác nhau, không cùng là nền mờ chồng lên nhau.
  4. Dải bất định hiệu chỉnh RIÊNG từng band giá (Mondrian) nên độ rộng có ý nghĩa.
  5. Thêm panel sai số và coverage — mentor hỏi "sai bao nhiêu ở thời điểm nhạy cảm",
     panel giá không trả lời được câu đó.
  6. Khống chế quãng đường 4–6 km để đường giá phản ánh THỜI ĐIỂM, không phải độ dài chuyến.
"""
import sys, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from pathlib import Path

BLUE, ORANGE, GREEN, RED, PURPLE, MUT = ("#0072B2", "#E69F00", "#009E73",
                                         "#D55E00", "#CC79A7", "#666666")
INK = "#222222"
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": .25,
    "savefig.dpi": 150, "savefig.bbox": "tight",
    "font.size": 11.5, "axes.titlesize": 13, "axes.labelsize": 11.5,
    "xtick.labelsize": 10.5, "ytick.labelsize": 10.5, "legend.fontsize": 10.5,
})

HERE = Path(__file__).resolve().parent
EVAL = HERE / "../evaluation"
HINH = (HERE / "../../docs/hinh_anh").resolve(); HINH.mkdir(parents=True, exist_ok=True)

MUC      = 0.90
CAO_DIEM = [(7, 9), (17, 19)]
MUA      = ["Rain", "Drizzle", "Thunderstorm"]
CAT      = [0, 50e3, 100e3, 150e3, 200e3, 300e3, np.inf]
NHAN     = ["<50k", "50–100k", "100–150k", "150–200k", "200–300k", ">300k"]

# ── dữ liệu ───────────────────────────────────────────────────────────────
uc = pd.read_parquet(EVAL / "uq_pred_calibration.parquet")
ut = pd.read_parquet(EVAL / "uq_pred_test.parquet")
uc = uc[uc.requested_lag_minutes == 5].copy()
t  = ut[ut.requested_lag_minutes == 5].copy()

# Conformal chuẩn hoá, hiệu chỉnh riêng từng band giá (Mondrian):
# mỗi band có hệ số riêng nên dải rộng đúng theo mức khó của band đó.
for d in (uc, t):
    d["band"] = pd.cut(d.hybrid_pred, CAT, labels=NHAN)
uc["res"] = (uc.hybrid_pred - uc.gia_that).abs() / uc.hybrid_pred
q_band = uc.groupby("band", observed=True).res.quantile(MUC)
q_all  = uc.res.quantile(MUC)
q = t.band.map(q_band).astype(float).fillna(q_all)

t["lo"]   = t.hybrid_pred * (1 - q)
t["hi"]   = t.hybrid_pred * (1 + q)
t["trong"] = (t.gia_that >= t.lo) & (t.gia_that <= t.hi)
t["sai"]  = (t.hybrid_pred - t.gia_that).abs() / t.gia_that
t["mua"]  = t.weather_main.isin(MUA)
t["ngay"] = t.target_timestamp.dt.date

# Khống chế quãng đường: chỉ còn dao động do thời điểm và cung–cầu
band46 = t[(t.quote_distance >= 4) & (t.quote_distance <= 6)].copy()

if len(sys.argv) > 1:
    NGAY = pd.Timestamp(sys.argv[1]).date()
else:                                    # ngày tương phản mưa/nắng rõ nhất
    ty = band46.groupby("ngay").mua.mean()
    NGAY = (ty - .5).abs().idxmin()

d = band46[band46.ngay == NGAY].copy()
d["buc"] = d.target_timestamp.dt.floor("30min")
g = d.groupby("buc").agg(that=("gia_that", "mean"), pred=("hybrid_pred", "mean"),
                         lo=("lo", "mean"), hi=("hi", "mean"),
                         cvg=("trong", "mean"), sai=("sai", "mean"),
                         mua=("mua", "mean"), n=("gia_that", "size"))
g = g[g.n >= 30]
if g.empty:
    sys.exit(f"Ngày {NGAY} không đủ chuyến 4–6 km để vẽ.")

T0 = pd.Timestamp(NGAY)
SAI_TB = t.sai.mean()

fig, ax = plt.subplots(3, 1, figsize=(14.5, 10.2), sharex=True,
                       gridspec_kw={"height_ratios": [2.5, 1, 1], "hspace": .32})

def nen_cao_diem(a):
    for h1, h2 in CAO_DIEM:
        a.axvspan(T0 + pd.Timedelta(hours=h1), T0 + pd.Timedelta(hours=h2 + 1),
                  color=ORANGE, alpha=.13, lw=0, zorder=0)

# ══ Panel 1 — giá ═════════════════════════════════════════════════════════
a = ax[0]; nen_cao_diem(a)
a.fill_between(g.index, g.lo/1000, g.hi/1000, color=BLUE, alpha=.16, lw=0)
a.plot(g.index, g.lo/1000, color=BLUE, lw=.9, alpha=.55)
a.plot(g.index, g.hi/1000, color=BLUE, lw=.9, alpha=.55)
a.plot(g.index, g.pred/1000, lw=2.4, color=BLUE, ls="--")
a.plot(g.index, g.that/1000, lw=2.6, color=INK)

ngoai = g[(g.that < g.lo) | (g.that > g.hi)]
if len(ngoai):
    a.plot(ngoai.index, ngoai.that/1000, "o", color=RED, ms=9, zorder=5)

# dải mưa nằm SÁT ĐÁY, không lơ lửng giữa hình
y0, y1 = (g.lo.min()/1000) - 14, (g.hi.max()/1000) + 8
a.set_ylim(y0, y1)
h_strip = (y1 - y0) * .035
for b_ in g.index[g.mua > .5]:
    a.add_patch(plt.Rectangle((mdates.date2num(b_), y0 + h_strip*.6),
                              30/(24*60), h_strip, color=PURPLE, alpha=.75,
                              lw=0, zorder=4))
a.axhline(y0 + h_strip*1.1, color=MUT, lw=.6, alpha=.5)
a.text(mdates.date2num(g.index[0]) - .012, y0 + h_strip*1.1, "mưa ",
       ha="right", va="center", fontsize=9.5, color=PURPLE, fontweight="bold")

a.set_ylabel("Giá chuyến 4–6 km (nghìn đ)")
a.legend(handles=[
    Line2D([], [], color=INK, lw=2.6, label="Giá thật"),
    Line2D([], [], color=BLUE, lw=2.4, ls="--", label="Giá dự đoán"),
    Patch(facecolor=BLUE, alpha=.16, label=f"Khoảng dự đoán {MUC:.0%}"),
    Line2D([], [], color=RED, marker="o", ls="", ms=8, label="Bucket rơi ngoài khoảng"),
    Patch(facecolor=ORANGE, alpha=.13, label="Giờ cao điểm"),
    Patch(facecolor=PURPLE, alpha=.75, label="Đang mưa"),
], frameon=True, framealpha=.95, edgecolor=MUT, ncol=3, loc="upper left")
a.set_title(f"Giá thật vs dự đoán ngày {NGAY} — chuyến 4–6 km, gộp 30 phút\n"
            f"khoảng {MUC:.0%} hiệu chỉnh riêng từng band giá (Mondrian)",
            fontweight="bold")

# ══ Panel 2 — sai số ══════════════════════════════════════════════════════
a = ax[1]; nen_cao_diem(a)
a.bar(g.index, g.sai*100, width=.019,
      color=[RED if v > SAI_TB*1.5 else BLUE for v in g.sai], alpha=.85)
a.axhline(SAI_TB*100, color=INK, lw=1.8, ls="--",
          label=f"TB toàn tập test {SAI_TB:.2%}")
a.set_ylim(0, g.sai.max()*100*1.35)
a.set_ylabel("Sai số tương đối (%)"); a.legend(frameon=False, loc="lower left")
a.set_title("Sai số theo từng bucket — đỏ = cao hơn 1,5 lần mức trung bình",
            fontweight="bold")

# ══ Panel 3 — coverage ════════════════════════════════════════════════════
a = ax[2]; nen_cao_diem(a)
a.bar(g.index, g.cvg*100, width=.019,
      color=[GREEN if v >= MUC else ORANGE for v in g.cvg], alpha=.85)
a.axhline(MUC*100, color=RED, lw=1.8, ls="--", label=f"danh nghĩa {MUC:.0%}")
a.set_ylim(70, 100); a.set_ylabel("Coverage (%)")
a.set_xlabel("Giờ trong ngày (giờ VN)"); a.legend(frameon=False, loc="lower left")
a.set_title("Tỷ lệ chuyến thật nằm trong khoảng — cam = hụt so với cam kết",
            fontweight="bold")
a.set_xlim(T0, T0 + pd.Timedelta(days=1))
a.xaxis.set_major_locator(mdates.HourLocator(interval=2))
a.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

fig.savefig(HINH / "TT0_chuoi_thoi_gian.png")
print(f"Ngày {NGAY} · {len(d):,} chuyến 4–6 km · {len(g)} bucket")
print(f"Độ rộng khoảng trung bình : {((g.hi-g.lo)/g.pred).mean():.1%} quanh giá dự đoán")
print(f"Sai số trong ngày         : {d.sai.mean():.2%}  (toàn tập test {SAI_TB:.2%})")
print(f"Coverage trong ngày       : {d.trong.mean():.1%}")
cd = d[d.gio_vn.apply(lambda h: any(x <= h <= y for x, y in CAO_DIEM))]
print(f"  cao điểm  sai {cd.sai.mean():.2%} · coverage {cd.trong.mean():.1%} · n={len(cd):,}")
kh = d.drop(cd.index)
print(f"  giờ thường sai {kh.sai.mean():.2%} · coverage {kh.trong.mean():.1%} · n={len(kh):,}")
mu = d[d.mua]
if len(mu):
    print(f"  đang mưa   sai {mu.sai.mean():.2%} · coverage {mu.trong.mean():.1%} · n={len(mu):,}")
print(f"→ {HINH/'TT0_chuoi_thoi_gian.png'}")
