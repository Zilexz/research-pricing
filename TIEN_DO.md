# TIẾN ĐỘ DỰ ÁN — đọc file này khi quay lại máy khác

> Cập nhật **20/08/2026** · nhánh `main` · commit `67bd280`
> Deadline gần nhất: **thứ 2, 24/08/2026** — mentor catch up trực tiếp.

File này trả lời ba câu: **đang ở đâu**, **cái gì đã xong**, **làm gì tiếp**.
Cài đặt môi trường thì xem `SETUP.md`; gộp bộ dữ liệu dẫn xuất thì xem `HUONG_DAN_GOP.md`.

---

## 1. Trạng thái một trang

| Cấu phần đề bài | Trạng thái | Kết quả chốt |
|---|---|---|
| **(i)** Yếu tố cấu thành giá | ✅ đóng | `giá = giá cơ bản × hệ số nhân` · cung–cầu +35,08% mạnh nhất |
| **(ii)** Model dự báo giá | ✅ đóng, **đã chạm trần** | Hybrid hai tầng · MAE **18.048đ** · MAPE **14,74%** · hơn persistence 47,4% |
| **(iii)** Khoảng tin cậy | ✅ đóng phần lõi, **còn 1 quyết định treo** | Conformal chuẩn hoá `p̂ × (1 ± 30,07%)` · coverage 89,81% |
| Acceptance *(mentor yêu cầu thêm)* | ⚠️ giả định, không train được | MNL 3 lựa chọn · +10% giá → chấp nhận giảm ~19% |

**Dữ liệu là synthetic** (`is_synthetic = True` toàn bộ, 1 nền tảng, 2 dịch vụ, 3 khu vực).
Mọi con số mô tả hành vi bộ sinh dữ liệu, **không phải thị trường TP.HCM thật**. Phải nói rõ chỗ này
mỗi lần trình bày.

---

## 2. Năm tuần đã làm gì

| Tuần | Việc chính | Thành phẩm |
|---|---|---|
| 1 | Làm quen bài toán trên bộ Boston, dựng pipeline và baseline | `boston_data/` — 16 notebook |
| 2 | Chuyển sang TP.HCM: phân tích yếu tố ảnh hưởng giá, chốt kiến trúc hai tầng | `analysis/` 22 nb · `bao_cao_tuan2_HOAN_CHINH` |
| 3 | Lượng hoá độ bất định: conformal, Mondrian, quantile regression | `model/uncertainty/` 7 nb · `bao_cao_uncertainty` |
| 4 | Chẩn đoán model, cấu thành giá, causality, transformer | `tuan_4/` 8 nb · `bao_cao_tuan4` |
| **5** | **Giảm sai số nhóm chuyến hiếm + xu hướng dự đoán** | **`tuan_5/` 11 nb · 4 báo cáo · 30 hình** |

Xuyên suốt: `docs/tai_lieu_bao_cao/` có **TECH_DOC** (1.387 dòng), **RESEARCH_PAPER** (772 dòng),
slide 26 trang và demo bản đồ — ba thứ này mở bằng trình duyệt/Word là đọc được, không cần Python.

---

## 3. Tuần 5 — chi tiết phần mới nhất

Câu hỏi của tuần: *giảm sai số ở nhóm chuyến dài và giá cao mà không làm kết quả chung tệ đi?*

### Bảng nộp mentor (D4)

Nhóm chia theo **giá thật** và **quãng đường** — hai đại lượng không phụ thuộc model nào.

| Phương án | `>15 km` | `12–15 km` | `>300k` | Toàn tập | Δ chung |
|---|---:|---:|---:|---:|---:|
| Hybrid GBM *(mốc)* | 17,52% | 15,26% | 23,67% | 14,65% | — |
| GAM đơn lẻ | 15,37% | 14,91% | 22,03% | 14,89% | +0,238 |
| Trọng số theo giá `w=10` | 21,69% | 18,23% | **20,44%** | 14,71% | +0,063 |
| Trọng số theo quãng đường `w=20` | 18,51% | 15,56% | 23,53% | 14,66% | +0,009 |
| **Ghép GAM–GBM** *(chọn)* | **15,40%** | **14,92%** | 22,24% | **14,64%** | **−0,011** |

Chỉ hàng **ghép** cải thiện cả bốn cột, CI 95% đều loại trừ 0. Tham số `d₀=6 km`, `d₁=14 km`,
`α_max=0,8`, dò trên `2026-01` và đánh giá trên hai tháng chưa đụng tới.

### Bốn kết quả tuần 5

| # | Việc | Kết quả |
|---|---|---|
| ① | Trọng số cho chuyến hiếm | ❌ **âm tính** — không mức nào cứu được `>15 km`; gán theo giá kéo được `>300k` (+3,23 điểm) nhưng mất 4,17 điểm ở `>15 km` |
| ② | Ghép GAM–GBM theo quãng đường | ✅ **nhận** — cải thiện cả hai nhóm mục tiêu, toàn tập không xấu đi |
| ③ | Khoảng bất đối xứng | ❌ cặp hằng số âm tính · ✅ **CQR** kéo band `>300k` 83,79% → 88,03%, giá phải trả +3,2% độ rộng |
| ④ | Xu hướng dự đoán *(mentor hỏi thêm)* | Tổng thể **không thiên lệch** (trung vị +0,01%), nhưng báo thấp ở chuyến dài và lúc thị trường vừa tăng giá |

