# `acceptance/` — Mức độ chấp nhận giá

**Side objective** theo yêu cầu mentor — không đi sâu, chờ dữ liệu bổ sung.

Dữ liệu **không có nhãn accept/reject**, nên đây là mô hình cấu trúc dựa trên lý thuyết lựa chọn rời rạc, không phải model học từ dữ liệu. Xem `KIEN_TRUC_CHOT.md` để biết chỗ nào là giả định.

## 12 notebook

| Notebook | Nội dung | Hình |
|---|---|---|
| [`00_TONG_HOP_chay_1_the.ipynb`](00_TONG_HOP_chay_1_the.ipynb) | Acceptance Rate Model — BẢN TỔNG HỢP (chạy 1 thể) | `AC*` |
| [`00_TRINH_BAY_acceptance.ipynb`](00_TRINH_BAY_acceptance.ipynb) | Acceptance Rate Model — bản v1 để review | `AT*` |
| [`01_acceptance_rate_model.ipynb`](01_acceptance_rate_model.ipynb) | Acceptance Rate Model — mô hình khả năng khách chấp nhận giá | `A*` |
| [`02_hai_model_theo_moc_gia.ipynb`](02_hai_model_theo_moc_gia.ipynb) | Hai model acceptance — trình bày theo **mốc tăng/giảm giá** | `A*` |
| [`03_truc_quan_chi_tiet.ipynb`](03_truc_quan_chi_tiet.ipynb) | Trực quan hoá chi tiết — Acceptance Rate Model | `V*` |
| [`04_mo_phong_dau_cuoi.ipynb`](04_mo_phong_dau_cuoi.ipynb) | Mô phỏng ĐẦU–CUỐI: dự đoán giá → chấp nhận → giá cuối → đối chiếu thực tế | `E*` |
| [`05_thu_nghiem_pseudo_label.ipynb`](05_thu_nghiem_pseudo_label.ipynb) | Thử nghiệm hướng PSEUDO-LABEL (rule-based weak labeling) | `PL*` |
| [`06_cung_quangduong_xuhuong.ipynb`](06_cung_quangduong_xuhuong.ipynb) | Cùng dải quãng đường — Giá dự đoán vs Giá thật, và Xu hướng chấp nhận theo mốc giá | `D*` |
| [`07_chiphi_bien_va_uncertainty.ipynb`](07_chiphi_bien_va_uncertainty.ipynb) | Chi phí biên + Uncertainty vào bài toán định giá | `UA*` |
| [`08_MNL_ba_lua_chon.ipynb`](08_MNL_ba_lua_chon.ipynb) | GĐ 3 — Nâng cấp lên MNL (Multinomial Logit) | `MNL*` |
| [`09_doi_chieu_literature.ipynb`](09_doi_chieu_literature.ipynb) | GĐ 2.4 — Đối chiếu dải elasticity với nghiên cứu đã công bố | `LIT*` |
| [`10_doi_chieu_nhanh_robustness.ipynb`](10_doi_chieu_nhanh_robustness.ipynb) | Đối chiếu với nhánh `acceptance-response robustness v2.0.0` | `BT*` |
