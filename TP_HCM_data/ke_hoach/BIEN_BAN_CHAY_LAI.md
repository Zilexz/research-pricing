# Biên bản chạy lại toàn bộ — 10/08/2026

Chạy lại **59 notebook** theo đúng thứ tự phụ thuộc, `nbconvert --execute --inplace`,
mỗi notebook chạy với thư mục làm việc là thư mục chứa nó.

**Kết quả: 59/59 thành công, 0 lỗi, tổng 83,9 phút.**

Bỏ qua 9 notebook trong `model/_archive/` và `analysis/_archive/` (bản cũ, không còn dùng).

---

## 1. Bảng chi tiết

### Nhóm 0 — Chuẩn bị dữ liệu

| Notebook | Giây |
|---|---:|
| `model/00_chuan_bi_du_lieu` | 147,0 |

### Nhóm 1 — Train (nặng nhất, 21 phút)

| Notebook | Giây |
|---|---:|
| `train/01_train_gia_co_ban` | 274,1 |
| `train/02_train_he_so_nhan` | 262,0 |
| `train/03_train_gia_truc_tiep` | 272,1 |
| `train/04_train_gam_doi_chieu` | **812,2** |
| `train/05_GAM_transformed_feature_space` | 178,8 |
| `train/06_train_quantile_da_muc` | 306,6 |

### Nhóm 2 — Evaluation

| Notebook | Giây |
|---|---:|
| `evaluation/01_eval_gia_co_ban` | 8,5 |
| `evaluation/02_eval_he_so_nhan` | 9,7 |
| `evaluation/03_eval_gia_truc_tiep` | 9,0 |
| `evaluation/04_eval_hybrid` | 13,8 |
| `evaluation/05_test_case_chi_tiet` | 173,7 |
| `evaluation/06_plot_uncertainty` | 11,3 |
| `evaluation/07_so_sanh_model_theo_thoi_gian` | 11,1 |
| `evaluation/08_truc_quan_GAM` | 16,5 |
| `evaluation/00_TRINH_BAY_model_gia` | 9,6 |

### Nhóm 3 — Uncertainty

> ⚠️ Tên dưới đây là tên **tại thời điểm chạy**. Thư mục `uncertainty/` đã được sắp xếp lại
> sau đó — xem mục 7.

| Notebook | Giây |
|---|---:|
| `uncertainty/01_conformal_prediction` | 6,9 |
| `uncertainty/02_quantile_va_CQR` | 6,9 |
| `uncertainty/03_truc_quan_UQ` | 10,4 |
| `uncertainty/04_UQ_theo_quang_duong` | 11,1 |
| `uncertainty/05_chon_muc_tin_cay` | 9,9 |
| `uncertainty/06_ba_pp_ba_muc` | 7,3 |
| `uncertainty/07_uq_theo_band_gia` | 9,8 |
| `uncertainty/08_uq_theo_thoi_gian` | 9,2 |
| `uncertainty/00_TRINH_BAY_so_sanh_3_pp` | 9,2 |

### Nhóm 4 — Acceptance

| Notebook | Giây |
|---|---:|
| `acceptance/01_acceptance_rate_model` | 7,6 |
| `acceptance/02_hai_model_theo_moc_gia` | 7,8 |
| `acceptance/03_truc_quan_chi_tiet` | 11,6 |
| `acceptance/04_mo_phong_dau_cuoi` | 10,0 |
| `acceptance/05_thu_nghiem_pseudo_label` | 12,1 |
| `acceptance/06_cung_quangduong_xuhuong` | 11,4 |
| `acceptance/07_chiphi_bien_va_uncertainty` | 275,4 |
| `acceptance/08_MNL_ba_lua_chon` | 6,7 |
| `acceptance/09_doi_chieu_literature` | 5,1 |
| `acceptance/10_doi_chieu_nhanh_robustness` | 7,7 |
| `acceptance/00_TONG_HOP_chay_1_the` | 11,8 |
| `acceptance/00_TRINH_BAY_acceptance` | 8,5 |

### Nhóm 5 — Analysis

