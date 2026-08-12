# Cấu trúc dự án — thư mục nào phục vụ việc gì

> Chụp ngày 11/08/2026. Tổng **2,2 GB** · **96 notebook** · **149 hình**.

---

## Toàn cảnh

```
Pricing_Reseach_Vin AI/                          2,2 GB
├── TP_HCM_data/          1.534 MB   ← ĐANG LÀM. Toàn bộ công việc tuần 2–4
├── boston_data/            678 MB   ← Tuần 1. Bộ dữ liệu cũ, để đối chiếu
└── setup_may_moi/           27 KB   ← Ghi chú cài máy mới
```

Ba cấu phần của đề bài nằm ở đâu:

| Cấu phần | Thư mục | Trạng thái |
|---|---|---|
| **(i)** Yếu tố nào ảnh hưởng giá | `TP_HCM_data/analysis/` | ✅ Xong |
| **(ii)** Model dự đoán giá đối thủ | `TP_HCM_data/model/train` + `evaluation` | ✅ Xong |
| **(iii)** Lượng hoá độ bất định | `TP_HCM_data/model/uncertainty/` | ✅ Xong |
| *(thêm)* Mức độ chấp nhận giá | `TP_HCM_data/model/acceptance/` | ⏸️ Side objective, chờ data |

---

## `TP_HCM_data/` — công việc chính

### Bốn tài liệu ở gốc

| File | Nội dung |
|---|---|
| `VIEC_TUAN_4.md` | Việc tuần 4 bóc từ feedback mentor, còn gì chưa làm |
| `TUAN4_DA_LAM.ipynb` | Sổ rà soát — đã làm gì, kiểm ở đâu, có cell kiểm tự động |
| `BIEN_BAN_CHAY_LAI.md` | Nhật ký chạy lại toàn bộ 59 notebook + vá lỗ hổng tái lập |
| `VIEC_CAN_LAM.md` | Danh sách việc tồn từ tuần trước |

### `analysis/` — 22 notebook · 6,8 MB · **cấu phần (i)**

Phân tích khám phá: yếu tố nào ảnh hưởng tới giá và ảnh hưởng bao nhiêu.

| Nhóm | Nội dung |
|---|---|
| `00a`–`00c` | Hiểu dữ liệu: từ điển 70 trường · thống kê mô tả · so TP.HCM vs Boston |
| `01`–`13` | Từng yếu tố: vị trí · thời gian · thời tiết · tắc đường · tốc độ · tuyến · surge · thời lượng |
| `14_ceteris_paribus` | **Đo tác động có kiểm soát** — trả lời ý 4 của mentor |
| `15`–`17` | Chọn feature cho ba model |
| `90` | Tiện ích sinh hình cho báo cáo tuần 2 |

### `model/` — 687 MB · **cấu phần (ii) và (iii)**

| Thư mục | Dung lượng | Việc |
|---|---:|---|
| `train/` | 498 KB | 7 notebook huấn luyện — giá cơ bản · hệ số nhân · giá trực tiếp · GAM · quantile · sinh dữ liệu UQ |
| `evaluation/` | **438,5 MB** | 9 notebook đánh giá + **11 file parquet dự đoán** (chỗ chiếm dung lượng) |
| `uncertainty/` | 11,3 MB | 7 notebook — ba phương pháp UQ, so sánh, phân rã, thu hẹp khoảng |
| `acceptance/` | 4,7 MB | 12 notebook — mô hình chấp nhận giá, đang tạm dừng |
| `_archive/` | 29,6 MB | Bản cũ không còn dùng |

**Model đã train** — 5 thư mục, tổng **202 MB**:

| Thư mục | Dung lượng | Nội dung |
|---|---:|---|
| `QuantileLGBM/` | 67,9 MB | 21 model quantile (7 phân vị × 3 tháng) + bộ 3 phân vị |
| `XGBoost/` | 63,2 MB | giá cuối · giá cơ bản · hệ số nhân |
| `LightGBM/` | 41,5 MB | như trên |
| `HistGB/` | 28,0 MB | như trên + 2 model riêng cho UQ |
| `GAM/` | 1,1 MB | 3 nhánh GAM + encoder |