### Vì sao ghép GAM–GBM có lý, không phải may rủi

`XU_HUONG_DU_DOAN` tìm ra **cơ chế**: cây quyết định không ngoại suy được, mà vùng `>20 km` chỉ
chiếm **0,06%** tập train. Hệ quả ở nhóm `>25 km`: giá thật TB 463k, GBM báo 329k (hụt 134.291đ mỗi
chuyến), GAM báo 462,7k — gần như trùng khít. Bản ghép kéo mức hụt từ 29,0% xuống 5,2%.

### Báo cáo tuần 5

| File trong `TP_HCM_data/docs/bao_cao_tuan/` | Nội dung |
|---|---|
| `bao_cao_tuan5_TONG_HOP.md/.docx` | **bản nộp mentor** — gộp cả ba phần, 23 bảng, 22 hình |
| `bao_cao_tuan5.md/.docx` | Hướng ① trọng số + ② ghép |
| `bao_cao_tuan5_uncertainty.md/.docx` | Hướng ③ khoảng bất đối xứng |
| `bao_cao_tuan5_xu_huong.md/.docx` | Hướng ④ model báo cao hay báo thấp |

Dựng lại `.docx`: `py -3.11 TP_HCM_data/docs/cong_cu/md_sang_docx.py <file>.md`

---

## 4. Chạy lại trên máy mới — cần gì trước khi mở `tuan_5/`

Repo **có sẵn** dữ liệu gốc TP.HCM (`TP_HCM_data/data/synthetic_data/`, ~461 MB) và Boston.

Repo **không có** (quá nặng cho Git, `.gitignore` chặn): `hcm_train_ready.parquet`, mọi `*.joblib`
và mọi `evaluation/*.parquet`. Đây chính là thứ notebook tuần 5 cần để chạy.

**Cách nhanh:** giải nén `bo_du_lieu_may_moi.zip` theo `HUONG_DAN_GOP.md` — khỏi train lại gì cả.

**Nếu không có zip**, phải chạy chuỗi này (tổng ~45 phút):

| # | Notebook | Sinh ra | Thời gian |
|---|---|---|---|
| 1 | `model/00_chuan_bi_du_lieu.ipynb` | `data/hcm_train_ready.parquet` | ~5 ph |
| 2 | `model/train/01_train_gia_co_ban.ipynb` | `pred_gia_co_ban.parquet` | ~3 ph |
| 3 | `model/train/02_train_he_so_nhan.ipynb` | `pred_heso.parquet` | ~3 ph |
| 4 | `model/train/03_train_gia_truc_tiep.ipynb` | `pred_gia.parquet` | ~3 ph |
| 5 | `model/train/04_train_gam_doi_chieu.ipynb` | `GAM/*.joblib` + `pred_gam.parquet` | ~25 ph |
| 6 | `model/train/06_train_quantile_da_muc.ipynb` | `QuantileLGBM/*.joblib` | ~3 ph |
| 7 | `model/train/07_sinh_du_lieu_UQ.ipynb` | `uq_pred_{calibration,test}.parquet` · `qr_pred_*.parquet` | ~3 ph |
| 8 | `model/evaluation/04_eval_hybrid.ipynb` | `pred_hybrid_cu.parquet` | ~1 ph |

Bước 5 cần `pip install pygam`. Bước 7 phải chạy sau bước 6.

### Notebook tuần 5 cần file nào

| Notebook | Cần |
|---|---|
| `HUONG_1_THAY_DOI_WEIGHT` | `hcm_train_ready.parquet` — **train lại 48 lượt, ~20 ph** |
| `HUONG_2_GAM_GBM` · `XU_HUONG_DU_DOAN` | `uq_pred_test` · `pred_gam` · `pred_gia_co_ban` · `pred_heso` |
| `HUONG_3_KHOANG_BAT_DOI_XUNG` | thêm `uq_pred_calibration` · `qr_pred_*` |
| `00_TONG_HOP` | chỉ đọc lại `tuan_5/ket_qua/` — **đã commit sẵn**, chạy được ngay |

Mọi bảng số của tuần 5 đã commit trong `tuan_5/ket_qua/` (CSV + JSON), nên **đọc kết quả thì không
cần train lại gì**. Chỉ khi muốn sinh lại hình hoặc đổi tham số mới cần chuỗi trên.

---

## 5. Làm gì tiếp

### 🟢 Làm được ngay, không phụ thuộc ai

**Chốt "model v2".** Hai cải tiến đã quyết — ghép GAM–GBM và Mondrian theo quãng đường — vẫn nằm rải
rác ở notebook tuần 5, chưa gộp vào pipeline chính trong `model/`. Nên có một bản v2 với **một** bảng
đánh giá duy nhất, tái lập được. Đây là thứ bàn giao được.