| Notebook | Giây |
|---|---:|
| `analysis/00a_tu_dien_70_truong` | 94,8 |
| `analysis/00b_thong_ke_mo_ta_du_lieu` | 87,1 |
| `analysis/00c_key_feature_hcm_vs_boston` | 97,9 |
| `analysis/00_TONG_HOP_SO_SANH` | 86,2 |
| `analysis/01_location` | 69,6 |
| `analysis/02_time` | 77,3 |
| `analysis/03_weather` | 72,3 |
| `analysis/04_traffic` | 71,7 |
| `analysis/05_kmpertime` | 98,3 |
| `analysis/05b_kmpertime_gia_coban` | 79,3 |
| `analysis/06_tuyen_chuanhoa` | 73,7 |
| `analysis/07_bien_do_surge_gia` | 71,7 |
| `analysis/08_yeu_to_giai_thich_gia` | 77,5 |
| `analysis/09_yeuto_gia_co_ban` | 73,0 |
| `analysis/10_yeuto_he_so_nhan` | 245,7 |
| `analysis/11_yeuto_thoi_luong` | 71,6 |
| `analysis/12_truc_quan_gio_thoitiet` | 72,8 |
| `analysis/15_chon_feature_gia_cuoi` | 164,6 |
| `analysis/16_chon_feature_gia_co_ban` | 147,6 |
| `analysis/17_chon_feature_he_so_nhan` | 140,7 |
| `analysis/90_sinh_hinh_bao_cao_tuan2` | 76,9 |

### Nhóm 6 — Tổng quan

| Notebook | Giây |
|---|---:|
| `model/99_TONG_QUAN_TOAN_DU_AN` | 7,7 |

---

## 2. Hình — 120/121 được vẽ lại

Một hình **không** được vẽ lại: `SS3_chuyen_that.png`. Đây là bản SS3 cũ, đã thay bằng
`SS3_ty_le.png`; không tài liệu nào tham chiếu tới nó nữa → **xoá được**.

---

## 3. Số liệu vẫn khớp báo cáo tuần 3

| Chỉ số | Tính lại | Báo cáo |
|---|---:|---:|
| MAE hybrid | 18.045đ | 18.045đ |
| MAPE hybrid | 14,74% | 14,74% |
| R² hybrid | 0,7299 | 0,7299 |
| q 90% | 30,11% | 30,11% |
| Coverage 90% | 89,58% | 89,58% |
| Độ rộng TB 90% | 72.686đ | 72.686đ |
| n test | 864.360 | 864.360 |
| n calibration | 615.908 | 615.908 |

---

## 4. 7 file KHÔNG được sinh lại — *(đã xử lý, xem mục 5)*

Toàn bộ model đã train lại hôm nay, nhưng 7 file dưới đây vẫn là bản **05/08** vì
**không notebook nào sinh ra chúng** (được tạo bằng script rời, đã mất):

| File | Ngày | Ai dùng |
|---|---|---|
| `evaluation/uq_pred_test.parquet` | 05-08 14:34 | **Toàn bộ 9 notebook UQ** |
| `evaluation/uq_pred_calibration.parquet` | 05-08 14:34 | **Toàn bộ 9 notebook UQ** |
| `evaluation/qr_pred_test.parquet` | 05-08 15:37 | UQ 02 (CQR) |
| `evaluation/qr_pred_calibration.parquet` | 05-08 15:37 | UQ 02 (CQR) |
| `HistGB/uq_gia_co_ban.joblib` | 05-08 14:34 | sinh uq_pred_* |
| `HistGB/uq_heso.joblib` | 05-08 14:34 | sinh uq_pred_* |
| `QuantileLGBM/quantile_models.joblib` | 05-08 15:37 | sinh qr_pred_* |

**Nghĩa là:** bảng ở mục 3 khớp 100% là *khớp hiển nhiên* — nó đọc từ chính file cũ đó,
không phải bằng chứng model train lại cho ra cùng kết quả.

### Đã kiểm chứng riêng — kết luận: **không sao**

So hybrid từ model **vừa train lại hôm nay** với hybrid trong file cũ, trên cùng 864.360 hàng
(đã assert `gia_that` trùng khớp từng hàng):

