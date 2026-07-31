# Competitor Fare Forecasting — XanhSM/GSM Internship

Nghiên cứu dự đoán giá đối thủ cho ride-hailing, gồm 2 bộ dữ liệu:

- **`boston_data/`** — Uber & Lyft Boston (Kaggle, dữ liệu thật)
- **`TP_HCM_data/`** — synthetic quote-context sandbox TP.HCM (do công ty cung cấp)

## ⚠️ Repo này KHÔNG chứa file dữ liệu

`.gitignore` loại bỏ toàn bộ `data/`, `*.parquet`, `*.joblib` (quá nặng cho Git, tổng ~1,8GB).
Cần setup lại ở máy mới theo 1 trong 2 cách:

### Cách 1 — Copy dữ liệu thủ công (nhanh nhất)
Copy các thư mục sau từ máy cũ (qua OneDrive/USB/ổ mạng):
```
TP_HCM_data/data/synthetic_data/     (~461 MB — dữ liệu gốc)
boston_data/data/                    (~659 MB — dữ liệu gốc)
```
Sau đó chạy `TP_HCM_data/model/00_chuan_bi_du_lieu.ipynb` để tự sinh `hcm_train_ready.parquet`
và các file `.joblib`/`.parquet` khác (chạy các notebook trong `model/train/` → `model/evaluation/`).

### Cách 2 — Chỉ có dữ liệu gốc, tự sinh lại mọi thứ
Nếu chỉ copy được `TP_HCM_data/data/synthetic_data/` (dữ liệu gốc), chạy tuần tự:
```
model/00_chuan_bi_du_lieu.ipynb
model/train/01_train_gia_co_ban.ipynb
model/train/02_train_he_so_nhan.ipynb
model/train/03_train_gia_truc_tiep.ipynb
model/train/04_train_gam_doi_chieu.ipynb   (can pip install pygam)
```
Xem chi tiết thứ tự chạy + phụ thuộc ở `TP_HCM_data/model/README.md`.

## Cài đặt môi trường Python

```
pip install pandas numpy scikit-learn lightgbm xgboost pygam optuna matplotlib python-docx pyarrow
```

## Cấu trúc chính

| Thư mục | Nội dung |
|---|---|
| `TP_HCM_data/analysis/` | Phân tích key feature ↔ giá & hệ số nhân (10 notebook) |
| `TP_HCM_data/model/` | Pipeline train (00 → train/ → evaluation/), xem `model/README.md` |
| `TP_HCM_data/docs/` | Báo cáo tuần (`report_tuan2.md`/`.docx`) |
| `boston_data/` | Tương tự, cho bộ Boston (tuần 1) |
