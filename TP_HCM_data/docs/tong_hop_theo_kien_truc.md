# Tổng hợp theo kiến trúc — Competitor Fare Forecasting

**GSM/XanhSM** · Tuần 1–3 · Tập test **864.360 chuyến**

---

# 1. BA MỤC ĐỀ BÀI

| # | Mục | Trạng thái |
|---|---|---|
| **(i)** | Study relation — feature nào ảnh hưởng giá, thế nào | ✅ Xong |
| **(ii)** | Build model — dự đoán giá đối thủ | ✅ Xong |
| **(iii)** | Uncertainty — khoảng tin cậy | ✅ Xong |
| **(+)** | Acceptance model *(mentor yêu cầu thêm)* | ✅ Bản v1 |

---

# 2. KIẾN TRÚC

```
TẦNG 0  Dữ liệu — 1,72tr lần báo giá · KHÔNG có nhãn accept/reject
   ├──────────────────────────────┐
   ▼                              ▼
TẦNG 1  Model giá      [HỌC]   ĐO THAM SỐ BỐI CẢNH   [ĐO]
   │  Hybrid = cơ bản × hệ số      mưa +4,61% · giờ 50,0%
   ▼  p̂ (một con số)                        │
TẦNG 1b  Uncertainty   [HỌC]  ← cấu phần (iii)
   ▼  f(p̂) (một phân phối)                  ▼ d
TẦNG 2  Acceptance  [GIẢ ĐỊNH] — không train, cấu trúc McFadden
   ▼
TẦNG 3  Quyết định giá — tích phân trên f, có chi phí biên
```

Tầng 1 · 1b **có train**. Tầng 2 · 3 **không train** ⇒ cả hệ thống chỉ có **một khối giả định**.

🖼️ `KT1_kien_truc_tang.png`

---

# 3. KẾT QUẢ TỪNG TẦNG

## TẦNG 1 — Model giá đối thủ *(cấu phần ii)*

| Model | MAE | MAPE | R² |
|---|---:|---:|---:|
| **Hybrid** (cơ bản × hệ số) | **~18.000đ** | **~14,7%** | ~0,73 |
| ├─ Giá cơ bản | 15.030đ | 14,58% | 0,6564 |
| └─ Hệ số nhân | 0,0232 | **1,90%** | **0,9609** |
| XGBoost → GAM (trực tiếp) | 18.807 → 19.173đ | | |
| — Persistence *(mốc)* | 33.683đ | 28,18% | 0,0191 |

1. Hybrid thắng dự đoán trực tiếp **24/24 giờ**, vượt persistence **46%**
2. Hai bài toán độ khó rất khác: hệ số nhân R² **0,96** (gần xong) · giá cơ bản R² **0,66** (**nút thắt**)
3. **Đã chạm trần dữ liệu** — 4 thuật toán chênh **1,9%**; thu hẹp quãng đường xuống **2 mét** mà hệ
   số biến thiên giá **không giảm** ⇒ phần dư là **nhiễu thật**, không phải model kém

🖼️ `U3` · `B5_cv_khong_giam.png`

---

## TẦNG 1b — Uncertainty *(cấu phần iii)*

Giữ riêng **615.908 chuyến** model chưa từng thấy → đo sai số → lấy phân vị 90%.
Có **bảo đảm hữu hạn mẫu**, không cần giả định phân phối.

```
khoảng = giá dự đoán × (1 ± 30%)        coverage ~89,6% / danh mục 90%
```

| Phương pháp | Coverage | Độ rộng |
|---|---:|---:|
| **Conformal chuẩn hoá** ⭐ | ~89,6% | **~72.700đ** |
| QR thô | 89,18% | 75.977đ |
| CQR | 89,56% | 76.546đ |

1. **Sao rộng thế?** Chuyến điển hình chỉ sai **12,14%** — nhưng cam kết đúng 90% số lần phải bao cả
   đuôi. Đã thử chia nhóm theo giờ/thời tiết/quãng đường: **không hẹp hơn được**. Muốn hẹp chỉ có hạ
   mức tin cậy (80% → hẹp **23%**) hoặc cải thiện model (đã chạm trần).
2. **Mondrian theo quãng đường** giảm **71%** độ lệch coverage giữa nhóm (2,81 → 0,81 điểm) mà độ
   rộng chỉ tăng 0,34%.

🖼️ `VQ2` · `VQ4`

---

## TẦNG 2 — Acceptance model *(mentor yêu cầu thêm)*

Dữ liệu **không có nhãn accept/reject**. Đã thử và loại trừ **8 hướng** bằng bằng chứng — rõ nhất:
gán nhãn theo luật cho AUC **1,0000** khi có `price_gap`, còn **0,4995** khi bỏ ⇒ **vòng tròn logic**.
Nên chuyển sang **mô hình cấu trúc** (McFadden), không phải ML.

| Đổi giá so với đối thủ | Chấp nhận (tương đối) |
|---|---:|
| +5% / **+10%** / +20% | −10% / **−19%** / −35% |
| −10% | +21% |