| | Model cũ (file 05/08) | Train lại hôm nay | Chênh |
|---|---:|---:|---:|
| MAE | 18.045đ | 18.066đ | **+21đ (+0,12%)** |
| MAPE | 14,74% | 14,76% | +0,013 điểm |
| R² | 0,7299 | 0,7289 | −0,0010 |
| Coverage 90% | 89,58% | 89,54% | −0,04 điểm |

Tương quan hai chuỗi dự đoán **0,998984**; sai lệch tuyệt đối trung bình 1.145đ.

→ **Mọi con số trong báo cáo tuần 3 vẫn đúng.** Chênh lệch chỉ là nhiễu do random seed của
XGBoost, không phải sai sót.

---

## 5. ✅ Đã vá — `train/07_sinh_du_lieu_UQ.ipynb`

### Công thức dựng lại được

Đọc ngược từ `HistGB/uq_gia_co_ban.joblib` và `HistGB/uq_heso.joblib`:

| | Model A — giá cơ bản | Model B — hệ số nhân |
|---|---|---|
| Thuật toán | HistGB, cấu hình `ALGOS["HistGB"]` | HistGB, cùng cấu hình |
| Feature | `CAT + B_NUM` (14) | `CAT + M_NUM` (11) |
| Target | `base_price`, **log** | `target_shown_multiplier`, **thô** |
| Train trên | `split == "train"`, riêng từng tháng | như trên |
| Dự đoán trên | `calibration` **và** `test` | như trên |

Khác `train/01` + `train/02` đúng một chỗ: hai notebook đó chỉ dự đoán trên `test`, nên không
sinh được tập `calibration` mà conformal bắt buộc phải có. `calibration` là split có sẵn trong
`hcm_train_ready.parquet` (615.908 dòng), không phải cắt ra từ train.

**Kiểm chứng công thức:** nạp `uq_gia_co_ban.joblib` cũ dự đoán lại tập test cho ra đúng cột
`base_pred` trong file cũ, lệch tối đa **1đ** trên thang ~87.000đ.

### Đối chiếu trước khi ghi đè

| Mức | q cũ | q mới | Chênh q | Coverage cũ | Coverage mới | Rộng cũ | Rộng mới |
|---|---:|---:|---:|---:|---:|---:|---:|
| 70% | 18,77% | 18,78% | +0,008 điểm | 69,68% | 69,73% | 45.306đ | 45.320đ |
| 80% | 23,25% | 23,25% | −0,004 điểm | 79,62% | 79,60% | 56.134đ | 56.118đ |
| 90% | 30,11% | 30,09% | −0,019 điểm | 89,58% | 89,55% | 72.686đ | 72.630đ |

MAE test 18.045 → 18.048đ (+0,02%), tương quan hai chuỗi dự đoán **0,999582**.
Lệch `q` lớn nhất 0,019 điểm — dưới ngưỡng 0,5 điểm mà notebook tự đặt.

### Bảy artifact nay đều có nguồn

| Artifact | Sinh bởi |
|---|---|
| `HistGB/uq_gia_co_ban.joblib` | `train/07` mục 1 |
| `HistGB/uq_heso.joblib` | `train/07` mục 1 |
| `evaluation/uq_pred_calibration.parquet` | `train/07` mục 2+4 |
| `evaluation/uq_pred_test.parquet` | `train/07` mục 2+4 |
| `evaluation/qr_pred_calibration.parquet` | `train/07` mục 5 |
| `evaluation/qr_pred_test.parquet` | `train/07` mục 5 |
| `QuantileLGBM/quantile_models.joblib` | `train/07` mục 5 |

`qr_pred_*` và `quantile_models.joblib` không train lại — chúng là **tập con 3 phân vị**
(`q05`/`q50`/`q95`) của bộ 7 phân vị mà `train/06` đã train. Coverage q05–q95 lệch bản cũ
0,09 điểm, tương quan 0,9985+.

Đã sửa lại phần markdown đã cũ trong `train/06` (chỗ nói bộ quantile do "script ngoài repo"
sinh ra, và chỗ mô tả mục 3 là kiểm chứng độc lập — thực ra nay là kiểm tra ổn định giữa hai
lần chạy).

