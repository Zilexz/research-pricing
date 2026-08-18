# Competitor Fare Forecasting — XanhSM/GSM Internship

Nghiên cứu dự đoán giá đối thủ cho ride-hailing, gồm 2 bộ dữ liệu:

- **`boston_data/`** — Uber & Lyft Boston (Kaggle, dữ liệu thật)
- **`TP_HCM_data/`** — synthetic quote-context sandbox TP.HCM (do công ty cung cấp)

> 📘 **Tài liệu kỹ thuật đầy đủ: [`TP_HCM_data/docs/TECH_DOC.md`](TP_HCM_data/docs/TECH_DOC.md)**
> — bài toán, dữ liệu, kiến trúc, đánh giá, uncertainty, vận hành và nhật ký đính chính.
> Đọc file đó trước nếu bạn mới tiếp cận dự án.

## ⚠️ Dữ liệu trong repo

**Có sẵn:** dữ liệu gốc TP.HCM (`TP_HCM_data/data/synthetic_data/`, ~461 MB) và dữ liệu Boston (`boston_data/data/`) — clone về là chạy được ngay.
Riêng 2 file Boston `rideshare_kaggle.csv` và `snapshot_price_15min.csv` lưu ở dạng `.gz`, phải giải nén trước — xem [SETUP.md](SETUP.md) mục 5.

**Không có** (quá nặng cho Git): `hcm_train_ready.parquet` và các `*.joblib`/`*.parquet` dẫn xuất — chạy notebook để sinh lại.

Sau khi clone, chạy tuần tự để sinh lại phần thiếu của TP.HCM:
```
model/00_chuan_bi_du_lieu.ipynb
model/train/01_train_gia_co_ban.ipynb
model/train/02_train_he_so_nhan.ipynb
model/train/03_train_gia_truc_tiep.ipynb
model/train/04_train_gam_doi_chieu.ipynb   (can pip install pygam)
```
Xem chi tiết thứ tự chạy + phụ thuộc ở `TP_HCM_data/model/README.md`.

## Cài đặt môi trường Python

Xem checklist đầy đủ cho máy mới ở **[SETUP.md](SETUP.md)**. Tóm tắt:

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Cấu trúc chính

| Thư mục | Nội dung |
|---|---|
| `TP_HCM_data/analysis/` | Phân tích key feature ↔ giá & hệ số nhân (10 notebook) |
| `TP_HCM_data/model/` | Pipeline train (00 → train/ → evaluation/), xem `model/README.md` |
| `TP_HCM_data/docs/` | **`TECH_DOC.md`** (tài liệu kỹ thuật) + báo cáo tuần |
| `TP_HCM_data/tuan_4/` | Tổng hợp tuần 4 — đọc `00_TONG_HOP.ipynb` trước |
| `boston_data/` | Tương tự, cho bộ Boston (tuần 1) |
