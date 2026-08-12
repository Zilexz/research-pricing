# KIẾN TRÚC CHỐT — Hệ thống dự đoán giá & khả năng chấp nhận

> Cập nhật **06/08/2026** — sau khi thêm Tầng 1b (uncertainty), sửa Tầng 3 (chi phí biên),
> và kiểm chứng chéo Tầng 2 bằng MNL.
> Đọc file này là đủ để triển khai lại từ đầu.
>
> 🖼️ Hình dựng lại được: `docs/hinh_anh/KT1_kien_truc_tang.png` · `KT2_tang3_quyet_dinh.png`
> — sinh bởi `model/99_TONG_QUAN_TOAN_DU_AN.ipynb`.

---

## Sơ đồ tổng thể

```
┌─────────────────────────────────────────────────────────────────────┐
│ TẦNG 0 — DỮ LIỆU                                          [dữ liệu] │
│ synthetic_quote_context_sandbox (TP.HCM)                            │
│ 1.724.714 lần báo giá × 4 mức lag  ·  70 cột  ·  3 tháng            │
│ ⚠️ KHÔNG có: nhãn accept/reject · outcome cuốc · customer_id        │
└──────────────┬──────────────────────────────────┬───────────────────┘
               │                                  │
               ▼                                  ▼
┌──────────────────────────────┐   ┌──────────────────────────────────┐
│ TẦNG 1 — MODEL GIÁ ĐỐI THỦ   │   │ ĐO THAM SỐ BỐI CẢNH              │
│                       [HỌC]  │   │                          [ĐO]    │
│ ✅ ML thật — có train/test   │   │ 📊 Thống kê mô tả, không train   │
│ Hybrid: giá = cơ bản × hệ số │   │ Hệ số nhân cân bằng ⇒ dịch WTP   │
│ MAE ~18.000đ · MAPE ~14,7%   │   │   mưa: +4,61%                    │
│ 4 thuật toán chênh 1,9%      │   │   giờ: biên độ 50,0% (3h→18h)    │
│   ⇒ đã chạm trần dữ liệu     │   │                                  │
└──────────────┬───────────────┘   └──────────────┬───────────────────┘
               │ p̂ (ước lượng điểm)               │
               ▼                                  │
┌──────────────────────────────┐                  │
│ TẦNG 1b — UNCERTAINTY [HỌC]  │                  │
│           (cấu phần iii)     │                  │
│ ✅ Hiệu chỉnh ở calibration  │                  │
│ Conformal chuẩn hoá: ±30%    │                  │
│   coverage ~89,6%            │                  │
│ CQR: coverage điều kiện tốt  │                  │
│   nhất (lệch 1,84 điểm)      │                  │
│ ⇒ cho ra PHÂN PHỐI f(p̂)      │                  │
└──────────────┬───────────────┘                  │
               │ f(p̂)                             │ d (dịch WTP)
               ▼                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ TẦNG 2 — ACCEPTANCE MODEL                             [GIẢ ĐỊNH]    │
│ ❌ KHÔNG train — mô hình cấu trúc (lý thuyết lựa chọn rời rạc)      │
│                                                                     │
│   P(chấp nhận) = σ( a + b·[ ln(p/p̂) − ln(1+d) ] )                   │
│   b = ε/(1−P₀)     a = logit(P₀)                                    │
│                                                                     │
│ ⚠️ ε và P₀ là GIẢ ĐỊNH — neo bằng literature (nb 09) + MNL (nb 08)  │
│ MNL 3 lựa chọn {không đi, mình, đối thủ}: khớp trong 3 điểm %       │
└──────────────────────────────┬──────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ TẦNG 3 — QUYẾT ĐỊNH GIÁ            ⚠️ MỞ RỘNG (mentor không yêu cầu)│
│                                                                     │
│   E[Π(p)] = ∫ (p − MC)·P(chấp nhận | p, p_đt)·f(p_đt) dp_đt         │
│                                                                     │
│   ① tích phân trên PHÂN PHỐI f (Tầng 1b), không cắm ước lượng điểm  │
│   ② có chi phí biên MC — quyết định CHIỀU của khuyến nghị           │
│   ③ dịch WTP nhân thẳng: r*(bối cảnh) = r*_gốc × (1 + d)            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Nguyên tắc chốt: **tách bạch phần HỌC và phần GIẢ ĐỊNH**

| Tầng | Bản chất | Có train? | Đánh giá bằng |
|---|---|---|---|
| **1** Model giá | Machine Learning | ✅ | MAE, R², train/test split |
| **1b** Uncertainty | Hiệu chỉnh thống kê | ✅ (calibration) | Coverage, độ rộng |
| **2** Acceptance | Structural (McFadden) | ❌ | Phân tích độ nhạy |
| **3** Quyết định giá | Tối ưu hoá | ❌ | Backtest mô phỏng |

> ⚠️ **Không trộn 2 tầng.** Trộn vào là ra "model AUC 1,0" nguỵ trang —
> xem `05_thu_nghiem_pseudo_label.ipynb`.

---

## TẦNG 1 — Model giá đối thủ

| | |
|---|---|
| **Mục tiêu** | Dự đoán `target_shown_price` từ thông tin biết trước thời điểm báo giá |
| **Kiến trúc** | Hybrid: `giá = Model_A(giá cơ bản) × Model_B(hệ số nhân)` |
| **Thuật toán** | HistGradientBoosting |
| **Kết quả** | MAE **~18.000đ** · MAPE **~14,7%** |
| **Notebook** | `model/train/01`–`04`, `model/evaluation/01`–`07` |

**So sánh 4 thuật toán (tập test 864.360 chuyến):**

| Thuật toán | MAE | MAPE |
|---|---:|---:|
| XGBoost | 18.807đ | 15,34% |
| LightGBM | 18.809đ | 15,34% |
| HistGB | 18.834đ | 15,36% |
| GAM | 19.170đ | 15,70% |
| — Persistence | 33.683đ | 28,18% |

Chênh nhau **1,9%**, đều tốt hơn persistence ~44%. **Trần đã chạm** — sàn nhiễu dữ liệu, không
phải model chưa tối ưu (chứng minh: hình `B5`, CV không giảm dù thu hẹp quãng đường tới 2 mét).

---

## TẦNG 1b — Uncertainty (cấu phần iii)

| Phương pháp | Coverage | Độ rộng TB | Bảo đảm |
|---|---:|---:|---|
| **Conformal chuẩn hoá** | ~89,6% | ~72.700đ | hữu hạn mẫu, phân phối tự do |
| Quantile Regression (thô) | ~89,1% | ~76.000đ | ❌ không |
| **CQR** | ~89,6% | ~76.500đ | hữu hạn mẫu |

Khoảng conformal: **`dự đoán × (1 ± 30%)`**.

**Coverage điều kiện** — lệch tối đa so với danh mục, đo trên 3 chiều:

| Phương pháp | Giờ | Quãng đường | Thời tiết | Xấu nhất |
|---|---:|---:|---:|---:|
| Conformal chuẩn hoá | **1,34** | 2,04 | **0,47** | 2,04 |
| QR thô | 2,19 | 1,91 | 0,94 | 2,19 |
| CQR | 1,84 | **0,95** | 0,57 | **1,84** |
| **Mondrian 10 nhóm theo quãng đường** | — | **0,81** | — | **0,81** |

> **Khuyến nghị:** **conformal chuẩn hoá làm mặc định** — hẹp nhất, đều nhất theo giờ và thời tiết.
> Nếu cần công bằng theo **quãng đường**: dùng **Mondrian** (tốt hơn CQR cả về công bằng 0,81 vs
> 1,09 lẫn độ rộng 72.935đ vs 76.546đ, và đơn giản hơn — chỉ lưu thêm 10 con số).
>
> ⚠️ Bản trước ghi *"CQR có coverage điều kiện tốt nhất"* — **sai**, vì chỉ so với QR thô.
> Không phương pháp nào thắng tuyệt đối trên cả 3 chiều.

**Về độ rộng ±30%:** đây là **độ bất định thật** của model, không phải lựa chọn phương pháp —
chia nhóm theo giờ/thời tiết/quãng đường đều không làm hẹp hơn (đo ở `uncertainty/04`). Sai số
tương đối gần như đồng đều trên mọi bối cảnh. Muốn hẹp chỉ có: hạ mức tin cậy (80% → hẹp **23%**)
hoặc cải thiện model giá (đã chạm trần dữ liệu).

**Vai trò trong kiến trúc:** Tầng 1b biến đầu ra của Tầng 1 từ **một con số** thành **một phân
phối** — đây là thứ Tầng 3 cần để lấy tích phân.

---

## TẦNG 2 — Acceptance model

### Công thức

```python
def P_accept(gia_minh, gia_doithu, eps, P0=0.5, dich_WTP=0.0):
    b = eps / (1 - P0)
    a = np.log(P0 / (1 - P0))
    z = a + b * (np.log(gia_minh / gia_doithu) - np.log1p(dich_WTP))
    return 1 / (1 + np.exp(-z))