### 🟡 Chờ mentor trả lời

| Câu hỏi | Mở khoá |
|---|---|
| Chấp nhận khoảng rộng thêm bao nhiêu % để coverage đều giữa band? | Chọn Mondrian (+0,34% độ rộng) hay CQR (+3,2%) — **đang treo** |
| Model nên báo đúng trung bình hay thận trọng lệch lên ở chuyến dài? | Cách hiệu chỉnh |
| Định nghĩa "chuyến giá cao" lúc train — theo giá thật hay quãng đường? | Hai cách cho hai model khác nhau |
| Ngưỡng đánh đổi: nhóm hiếm giảm bao nhiêu thì đáng để toàn tập xấu đi 0,1 điểm? | Tiêu chí nhận phương án |
| Tỷ lệ khách xem giá rồi không đặt (`P₀`)? | Tham số nhạy nhất của acceptance |
| Thị phần XanhSM vs đối thủ chính? | Quy market → firm elasticity, mở khoá MNL |
| Xin được `--artifact-profile full` không? | Bảng `quotes` có trường `discount` — nghi là nguyên nhân sàn nhiễu |

### 🔴 Chặn bởi dữ liệu — không tự gỡ được

- **Dữ liệu thật** — giới hạn lớn nhất. Bộ sinh hiện tại đã chứng minh là bỏ sót ít nhất một hiện
  tượng thật: không mô hình hoá ngày lễ (Tết 17/02 xếp hạng 81/90 ngày đắt nhất).
- **Nhãn accept/reject** → supervised acceptance. Hiện `β` đang suy ngược chứ không đo từ số thật.
- **GAM trên transformed feature space** — mentor gợi ý trao đổi anh Khoa, chưa làm.

### ⛔ Đừng làm nữa

**Tinh chỉnh model.** Năm bằng chứng độc lập đều nói hết dư địa: 4 thuật toán chênh nhau 1,9% ·
Transformer hoà · Optuna 40 trial được **+2 VND** · thêm 49 cột feature được **+6 VND** · oracle
biết mọi thứ quan sát được đạt 14,58% mà model **đã ngang**. Muốn tiến thêm phải **thêm thông tin
mới**, không phải chỉnh model.

**Lặp lại thí nghiệm khoảng bất đối xứng bằng cặp hằng số.** Đã thử đủ 9 mức chia rủi ro, âm tính,
và giải thích được: khoảng là **nhân tính** nên đã hấp thụ sẵn độ lệch phải của phân phối giá.

---

## 6. Ba chỗ dễ vấp khi đọc lại số

**Nhóm cố định.** Mọi so sánh model phải chia nhóm theo **giá thật** hoặc **quãng đường**, không
được để mỗi model tự chia theo giá nó dự đoán. Mức ảnh hưởng không nhỏ: nhóm `>300k` có 869 chuyến
theo giá thật nhưng chỉ 327 theo giá Hybrid dự đoán, và lợi thế đo được của GAM phồng từ 1,65 lên
4,02 điểm. **Ngoại lệ có chủ ý:** coverage vẫn chia theo giá **dự đoán**, vì khoảng tin cậy là lời
hứa đưa ra khi chưa biết giá thật.

**Nhóm `>15 km` chỉ có 660 chuyến** trong tập test. Chênh lệch 1–2 điểm rất dễ là nhiễu — mọi con số
trong tuần 5 đều kèm CI bootstrap. Đếm dấu không phải đếm bằng chứng: tiêu chí ổn định đếm số lát có
CI **loại trừ được 0**.

**Hai tập đánh giá khác nhau.** `14,74%` đo trên tập test đầy đủ 864.360 chuyến (mọi độ trễ), còn
`14,65%` đo trên tập độ trễ 5 phút 216.090 chuyến. Tuần 5 dùng con số thứ hai. Đừng so chéo hai cái.

---

## 7. Bản đồ repo

| Thư mục | Nội dung |
|---|---|
| `TP_HCM_data/analysis/` | Phân tích key feature ↔ giá & hệ số nhân — 22 notebook |
| `TP_HCM_data/model/` | Pipeline train `00 → train/ → evaluation/` + `uncertainty/` + `acceptance/` |
| `TP_HCM_data/tuan_4/` · `tuan_5/` | Việc theo tuần — đọc `README.md` của từng thư mục trước |
| `TP_HCM_data/docs/tai_lieu_bao_cao/` | TECH_DOC · RESEARCH_PAPER · slide |
| `TP_HCM_data/docs/bao_cao_tuan/` | Báo cáo tuần 2 → 5 |
| `TP_HCM_data/ke_hoach/` | `VIEC_TUAN_5.md` · `VIEC_CAN_LAM.md` · `PHAN_TICH_FEEDBACK_MENTOR.md` |
| `TP_HCM_data/demo/` | Demo bản đồ, mở `index.html` là chạy |
| `boston_data/` | Tương tự cho bộ Boston (tuần 1) |