- Trời mưa → **+4,5 điểm %** ≈ tăng giá được 4,6% mà không mất khách
- **Giờ tác động mạnh hơn thời tiết 8,3 lần** ⇒ chọn một tín hiệu định giá động thì chọn **giờ**
- **3 kết luận trên vững trên toàn dải giả định (3/3)**

**Kiểm chứng chéo — MNL 3 lựa chọn** `{không đi, mình, đối thủ}`: khớp logit nhị phân trong **3 điểm %**,
suy ngược ra tỷ lệ khách không đặt `s₀` = **14,3%** (nằm trong khoảng hợp lý 5–30%). Đối chiếu
literature (Cohen 2016, ε ≈ −1,6): dải giả định cùng bậc.

🖼️ `AC3` · `PL1`

---

## TẦNG 3 — Quyết định giá *(mở rộng)*

### 🔴 Một đính chính

Bản đầu tối đa hoá **doanh thu** → luôn khuyến nghị bán rẻ hơn đối thủ 24% ở **mọi** bối cảnh.
Lỗi: không có chi phí thì không gì hãm việc giảm giá. Sửa thành tối đa hoá **lợi nhuận**:

| `ε` | −1,2 | **−2,0** | −3,0 |
|---|---:|---:|---:|
| Ngưỡng đảo chiều `c*` | 16,6% | **50,0%** | 66,7% |

Ngành trả tài xế **75–80%** cước ⇒ vượt ngưỡng ⇒ **nên báo giá CAO HƠN đối thủ** — ngược hẳn.

### Nối cả 3 cấu phần

Quyết định giá lấy **tích phân trên phân phối dự đoán** thay vì cắm ước lượng điểm.
Backtest 864.360 chuyến: lấy lại **+185đ/chuyến (+0,61%)**.

Nhỏ — nhưng quan hệ **siêu tuyến tính**: model bất định gấp đôi thì thiệt hại **gấp 7 lần**
(0,62% → 4,36%). Nhỏ chỉ vì model giá đang tốt.

🖼️ `UA2`

---

## GAM *(bổ sung theo gợi ý mentor)*

| Nhánh | GAM vs cây |
|---|---:|
| Giá cơ bản | **+0,5%** — ngang (R² còn cao hơn) |
| **Hệ số nhân** | **+30,5%** |

**Vì sao:** cho cây học lại phần dư của GAM → R² **0,562** ở hệ số nhân vs **0,018** ở giá cơ bản
⇒ giá cơ bản là quan hệ **cộng dồn thuần**; hệ số nhân **có tương tác** mà GAM không bắt được.

**Transformed feature space** (gợi ý của mentor): thêm tensor `te()` cho 3 cặp tương tác mạnh nhất
→ đóng được **52%** khoảng cách (+30,7% → +14,7%).

**Giá trị riêng của GAM:** p-value tìm ra **4 feature không có ý nghĩa thống kê** — bỏ được khỏi
feature contract. Trong đó `weather_main` **không ảnh hưởng giá cơ bản** nhưng rất mạnh với hệ số
nhân, xác nhận độc lập cho kết luận tuần 2.

🖼️ `GA1` · `TF2`

---

# 4. BA GIỚI HẠN THẬT

| # | Giới hạn | Hệ quả |
|---|---|---|
| **1** | Không có nhãn accept/reject | Tầng 2 là **mô phỏng dưới giả định**, không phải model học từ dữ liệu |
| **2** | **Chi phí biên chưa biết** | Quyết định **CHIỀU** của khuyến nghị giá |
| **3** | Model tái tạo ~70% dao động thật | Phần dư là **nhiễu thật** (chứng minh bằng `B5`) |

⚠️ Số literature ghi từ trí nhớ, **chưa đối chiếu bản gốc**.

---

# 5. CÂU HỎI GỬI MENTOR

| # | Câu hỏi | Mở khoá |
|---|---|---|
| **1** | **Chi phí biên mỗi cuốc / tỷ lệ ăn chia tài xế?** | Chốt **CHIỀU** của khuyến nghị giá |
| **2** | Team tối ưu **GMV** hay **LỢI NHUẬN**? | Chọn giữa hai khung kết quả khác hẳn |
| **3** | **% khách xem giá rồi không đặt** + thị phần? | Chốt `β` ⇒ hết phải giả định elasticity |
| **4** | Surge có **ngưỡng nhảy bậc** không? | Mở khoá RD ⇒ `ε` **thật** từ dữ liệu lịch sử |

> **Nếu chỉ trả lời được 2: xin câu 1 và câu 3.**

---

**Sáu con số nên thuộc:** ~18.000đ · ±30% · ~89,6% · −19% · 8,3 lần · c\* = 50%

**Cần số nào khác:** chạy `model/99_TONG_QUAN_TOAN_DU_AN.ipynb` → `Run All` ~1 phút ra hết.
