# Việc tuần 5 — từ feedback mentor tuần 4

> Lập 17/08/2026. Hạn: **thứ 2, 24/08/2026** — mentor catch up trực tiếp.

---

## Câu hỏi chính của tuần

> **Có thể giảm sai số ở nhóm chuyến dài và giá cao mà không làm kết quả chung tệ đi đáng kể
> hay không?**

Mọi việc dưới đây phục vụ đúng câu này. Mentor đã nói rõ: **không cần làm lại các bảng phân tích của
tuần 4**. Dùng kết quả hiện tại làm baseline, chỉ bổ sung một bảng ngắn so sánh phương án mới.

## Ràng buộc phương pháp — áp cho mọi thí nghiệm

> *"Các em cần giữ nguyên nhóm chuyến giữa các model. Không nên để mỗi model tự chia nhóm theo giá
> mà chính nó dự đoán, vì như vậy các model có thể đang được đánh giá trên những nhóm chuyến khác
> nhau."*

Đây không phải góp ý nhỏ. Kiểm lại trong `RESEARCH_PAPER` §6.5 cho thấy mức ảnh hưởng thật:

| Cách chia nhóm | Số chuyến `>300k` | Chênh lệch GAM − Hybrid |
|---|---:|---:|
| Theo **giá thật** | 869 | **+1,65 điểm** [+1,17, +2,12] |
| Theo giá Hybrid dự đoán | 327 | +4,02 điểm [+2,74, +5,32] |
| Theo giá GAM dự đoán | 330 | — |

**Quy tắc chốt cho tuần 5:** so sánh model thì chia nhóm theo **giá thật** hoặc **quãng đường** —
hai thứ không phụ thuộc model nào. Riêng đánh giá coverage thì vẫn chia theo **giá dự đoán**, vì
coverage là lời hứa đưa ra tại thời điểm dự báo (xem `RESEARCH_PAPER` §7.2).

---

# ✅ ĐÃ XONG — làm trong lúc viết research paper

| # | Việc | Kết quả | Nguồn |
|---|---|---|---|
| **X1** | Tính lại so sánh GAM–Hybrid trên nhóm cố định | Lợi thế `>300k` giảm **4,02 → 1,65 điểm**; lợi thế `>15 km` **+2,16 điểm** vẫn vững | §6.5 |
| **X2** | Thử khoảng bất đối xứng đơn giản | **Âm tính** — coverage y hệt 89,81%, độ rộng −0,13%, lệch giữa band tăng 6,21 → 6,51 điểm | §7.5 |
| **X3** | Tech doc | Xong, 1.387 dòng · `docs/TECH_DOC.docx` | |
| **X4** | Research paper | Xong, 772 dòng · `docs/RESEARCH_PAPER.docx` | |

**X2 tiết kiệm được một hướng.** Mentor đề xuất giữ độ rộng tương đương nhưng dành nhiều khoảng hơn
cho phía giá cao. Đã thử 5 tỷ lệ chia rủi ro khác nhau, phương án tốt nhất (3% dưới / 7% trên) cho:

| | Đối xứng hiện tại | Bất đối xứng 3/7 |
|---|---:|---:|
| Coverage | 89,81% | 89,81% |
| Độ rộng TB | 72.637đ | 72.541đ (−0,13%) |
| Vượt cận trên | 7,64% | 7,30% |
| Thấp hơn cận dưới | 2,55% | 2,90% |
| Lệch coverage giữa các band | 6,21 điểm | **6,51 điểm** |

Lý do không ăn thua: khoảng hiện tại là **nhân tính** `p̂ × (1 ± q)` chứ không cộng tính, nên đã hấp
thụ sẵn phần lớn độ lệch phải của phân phối giá. Phần bất đối xứng còn lại quá nhỏ để một cặp hằng
số khai thác được.

⇒ **Không lặp lại thí nghiệm này.** Nếu vẫn theo đuổi hướng bất đối xứng thì phải để độ lệch **thay
đổi theo từng chuyến** — xem C2.

---

# 🔴 A. Đặt trọng số cao hơn cho chuyến hiếm

> *"Giữ model hiện tại làm model mốc, sau đó đặt weight lớn hơn cho các chuyến hiếm, cụ thể là chuyến
> trên 300k hoặc trên 15 km. Kiểm tra xem sai số ở hai nhóm này giảm bao nhiêu và kết quả chung phải
> đánh đổi bao nhiêu."*

