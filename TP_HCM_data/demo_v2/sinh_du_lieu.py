# -*- coding: utf-8 -*-
"""Sinh lại dữ liệu cho demo và nhúng thẳng vào index.html.

Chạy:  python sinh_du_lieu.py            # cả tập test (mặc định)
       python sinh_du_lieu.py 30000      # lấy mẫu ngẫu nhiên 30.000 chuyến

PHẢI chạy lại mỗi khi model được train lại, nếu không demo hiển thị dự đoán cũ.

Định dạng lưu là **theo cột + từ điển** chứ không phải mảng object:
mỗi chuyến còn ~66 byte thay vì 205, tức gọn 3 lần. Trang web bung ngược
thành mảng object lúc mở nên phần còn lại của demo không phải sửa gì.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

D = Path(__file__).resolve().parent
EVAL = D.parent / "model" / "evaluation"
DATA = D.parent / "data" / "hcm_train_ready.parquet"
MUC = [0.7, 0.8, 0.9]
BAND_CANH = [0, 50e3, 100e3, 150e3, 200e3, 300e3]
BAND_TEN = ["<50k", "50-100k", "100-150k", "150-200k", "200-300k", ">300k"]

N_MAU = int(sys.argv[1]) if len(sys.argv) > 1 else 0      # 0 = lấy hết


def nap():
    ut = pd.read_parquet(EVAL / "uq_pred_test.parquet")
    ut = ut[ut.requested_lag_minutes == 5].reset_index(drop=True)

    cot = ["evaluation_month", "split", "requested_lag_minutes", "service_name",
           "pickup_location_name", "dropoff_location_name"]
    g = pd.read_parquet(DATA, columns=cot)
    thang = sorted(g.evaluation_month.unique())
    g = pd.concat([g[(g.evaluation_month == m) & (g.split == "test")] for m in thang])
    g = g.reset_index(drop=True)
    g = g[g.requested_lag_minutes == 5].reset_index(drop=True)
    assert len(g) == len(ut), f"lệch số dòng: {len(g)} vs {len(ut)}"

    d = ut.copy()
    for c in ["service_name", "pickup_location_name", "dropoff_location_name"]:
        d[c] = g[c].values
    return d


def hieu_chinh(muc):
    """Tham số q cho từng mức tin cậy × band, tính trên tập calibration."""
    uc = pd.read_parquet(EVAL / "uq_pred_calibration.parquet")
    uc = uc[uc.requested_lag_minutes == 5].copy()
    uc["res"] = (uc.hybrid_pred - uc.gia_that).abs() / uc.hybrid_pred
    uc["band"] = pd.cut(uc.hybrid_pred, BAND_CANH + [np.inf], labels=BAND_TEN)
    q_chung, q_band = {}, {}
    for m in muc:
        q_chung[str(m)] = float(uc.res.quantile(m))
        g = uc.groupby("band", observed=True).res.quantile(m).reindex(BAND_TEN)
        q_band[str(m)] = [float(x) if pd.notna(x) else q_chung[str(m)] for x in g]
    return q_chung, q_band


def dong_goi(d):
    # "Synthetic Premium Car" -> "Premium" cho gon nhan tren giao dien
    ten_xe = (d.service_name.str.replace("Synthetic ", "", regex=False)
                            .str.replace(" Car", "", regex=False))
    dv = pd.factorize(ten_xe)
    don = pd.factorize(d.pickup_location_name)
    tra = pd.factorize(d.dropoff_location_name)
    tt = pd.factorize(d.weather_main)
    # gio ton tai truoc: dung don/tra chung MOT tu dien de tiet kiem
    diem = list(dict.fromkeys(list(don[1]) + list(tra[1])))
    mi = {t: i for i, t in enumerate(diem)}
    return {
        "ten": {"xe": list(dv[1]), "diem": diem, "tt": list(tt[1])},
        # thoi diem luu bang SO PHUT ke tu epoch -> gon hon chuoi rat nhieu
        "t":    [int(x.value // 10**9 // 60) for x in d.target_timestamp],
        "gio":  d.gio_vn.astype(int).tolist(),
        "xe":   dv[0].tolist(),
        "don":  [mi[x] for x in d.pickup_location_name],
        "tra":  [mi[x] for x in d.dropoff_location_name],
        "tt":   tt[0].tolist(),
        "km":   [round(float(x), 2) for x in d.quote_distance],
        "phut": [round(float(x) / 60, 1) for x in d.quote_duration],
        "p":    [int(x) for x in d.hybrid_pred],
        "y":    [int(x) for x in d.gia_that],
        "hsp":  [round(float(x), 3) for x in d.heso_pred],
        "hsy":  [round(float(x), 3) for x in d.heso_that],
        "bp":   [int(x) for x in d.base_pred],
        "pers": [int(x) for x in d.persistence],
    }


def thay_hang(html, ten, gia_tri_json):
    """Thay `const <ten> = ...;` bằng giá trị mới, an toàn khi chạy lại nhiều lần.

    KHÔNG dùng regex kiểu `.*?;` với cờ DOTALL: sau lần chạy đầu, giá trị nằm gọn
    trên MỘT dòng và không còn dòng `};` riêng, nên mẫu cũ sẽ ăn lan sang tận khối
    code phía dưới rồi xoá mất — đã từng làm hỏng file thật.
    Ở đây quét ngoặc để tìm đúng điểm kết thúc của giá trị.
    """
    moc = f"const {ten} = "
    i = html.find(moc)
    if i < 0:
        raise SystemExit(f"Không thấy '{moc}' trong index.html")
    j = i + len(moc)
    if html[j] in "{[":                       # giá trị là object/array -> quét ngoặc
        mo, dong = html[j], {"{": "}", "[": "]"}[html[j]]
        sau, k, trong_chuoi, thoat = 1, j + 1, False, False
        while k < len(html) and sau:
            c = html[k]
            if thoat:
                thoat = False
            elif c == "\\":
                thoat = True
            elif c == '"':
                trong_chuoi = not trong_chuoi
            elif not trong_chuoi:
                if c == mo:
                    sau += 1
                elif c == dong:
                    sau -= 1
            k += 1
    else:                                     # giá trị đơn (vd null) -> tới hết dòng
        k = html.find("\n", j)
    while k < len(html) and html[k] in " ;":  # nuốt nốt dấu ';'
        k += 1
    return html[:i] + moc + gia_tri_json + ";" + html[k:]


def main():
    print("Nạp dự đoán trên tập test…")
    d = nap()
    print(f"  {len(d):,} chuyến (độ trễ 5 phút)")

    if N_MAU and N_MAU < len(d):
        d = d.sample(N_MAU, random_state=42).sort_values("target_timestamp")
        d = d.reset_index(drop=True)
        print(f"  lấy mẫu ngẫu nhiên còn {len(d):,} chuyến")

    kho = dong_goi(d)
    q_chung, q_band = hieu_chinh(MUC)
    ch = {
        "muc": MUC, "band_canh": BAND_CANH, "band_ten": BAND_TEN,
        "q_chung": q_chung, "q_band": q_band,
        "diem": {"EcoGreen Sài Gòn": [10.744613, 106.732216],
                 "SC Vivo City": [10.721699, 106.705544],
                 "Crescent Mall": [10.726606, 106.728165]},
        "n_test_goc": 864360,
        "mae": float((d.hybrid_pred - d.gia_that).abs().mean()),
        "mape": float(((d.hybrid_pred - d.gia_that).abs() / d.gia_that).mean()),
    }

    js_kho = json.dumps(kho, separators=(",", ":"), ensure_ascii=False)
    js_ch = json.dumps(ch, ensure_ascii=False)
    print(f"  dữ liệu nén: {len(js_kho)/1024/1024:.2f} MB "
          f"({len(js_kho)/len(d):.0f} byte/chuyến)")

    html = (D / "index.html").read_text(encoding="utf-8")
    html = thay_hang(html, "KHO_NEN", js_kho)
    html = thay_hang(html, "CH", js_ch)

    (D / "index.html").write_text(html, encoding="utf-8")
    print(f"\nĐã ghi index.html — {(D / 'index.html').stat().st_size/1024/1024:.2f} MB")
    print(f"MAE {ch['mae']:,.0f}đ · MAPE {ch['mape']:.2%}")


if __name__ == "__main__":
    main()
