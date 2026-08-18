# HƯỚNG DẪN GỘP — dựng lại dự án trên máy mới

Dự án được chia làm **hai mảnh**, vì GitHub chặn file quá 100 MB nên không thể
để tất cả vào một chỗ:

| Mảnh | Lấy ở đâu | Cỡ | Chứa gì |
|---|---|---|---|
| **A. Repo** | `git clone` từ GitHub | ~825 MB | code, notebook, tài liệu, slide, demo, **dữ liệu gốc TP.HCM và Boston** |
| **B. Zip dữ liệu dẫn xuất** | `bo_du_lieu_may_moi.zip` (USB / OneDrive) | ~1,2 GB | model đã train (`.joblib`) và dự đoán đã tính sẵn (`.parquet`) |

Gộp hai mảnh lại là chạy được ngay, **không phải train lại gì cả**.
Nếu không có mảnh B thì vẫn chạy được, nhưng phải train lại từ đầu — mất vài giờ.

---

## Bước 1 — Clone repo

```powershell
git clone --depth 1 https://github.com/Zilexz/research-pricing.git
cd research-pricing
```

`--depth 1` bỏ qua lịch sử commit, kéo nhanh hơn nhiều.

> **Mạng công ty chặn file lớn?** Repo nén lại khoảng 700 MB, nhiều mạng chặn ở
> mức 300 MB. Khi đó dùng bộ đã cắt sẵn ở
> [Releases → data-v1](https://github.com/Zilexz/research-pricing/releases/tag/data-v1),
> mỗi file dưới 300 MB. Xem cách ghép ở `SETUP.md` mục 2, cách B.
> Lưu ý `1_code.zip` trong release đó là code **cũ** (12/08), chưa có tuần 5 —
> ghép xong nhớ chạy `git pull` để lấy bản mới nhất.

## Bước 2 — Giải nén mảnh B đè lên repo

Giải nén `bo_du_lieu_may_moi.zip` vào **đúng thư mục `research-pricing`** vừa clone.

Zip giữ nguyên cây thư mục nên các file tự rơi vào đúng chỗ, không đè lên file
nào của repo. Nhớ chọn **Extract Here**, đừng để 7-Zip/WinRAR tự tạo thư mục con
theo tên file — nếu không sẽ ra `bo_du_lieu_may_moi/TP_HCM_data/...` là sai.

Bằng lệnh thì gọn hơn:

```powershell
tar -xf "D:\bo_du_lieu_may_moi.zip" -C "C:\duong\dan\research-pricing"
```

*(`tar` có sẵn trong Windows 10/11, đọc được file zip.)*

## Bước 3 — Giải nén 2 file Boston

Hai file này nằm trong repo dưới dạng `.gz` vì vượt giới hạn 100 MB của GitHub:

```powershell
cd boston_data\data
python -c "import gzip,shutil; [shutil.copyfileobj(gzip.open(f+'.gz','rb'), open(f,'wb')) for f in ['rideshare_kaggle.csv','snapshot_price_15min.csv']]"
cd ..\..
```

Bỏ qua bước này nếu không đụng tới phần Boston.

## Bước 4 — Môi trường Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Python **3.10–3.12** (3.13 chưa chắc có wheel cho `lightgbm` và `pygam`).
Chi tiết và cách xử lý lỗi hay gặp: xem `SETUP.md`.

---

## Kiểm tra đã gộp đúng chưa

Chạy đoạn này ở thư mục gốc repo. Đủ 6 dòng ✔ là xong:

```powershell
python -c @"
import os
for p, cho in [
    ('TP_HCM_data/data/synthetic_data', 'repo'),
    ('TP_HCM_data/data/hcm_train_ready.parquet', 'zip'),
    ('TP_HCM_data/model/evaluation/uq_pred_test.parquet', 'zip'),
    ('TP_HCM_data/model/XGBoost/gia.joblib', 'zip'),
    ('TP_HCM_data/docs/tai_lieu_bao_cao/slide_trinh_bay.html', 'repo'),
    ('TP_HCM_data/demo/index.html', 'repo'),
]:
    print(('OK  ' if os.path.exists(p) else 'THIEU') + f'  [{cho}]  {p}')
"@
```

Dòng nào `THIEU [zip]` là chưa giải nén mảnh B, hoặc giải nén nhầm chỗ.
Dòng nào `THIEU [repo]` là clone chưa xong.

---

## Muốn xem nhanh, không cần cài gì

Ba file này tự chứa, clone xong mở bằng trình duyệt hoặc Word là đọc được ngay,
không cần Python, không cần mạng, không cần mảnh B:

| File | Là gì |
|---|---|
| `TP_HCM_data/docs/tai_lieu_bao_cao/slide_trinh_bay.html` | 26 slide trình bày toàn bộ dự án |
| `TP_HCM_data/demo/index.html` | demo mô phỏng trên bản đồ, đủ 216.090 chuyến tập test |
| `TP_HCM_data/docs/tai_lieu_bao_cao/RESEARCH_PAPER.docx` · `TECH_DOC.docx` | báo cáo nghiên cứu và tài liệu kỹ thuật |

---

## Cây thư mục sau khi gộp

```
research-pricing/
├─ README.md · SETUP.md · HUONG_DAN_GOP.md
├─ TP_HCM_data/
│  ├─ data/          synthetic_data/ [repo]  ·  hcm_train_ready.parquet [zip]
│  ├─ model/         notebook train + evaluation [repo]  ·  *.joblib, *.parquet [zip]
│  ├─ docs/          paper, tech doc, slide, hình, báo cáo tuần [repo]
│  ├─ demo/          index.html [repo]
│  ├─ tuan_4/ tuan_5/   notebook + ket_qua [repo]
│  └─ transformer/   notebook [repo]  ·  du_lieu/mau.parquet [zip]
└─ boston_data/      data [repo, cần giải nén .gz]  ·  model/*.joblib [zip]
```
