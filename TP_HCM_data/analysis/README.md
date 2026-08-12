# `analysis/` — Phân tích khám phá

Trả lời câu **(i)** của đề bài: *yếu tố nào ảnh hưởng tới giá, ảnh hưởng bao nhiêu.*

Thứ tự đọc: `00a`–`00c` hiểu dữ liệu → `01`–`13` phân tích từng yếu tố → `14` đo tác động có kiểm soát → `15`–`17` chọn feature cho model.

## 22 notebook

| Notebook | Nội dung | Hình |
|---|---|---|
| [`00_TONG_HOP_SO_SANH.ipynb`](00_TONG_HOP_SO_SANH.ipynb) | 00 — TỔNG HỢP: Giờ & Thời tiết ảnh hưởng giá thế nào? (Boston vs TP.HCM) | — |
| [`00a_tu_dien_70_truong.ipynb`](00a_tu_dien_70_truong.ipynb) | 00a — TỪ ĐIỂN 70 TRƯỜNG DỮ LIỆU · Synthetic Quote-Context (TP.HCM, VND) | — |
| [`00b_thong_ke_mo_ta_du_lieu.ipynb`](00b_thong_ke_mo_ta_du_lieu.ipynb) | 00b — THỐNG KÊ MÔ TẢ DỮ LIỆU · Synthetic Quote-Context (VND, TP.HCM) | — |
| [`00c_key_feature_hcm_vs_boston.ipynb`](00c_key_feature_hcm_vs_boston.ipynb) | 00c — KEY FEATURE: TP.HCM so với Boston | — |
| [`01_location.ipynb`](01_location.ipynb) | 01 — VỊ TRÍ (Location) · bộ TP.HCM | — |
| [`02_time.ipynb`](02_time.ipynb) | 02 — THỜI GIAN (Time) · TP.HCM | — |
| [`03_weather.ipynb`](03_weather.ipynb) | 03 — THỜI TIẾT (Weather) · bộ TP.HCM | — |
| [`04_traffic.ipynb`](04_traffic.ipynb) | 04 — TẮC ĐƯỜNG (Traffic) · bộ TP.HCM | — |
| [`05_kmpertime.ipynb`](05_kmpertime.ipynb) | 05 — Tốc độ & Giá mỗi km · có đáng khai thác thêm cho model giá không? | — |
| [`05b_kmpertime_gia_coban.ipynb`](05b_kmpertime_gia_coban.ipynb) | 05b — Tốc độ & Giá/km trên GIÁ CƠ BẢN (trước khi nhân hệ số) | — |
| [`06_tuyen_chuanhoa.ipynb`](06_tuyen_chuanhoa.ipynb) | 06 — Giá cơ bản theo TUYẾN + KHU VỰC, đã chuẩn hoá | — |
| [`07_bien_do_surge_gia.ipynb`](07_bien_do_surge_gia.ipynb) | 07 — Biên độ dao động Surge & Giá theo giờ · Hệ số nhân giải thích bao nhiêu chênh lệch giá? | — |
| [`08_yeu_to_giai_thich_gia.ipynb`](08_yeu_to_giai_thich_gia.ipynb) | 08 — Cùng tuyến, cùng loại xe, cùng quãng đường: yếu tố nào giải thích chênh lệch GIÁ CUỐI? | — |
| [`09_yeuto_gia_co_ban.ipynb`](09_yeuto_gia_co_ban.ipynb) | 09 — Cố định quãng đường: yếu tố nào ảnh hưởng đến GIÁ CƠ BẢN? | — |
| [`10_yeuto_he_so_nhan.ipynb`](10_yeuto_he_so_nhan.ipynb) | 10 — Bộ dữ liệu giải thích được bao nhiêu % chênh lệch HỆ SỐ NHÂN? | — |
| [`11_yeuto_thoi_luong.ipynb`](11_yeuto_thoi_luong.ipynb) | 11 — Truy tận gốc: bản thân THỜI LƯỢNG ĐI có dự đoán được không? | — |
| [`12_truc_quan_gio_thoitiet.ipynb`](12_truc_quan_gio_thoitiet.ipynb) | 12 — Trực quan hóa: Thời lượng đi · Giá cơ bản · Hệ số nhân theo GIỜ và THỜI TIẾT | — |
| [`14_ceteris_paribus.ipynb`](14_ceteris_paribus.ipynb) | Giá phản ứng thế nào với từng yếu tố thị trường | `CP*` |
| [`15_chon_feature_gia_cuoi.ipynb`](15_chon_feature_gia_cuoi.ipynb) | 15 — Chọn feature cho model GIÁ CUỐI (bộ TP.HCM) | — |
| [`16_chon_feature_gia_co_ban.ipynb`](16_chon_feature_gia_co_ban.ipynb) | 16 — Chọn feature cho model GIÁ CƠ BẢN (bộ TP.HCM) | — |
| [`17_chon_feature_he_so_nhan.ipynb`](17_chon_feature_he_so_nhan.ipynb) | 17 — Chọn feature cho model HỆ SỐ NHÂN (bộ TP.HCM) | — |
| [`90_sinh_hinh_bao_cao_tuan2.ipynb`](90_sinh_hinh_bao_cao_tuan2.ipynb) | 90 — Tiện ích: sinh 14 hình cho báo cáo tuần 2 | `B*` · `F*` · `M*` · `O*` · `T*` |

> `_archive/` — 1 file bản cũ, giữ lại để đối chiếu, không còn dùng.