### `data/` — 819,5 MB · dữ liệu thô

| | Dung lượng | |
|---|---:|---|
| `hcm_train_ready.parquet` | 368,6 MB | Dữ liệu đã làm sạch, 6.897.051 dòng — **mọi notebook đọc từ đây** |
| `synthetic_data/` | 459,5 MB | 267 file `.csv.gz` gốc mentor gửi, chia theo 3 hex |

### `docs/` — 20,6 MB · báo cáo

| File | |
|---|---|
| `bao_cao_tuan2_HOAN_CHINH.md/.docx` | Báo cáo tuần 2 |
| `bao_cao_tuan3.md/.docx` | Báo cáo tuần 3 — **đã nộp** |
| `bao_cao_uncertainty.md/.docx` | Báo cáo tổng hợp cấu phần (iii) |
| `tong_hop_theo_kien_truc.md` | Tóm tắt theo kiến trúc 5 tầng |
| `hinh_anh/` | **147 hình** — 17,6 MB |

### `demo/` — 543 KB · bản demo cho anh product

| File | |
|---|---|
| `index.html` | App mô phỏng trên bản đồ thật, nháy đúp là chạy |
| `du_lieu/chuyen.json` | 900 chuyến đại diện + 327 chuyến >300k |
| `README.md` | Kịch bản demo và các hạn chế cần nói trước |

---

## `boston_data/` — 678 MB · tuần 1

Bộ dữ liệu Uber/Lyft Boston làm trước khi mentor gửi dữ liệu TP.HCM. Giữ lại để **đối chiếu**
— nhiều kết luận tuần 2–3 có so với Boston (biên độ surge, hệ số co giãn).

| Thư mục | |
|---|---|
| `data/` (658,7 MB) | Dữ liệu Boston thô |
| `analysis/` (6,8 MB) | 11 notebook EDA |
| `model/` (7,9 MB) | 5 notebook model |
| `docs/` (687 KB) | 9 tài liệu |
| `demo/` (3,8 MB) | Demo cũ |
| `GSM_png_test/` (559 KB) | 5 ảnh chụp app GSM để tham khảo giao diện |

---

## Dung lượng — chỗ nào nặng

| Hạng mục | Dung lượng | Có xoá được không |
|---|---:|---|
| `boston_data/data/` | 658,7 MB | Được nếu không cần đối chiếu Boston nữa |
| `data/synthetic_data/` | 459,5 MB | **Không** — dữ liệu gốc, `hcm_train_ready` sinh từ đây |
| `evaluation/*.parquet` | ~438 MB | Được — sinh lại bằng `train/` nhưng mất ~25 phút |
| `data/hcm_train_ready.parquet` | 368,6 MB | Được — sinh lại bằng `00_chuan_bi_du_lieu` (~2,5 phút) |
| Model `.joblib` | 202 MB | Được — sinh lại bằng `train/` (~21 phút) |
| `model/_archive/gam_lam_mac_dinh_backup/` | 29,1 MB | **Xoá được, không ai đọc** |
| `docs/hinh_anh/` | 17,6 MB | Không — báo cáo tham chiếu |

> ⚠️ `.gitignore` loại `*.parquet` và `*.joblib`, nên **không file dữ liệu/model nào có trong
> git**. Xoá là mất hẳn, chỉ khôi phục được bằng cách chạy lại notebook.

---

## Quy ước đặt tên

| Quy ước | Ví dụ |
|---|---|
| Số thứ tự = thứ tự chạy | `01_train_gia_co_ban` → `02_train_he_so_nhan` |
| `00_` = điểm vào / tổng quan | `00_TONG_QUAN`, `00_chuan_bi_du_lieu` |
| `00_TRINH_BAY_` = bản rút gọn để trình bày | `00_TRINH_BAY_model_gia` |
| `90+` = tiện ích, không thuộc luồng chính | `90_sinh_hinh_bao_cao_tuan2` |
| `_archive/` = bản cũ, không còn dùng | |
| Tiền tố hình = notebook sinh ra nó | `CP*` ← `14_ceteris_paribus` |

Mỗi thư mục notebook có `README.md` liệt kê từng file và nội dung — sinh tự động từ tiêu đề
trong notebook nên không lệch.
