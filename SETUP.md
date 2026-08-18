# SETUP — Cài đặt để chạy dự án trên máy mới

Checklist chạy từ trên xuống. Sau bước 5 là có thể mở notebook chạy được.

> Nếu bro có sẵn `bo_du_lieu_may_moi.zip` (bộ model và dự đoán đã tính sẵn)
> thì đọc **`HUONG_DAN_GOP.md`** trước — gộp theo cách đó thì khỏi phải train lại,
> tiết kiệm vài giờ. File này chỉ cần khi phải dựng lại tất cả từ đầu.

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

## 2. Lấy source + dữ liệu

### Cách A — clone (thử cách này trước)

```powershell
git clone --depth 1 https://github.com/Zilexz/research-pricing.git
cd research-pricing
```

`--depth 1` chỉ kéo bản mới nhất, nhẹ hơn nhiều so với kéo cả lịch sử.

### Cách B — tải file rời (khi mạng công ty chặn file lớn)

Repo nén lại là ~627 MB, vượt giới hạn tải 300 MB. Dùng bộ đã cắt sẵn ở
**[Releases → data-v1](https://github.com/Zilexz/research-pricing/releases/tag/data-v1)** — mỗi file dưới 300 MB:

| File | Cỡ | Nội dung |
|---|---|---|
| `1_code.zip` | 47 MB | code, notebook, báo cáo, hình — **bản 12/08, chưa có tuần 5**; ghép xong chạy `git pull` để cập nhật |
| `2_hcm_hex_a.zip` | 154 MB | data TP.HCM — hex `...574a` |
| `3_hcm_hex_b.zip` | 156 MB | data TP.HCM — hex `...574b` |
| `4_hcm_hex_c.zip` | 148 MB | data TP.HCM — hex `...759f` + `shared/` + metadata |
| `5_boston_data.zip` | 120 MB | `boston_data/data/` |

Cách dùng:

1. Repo đang để **public** nên tải được ngay, không cần đăng nhập.
2. Tải lần lượt 5 file. Hỏng file nào chỉ cần tải lại file đó.
3. Tạo một thư mục, ví dụ `research-pricing`, rồi **giải nén cả 5 file vào CÙNG thư mục đó**. Các zip không đè lên nhau, ghép lại thành đúng cây thư mục gốc.
4. Chọn *Extract Here* / bỏ tick "tạo thư mục con theo tên file" — nếu không sẽ ra `1_code/TP_HCM_data/...` là sai.

Kiểm tra sau khi giải nén — phải thấy đủ:
```powershell
dir TP_HCM_data\data\synthetic_data\*\hexes      # 3 thư mục hex
dir boston_data\data                             # 12 file
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

**Dữ liệu Boston cũng đã có trong repo** (`boston_data/data/`). Riêng 2 file vượt giới hạn 100 MB của GitHub nên được nén lại — **phải giải nén trước khi chạy phần Boston**:

```powershell
cd boston_data\data
python -c "import gzip,shutil; [shutil.copyfileobj(gzip.open(f+'.gz','rb'), open(f,'wb')) for f in ['rideshare_kaggle.csv','snapshot_price_15min.csv']]"
cd ..\..
```

> Phần TP.HCM không cần bước này. Nếu có 7-Zip thì chuột phải → Extract vào đúng thư mục cũng được.

Những thứ **không** có trong repo, cần sinh lại hoặc copy USB:

| Thiếu | Cỡ | Cách có lại |
|---|---|---|
| `TP_HCM_data/data/hcm_train_ready.parquet` | 360 MB | chạy notebook ở bước 6 để sinh lại |
| `TP_HCM_data/model/{GAM,LightGBM,XGBoost,...}/*.joblib` | — | train lại ở bước 6, hoặc copy USB cho nhanh |
| `TP_HCM_data/model/evaluation/*.parquet` | — | chạy notebook `evaluation/` |

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
