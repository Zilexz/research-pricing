# Việc cần làm — trạng thái & thứ tự chạy

> Cập nhật: sau khi hoàn thành UQ và dọn dẹp cấu trúc.

---

## ⚠️ Việc CẦN SỬA (theo thứ tự ưu tiên)

### 1. ✅ 14 hình báo cáo không tái tạo được — ĐÃ XONG

Đã tạo **`analysis/90_sinh_hinh_bao_cao_tuan2.ipynb`** (22 cell, ~4 phút) sinh lại đủ 14 hình mà
`bao_cao_tuan2_HOAN_CHINH.md` dùng:

```
O1_r2_giaithich                      O2_phanra_phuongsai
B1_B2_distance_duration_vs_baseprice B3_B4_hour_weather_vs_baseprice
B5_cv_khong_giam                     B6_permutation_baseprice
M1_M2_imbalance_lastmult             M3_M4_hour_weather_vs_multiplier
M5_hang_so_thi_truong                F1_amplitude_gia_cuoi
F2_boston_vs_hcm                     F3_phanbo_cungdieukien
T1_thoiluong_tocdo_theo_gio          T2_6khunggio
```

**Nguồn dữ liệu:** đọc thẳng dữ liệu gốc qua `analysis/_common.py` — `load(frac=0.2)`.
Không cần `hcm_train_ready.parquet`, không cần model đã train → chạy độc lập được.

⚠️ `F2` dùng bội số Boston tính sẵn từ tuần 1 (hằng số 69,5× / 74,0× / 97,2×), không đọc lại
bộ Boston. Nếu bộ Boston đổi thì phải cập nhật tay.

**Đã chạy, số liệu khớp báo cáo:**

| Kiểm chứng | Kết quả |
|---|---|
| Phân rã phương sai (O2) | giá cơ bản 61% · hệ số nhân 31% · chồng lấn 8% |
| CV giá cơ bản khi thu hẹp dải tới 2m (B5) | 20,9% → 19,3% — **không giảm** |
| Biên độ theo giờ | giá cơ bản **4,0%** vs hệ số nhân **50%** |
| Hệ số nhân trong 1 khu + 5 phút (M5) | std còn **19,2%** của toàn bộ |

### 2. ✅ Model `.joblib` cũ bị ghi đè — ĐÃ XONG

Đã chạy lại `train/01`–`03` chiều **05/08**. Dấu thời gian giờ khớp:

| Model | `.joblib` | `pred_*.parquet` |
|---|---|---|
| Giá cơ bản | 17:17:26 | 17:17:27 |
| Hệ số nhân | 17:21:13 | 17:21:15 |
| Giá trực tiếp | 17:25:53 | 17:25:55 |

Lệch 1–2 giây ⟹ model lưu ra **chính là** model sinh dự đoán. Trước đó lệch cả ngày
(joblib 30/07 17:30 vs pred 29/07 11:22).

### 3. ✅ Thiếu `pred_gia_co_ban.parquet` — ĐÃ XONG

Đã có trong `evaluation/` (24,7 MB, 05/08 17:17). Không cần lấy tạm từ `_archive/` nữa.

---

## 🔴 Việc CẦN LÀM tiếp: cập nhật báo cáo

`bao_cao_tuan2_HOAN_CHINH.md` dừng ở **03/08**, tức **trước** toàn bộ công việc 04/08–06/08.
Nó chỉ dùng **18/52 hình**. 34 hình chưa vào báo cáo:

| Nhóm | Số hình | Nội dung thiếu |
|---|---|---|
| `UQ1`–`UQ4` | 4 | Conformal · QR · CQR — **cấu phần (iii) của đề bài** |
| `AC1`–`AC7` | 7 | Acceptance model — mentor yêu cầu thêm |
| `MT1`–`MT5` | 5 | 5 hình theo góp ý vẽ biểu đồ của mentor |
| `PL1`, `PL2` | 2 | Bác bỏ hướng pseudo-label |
| `D1`,`D2`,`E1`,`E2` | 4 | Mô phỏng đầu cuối |
| `A1`–`A5`, `V1`–`V7` | 12 | Bản cũ của acceptance, phần lớn đã bị `AC*` thay thế → cân nhắc xoá |

⚠️ Repo **không có script build `.docx`** — file `bao_cao_tuan2_HOAN_CHINH.docx` (03/08) hiện
không tái tạo được, cùng loại vấn đề với 14 hình đã sửa ở mục 1.

---

## Thứ tự chạy lại từ đầu