```

### Bốn tham số — nguồn gốc rõ ràng

| Tham số | Nguồn | Giá trị | Kiểm chứng được? |
|---|---|---|---|
| `gia_doithu` | 📊 Tầng 1 | p̂ | ✅ MAE ~18.000đ |
| `dich_WTP` | 📊 Đo từ dữ liệu | mưa +4,61% · giờ ±25% | ✅ Từ hệ số nhân cân bằng |
| `P₀` | ⚠️ Quy ước | 0,5 | ❌ Cần hỏi mentor |
| `ε` | ⚠️ **Giả định** | −2,0 (dải −1,2 → −3,0) | 🟡 Neo bằng literature + MNL |

→ **Chỉ 2/4 tham số là giả định**, cả hai đều được quét dải trong phân tích độ nhạy.

### Cách trình bày — dùng % thay đổi TƯƠNG ĐỐI

| Cách báo cáo | Dao động khi `P₀` chạy 0,30 → 0,70 |
|---|---:|
| Mức tuyệt đối | 30,7 điểm ❌ |
| Thay đổi tuyệt đối | 9,3 điểm ⚠️ |
| **Thay đổi tương đối** | **3,1 điểm** ✅ |

### Kết quả

| Đổi giá so với đối thủ | Chấp nhận (tương đối) |
|---|---:|
| +5% / +10% / +20% | −10% / **−19%** / −35% |
| −5% / −10% / −20% | +10% / +21% / +42% |

Trời mưa → chấp nhận **+4,49 điểm %** (≈ tăng giá được 4,6% mà không mất khách).

### Ba kết luận vững (3/3 mức elasticity)

1. Giá cao hơn đối thủ → chấp nhận **giảm**
2. Mưa → chấp nhận **tăng**
3. **Giờ** tác động mạnh hơn **thời tiết** ~8,3 lần

### Kiểm chứng chéo bằng MNL — `08_MNL_ba_lua_chon.ipynb`

MNL 3 lựa chọn ràng buộc **cả hai elasticity vào một `β`**:

$$\varepsilon_{\text{firm}} = -\beta(1-s_1) \qquad \varepsilon_{\text{market}} = -\beta s_0
\qquad s_0 = \frac{1-m}{R-m}$$

| Kết quả | |
|---|---|
| `s₀` (khách không đi) | **14,3%** — trong khoảng hợp lý [5%; 30%] |
| `s₁` = `s₂` | 42,9% |
| `β` | 3,500 |
| MNL vs logit nhị phân | khớp trong **3 điểm %** |
| Ngưỡng đảo chiều `c*` | **trùng khít 50,0%** ở cả hai mô hình |

> ⚠️ Tổ hợp `ε_firm = −1,2` + `ε_market = −0,7` cho `s₀ = 41,2%` — **không nhất quán, không dùng
> đồng thời**. Đây là loại mâu thuẫn logit nhị phân không phát hiện được.

---

## TẦNG 3 — Quyết định giá (mở rộng)

### 🔴 Hai lần sửa quan trọng

**Lần 1 — chi phí biên** (`07_chiphi_bien_va_uncertainty.ipynb`)

| | Bản đầu ❌ | Bản sửa ✅ |
|---|---|---|
| Hàm mục tiêu | `p · P(chấp nhận)` — **doanh thu** | `(p − MC) · P(chấp nhận)` — **lợi nhuận** |
| Kết quả | `r*` = 0,760 ở **mọi** bối cảnh | Đảo chiều quanh `c*` |
| Vấn đề | Không có chi phí ⇒ không gì hãm việc giảm giá | — |

**Ngưỡng đảo chiều `c*`** (chi phí biên tính theo % giá đối thủ):

| `ε` | `c*` (ngây thơ) | `c*` (có tích phân UQ) |
|---:|---:|---:|
| −1,2 | 16,6% | 13,4% |
| −2,0 | **50,0%** | **44,4%** |
| −3,0 | 66,7% | 58,8% |

Ngành gọi xe VN trả tài xế **75–80%** cước ⇒ `c ≈ 0,75–0,80` ⇒ **cả 3 kịch bản đều vượt ngưỡng**
⇒ nên báo giá **cao hơn** đối thủ.

**Lần 2 — tích phân trên phân phối dự đoán**

$$\mathbb{E}[\Pi(p)] = \int (p - MC)\cdot P(\text{chấp nhận} \mid p, p_{đt})\cdot f(p_{đt})\, dp_{đt}$$

| | Lợi nhuận TB/chuyến (`c` = 50%) |
|---|---:|
| Ngây thơ (`r*` = 1,000) | 30.314đ |
| **Vững** (`r*` = 1,040) | **30.499đ** |
| Chênh — lấy lại miễn phí | **+185đ (+0,61%)** |
| Oracle (biết trước giá thật) | 30.747đ |

**+0,61% là nhỏ.** Điều đáng nói là quan hệ **siêu tuyến tính** với độ bất định:

| Độ rộng phân phối | % lợi nhuận mất nếu bỏ qua bất định |
|---:|---:|
| 0,5× | 0,08% |
| **1,0× (hiện tại)** | **0,62%** |
| 1,5× | 2,01% |
| 2,0× | 4,36% |

Rộng gấp đôi ⇒ thiệt hại gấp ~7 lần. Cách ngây thơ chỉ tạm ổn **vì model giá hiện đã khá tốt**.

⚠️ Ở `c = 0` cách "vững" **không thắng** (kém 0,008% ngoài mẫu) — phân phối lệch nhẹ giữa
calibration (TB 1,010) và test (1,025), và đường lợi nhuận quá phẳng quanh đỉnh.

### Bảng tra cứu

`bang_tra_cuu_gia.csv` — giá nên báo theo **giờ × thời tiết**, tính bằng bội của giá đối thủ.
Dịch WTP **không cần tối ưu lại**, nó nhân thẳng vào nghiệm: `r*(bối cảnh) = r*_gốc × (1 + d)`.

---

## ❌ CÁC HƯỚNG ĐÃ THỬ VÀ LOẠI TRỪ

| Hướng | Vì sao loại | Bằng chứng |
|---|---|---|
| **Supervised học từ nhãn thật** | Không có nhãn | `booking_or_completion_outcomes_generated = False`; 0/251 cột |
| **Unsupervised** | Acceptance không tồn tại dưới dạng ẩn nào | Đã quét toàn bộ 70 cột |
| **Rule-based weak labeling** | **Vòng tròn logic** | AUC 1,0000 → bỏ `price_gap` còn 0,4995; ε ngụ ý = 0 hoặc −44,5 |
| **Proxy label từ cột khác** | Không có cột nào phù hợp | Rà hết 70 cột |
| **PU learning** | Cần ít nhất vài ca dương | Quan sát được **0** ca |
| **Ước lượng cầu trực tiếp** | Nội sinh | Hồi quy thô cho hệ số **+0,40** — sai dấu |
| **Biến công cụ (IV)** | IV không hợp lệ | Bỏ biến giờ ⇒ hệ số lật từ −0,95 sang **+0,36** |
| **Chỉ số Lerner** | Cho `ε` vô lý | −33 đến −2,5 |
| **Đảo ngược quy tắc định giá** | Surge sinh cơ học, không tối ưu hoá | Công thức `m = f(imbalance)` |
| **SMM / indirect inference** | Mô-men không chứa thông tin acceptance | Placebo test: tương quan 0,004 |
| **Personalized model** | Không có `customer_id` | `personalized_wrapper_enabled = False` |

---

## Thứ tự triển khai lại từ đầu

| Bước | Việc | File | Thời gian |
|---|---|---|---|
| 1 | Chuẩn bị dữ liệu, chia train/val/calib/test theo tháng | `model/00_chuan_bi_du_lieu.ipynb` | ~5 ph |
| 2–4 | Train Model A · B · baseline trực tiếp | `model/train/01`–`03` | ~9 ph |
| 5 | Train GAM đối chiếu | `model/train/04` | ~13 ph |
| 6 | Ghép Hybrid, đánh giá | `model/evaluation/04` | ~1 ph |
| 7–8 | Biểu đồ uncertainty · theo góp ý mentor | `model/evaluation/06`, `07` | ~3 ph |
| 9–10 | **Tầng 1b** — conformal · quantile + CQR | `model/uncertainty/01`, `02` | ~2 ph |
| 11 | **Tầng 2** — acceptance, chạy 1 thể | `model/acceptance/00_TONG_HOP` | ~1 ph |
| 12 | **Tầng 3** — chi phí biên + tích phân UQ | `model/acceptance/07` | ~2 ph |
| 13 | Kiểm chứng chéo MNL | `model/acceptance/08` | ~20 gy |
| 14 | Đối chiếu literature | `model/acceptance/09` | ~10 gy |
| 15 | **Tổng quan + sinh hình kiến trúc** | `model/99_TONG_QUAN_TOAN_DU_AN` | ~1 ph |

**Notebook trực quan (không bắt buộc để chạy pipeline):**

| File | Nội dung | Hình |
|---|---|---|
| `uncertainty/00_TONG_QUAN` | Cơ chế UQ · coverage điều kiện 3 chiều | `VQ1`–`VQ7` |
| `uncertainty/01_conformal_chuan_hoa` | Mondrian — có hiệu quả không | `MD1`–`MD6` |
| `evaluation/08_truc_quan_GAM` | Đường cong · p-value · bằng chứng tương tác | `GA1`–`GA6` |

**Bước 11 độc lập** — chỉ cần `data/hcm_train_ready.parquet`.
**Bước 12** cần thêm `evaluation/qr_pred_{calibration,test}.parquet` từ bước 10.
**Bước 13, 14** thuần tính toán, không cần dữ liệu.

---

## 🔒 Điều kiện để nâng cấp kiến trúc

Kiến trúc hiện tại là **tối ưu với dữ liệu đang có**. Chỉ nâng cấp khi có thêm dữ liệu:

| Nếu có | Thì đổi thành | Lợi ích |
|---|---|---|
| **Chi phí biên `MC`** | Tầng 3 chốt được **chiều** khuyến nghị | Hết phải quét dải `c` |
| **`s₀` + thị phần** | MNL hiệu chỉnh bằng số **thật** thay vì suy ngược | Chốt `β` ⇒ hết giả định elasticity |
| **Ngưỡng nhảy bậc surge** | RD như Cohen 2016 trên dữ liệu lịch sử | `ε` **thật**, không cần thí nghiệm |
| **`outcome` cuốc** | Tầng 2 → **supervised thật** + xử lý nội sinh | `ε` ước lượng thay vì giả định |
| **Thí nghiệm giá ngẫu nhiên** | Elasticity nhân quả sạch | Chuẩn vàng |
| Nghi ngờ giả định **IIA** | MNL → **Nested Logit** | Xử lý thay thế không đối xứng |

---

## 📮 Câu hỏi chặn tiến độ (gửi mentor)

| # | Câu hỏi | Mở khoá | Ưu tiên |
|---|---|---|---|
| 1 | **Chi phí biên mỗi cuốc / tỷ lệ ăn chia tài xế?** | Chốt **CHIỀU** của toàn bộ khuyến nghị giá | 🔴 |
| 2 | **Team tối ưu GMV hay LỢI NHUẬN?** | Chọn giữa kết quả cũ và Tầng 3 hiện tại | 🔴 |
| 3 | **Bao nhiêu % khách xem giá rồi không đặt (`s₀`)?** | Chốt `β` ⇒ chốt **cả hai** elasticity | 🔴 |
| 4 | **Thị phần XanhSM vs đối thủ chính?** | Cùng `s₀` là đủ hiệu chỉnh MNL hoàn chỉnh | 🔴 |
| 5 | Công thức surge có **ngưỡng nhảy bậc** không? | Cho phép Regression Discontinuity | 🟠 |
| 6 | Có bộ `giá đã hiện` + `outcome` không? | Điều kiện cho supervised | 🟠 |
| 7 | Outcome tách được `no_driver_found` khỏi khách chủ động không đặt? | Tránh học nhầm | 🟠 |

> **Nếu chỉ hỏi được 2 câu: hỏi câu 1 và câu 3.**

---

## ⚠️ Phải nêu rõ khi báo cáo

| Điểm | Cách phát biểu đúng |
|---|---|
| Tầng 2 không phải ML | *"Model cấu trúc từ lý thuyết lựa chọn rời rạc, không train"* |
| Kết quả phụ thuộc giả định | *"Dưới giả định ε ∈ [−1,2; −3,0]..."* |
| Lợi nhuận là mô phỏng | *"Lợi nhuận kỳ vọng theo mô hình, không phải đo được"* |
| `P₀` chưa kiểm chứng | *"Con số tuyệt đối phụ thuộc giả định P₀ = 0,5"* |
| Chiều khuyến nghị phụ thuộc `c` | *"Với `c` chưa biết, kết luận chiều chưa chốt được"* |
| Model tĩnh | *"Chưa tính phản ứng của đối thủ"* |
| Literature chưa xác minh | *"Số trích từ trí nhớ, cần kiểm chứng lại nguồn gốc"* |
