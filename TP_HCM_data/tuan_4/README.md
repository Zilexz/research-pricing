# Tuần 4 — trả lời feedback mentor

Năm notebook, **đã chạy sẵn và nhúng kết quả** — mở lên là thấy hình và số, không cần chạy lại.

> ⭐ **Đọc [`00_TONG_HOP`](00_TONG_HOP.ipynb) trước.** Đó là bản một trang gom toàn bộ kết quả
> thành một mạch, tự tính lại số từ dữ liệu. Bốn notebook còn lại là bản đào sâu từng ý mentor.

| # | Notebook | Trả lời ý nào của mentor | Kết luận một dòng |
|---|---|---|---|
| **00** | [`00_TONG_HOP`](00_TONG_HOP.ipynb) | — bản tổng hợp cả tuần | **MAPE 14,65% đã gần sàn của bộ dữ liệu** — ràng buộc là dữ liệu, không phải model |
| **01** | [`01_BA_KICH_BAN`](01_BA_KICH_BAN.ipynb) | *"3 model này sẽ rất là khác nhau…"* | Model = **kịch bản A** (±30% đều). B và C không tồn tại được: khung ±10% chỉ giữ **42,3%** coverage |
| **02** | [`02_IMPROVE_HAY_GIAM_UNCERTAINTY`](02_IMPROVE_HAY_GIAM_UNCERTAINTY.ipynb) | *"nên improve model hay giữ model nhưng giảm uncertainty"* · *"model fail ở đâu"* | **Phải improve model.** Hiệu chỉnh lại chỉ được **−0,37%** độ rộng; độ khó từng chuyến không dự đoán được (tương quan hạng **0,05**) |
| **03** | [`03_CETERIS_PARIBUS_VA_CAUSALITY`](03_CETERIS_PARIBUS_VA_CAUSALITY.ipynb) | *"thay đổi 1 yếu tố, fix phần còn lại"* · *"encode causality"* | Model **hiểu cơ chế**, nhưng không dùng khi còn giá trễ để chép. Rút giá trễ ra (lag 30'), nó **tự bù 94%** hiệu ứng mưa |
| **04** | [`04_CAU_THANH_GIA`](04_CAU_THANH_GIA.ipynb) | *"yếu tố nào cấu thành 1 mức giá (distance, weather, rush hour, public holiday, demand-supply)"* | **Cung–cầu mạnh nhất (+35,1%)**, và mọi yếu tố thị trường đi qua **hệ số nhân**. Model giá cơ bản **đã chạm trần thông tin** |
| **05** | [`05_DUONG_PHAN_UNG`](05_DUONG_PHAN_UNG.ipynb) | *"khi mình thay đổi 1 feature thì price sẽ **diễn biến** thế nào"* | Mọi quan hệ **đơn điệu và liên tục**, **không có ngưỡng nhảy bậc** ⇒ không dùng được Regression Discontinuity |
| **06** | [`06_ENCODE_CAUSALITY`](06_ENCODE_CAUSALITY.ipynb) | *"**encode** được causality info này vào 1 model"* | Khoảng cách PDP **không phải lỗi model** — mưa tác động **qua cung–cầu**. Encode được, nhưng là **đánh đổi**: bắt 63% hiệu ứng đổi lấy **+10,9% MAE** |

## Hình sinh ra

| Notebook | Hình |
|---|---|
| **00** | `TK1_sai_so_o_tang_nao` · `TK2_cau_thanh_gia` · `TK3_khoang_bat_dinh` · `TK4_rut_cai_nang` |
| 01 | `TT5_ba_kich_ban_theo_thoi_gian` · `TT6_coverage_ba_kich_ban` |
| 02 | `QD1_mondrian_lam_deu` · `QD2_tran_ly_thuyet` · `QD3_fail_o_dau` · `QD4_bien_dong_vs_khoang` |
| 03 | `PU1_rut_cai_nang` · `PU2_di_qua_tang_nao` |
| 04 | `CG1_xep_hang_yeu_to` · `CG2_cau_truc_vs_thi_truong` · `CG3_tran_thong_tin_gia_co_ban` |
| 05 | `DP1_tin_hieu_thi_truong` · `DP2_quangduong_tacduong` · `DP3_nhip_gia_theo_gio` |
| 06 | `EC1_hai_kenh_trung_gian` |

Tất cả ở `docs/hinh_anh/`.

## Bốn số đáng mang đi họp

1. **Cung–cầu là yếu tố mạnh nhất: +35,1%** khi đi từ nhóm cung dư sang nhóm cầu vượt cung — gấp
   ba lần giờ cao điểm. Và **80% đi qua hệ số nhân**, đúng cấu trúc *market signal multiplier*.
2. **Coverage nhóm `>15 km` chỉ 82,6%** dưới hiệu chỉnh toàn cục, trong khi cam kết 90% — nhóm
   chuyến đắt tiền nhất lại bị phục vụ tệ nhất. Bật Mondrian kéo lệch từ **12,6 → 2,5 điểm**, tốn
   vài giờ, không train lại.
3. **Chỗ hỏng nằm ở quãng đường (η² 0,0106), không phải thời điểm (η² ≤ 0,0001).** Đi ngược trực
   giác của ba kịch bản rush-hour mà mentor nêu — và đây là số đo, không phải phỏng đoán.
4. **MAPE 14,65% đã gần sàn của bộ dữ liệu.** 98,9% sai số nằm ở tầng giá cơ bản, mà tầng đó có
   trần lý thuyết **14,98%** trong khi model đạt **14,58%**. Các chuyến giống hệt nhau về mọi
   thuộc tính quan sát được vẫn lệch giá cơ bản **CV 18,6%**.

## ⚠️ Kết luận thay đổi giữa notebook 02 và 04

`02` kết luận *"đường giảm uncertainty đã cạn ⇒ phải improve model"*. `04` bổ sung: **đường improve
model cũng cạn trên bộ dữ liệu này** — mọi yếu tố thị trường đi vào tầng hệ số nhân (đã đạt MAPE
1,42%), còn tầng giá cơ bản thì đã chạm trần thông tin. Ràng buộc thật sự là **dữ liệu**, không
phải model. Đọc `04` mục 5 trước khi lập kế hoạch cải thiện.

## ⚠️ Bẫy dữ liệu đã vấp

`quote_duration` tính bằng **giây**, không phải phút (trung vị 1.368s ≈ 23 phút, tốc độ 16,5 km/h).
Dùng nhầm đơn vị khi chia ô khống chế sẽ tạo ra ô 5 **giây** thay vì 5 **phút** — trần lý thuyết
tính ra thấp giả tạo (14,84% thay vì 14,98%) và chỉ phủ 72% dữ liệu thay vì 99%. Đã sửa ở `00`
và `04`.

## Bản đào sâu

Ba notebook trên là bản **tổng hợp ra quyết định**. Chi tiết phương pháp ở:

| Chủ đề | Notebook |
|---|---|
| 5 cách thu hẹp khoảng × 7 nhóm | `model/uncertainty/06_thu_hep_khoang` |
| Xếp hạng 10 chiều, thiên lệch hệ thống | `model/evaluation/09_chan_doan_model` |
| Partial dependence, ablation, chuỗi nhân quả của mưa | `analysis/14_ceteris_paribus` |
| Ba phương pháp dựng khoảng | `model/uncertainty/00_TONG_QUAN` → `04_SO_SANH` |

## Câu cần hỏi mentor

| # | Câu hỏi | Vì sao chặn |
|---|---|---|
| **1** ⭐ | **Dữ liệu thật có mức nhiễu báo giá như bộ synthetic không?** | Nếu có, MAPE ~14,6% là sàn và mọi nỗ lực improve model là vô ích. Câu này giờ quan trọng hơn cả câu về đánh đổi |
| **2** | Ưu tiên độ chính xác hay khả năng giải thích? | Độ chính xác đã kịch trần ⇒ cán cân nghiêng hẳn về giải thích. Model bỏ feature giá quan sát kém 8% MAE nhưng hiệu ứng cao điểm khớp thực tế |
| **3** | Ngày lễ — dữ liệu thật có hiệu ứng này không? | Bộ synthetic **không có**: kỳ dữ liệu chứa Tết 17/02/2026 nhưng ngày đó xếp thứ **81/90** về giá. Thêm cột `public_holiday` vào bộ hiện tại sẽ tạo feature rỗng tín hiệu |
| **4** | *"Encode causality"* — chọn hướng nào? | Xem `03`: model đã có tín hiệu, nên hướng rẻ nhất có thể là train ở horizon dài hơn |

Chi tiết ở `PHAN_TICH_FEEDBACK_MENTOR.md`.
