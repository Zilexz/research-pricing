# Pipeline Model — bộ TP.HCM

## Kiến trúc đã chốt (tuần 2)

```
giá cuối dự đoán  =  MODEL A (giá cơ bản)  ×  MODEL B (hệ số nhân)
```

**Vì sao tách 2 model:** giá cơ bản và hệ số nhân do 2 nhóm yếu tố hoàn toàn khác nhau quyết định
— giá cơ bản ← quãng đường + thời lượng (~92%); hệ số nhân ← cung–cầu (corr 0,80).
Đã chứng minh Hybrid thắng dự đoán trực tiếp: MAE **18.048** vs **18.834** VND.

## Thứ tự chạy

| # | File | Vai trò | Sinh ra |
|---|---|---|---|
| 0 | `00_chuan_bi_du_lieu.ipynb` | Làm sạch, chia train/val/calib/test theo tháng | `data/hcm_train_ready.parquet` |
| 1 | `train/01_train_gia_co_ban.ipynb` | **MODEL A** — giá cơ bản (3 thuật toán) | `*/gia_co_ban.joblib`, `evaluation/pred_gia_co_ban.parquet` |
| 2 | `train/02_train_he_so_nhan.ipynb` | **MODEL B** — hệ số nhân (3 thuật toán) | `*/heso.joblib`, `evaluation/pred_heso.parquet` |
| 3 | `train/03_train_gia_truc_tiep.ipynb` | Baseline đối chiếu — đoán thẳng giá cuối | `*/gia.joblib`, `evaluation/pred_gia.parquet` |
| 4 | `train/04_train_gam_doi_chieu.ipynb` | Đối chiếu GAM (dễ giải thích, có p-value) | — |
| 5 | `evaluation/01_eval_gia_co_ban.ipynb` | Đánh giá Model A | — |
| 6 | `evaluation/02_eval_he_so_nhan.ipynb` | Đánh giá Model B | — |
| 7 | `evaluation/03_eval_gia_truc_tiep.ipynb` | Đánh giá baseline Hướng 1 | — |
| 8 | `evaluation/04_eval_hybrid.ipynb` | ⭐ **Ghép A × B, so với Hướng 1** | — |
| 9 | `evaluation/05_test_case_chi_tiet.ipynb` | 20 test case thực tế | — |

**Lưu ý:**
- Bước 1–4 **độc lập nhau**, chạy thứ tự nào cũng được (mỗi file train đúng 1 model, không phụ thuộc chéo).
- Bước 5–9 chỉ đọc file `.parquet`, **không train lại** → chạy rất nhanh.
- Bước 8 cần cả 3 file parquet từ bước 1, 2, 3.
- Nên **đóng kernel** sau mỗi notebook train (mỗi kernel giữ vài GB RAM).

## Cấu hình dùng chung

`_common_train.py` — bộ feature (`B_NUM`, `M_NUM`, `D_NUM`, `CAT`), 3 thuật toán (`ALGOS`), hàm `metrics`.

| Bộ feature | Dùng cho | Ghi chú |
|---|---|---|
| `B_NUM` + `CAT` | Model A (giá cơ bản) | Dùng `latest_observed_base` (đã bỏ surge) |
| `M_NUM` + `CAT` | Model B (hệ số nhân) | Nhóm cung–cầu + hệ số nhân quan sát gần nhất |
| `D_NUM` + `CAT` | Baseline Hướng 1 | Dùng `latest_observed_price` (còn surge) |

## Kết quả tham chiếu (tuần 2)

| Model | MAE | R² | MAPE |
|---|---|---|---|
| A. Giá cơ bản | 15.032 VND | 0,656 | 14,6% |
| B. Hệ số nhân | 0,0233 | 0,961 | — (ROC-AUC 0,998) |
| **Hybrid → giá cuối** | **18.048 VND** | **0,730** | **14,74%** |
| Hướng 1 (trực tiếp) | 18.834 VND | 0,700 | 15,36% |
| Baseline persistence | 33.683 VND | — | — |

→ Hybrid vượt baseline persistence **44,1%**.

## ⚠️ Sàn nhiễu — đã xác nhận

MAE ~15.000 VND (MAPE ~14,6%) trên giá cơ bản là **giới hạn của dữ liệu**, không phải model chưa tối ưu.
Đã thử **8 hướng độc lập** (đổi thuật toán, đổi loss, thêm feature, đổi target, chuẩn hóa theo tuyến,
ném hết 49 feature, fine-tune Optuna, Neural Network) — tất cả dừng ở cùng mức.
Chi tiết: `docs/report_tuan2.md` mục 5 · Notebook: `_archive/thu_nghiem/`

**→ Hướng đi tiếp: Uncertainty Quantification (cấu phần iii)** — tập `calibration` (615.908 dòng) đã
có sẵn dành riêng cho việc này.