| # | Việc | Ghi chú |
|---|---|---|
| **A1** | Chốt định nghĩa "chuyến hiếm" theo biến **quan sát được lúc train** | `quote_distance > 15` dùng được ngay. `>300k` thì phải dùng **giá thật** ở tập train — hợp lệ vì lúc train có nhãn |
| **A2** | Chạy lưới trọng số `w ∈ {1, 2, 3, 5, 10}` cho nhóm hiếm | Dùng `sample_weight` của HistGB, không đổi kiến trúc |
| **A3** | Với mỗi `w`, đo MAPE trên **nhóm cố định** | `>15 km` · `12–15 km` · `>300k` (giá thật) · toàn tập |
| **A4** | Vẽ đường đánh đổi | Trục ngang: MAPE toàn tập · trục dọc: MAPE nhóm hiếm. Mỗi điểm một `w` |
| **A5** | Chốt `w` khuyến nghị | Tiêu chí ở dưới |

**Baseline để so** (test lag 5 phút, nhóm cố định):

| Nhóm | n | MAPE Hybrid hiện tại |
|---|---:|---:|
| Toàn tập | 216.090 | **14,65%** |
| `>15 km` | 660 | **17,52%** |
| `12–15 km` | 2.045 | 15,26% |
| `>300k` (giá thật) | 869 | **23,67%** |

**Tiêu chí chấp nhận đề xuất:** nhóm hiếm giảm ≥1 điểm MAPE trong khi toàn tập xấu đi ≤0,15 điểm.
Con số này cần bootstrap CI để biết chênh lệch có thật hay chỉ là nhiễu — nhóm `>15 km` chỉ có 660
chuyến nên rất dễ ra kết quả giả.

> ⚠️ Rủi ro cần lường trước: nhóm hiếm ít chuyến nên tăng trọng số dễ dẫn tới overfit chính chúng.
> Phải đo trên tập test tách theo thời gian, không đo trên tập train.

---

# 🔴 B. Kiểm định lại lợi thế của GAM

> *"Kiểm tra lại lợi thế của GAM trên nhiều lần chia dữ liệu theo thời gian. Nếu GAM vẫn tốt hơn ổn
> định ở chuyến dài và giá cao, các em có thể thử một cách kết hợp GAM–GBM đơn giản."*

## B1. Độ ổn định qua nhiều lần chia

| # | Việc | Ghi chú |
|---|---|---|
| **B1a** | Dựng ≥3 lần chia train/test theo thời gian | Ví dụ cắt theo tuần trượt, hoặc train tháng 1 → test tháng 2, train 1–2 → test 3 |
| **B1b** | Mỗi lần chia, đo chênh lệch GAM − Hybrid ở `>15 km`, `12–15 km`, `>300k` | Kèm bootstrap CI |
| **B1c** | Kết luận: lợi thế có **đổi dấu** ở lần chia nào không | Đây là câu hỏi cần trả lời, không phải con số trung bình |

Kết quả trên **một** lần chia hiện có:

| Nhóm | Hybrid | GAM | Chênh | CI 95% |
|---|---:|---:|---:|---|
| `>15 km` | 17,52% | 15,37% | **+2,16** | [+1,36, +2,91] |
| `12–15 km` | 15,26% | 14,91% | +0,35 | [+0,15, +0,56] |
| `>300k` (giá thật) | 23,67% | 22,03% | **+1,65** | [+1,17, +2,12] |
| Toàn tập | 14,65% | 14,89% | −0,24 | [−0,25, −0,22] |

## B2. Ghép GAM–GBM theo quãng đường

Chỉ làm **nếu B1 cho thấy lợi thế ổn định**. Mentor nói rõ *"không cần xây thêm kiến trúc phức tạp"*.

Dạng đơn giản nhất — trộn tuyến tính, trọng số tăng dần theo quãng đường:

```
p̂ = (1 − α(d)) · p̂_GBM  +  α(d) · p̂_GAM

α(d) = 0                       nếu d ≤ d₀
     = (d − d₀) / (d₁ − d₀)    nếu d₀ < d < d₁
     = α_max                   nếu d ≥ d₁
```

