# SETUP — Cài đặt để chạy dự án trên máy mới

Checklist chạy từ trên xuống. Sau bước 5 là có thể mở notebook chạy được.

---

## 1. Phần mềm cần cài

| Thứ | Phiên bản | Ghi chú |
|---|---|---|
| **Python** | 3.10 – 3.12 | 3.13 chưa chắc có wheel cho lightgbm/pygam. Tải ở python.org, nhớ tick **"Add Python to PATH"** |
| **Git** | mới nhất | git-scm.com |
| **VS Code** | mới nhất | + extension **Python** và **Jupyter** |

Kiểm tra sau khi cài:
```powershell
python --version
git --version
```

---

## 2. Clone repo

```powershell
git clone https://github.com/Zilexz/research-pricing.git
cd research-pricing
```

---

## 3. Tạo virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

> Nếu PowerShell chặn script: chạy `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` một lần rồi activate lại.
> Trên Git Bash / macOS / Linux dùng: `source .venv/bin/activate`

---

## 4. Cài thư viện Python

```powershell
pip install -r requirements.txt
```

Hoặc cài tay (tương đương):

```powershell
pip install pandas numpy scipy scikit-learn lightgbm xgboost shap optuna pygam matplotlib seaborn pyarrow joblib python-docx jupyter ipykernel
```

Vai trò từng gói:

| Gói | Dùng để làm gì |
|---|---|
| `pandas`, `numpy`, `scipy` | xử lý dữ liệu, thống kê |
| `scikit-learn` | tiền xử lý, metric, model baseline |
| `lightgbm`, `xgboost` | model chính (giá cơ bản, hệ số nhân, giá trực tiếp) |
| `shap` | feature selection trong `analysis/FS_model_*.ipynb` |
| `optuna` | tune siêu tham số (`model/_archive/thu_nghiem/`) |
| `pygam` | model GAM đối chiếu (`train/04_train_gam_doi_chieu.ipynb`) |
| `matplotlib`, `seaborn` | vẽ biểu đồ trong analysis |
| `pyarrow` | đọc/ghi file `.parquet` |
| `joblib` | lưu/nạp model `.joblib` |
| `python-docx` | xuất báo cáo `.docx` trong `docs/` |
| `jupyter`, `ipykernel` | chạy notebook |

---

## 5. Dữ liệu

**Dữ liệu gốc TP.HCM đã nằm sẵn trong repo** (`TP_HCM_data/data/synthetic_data/`, ~461 MB) — clone về là có luôn, không cần copy tay. Vì vậy bước clone ở mục 2 sẽ hơi lâu.

Những thứ **không** có trong repo (quá nặng cho Git), cần copy USB nếu dùng tới:

| Thiếu | Cỡ | Cách có lại |
|---|---|---|
| `TP_HCM_data/data/hcm_train_ready.parquet` | 360 MB | chạy notebook ở bước 6 để sinh lại |
| `TP_HCM_data/model/{GAM,LightGBM,XGBoost,...}/*.joblib` | — | train lại ở bước 6, hoặc copy USB cho nhanh |
| `TP_HCM_data/model/evaluation/*.parquet` | — | chạy notebook `evaluation/` |
| `boston_data/data/` (tuần 1) | ~659 MB | copy USB, hoặc tải lại `rideshare_kaggle.csv` từ Kaggle |

---

## 6. Sinh lại file dẫn xuất (parquet / joblib)

Nếu chỉ copy được dữ liệu gốc, chạy tuần tự các notebook:

```
TP_HCM_data/model/00_chuan_bi_du_lieu.ipynb      → hcm_train_ready.parquet
TP_HCM_data/model/train/01_train_gia_co_ban.ipynb
TP_HCM_data/model/train/02_train_he_so_nhan.ipynb
TP_HCM_data/model/train/03_train_gia_truc_tiep.ipynb
TP_HCM_data/model/train/04_train_gam_doi_chieu.ipynb
TP_HCM_data/model/evaluation/...
```

Chi tiết thứ tự + phụ thuộc giữa các notebook: xem `TP_HCM_data/model/README.md`.

---

## 7. Chạy notebook

Mở VS Code tại thư mục repo → mở file `.ipynb` → chọn kernel là `.venv` vừa tạo.

Hoặc chạy Jupyter trên trình duyệt:
```powershell
jupyter notebook
```

---

## Xử lý lỗi hay gặp

| Lỗi | Cách xử lý |
|---|---|
| `FileNotFoundError: ...parquet` | Chưa làm bước 5/6 — thiếu data hoặc chưa chạy notebook `00_chuan_bi_du_lieu` |
| `ModuleNotFoundError` | Chưa activate `.venv`, hoặc VS Code đang chọn nhầm kernel |
| `pip install pygam` fail | Python 3.13 → hạ về 3.11/3.12 |
| `lightgbm` lỗi DLL trên Windows | Cài **Microsoft Visual C++ Redistributable (x64)** |
| Notebook chạy rất chậm | Bình thường với data ~460 MB; đóng bớt notebook khác cho đỡ tốn RAM |