### Chạy lại hạ nguồn

18 notebook đọc `uq_pred_*` / `qr_pred_*` đã chạy lại — **18/18 OK, 11,0 phút**:
`evaluation/04·05·06·07·00_TRINH_BAY` · `uncertainty/01–08 + 00_TRINH_BAY` ·
`acceptance/07·00_TONG_HOP·00_TRINH_BAY` · `99_TONG_QUAN`.

### Thứ tự chạy chuẩn từ nay

```
model/00_chuan_bi_du_lieu
  └─ train/01 · 02 · 03 · 04 · 05
  └─ train/06_train_quantile_da_muc      (21 model quantile)
       └─ train/07_sinh_du_lieu_UQ       ← MỚI
            └─ uncertainty/01 … 08
            └─ evaluation/04 · 06 · 07
```

---

## 6. ⚠️ Số trong báo cáo tuần 3 nay lệch ở hàng thập phân

Vì file UQ đã được sinh lại bằng model train mới, các con số này **không còn khớp tuyệt đối**:

| Chỉ số | Báo cáo tuần 3 | Hiện tại |
|---|---:|---:|
| MAE hybrid | 18.045đ | 18.048đ |
| R² hybrid | 0,7299 | 0,7297 |
| q 70% / 80% / 90% | 18,77% · 23,25% · 30,11% | 18,78% · 23,25% · **30,09%** |
| Coverage 70/80/90% | 69,68% · 79,62% · 89,58% | 69,73% · 79,60% · **89,55%** |
| Độ rộng 70/80/90% | 45.306 · 56.134 · 72.686đ | 45.320 · 56.118 · **72.630đ** |
| MAPE hybrid | 14,74% | 14,74% (không đổi) |

**Chưa sửa** `docs/bao_cao_tuan3.md` và `.docx` — báo cáo đã nộp, và mức lệch này nằm trong
nhiễu ngẫu nhiên của gradient boosting, sẽ tái diễn ở mọi lần train lại. Sửa cứng từng chữ số
chỉ tạo công việc lặp.

Các tài liệu **đang dùng** thì nên nói theo khoảng thay vì chữ số cứng, ví dụ
`±30%` thay cho `±30,11%`. Ba file có số cứng: `docs/tong_hop_theo_kien_truc.md`,
`model/acceptance/KIEN_TRUC_CHOT.md`, `VIEC_CAN_LAM.md`.

---

## 7. Sắp xếp lại thư mục `uncertainty/` — 10/08/2026

10 notebook được gộp thành **6, tổ chức theo phương pháp**. Code cell tái sử dụng nguyên bản
nên **42 hình cũ sinh ra y hệt**, không tham chiếu nào bị hỏng. Thêm 8 hình mới.

| Notebook mới | Gộp từ | Hình |
|---|---|---|
| `00_TONG_QUAN` | `03_truc_quan_UQ` | `VQ1`–`VQ7` |
| `01_conformal_chuan_hoa` | `01` + `05` + `04` + `07` | `UQ1` `UQ2` · `TC1`–`TC4` · `MD1`–`MD6` · `BG1`–`BG4` |
| `02_quantile_regression` | **viết mới** | `QR1`–`QR4` |
| `03_CQR` | **viết mới** | `CQ1`–`CQ4` |
| `04_SO_SANH` | `02` + `06` + `09` + `00_TRINH_BAY` | `UQ3` `UQ4` · `PM1`–`PM4` · `BM1`–`BM3` · `SS1`–`SS5` |
| `05_PHAN_RA_theo_thoi_gian` | `08` | `TT1`–`TT4` |

10 file cũ chuyển vào `model/uncertainty/_archive/`.

**Vì sao trước đây thiếu:** QR và CQR chưa từng có notebook riêng — chúng chỉ xuất hiện xen kẽ
trong notebook so sánh. Nay mỗi phương pháp có một notebook đi từ cơ chế → dựng khoảng → ba mức
tin cậy → phân rã theo band/giờ/quãng đường/thời tiết → điểm mạnh yếu.