| # | Việc | Ghi chú |
|---|---|---|
| **B2a** | Chốt `d₀`, `d₁`, `α_max` **trên tập calibration**, không phải test | Nếu dò tham số trên test thì kết quả vô nghĩa |
| **B2b** | Đo trên nhóm cố định, so với cả GBM đơn lẻ lẫn GAM đơn lẻ | |
| **B2c** | Kiểm tra chuyển tiếp có mượt không | Đừng để giá nhảy bậc tại `d₀` — khách đi 14,9 km và 15,1 km không nên nhận giá lệch hẳn nhau |

**Điểm khởi đầu gợi ý:** `d₀ = 10 km`, `d₁ = 18 km`, `α_max = 1`. Lý do: §6.5 cho thấy GBM còn thắng
ở `8–12 km` (+0,07 điểm) và bắt đầu thua từ `12–15 km`.

---

# 🟠 C. Uncertainty

## C1. Bật Mondrian theo quãng đường

Việc rẻ nhất trong cả tuần, và đã đủ bằng chứng để làm ngay:

| | Toàn cục | Mondrian theo quãng đường |
|---|---:|---:|
| Nửa độ rộng | ±30,07% | ±29,96% |
| Coverage | 89,81% | 89,77% |
| Lệch coverage giữa các nhóm | 12,61 điểm | **2,53 điểm** |
| Coverage nhóm `>15 km` | 82,58% | **87,58%** |

Chi phí: vài giờ, **không train lại model**, tốn thêm 0,04% độ rộng.

## C2. Bất đối xứng theo từng chuyến — chỉ làm nếu còn thời gian

X2 đã loại phương án một cặp hằng số. Phương án còn lại là ước lượng **hai phân vị điều kiện riêng
biệt** cho mỗi chuyến, tức quay lại họ CQR nhưng bất đối xứng.

Chi phí cao hơn hẳn và lợi ích chưa rõ. **Ưu tiên thấp nhất trong tuần** — chỉ đụng vào khi A và B
đã xong.

---

# 📄 D. Tài liệu nộp

> *"RnD viết đủ báo cáo, tech docs, và research papers nộp nhé."*

| # | Tài liệu | Trạng thái |
|---|---|---|
| **D1** | Tech doc | ✅ `docs/TECH_DOC.docx` — 1.387 dòng, 70 bảng, 12 hình |
| **D2** | Research paper | ✅ `docs/RESEARCH_PAPER.docx` — 772 dòng, 29 bảng, 12 hình |
| **D3** | Báo cáo tuần 5 | 🔴 Viết cuối tuần, sau khi có kết quả A và B |
| **D4** | Bảng so sánh phương án mới | 🔴 Xem mẫu dưới — đây là thứ mentor yêu cầu cụ thể nhất |

## Mẫu bảng D4

Mentor yêu cầu bảng này trả lời rõ **hai câu**: nhóm chuyến dài và giá cao có thực sự tốt hơn không,
và kết quả chung bị ảnh hưởng thế nào. Nên bảng phải có đủ cả hai cột đó trên cùng một hàng:

| Phương án | `>15 km` (660) | `>300k` (869) | Toàn tập (216.090) | Đánh đổi |
|---|---:|---:|---:|---|
| **Hybrid GBM** *(mốc)* | 17,52% | 23,67% | **14,65%** | — |
| GAM đơn lẻ | 15,37% | 22,03% | 14,89% | −0,24 điểm toàn tập |
| Trọng số `w = ?` | | | | |
| Ghép GAM–GBM | | | | |

Kèm bootstrap CI cho mọi chênh lệch. Nhóm chia theo **quãng đường** và **giá thật** — cố định cho
mọi phương án.

---

# ❓ Câu hỏi cho mentor thứ 2

1. **Định nghĩa "chuyến giá cao" lúc train.** Dùng giá thật ở tập train là hợp lệ, nhưng lúc suy
   luận thì không biết giá thật. Vậy trọng số nên đặt theo quãng đường (quan sát được) hay theo giá
   thật (chỉ có lúc train)? Hai cách cho hai model khác nhau.

2. **Ngưỡng chấp nhận đánh đổi.** Nhóm hiếm giảm bao nhiêu điểm thì đáng để toàn tập xấu đi 0,1
   điểm? Nhóm `>15 km` chỉ chiếm 0,3% số chuyến nhưng là chuyến đắt tiền nhất — trọng số kinh doanh
   của nó không bằng trọng số theo số lượng.

3. **Dữ liệu thật có mức nhiễu báo giá tương đương bộ mô phỏng không?** Câu hỏi từ tuần 4 chưa được
   trả lời, và nó quyết định việc mở rộng phạm vi có nghĩa hay không.
