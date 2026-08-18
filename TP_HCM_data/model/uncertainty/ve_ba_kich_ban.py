# -*- coding: utf-8 -*-
"""
Ba kịch bản uncertainty của mentor — vẽ TRÊN ĐƯỜNG GIÁ THEO THỜI GIAN.

Chạy:  py -3.11 ve_ba_kich_ban.py [YYYY-MM-DD]
Xuất:  docs/hinh_anh/TT5_ba_kich_ban_theo_thoi_gian.png
       docs/hinh_anh/TT6_coverage_ba_kich_ban.png

Vì sao cần hình này khi đã có TT4:
  TT4 trả lời câu "model mình thuộc kịch bản nào" bằng 4 cột số — đúng kiểu
  "aggregate về một vài con số" mà mentor chê ở chính comment đó. Mentor nêu ba
  kịch bản NGAY SAU khi đòi vẽ price-over-time, nên chúng phải nằm chung một hình:
  cùng một ngày, cùng đường giá thật, chỉ khác dải bất định.

  Nhìn hình sẽ thấy ngay thứ bảng số không nói được:
    · Kịch bản B (10% cao điểm) dải teo lại đúng lúc giá dựng đứng → đẹp mắt
      nhưng giá thật văng ra ngoài liên tục ở cao điểm.
    · Kịch bản C (40% cao điểm) dải phình ở cao điểm → an toàn nhưng khoảng
      rộng tới mức vô dụng đúng lúc cần định giá gắt nhất.
    · Model mình: dải rộng đều — không mù ở chỗ quan trọng, cũng không sắc hơn
      ở chỗ quan trọng.

  Coverage/độ rộng in trên mỗi panel tính trên TOÀN TẬP TEST (216k chuyến),
  không phải trên một ngày — hình để nhìn, số để tin.
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
    "font.size": 11.5, "axes.titlesize": 12.5, "axes.labelsize": 11.5,
    "xtick.labelsize": 10, "ytick.labelsize": 10, "legend.fontsize": 10.5,
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

for d in (uc, t):
    d["cao_diem"] = d.gio_vn.apply(lambda h: any(x <= h <= y for x, y in CAO_DIEM))

# Model thật: conformal chuẩn hoá, hiệu chỉnh riêng từng band giá (Mondrian)
for d in (uc, t):
    d["band"] = pd.cut(d.hybrid_pred, CAT, labels=NHAN)
uc["res"] = (uc.hybrid_pred - uc.gia_that).abs() / uc.hybrid_pred
q_band = uc.groupby("band", observed=True).res.quantile(MUC)
q_mine = t.band.map(q_band).astype(float).fillna(uc.res.quantile(MUC))

# Bốn kịch bản: mỗi cái là một hàm cho ra nửa-độ-rộng tương đối theo từng chuyến
KICH_BAN = [
    ("A · đều ±30%",                    lambda d: pd.Series(.30, index=d.index),   MUT),
    ("B · ±10% cao điểm / ±40% thường", lambda d: np.where(d.cao_diem, .10, .40),  GREEN),
    ("C · ±40% cao điểm / ±10% thường", lambda d: np.where(d.cao_diem, .40, .10),  ORANGE),
    ("MODEL CỦA MÌNH",                  lambda d: q_mine.reindex(d.index),         BLUE),
]

def do_kich_ban(ten, ham):
    """Coverage và độ rộng trên toàn tập test, tách cao điểm / giờ thường."""
    q = pd.Series(np.asarray(ham(t), dtype=float), index=t.index)
    lo, hi = t.hybrid_pred * (1 - q), t.hybrid_pred * (1 + q)
    trong = (t.gia_that >= lo) & (t.gia_that <= hi)
    cd = t.cao_diem
    # rong = NỬA độ rộng (±%) — đúng cách mentor phát biểu "uncertainty 30%"
    return dict(ten=ten, cvg=trong.mean(), rong=q.mean(),
                cvg_cd=trong[cd].mean(),  rong_cd=q[cd].mean(),
                cvg_gt=trong[~cd].mean(), rong_gt=q[~cd].mean())

TONG = [do_kich_ban(ten, ham) for ten, ham, _ in KICH_BAN]

# ── chọn ngày và gộp bucket 30 phút, khống chế quãng đường 4–6 km ─────────
t["ngay"] = t.target_timestamp.dt.date
t["mua"]  = t.weather_main.isin(MUA)
band46 = t[(t.quote_distance >= 4) & (t.quote_distance <= 6)].copy()

if len(sys.argv) > 1:
    NGAY = pd.Timestamp(sys.argv[1]).date()
else:
    ty = band46.groupby("ngay").mua.mean()
    NGAY = (ty - .5).abs().idxmin()

d = band46[band46.ngay == NGAY].copy()
d["buc"] = d.target_timestamp.dt.floor("30min")
if d.empty:
    sys.exit(f"Ngày {NGAY} không có chuyến 4–6 km.")

cot = {"that": ("gia_that", "mean"), "pred": ("hybrid_pred", "mean"),
       "mua": ("mua", "mean"), "n": ("gia_that", "size")}
for i, (ten, ham, _) in enumerate(KICH_BAN):
    q = pd.Series(np.asarray(ham(d), dtype=float), index=d.index)
    d[f"lo{i}"], d[f"hi{i}"] = d.hybrid_pred * (1 - q), d.hybrid_pred * (1 + q)
    d[f"tr{i}"] = (d.gia_that >= d[f"lo{i}"]) & (d.gia_that <= d[f"hi{i}"])
    cot |= {f"lo{i}": (f"lo{i}", "mean"), f"hi{i}": (f"hi{i}", "mean"),
            f"tr{i}": (f"tr{i}", "mean")}

g = d.groupby("buc").agg(**cot)
g = g[g.n >= 30]
if g.empty:
    sys.exit(f"Ngày {NGAY} không đủ chuyến 4–6 km để vẽ.")

T0 = pd.Timestamp(NGAY)

# ══ Hình 1 — bốn dải bất định trên cùng một đường giá ═════════════════════
fig, ax = plt.subplots(2, 2, figsize=(16.5, 9), sharex=True, sharey=True)
ax = ax.ravel()

ylo = min(g[[f"lo{i}" for i in range(4)]].min()) / 1000
yhi = max(g[[f"hi{i}" for i in range(4)]].max()) / 1000
pad = (yhi - ylo) * .06

for i, ((ten, _, mau), s) in enumerate(zip(KICH_BAN, TONG)):
    a = ax[i]
    for h1, h2 in CAO_DIEM:
        a.axvspan(T0 + pd.Timedelta(hours=h1), T0 + pd.Timedelta(hours=h2 + 1),
                  color=ORANGE, alpha=.13, lw=0, zorder=0)
    a.fill_between(g.index, g[f"lo{i}"]/1000, g[f"hi{i}"]/1000,
                   color=mau, alpha=.18, lw=0)
    a.plot(g.index, g[f"lo{i}"]/1000, color=mau, lw=.9, alpha=.6)
    a.plot(g.index, g[f"hi{i}"]/1000, color=mau, lw=.9, alpha=.6)
    a.plot(g.index, g.pred/1000, lw=2.1, color=mau, ls="--")
    a.plot(g.index, g.that/1000, lw=2.4, color=INK)

    # Chấm đỏ = bucket có COVERAGE CẤP CHUYẾN hụt cam kết. Không dùng phép thử
    # "giá trung bình rơi ngoài dải trung bình" — trung bình hoá làm biến mất
    # đúng thứ cần thấy: ở kịch bản B, cao điểm hụt tới 42% mà đường trung bình
    # vẫn nằm gọn trong dải.
    ngoai = g[g[f"tr{i}"] < MUC]
    if len(ngoai):
        a.plot(ngoai.index, ngoai.that/1000, "o", color=RED, ms=5.5, zorder=5, alpha=.9)

    a.set_title(f"{ten}\n"
                f"cao điểm ±{s['rong_cd']:.0%} → coverage {s['cvg_cd']:.1%}\n"
                f"giờ thường ±{s['rong_gt']:.0%} → coverage {s['cvg_gt']:.1%}",
                fontsize=11, fontweight="bold", color=mau if i == 3 else INK)
    if i % 2 == 0:
        a.set_ylabel("Giá chuyến 4–6 km (nghìn đ)")
    if i >= 2:
        a.set_xlabel("Giờ trong ngày (giờ VN)")
    a.set_ylim(ylo - pad, yhi + pad)

ax[0].legend(handles=[
    Line2D([], [], color=INK, lw=2.4, label="Giá thật"),
    Line2D([], [], color=MUT, lw=2.1, ls="--", label="Giá dự đoán"),
    Patch(facecolor=MUT, alpha=.18, label=f"Khoảng {MUC:.0%}"),
    Line2D([], [], color=RED, marker="o", ls="", ms=5.5, label=f"Bucket coverage <{MUC:.0%}"),
    Patch(facecolor=ORANGE, alpha=.13, label="Giờ cao điểm"),
], frameon=True, framealpha=.95, edgecolor=MUT, ncol=2, loc="lower left", fontsize=9.5)

ax[0].set_xlim(T0, T0 + pd.Timedelta(days=1))
ax[0].xaxis.set_major_locator(mdates.HourLocator(interval=3))
ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

fig.suptitle(f"TT5 — Ba kịch bản uncertainty mentor nêu, đặt lên cùng một ngày giá thật "
             f"({NGAY}, chuyến 4–6 km, gộp 30 phút)\n"
             f"Cùng một đường giá, cùng một dự đoán — chỉ khác cách phân bổ độ rộng khoảng "
             f"giữa cao điểm và giờ thường",
             fontweight="bold", fontsize=14, y=1.015)
fig.tight_layout()
fig.savefig(HINH / "TT5_ba_kich_ban_theo_thoi_gian.png")

# ══ Hình 2 — cái giá phải trả: coverage đổi lấy độ rộng ═══════════════════
fig2, ax2 = plt.subplots(1, 2, figsize=(14.5, 5.4))
x = np.arange(len(TONG)); w = .36
ten_ngan = ["A\nđều ±30%", "B\n±10% CĐ / ±40% GT", "C\n±40% CĐ / ±10% GT", "MODEL\nCỦA MÌNH"]

a = ax2[0]
a.bar(x - w/2, [s["rong_cd"]*100 for s in TONG], w, color=ORANGE, alpha=.9, label="Cao điểm")
a.bar(x + w/2, [s["rong_gt"]*100 for s in TONG], w, color=BLUE,   alpha=.9, label="Giờ thường")
for i, s in enumerate(TONG):
    a.text(i - w/2, s["rong_cd"]*100 + .8, f"±{s['rong_cd']:.0%}", ha="center", fontweight="bold")
    a.text(i + w/2, s["rong_gt"]*100 + .8, f"±{s['rong_gt']:.0%}", ha="center", fontweight="bold")
a.set_xticks(x); a.set_xticklabels(ten_ngan)
a.set_ylim(0, 46)
a.set_ylabel("Nửa độ rộng khoảng (± % so với giá dự đoán)")
a.set_title("Độ rộng — cái mình HỨA", fontweight="bold")
a.legend(frameon=False)

a = ax2[1]
a.bar(x - w/2, [s["cvg_cd"]*100 for s in TONG], w, color=ORANGE, alpha=.9, label="Cao điểm")
a.bar(x + w/2, [s["cvg_gt"]*100 for s in TONG], w, color=BLUE,   alpha=.9, label="Giờ thường")
a.axhline(MUC*100, color=RED, lw=1.8, ls="--", label=f"cam kết {MUC:.0%}")
for i, s in enumerate(TONG):
    a.text(i - w/2, s["cvg_cd"]*100 + 1.5, f"{s['cvg_cd']:.0%}", ha="center", fontweight="bold")
    a.text(i + w/2, s["cvg_gt"]*100 + 1.5, f"{s['cvg_gt']:.0%}", ha="center", fontweight="bold")
a.set_xticks(x); a.set_xticklabels(ten_ngan)
a.set_ylim(0, 108); a.set_ylabel("Coverage thực tế (%)")
a.set_title("Coverage — cái mình GIỮ ĐƯỢC", fontweight="bold")
a.legend(frameon=False, loc="lower right")

fig2.suptitle("TT6 — Kịch bản B và C hẹp hơn ở một khung giờ, nhưng trả giá bằng coverage sụp "
              "ở đúng khung đó\n(toàn tập test, lag 5 phút)",
              fontweight="bold", fontsize=13, y=1.02)
fig2.tight_layout()
fig2.savefig(HINH / "TT6_coverage_ba_kich_ban.png")

# ── số in ra để dán vào báo cáo ──────────────────────────────────────────
print(f"Ngày vẽ {NGAY} · {len(d):,} chuyến 4–6 km · {len(g)} bucket")
print(f"Toàn tập test: {len(t):,} chuyến "
      f"({t.cao_diem.sum():,} cao điểm · {(~t.cao_diem).sum():,} giờ thường)\n")
print(f"{'Kịch bản':36}{'±CĐ':>9}{'cvg CĐ':>9}{'±GT':>9}{'cvg GT':>9}"
      f"{'±TB':>9}{'cvg TB':>9}")
for s in TONG:
    print(f"{s['ten']:36}{s['rong_cd']:>8.1%}{s['cvg_cd']:>9.1%}"
          f"{s['rong_gt']:>9.1%}{s['cvg_gt']:>9.1%}"
          f"{s['rong']:>9.1%}{s['cvg']:>9.1%}")
m = TONG[3]
print(f"\nTỷ lệ độ rộng cao điểm / giờ thường của model mình: "
      f"{m['rong_cd']/m['rong_gt']:.3f}  ⇒ kịch bản A (đều)")
print(f"→ {HINH/'TT5_ba_kich_ban_theo_thoi_gian.png'}")
print(f"→ {HINH/'TT6_coverage_ba_kich_ban.png'}")
