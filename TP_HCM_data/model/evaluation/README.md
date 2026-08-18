# `evaluation/` — Đánh giá model giá

Đọc dự đoán từ `train/`, không train lại. `00_TRINH_BAY_model_gia.ipynb` là bản tóm tắt để trình bày.

## 11 notebook

| Notebook | Nội dung | Hình |
|---|---|---|
| [`00_TRINH_BAY_model_gia.ipynb`](00_TRINH_BAY_model_gia.ipynb) | Cấu phần (ii) — Model dự đoán giá đối thủ | `MG*` |
| [`01_eval_gia_co_ban.ipynb`](01_eval_gia_co_ban.ipynb) | 01 — Đánh giá MODEL A: GIÁ CƠ BẢN | — |
| [`02_eval_he_so_nhan.ipynb`](02_eval_he_so_nhan.ipynb) | Đánh giá model HỆ SỐ NHÂN — so sánh 3 thuật toán | — |
| [`03_eval_gia_truc_tiep.ipynb`](03_eval_gia_truc_tiep.ipynb) | Đánh giá model GIÁ CUỐI (Hướng 1) — so sánh 3 thuật toán | — |
| [`04_eval_hybrid.ipynb`](04_eval_hybrid.ipynb) | 04 — Đánh giá HYBRID: giá cơ bản × hệ số nhân | — |
| [`05_test_case_chi_tiet.ipynb`](05_test_case_chi_tiet.ipynb) | Test chi tiết — 20 case: giá & hệ số nhân (thực vs dự đoán) | — |
| [`06_plot_uncertainty.ipynb`](06_plot_uncertainty.ipynb) | 06 — Biểu đồ so sánh model & đánh giá UNCERTAINTY | `U*` |
| [`07_so_sanh_model_theo_thoi_gian.ipynb`](07_so_sanh_model_theo_thoi_gian.ipynb) | 07 — So sánh model theo thời gian | `MT*` |
| [`08_truc_quan_GAM.ipynb`](08_truc_quan_GAM.ipynb) | Trực quan kết quả GAM | `GA*` |
| [`09_chan_doan_model.ipynb`](09_chan_doan_model.ipynb) | 09 — Chẩn đoán: model fail ở đâu, xếp hạng 10 chiều bằng η² | `CD*` |
| [`10_sai_so_chi_tiet.ipynb`](10_sai_so_chi_tiet.ipynb) | 10 — Sai số chi tiết theo khoảng giá · thời tiết · khung giờ | `CT*` |