| # | File | Thời gian | Sinh ra |
|---|---|---|---|
| 1 | `model/00_chuan_bi_du_lieu.ipynb` | ~5 ph | `data/hcm_train_ready.parquet` |
| 2 | `model/train/01_train_gia_co_ban.ipynb` | ~3 ph | Model A + `pred_gia_co_ban.parquet` |
| 3 | `model/train/02_train_he_so_nhan.ipynb` | ~3 ph | Model B + `pred_heso.parquet` |
| 4 | `model/train/03_train_gia_truc_tiep.ipynb` | ~3 ph | Baseline + `pred_gia.parquet` |
| 5 | `model/train/04_train_gam_doi_chieu.ipynb` | ~25 ph | GAM 3 nhánh + `GAM/*.joblib` + `pred_gam.parquet` |
| 6 | `model/evaluation/04_eval_hybrid.ipynb` | ~1 ph | Ghép A × B |
| 7 | `model/evaluation/06_plot_uncertainty.ipynb` | ~1 ph | `U1`–`U4` |
| 8 | `model/evaluation/07_so_sanh_model_theo_thoi_gian.ipynb` | ~2 ph | `MT1`–`MT5` |
| 9 | `model/uncertainty/01_conformal_chuan_hoa.ipynb` | ~1 ph | `UQ1`, `UQ2` |
| 10 | `model/uncertainty/04_SO_SANH.ipynb` | ~1 ph | `UQ3`, `UQ4` |
| 11 | `model/acceptance/00_TONG_HOP_chay_1_the.ipynb` | ~1 ph | `AC1`–`AC7` |
| 12 | `analysis/90_sinh_hinh_bao_cao_tuan2.ipynb` | ~4 ph | 14 hình `O`/`B`/`M`/`F`/`T` |
| 13 | `model/acceptance/07_chiphi_bien_va_uncertainty.ipynb` | ~2 ph | `UA1`–`UA5` + `bang_tra_cuu_gia.csv` |
| 14 | `model/acceptance/08_MNL_ba_lua_chon.ipynb` | ~20 gy | `MNL1`–`MNL3` |
| 15 | `model/acceptance/09_doi_chieu_literature.ipynb` | ~10 gy | `LIT1` |
| 16 | `model/99_TONG_QUAN_TOAN_DU_AN.ipynb` | ~1 ph | `TQ1`, `KT1`, `KT2` — tổng quan + kiến trúc |
| 17 | `model/uncertainty/00_TONG_QUAN.ipynb` | ~2 ph | `VQ1`–`VQ7` — trực quan cơ chế UQ |
| 18 | `model/uncertainty/01_conformal_chuan_hoa.ipynb` | ~3 ph | `MD1`–`MD6` — Mondrian theo quãng đường |
| 19 | `model/evaluation/08_truc_quan_GAM.ipynb` | ~3 ph | `GA1`–`GA6` — trực quan kết quả GAM |

**Điều kiện tiên quyết cho từng bước:**

| Bước | Cần có trước |
|---|---|
| 7, 8 | `evaluation/pred_hybrid_cu.parquet` + `evaluation/pred_gam.parquet` |
| 9, 10 | `evaluation/uq_pred_{calibration,test}.parquet` và `qr_pred_*.parquet` |
| 11 | Chỉ cần `hcm_train_ready.parquet` (Phần 8 cần thêm file archive) |
| 12 | Không cần gì — đọc thẳng dữ liệu gốc, chạy được bất cứ lúc nào |
| 13 | `evaluation/qr_pred_{calibration,test}.parquet` |
| 14, 15 | Không cần gì — thuần tính toán |
| 16 | Các file `evaluation/pred_*.parquet` (bước 2–6) |
| 17, 18 | `evaluation/uq_pred_*` + `qr_pred_*` |
| 19 | `GAM/*.joblib` + `pred_gam.parquet` (bước 5) |

⚠️ **Bước 9, 10 cần script train riêng** (hiện nằm ở thư mục tạm) để sinh dự đoán trên
`calibration` — các file `pred_*.parquet` gốc chỉ có `split=test`.

---

## Trạng thái 3 cấu phần đề bài

| Cấu phần | Trạng thái | Kết quả chính |
|---|---|---|
| **(i) Study relation** | ✅ Xong | Giờ ảnh hưởng gấp 74× Boston; mưa +7,3% |
| **(ii) Build model** | ✅ Xong | Hybrid HistGB MAE **18.048đ** · 4 thuật toán chênh 1,1% |
| **(iii) Uncertainty** | ✅ Xong | Conformal chuẩn hoá **±30%**, coverage **~89,6%** |
| Acceptance (mentor yêu cầu thêm) | ✅ Xong | Tăng giá +10% → chấp nhận **giảm ~19%** |

---

## Việc còn mở

| Việc | Chặn bởi |
|---|---|
| **GAM trên transformed feature space** | Chưa làm — mentor gợi ý trao đổi với anh Khoa |
| ~~Nối khoảng UQ vào acceptance model~~ | ✅ xong — `acceptance/07` |
| ~~Nâng acceptance lên MNL~~ | ✅ xong — `acceptance/08`, dùng `s₀` suy ngược thay vì số thật |
| Chốt `β` bằng số thật thay vì suy ngược | Cần **thị phần** + **tỷ lệ không đi** từ mentor |
| Tự kiểm chứng nguồn literature ở `acceptance/09` | Số đang ghi từ trí nhớ, chưa trích từ PDF |
| Supervised acceptance | Cần dữ liệu có `outcome` |
| Viết báo cáo tuần 3 | Không chặn — 34+ hình chưa dùng |

---

## 📮 Câu hỏi gửi mentor (xếp theo giá trị)

| # | Câu hỏi | Mở khoá |
|---|---|---|
| 1 | Tỷ lệ khách **xem giá rồi không đặt** (`P₀`)? | Tham số nhạy nhất, đo trực tiếp được |
| 2 | Công thức surge có **ngưỡng nhảy bậc** không? | Regression Discontinuity → elasticity thật từ dữ liệu lịch sử |
| 3 | **Thị phần** XanhSM vs đối thủ chính? | Quy market → firm elasticity, mở khoá MNL |
| 4 | Có bộ `giá đã hiện` + `outcome` không? | Supervised acceptance |
| 5 | Xin được **`--artifact-profile full`** không? | `customer_profiles`, `quotes` (có `discount`), `market_context` |

Câu 5 đáng chú ý: README dataset cho biết bản `full` có thêm 4 bảng, trong đó `synthetic_quotes_v1`
chứa trường **discount** — đúng thứ nghi là nguyên nhân sàn nhiễu.
