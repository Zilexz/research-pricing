# Cấu trúc dự án — thư mục nào phục vụ việc gì

> Chụp ngày 17/08/2026, sau đợt dọn dẹp. Tổng **2,5 GB** · **115 notebook** · **204 hình**.

---

## Toàn cảnh

```
Pricing_Reseach_Vin AI/                        2,5 GB
├── TP_HCM_data/           1.743 MB   ← ĐANG LÀM. Toàn bộ công việc tuần 2–5
├── boston_data/             738 MB   ← Tuần 1. Bộ dữ liệu cũ, để đối chiếu
├── tai_lieu_tham_khao/      5,3 MB   ← Tài liệu người khác gửi: paper, báo cáo bạn cùng team
├── setup_may_moi/            27 KB   ← Ghi chú cài máy mới
├── README.md · SETUP.md · requirements.txt
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

### Ba file ở gốc

Chỉ giữ lại thứ cần mở đầu tiên. Mọi tài liệu làm việc khác đã gom vào `ke_hoach/`.

| File | Nội dung |
|---|---|
| **`THANH_PHAM_4_TUAN.md/.docx`** | ⭐ **Đọc trước** — đang có gì, nằm ở đâu, mở thế nào, kịch bản demo |
| `CAU_TRUC_DU_AN.md` | Chính file này |

### `ke_hoach/` — 72 KB · tài liệu làm việc

| File | Nội dung |
|---|---|
| `VIEC_TUAN_5.md` | ⭐ Việc tuần này, bóc từ feedback mentor tuần 4 |
| `VIEC_TUAN_4.md` | Việc tuần 4 *(lưu lại để đối chiếu)* |
| `VIEC_CAN_LAM.md` | Danh sách việc tồn |
| `PHAN_TICH_FEEDBACK_MENTOR.md` | Mổ xẻ từng đề xuất của mentor |
| `BIEN_BAN_CHAY_LAI.md` | Nhật ký chạy lại 59 notebook để kiểm tính tái lập |

### `analysis/` — 23 notebook · 6,8 MB · **cấu phần (i)**

Phân tích khám phá: yếu tố nào ảnh hưởng tới giá và ảnh hưởng bao nhiêu.

| Nhóm | Nội dung |
|---|---|
| `00a`–`00c` | Hiểu dữ liệu: từ điển 70 trường · thống kê mô tả · so TP.HCM vs Boston |
| `01`–`13` | Từng yếu tố: vị trí · thời gian · thời tiết · tắc đường · tốc độ · tuyến · surge · thời lượng |
| `14_ceteris_paribus` | **Đo tác động có kiểm soát** |
| `15`–`17` | Chọn feature cho ba model |
| `90` | Tiện ích sinh hình cho báo cáo tuần 2 |

### `model/` — 60 notebook · 689 MB · **cấu phần (ii) và (iii)**

| Thư mục | Dung lượng | Việc |
|---|---:|---|
| `train/` | 498 KB | 7 notebook huấn luyện — giá cơ bản · hệ số nhân · giá trực tiếp · GAM · quantile · sinh dữ liệu UQ |
| `evaluation/` | **438,5 MB** | 11 notebook đánh giá + **11 file parquet dự đoán** (chỗ chiếm dung lượng) |
| `uncertainty/` | 11,3 MB | 9 notebook — ba phương pháp UQ, so sánh, phân rã, thu hẹp khoảng |
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

### `tuan_4/` — 8 notebook · 2,7 MB

Tổng hợp tuần 4: ba kịch bản uncertainty · improve hay giảm bất định · ceteris paribus và
causality · cấu thành giá · đường phản ứng · encode causality. Kèm `TUAN4_DA_LAM.ipynb` là sổ rà
soát có cell kiểm tự động.

### `tuan_5/` — 6 notebook · 3,6 MB

Giảm sai số ở nhóm chuyến dài và giá cao. `00` là bảng nộp mentor, `01`–`05` là từng việc. Kết quả
đã chạy nằm trong `tuan_5/ket_qua/`. Xem `tuan_5/README.md` để biết thứ tự chạy.

### `data/` — 819,5 MB · dữ liệu thô

| | Dung lượng | |
|---|---:|---|
| `hcm_train_ready.parquet` | 368,6 MB | Dữ liệu đã làm sạch, 6.897.051 dòng — **mọi notebook đọc từ đây** |
| `synthetic_data/` | 459,5 MB | 267 file `.csv.gz` gốc mentor gửi, chia theo 3 hex |

### `docs/` — 38 MB · tài liệu

| | Nội dung |
|---|---|
| **`TECH_DOC.md/.docx`** | ⭐ **Tài liệu kỹ thuật** — bài toán, dữ liệu, kiến trúc, đánh giá, vận hành |
| **`RESEARCH_PAPER.md/.docx`** | ⭐ **Research paper** — đóng gói kết quả đã hoàn thiện |
| `bao_cao_tuan/` | Báo cáo theo tuần: tuần 2 · tuần 3 · tuần 4 · uncertainty |
| `cong_cu/` | `md_sang_docx.py` + `latex_sang_chu.py` — chuyển Markdown sang Word, dịch cả LaTeX |
| `hinh_anh/` | **204 hình** — 25,9 MB, dùng chung cho mọi tài liệu |

Xuất Word: `python cong_cu/md_sang_docx.py <file.md>` — chạy từ trong `docs/`. Script tự tìm
`hinh_anh/` kể cả khi file `.md` nằm trong thư mục con.

### `demo/` — 6,1 MB · bản demo trình bày

| File | |
|---|---|
| `index.html` | App mô phỏng trên bản đồ thật, nháy đúp là chạy |
| `du_lieu/` | 900 chuyến đại diện + 327 chuyến >300k, kèm tham số hiệu chỉnh |
| `anh_chay_thu/` | Ảnh chụp một lượt chạy thật, để đối chiếu khi nghi hiển thị sai |
| `README.md` | Kịch bản demo 5 bước và các hạn chế cần nói trước |

### `transformer/` — 2 notebook · 177 MB

Thử nghiệm kiến trúc Transformer đọc chuỗi báo giá. Kết quả hoà với Hybrid GBM.

---

## `tai_lieu_tham_khao/` — 5,3 MB

Tài liệu do người khác cung cấp, không phải sản phẩm của nhóm:

| File | Nguồn |
|---|---|
| `shokoohyar2020.pdf` | Paper học thuật về định giá gọi xe |
| `tphcm_acceptance_response_v2_0_0_explained_report.pdf` | Tài liệu mô tả bộ dữ liệu |
| `bao_cao_tuan4_uncertainty_quantification.pdf` | Báo cáo tuần 4 của bạn cùng team |
| `03_final_point_pricing_report_goc_cua_ban_cung_team.md` | Báo cáo point pricing của bạn cùng team |

## `boston_data/` — 738 MB · tuần 1

Bộ dữ liệu Boston dùng ở tuần 1 để làm quen bài toán. Giữ lại để đối chiếu, không còn phát triển
tiếp. Báo cáo tuần 1 ở `boston_data/docs/report_full.md` và `report_tuan1.docx`.

---

## Dung lượng — chỗ nào nặng

| Hạng mục | Dung lượng | Sinh lại được không |
|---|---:|---|
| `data/synthetic_data/` | 459,5 MB | **Không** — dữ liệu gốc |
| `evaluation/*.parquet` | 438,5 MB | Có, ~25 phút |
| `data/hcm_train_ready.parquet` | 368,6 MB | Có, ~2,5 phút |
| Model `.joblib` | 202 MB | Có, ~21 phút |
| `transformer/` | 177 MB | Có |
| `docs/hinh_anh/` | 25,9 MB | Có, theo notebook sinh ra |

---

## Quy ước đặt tên

| Quy ước | Ví dụ |
|---|---|
| Số thứ tự = thứ tự chạy | `01_train_gia_co_ban` → `02_train_he_so_nhan` |
| `00_` = điểm vào / tổng quan | `00_TONG_HOP`, `00_chuan_bi_du_lieu` |
| `00_TRINH_BAY_` = bản rút gọn để trình bày | `00_TRINH_BAY_model_gia` |
| `90+` = tiện ích, không thuộc luồng chính | `90_sinh_hinh_bao_cao_tuan2` |
| `_archive/` = bản cũ, không còn dùng | |
| **Tiền tố hình = notebook sinh ra nó** | `CP*` ← `14_ceteris_paribus` |

Mỗi thư mục notebook có `README.md` liệt kê từng file.
