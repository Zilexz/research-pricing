# Feedback mentor — mổ xẻ từng đề xuất

> Bóc từ feedback tuần 3. Mỗi dòng trả lời bốn câu: **làm gì · vì sao · ra cái gì · đo bằng gì.**

---

## Thông điệp xuyên suốt

> Đừng báo cáo model **chính xác bao nhiêu**. Chỉ ra model **sai ở đâu**, **vì sao**, và
> **giá phản ứng thế nào với từng yếu tố**.

Từ nặng nhất: ***"thay vì chung chung model mình chính xác tới mức nào"*** — mentor đang gọi cách
báo cáo cũ là **mô tả**, và muốn chuyển sang **chẩn đoán**.

| | Cách cũ | Cách mentor muốn |
|---|---|---|
| Kiểu báo cáo | Mô tả — "MAE 18.048đ" | Chẩn đoán — sai ở đâu, sửa thế nào |
| Vai trò của giá | Thứ cần **dự đoán** | **Kết quả phản ứng** với thay đổi thị trường |
| Mục đích | Nộp báo cáo | **Ra quyết định** + demo đáng tin |

---

## Bảng chi tiết 8 đề xuất

### 1. Đừng average out — phân rã uncertainty theo mức giá

| | |
|---|---|
| **Mentor nói** | *"Uncertainty range 280k–320k cho 1 cuốc 300k sẽ có độ ảnh hưởng khác nhiều so với range 30–70k cho 1 cuốc 50k."* Kèm bảng yêu cầu điền |
| **Cần làm** | Chia tập test theo band giá dự đoán → tính riêng từng band: số chuyến · coverage · độ rộng trung vị · P90 độ rộng · độ rộng tương đối · tỷ lệ vượt cận trên/dưới |
| **Ý nghĩa** | Cùng "±30%" nhưng chuyến 50k ra khoảng 35–65k (còn dùng được), chuyến 300k ra 210–390k (vô dụng cho định giá). Con số trung bình **giấu mất nhóm bị phục vụ tệ nhất** |
| **Kết quả cần ra** | Bảng 6 band × 7 cột, cho cả 3 phương pháp × 3 mức tin cậy |
| **Đánh giá bằng** | **Lệch coverage tối đa giữa các band** (điểm %). Kèm sai số lấy mẫu để biết lệch có thật không |
| **Đã làm** | ✅ `uncertainty/01_conformal_chuan_hoa` mục 4 · `04_SO_SANH` mục 3 |
| **Kết quả thật** | Coverage tổng 89,6% nhưng **>300k chỉ 82,7%** — lệch **7,28 điểm**. Gốc: độ rộng tương đối **y hệt 60,2% ở cả 6 band** trong khi band >300k cần ±41,0% |

### 2. Vẽ giá theo thời gian, có dải uncertainty và chú thích

| | |
|---|---|
| **Mentor nói** | *"Plot price over time với 1 đường predicted + vùng uncertainty và 1 đường ground truth và có annotate rush hour hay weather… một cách **trực quan**"* |
| **Cần làm** | Chọn một ngày có biến động rõ · khống chế cùng dải quãng đường để loại nhiễu · gộp bucket 30 phút · vẽ 3 đường + tô nền cao điểm và mưa |
| **Ý nghĩa** | Từ **"trực quan"** là mấu chốt — mentor muốn **nhìn thấy**, không muốn đọc bảng. Sai số ở thời điểm critical quan trọng hơn sai số trung bình |
| **Kết quả cần ra** | Hình chuỗi thời gian 3 tầng: giá · sai số · coverage. Thêm sai số theo 24 giờ và theo đợt demand surge |
| **Đánh giá bằng** | Sai số tương đối và coverage ở **cao điểm vs giờ thường**; biên độ qua 24 giờ |
| **Đã làm** | ✅ `uncertainty/05_PHAN_RA_theo_thoi_gian` — hình `TT1`–`TT3` |
| **Kết quả thật** | Cao điểm 14,74% vs giờ thường 14,75%. Biên độ 24 giờ chỉ **3,8%**. Đợt surge sai số còn **giảm** nhẹ |

### 3. Ba kịch bản uncertainty — model mình thuộc loại nào

| | |
|---|---|
| **Mentor nói** | Ba model có MAE bằng nhau nhưng khác hẳn: đều 30% · 10% cao điểm–40% thường · 40% cao điểm–10% thường |
| **Cần làm** | Đo độ rộng khoảng riêng cho cao điểm và giờ thường, xếp model vào một trong ba. **Và vẽ cả ba kịch bản lên chính đường giá theo thời gian** — mentor nêu chúng ngay sau khi đòi plot price-over-time, nên chúng thuộc về cùng một hình |
| **Ý nghĩa** | MAE trung bình **không phân biệt được** ba model này, nhưng giá trị vận hành khác hẳn. Uncertainty thấp ở cao điểm = **chắc chắn ở đúng chỗ quan trọng** |
| **Kết quả cần ra** | Hình 4 cột (`TT4`) **+ hình 4 panel chuỗi thời gian** (`TT5`): cùng một ngày, cùng một đường giá thật, chỉ khác dải bất định. Kèm `TT6`: độ rộng mình **hứa** vs coverage mình **giữ được** |
| **Đánh giá bằng** | **Tỷ lệ độ rộng cao điểm / giờ thường**. Bằng 1 = kịch bản 1. Kèm coverage thực tế của từng kịch bản ở từng khung giờ |
| **Đã làm** | ✅ `TT4` · **`uncertainty/07_BA_KICH_BAN`** — hình `TT5`–`TT6` |
| **Kết quả thật** | **Kịch bản 1** — ±30,2% cao điểm vs ±30,1% giờ thường, tỷ lệ **1,004**. Tin **trung tính**: không mù ở chỗ quan trọng, nhưng cũng không có gì để khoe |

**Ba kịch bản chạy trên tập test thật (216.090 chuyến, lag 5 phút):**

| Kịch bản | ± cao điểm | coverage cao điểm | ± giờ thường | coverage giờ thường | ± trung bình | coverage chung |
|---|---:|---:|---:|---:|---:|---:|
| A · đều ±30% | 30,0% | 89,9% | 30,0% | 89,7% | 30,0% | 89,7% |
| B · ±10% CĐ / ±40% GT | 10,0% | **42,3%** | 40,0% | 96,3% | 32,0% | 81,9% |
| C · ±40% CĐ / ±10% GT | 40,0% | 96,5% | 10,0% | **42,3%** | 18,0% | 56,7% |
| **Model của mình** | 30,2% | **90,1%** | 30,1% | **89,7%** | 30,1% | 89,8% |

Ba điều chỉ nhìn hình mới thấy:

1. **Con số ±30% mentor đưa ra gần như trúng phóc.** Chạy thật, ±30% cho coverage 89,7% — sát mức cam kết 90%. Nói cách khác model mình *đang là* kịch bản A của mentor, không phải đại khái giống.
2. **Kịch bản B và C không phải "cùng MAE, khác phân bổ" — chúng hỏng.** Khung giờ được cấp ±10% chỉ giữ được **42,3%** coverage, hụt gần 48 điểm. Muốn hẹp ở cao điểm mà vẫn giữ 90% thì sai số **ở cao điểm phải nhỏ hơn thật sự**, chứ không phải khai hẹp lại. Dữ liệu nói sai số cao điểm và giờ thường bằng nhau (14,74% vs 14,75%), nên B và C **không tồn tại được** trên tập này.
3. **Chấm đỏ trong `TT5` bám coverage cấp chuyến, không phải "đường trung bình rơi ngoài dải".** Ở kịch bản B, đường giá trung bình vẫn nằm gọn trong dải suốt cao điểm dù coverage thật chỉ 42% — đúng kiểu trung bình hoá che mất vấn đề mà mentor cảnh báo ở comment 1.

### 4. Improve model hay giữ model rồi giảm uncertainty

| | |
|---|---|
| **Mentor nói** | *"Có insight này thì các em cũng sẽ dễ quyết định hơn là nên improve model hay là giữ model nhưng tìm cách giảm uncertainty"* |
| **Cần làm** | Thử **hết** cách hiệu chỉnh (không đụng model) rồi đo dư địa còn lại. Chỉ khi cạn mới kết luận phải improve model |
| **Ý nghĩa** | Hai đường chi phí khác nhau **cả chục lần**: hiệu chỉnh mất vài giờ, cải thiện model mất vài tuần. Chọn sai là đốt thời gian |
| **Kết quả cần ra** | Bảng so các cách hiệu chỉnh + **trần lý thuyết** (nếu biết trước độ khó từng chuyến thì hẹp được bao nhiêu) |
| **Đánh giá bằng** | **% thu hẹp được ở cùng mức coverage**. Kèm bằng chứng vì sao không hẹp thêm được |
| **Đã làm** | ✅ **`tuan_4/02_IMPROVE_HAY_GIAM_UNCERTAINTY`** (bản ra quyết định, hình `QD1`–`QD3`) · `uncertainty/06_thu_hep_khoang` (bản đào sâu, `TH1`–`TH5`) |
| **Kết quả thật** | Thử **5 cách × 7 nhóm**, tốt nhất **−0,43%**. Trần lý thuyết **−51%** nhưng độ lớn sai số **không dự đoán được** — GBM dự đoán độ khó chỉ đạt tương quan hạng **0,05** với sai số thật. ⇒ **Phải improve model** |
| **Bổ sung tuần 4** | Mondrian **không làm hẹp** nhưng **làm đều**: lệch coverage giữa các nhóm quãng đường **12,61 → 2,53 điểm**, tốn +0,04% độ rộng. Làm ngay, vài giờ, không train lại |

### 5. Model fail ở đâu, không phải chính xác tới mức nào

| | |
|---|---|
| **Mentor nói** | *"Đào sâu được vào là model mình đang fail ở đâu và làm sao để khắc phục thay vì chung chung model mình chính xác tới mức nào"* |
| **Cần làm** | Phân rã coverage theo **mọi chiều**: band giá · giờ · quãng đường · thời tiết. Tìm nhóm hụt nặng nhất rồi truy nguyên nhân |
| **Ý nghĩa** | Đây là khác biệt giữa **mô tả** và **chẩn đoán**. Biết fail ở đâu mới biết đầu tư vào đâu |
| **Kết quả cần ra** | Chỉ đích danh nhóm fail + nguyên nhân + cách sửa kèm chi phí |
| **Đánh giá bằng** | Lệch coverage tối đa theo từng chiều; sửa xong giảm còn bao nhiêu, tốn bao nhiêu độ rộng |
| **Đã làm** | ✅ **`model/evaluation/09_chan_doan_model`** — notebook riêng cho ý này. Thêm: `01_conformal_chuan_hoa` · `04_SO_SANH` · `05_PHAN_RA_theo_thoi_gian` |
| **Kết quả thật** | Xếp hạng 10 chiều bằng **η²** (tỷ lệ phương sai sai số giải thích được). Xem chi tiết dưới |

**Kết quả chẩn đoán (216.090 chuyến test độc lập, MAPE 14,65%):**

| Chiều | η² | MAPE thấp → cao | Kết luận |
|---|---:|---|---|
| **Quãng đường** | **0,0099** | 10,32% → 17,52% (>15 km) | 🔴 Chỗ hỏng nặng nhất |
| **Tuyến** | 0,0079 | 10,96% → 15,00% | 🔴 Tương quan với quãng đường **0,894** ⇒ cùng một nguyên nhân |
| Band giá | 0,0015 | 13,46% → 18,55% (>300k) | 🟠 Sửa bằng Mondrian |
| Loại xe · Giờ · Surge · Thời tiết · Cao điểm · Cuối tuần · Tháng | ≤0,0007 | biên độ 0,05–0,61 điểm | 🟢 Gần như vô dụng |

Bốn phát hiện đi ngược trực giác:

1. **Giờ cao điểm KHÔNG phải chỗ hỏng** (η² 0,0000, biên độ 0,05 điểm) — dù mentor nêu ba kịch bản uncertainty theo rush hour. Chiều thật sự quan trọng là quãng đường, mạnh gấp ~100 lần.
2. **Không có thiên lệch hệ thống.** Trung bình lệch +1,60% nhưng **trung vị +0,01%** và tỷ lệ đoán cao hơn thật **50,02%** ⇒ do đuôi phải của phân phối giá, không phải model lệch. Trừ đi một hằng số sẽ làm hỏng nửa số chuyến đoán thấp.
3. **Không có nhóm ngoại lai chi phối.** 1% chuyến sai nhất (sai ≥53,1%) chỉ đóng góp **2,7%** tổng sai số tuyệt đối. Không có phím tắt.
4. **Model tốt nhất ở chính band mà khoảng tin cậy hỏng nặng nhất.** Band >300k: hơn persistence **65,1%** (tốt nhất trong mọi band) nhưng coverage chỉ 82,7%. ⇒ Chỗ hỏng nằm ở **hiệu chỉnh khoảng**, không phải ở model — và Mondrian sửa được: **7,28 → 0,83 điểm**, tốn **+0,46%** độ rộng, không train lại.

### 6. Ceteris paribus — đổi 1 yếu tố, giữ nguyên phần còn lại

| | |
|---|---|
| **Mentor nói** | *"Nếu mình chỉ thay đổi 1 yếu tố nhưng fix các cái còn lại thì giá sẽ thay đổi thế nào… Ở các version pricing của bọn anh, bọn anh đều **measure price như là kết quả của một thay đổi của yếu tố thị trường**"* |
| **Cần làm** | Hai đường **độc lập**: ① hỏi model (partial dependence có kiểm soát) ② hỏi dữ liệu thật (ghép cặp chuyến giống nhau trừ một yếu tố). Rồi đối chiếu |
| **Ý nghĩa** | Đây không phải gợi ý phân tích thêm — đây là **cách team mentor nghĩ về bài toán**. Tuần 1 đo **tương quan**, cái này đo **thay đổi có kiểm soát**, gần nhân quả hơn |
| **Kết quả cần ra** | Bảng phản ứng giá: mỗi yếu tố đổi bao nhiêu thì giá đổi bao nhiêu, đi qua giá cơ bản hay hệ số nhân |
| **Đánh giá bằng** | **Model nói vs dữ liệu thật có khớp không.** Khớp ⇒ số đem đi demo được. Lệch ⇒ model học nhầm, và biết nhầm chỗ nào |
| **Đã làm** | ✅ **`tuan_4/03_CETERIS_PARIBUS_VA_CAUSALITY`** (hình `PU1` `PU2`) · `analysis/14_ceteris_paribus` (bản đào sâu, `CP1`–`CP9`) |
| **Kết quả thật** | Partial dependence: mưa model +0,93% vs thật +11,05% — **lệch 10 điểm**. Nhưng đo bằng ghép cặp thì model ra **+10,34%** vs thật **+10,30%**, khớp gần hoàn hảo |

**⚠️ Kết luận tuần 3 cần sửa lại.** Trước đây ghi *"model bám giá quan sát chứ không hiểu cơ chế"*.
Bằng chứng mới ở `tuan_4/03` cho thấy phát biểu đó **quá nặng**:

| Đo gì | Kết quả | Nghĩa là |
|---|---|---|
| Ghép cặp trên `hybrid_pred` | Mưa **+10,34%** vs thật +10,30% | Model **dự đoán đúng** phản ứng giá |
| Ghép cặp trên `persistence` (giá trễ, **mù thời tiết**) | **+8,99%** | 87% hiệu ứng đến miễn phí qua giá trễ — đây là cái "nạng" |
| Partial dependence (đổi riêng feature thời tiết) | **+0,93%** | Ở lag 5', model dồn gần hết trọng số vào nạng |
| **Rút nạng ra — lag 30'** | persistence tụt còn **+4,53%**, model vẫn **+9,97%** | Model **tự bù 94%** phần thiếu |

⇒ Phát biểu đúng: **model hiểu cơ chế, nhưng ưu tiên đường tắt khi đường tắt còn dùng được.** Đây
là hành vi hợp lý của một model tối ưu MAE, không phải lỗi. Hệ quả cho mục 7: việc cần làm không
phải *dạy* model cơ chế từ đầu, mà **buộc** nó dùng cơ chế nó đã có — train ở horizon dài hơn, hoặc
phạt sự phụ thuộc vào giá trễ. Rẻ hơn hẳn so với đổi kiến trúc.

**Bộ yếu tố đầy đủ mentor liệt kê** — `tuan_4/04_CAU_THANH_GIA`, 1,72 triệu chuyến gốc:

| Yếu tố | Giá đổi | Qua hệ số nhân | Đọc thế nào |
|---|---:|---:|---|
| **Cung–cầu (Q1→Q5)** | **+35,1%** | 80% | Mạnh nhất, gấp 3 lần cao điểm. Đúng *market signal multiplier* |
| Giờ cao điểm | +11,9% | 93% | Thuần điều tiết theo nhịp ngày |
| Đường tắc (chậm hơn TB, cùng km) | +16,5% | 16% | Đi vào **giá cơ bản** — chuyến lâu hơn |
| Trời mưa | +9,7% | 63% | Yếu tố **lai**: vừa tăng cầu, vừa làm tắc đường |
| Cuối tuần | +6,3% | 96% | Cầu giải trí |
| Dịch vụ Premium | −1,3% | — | Hai dịch vụ gần như cùng mức giá |
| **Ngày lễ** | **không có** | — | Kỳ dữ liệu chứa Tết 17/02/2026 nhưng ngày đó xếp **81/90** về giá |

**Quy luật xuyên suốt:** yếu tố **thị trường** đi qua hệ số nhân; yếu tố **cấu trúc chuyến** (quãng
đường, tắc đường) đi qua giá cơ bản. Mưa là ngoại lệ duy nhất vì nó tác động cả hai đường.

**⚠️ Hệ quả làm thay đổi kế hoạch improve model:**

| Mảnh bằng chứng | Nguồn |
|---|---|
| **98,9%** phương sai sai số nằm ở tầng **giá cơ bản**; hệ số nhân đã đạt MAPE **1,42%** | Phân rã log, `tuan_4/04` |
| **Mọi yếu tố thị trường** đi vào tầng hệ số nhân — tầng đã gần hoàn hảo | `tuan_4/04` mục 1–2 |
| Model giá cơ bản **đã chạm trần thông tin**: trần lý thuyết **14,98%**, model đạt **14,58%** | `tuan_4/04` mục 5 |

⇒ **Thêm feature thị trường sẽ không cải thiện độ chính xác giá cuối.** Các chuyến giống hệt nhau
về mọi thuộc tính quan sát được vẫn có giá cơ bản lệch nhau **~18%** — nhiễu bộ sinh dữ liệu bơm
vào từng báo giá, không có quy luật để học. **MAPE 14,65% rất gần sàn của bộ dữ liệu này.**

### 7. Encode causality vào model

| | |
|---|---|
| **Mentor nói** | *"Encode được causality info này vào 1 model sẽ khá là tốt trong việc improve accuracy hay uncertainty"* |
| **Cần làm** | ⏸️ **Chờ mentor chọn hướng** — ràng buộc đơn điệu / feature biến đổi / mô hình cấu trúc. Ba hướng khác nhau hoàn toàn về công sức |
| **Ý nghĩa** | Nếu model hiểu cơ chế thay vì bám giá quan sát, nó vừa dự đoán tốt hơn vừa **trả lời được câu what-if** — thứ hiện tại chưa làm được |
| **Kết quả cần ra** | Model có ràng buộc nhân quả + đo lại accuracy và độ rộng khoảng |
| **Đánh giá bằng** | MAE trước/sau · độ rộng khoảng trước/sau · **và** partial dependence có khớp dữ liệu thật hơn không |
| **Đã làm** | ⏸️ Chặn bởi câu hỏi cho mentor |
| **Đã chuẩn bị sẵn** | Đo được cái giá của việc này: model bỏ feature giá quan sát kém **8% MAE** (19.660 vs 18.208đ) nhưng hiệu ứng cao điểm bật từ +2,4% lên **+13,4%**, khớp thực tế |
| **Cập nhật tuần 4** | Việc này **rẻ hơn tưởng**. `tuan_4/03` cho thấy model **đã có** tín hiệu nhân quả — nó chỉ không dùng khi còn giá trễ để chép. Nên hướng thứ tư đáng cân nhắc trước ba hướng cũ: **train ở horizon dài hơn** hoặc phạt phụ thuộc giá trễ, thay vì đổi kiến trúc |

### 8. Trình bày as part of demo

| | |
|---|---|
| **Mentor nói** | *"Khi các em trình bày được những yếu tố này as part of demo thì kết quả của mình sẽ rất đáng tin cậy"* |
| **Cần làm** | Đưa dự đoán + khoảng tin cậy + giá thật vào một bản chạy được, người ngoài nhóm kỹ thuật xem hiểu ngay |
| **Ý nghĩa** | Hàm ý ngược lại: **kết quả hiện tại chưa đủ đáng tin để demo**. Một con số MAE từ hộp đen không thuyết phục ai |
| **Kết quả cần ra** | App chạy được, không cần cài đặt |
| **Đánh giá bằng** | Người không chuyên nhìn có hiểu không; có chỉ ra được điểm yếu của model ngay trên demo không |
| **Đã làm** | ✅ `demo/index.html` — bản đồ thật Phú Mỹ Hưng, nhiều xe chạy, coverage cập nhật trực tiếp |
| **Điểm mạnh** | Có nút bật/tắt hiệu chỉnh theo band → thấy ngay coverage nhóm >300k nhảy từ **84% lên 91%** |

### 9. Acceptance rate — hạ xuống side objective

| | |
|---|---|
| **Mentor nói** | *"Nên treat nó như một cái side objective… đừng đi sâu vào nó quá. Anh sẽ gửi data bổ sung"* |
| **Cần làm** | **Dừng** phát triển thêm. Giữ bản v1 + notebook trình bày. Chờ data |
| **Ý nghĩa** | Không phải làm sai — **sai thứ tự ưu tiên**. Mentor công nhận rào cản dữ liệu là thật (nên mới gửi data), nhưng forecast giá mới là trọng tâm |
| **Kết quả cần ra** | Giữ nguyên, không đầu tư thêm |
| **Đánh giá bằng** | Khi có data: kiểm có trường `outcome` và `exposure denominator` không |
| **Đã làm** | ✅ Đã dừng ở v1 |

---

## Tổng kết — kèm nguyên văn mentor nhắn

| # | Mentor nhắn nguyên văn | Đề xuất | Kết quả thật | Trạng thái |
|---|---|---|---|---|
| 1 | *"Các em đưa ra các % uncertainty nhưng mà trong report các em thường average out. Thì như vậy theo anh nó làm mất đi độ insight. Ví dụ như uncertainty range 280k-320k cho 1 cuốc 300k nó cũng sẽ có độ ảnh hưởng khác nhiều so với range 30-70k cho 1 cuốc 50k á. Vì vậy nên việc mình present những cái số này nó khá là quan trọng. Các em có thể fill vào cái bảng này chẳng hạn"* | Phân rã theo band giá | Coverage tổng 89,6% nhưng **>300k chỉ 82,7%** — lệch 7,28 điểm | ✅ |
| 2 | *"Việc các em plot ra price over time với 1 đường predicted + vùng uncertainty và 1 đường ground truth và có annotate rush hour hay weather cũng sẽ meaningful hơn là các em aggregate về một vài con số. Khi mình làm bài toán pricing thì có những đoạn critical ví dụ như rush hour hay demand surge và đo đạc được mức độ sai số ở những thời điểm nhạy cảm một cách trực quan anh nghĩ khá là quan trọng."* | Vẽ giá theo thời gian có chú thích | Cao điểm 14,74% vs giờ thường 14,75% · biên độ 24 giờ chỉ **3,8%** | ✅ |
| 3 | *"Ví dụ như 3 model này sẽ rất là khác nhau: một model uncertainty đều 30% so với giá predicted · một model uncertainty 10% ở rush hour - 40% ở normal hour · một model uncertainty 40% ở rush hour - 10% ở normal hour."* | Xác định model thuộc kịch bản nào | **Kịch bản 1** — ±30% cả hai khung (tỷ lệ 1,004). B và C không tồn tại được: khung ±10% chỉ giữ **42,3%** coverage | ✅ |
| 4 | *"Anh nghĩ là có insight này thì các em cũng sẽ dễ quyết định hơn là nên improve model hay là giữ model nhưng tìm cách giảm uncertainty."* | Đo dư địa của việc hiệu chỉnh | Thử 5 cách × 7 nhóm, tốt nhất **−0,43%** ⇒ **phải improve model** | ✅ |
| 5 | *"Việc mình forecast giá đối thủ mình cũng sẽ đào sâu được vào là: model mình đang fail ở đâu và làm sao để khắc phục thay vì là chung chung model mình chính xác tới mức nào."* | Chẩn đoán thay vì mô tả | **Fail theo QUÃNG ĐƯỜNG (η² 0,0099), không phải theo thời điểm (η² 0,0000).** Không thiên lệch hệ thống (trung vị +0,01%). Mondrian sửa coverage 7,28 → 0,83 điểm | ✅ `09_chan_doan_model` |
| 6 | *"Mình cũng nên nghiên cứu kỹ hơn các yếu tố nào cấu thành 1 mức giá (distance, weather, rush hour, public holiday, demand-supply, etc.) và nếu mình chỉ thay đổi 1 yếu tố nhưng fix các cái còn lại thì giá sẽ thay đổi thế nào. Ở week 1 các em phân tích impact của các variable rồi thì anh nghĩ đây là 1 cái natural step further."* | Ceteris paribus | Model **dự đoán đúng** (+10,34% vs thật +10,30%) nhưng ở lag ngắn chủ yếu **chép giá trễ**. Rút giá trễ ra thì nó tự bù **94%** ⇒ có hiểu cơ chế | ✅ |
| 7 | *"Khi mình thay đổi 1 feature thì price sẽ diễn biến thế nào và anh nghĩ encode được causality info này vào 1 model sẽ khá là tốt trong việc improve accuracy hay uncertainty. Ở các cái version pricing của bọn anh từ market signal multiplier đến personalized multiplier thì bọn anh đều measure price như là kết quả của một thay đổi của yếu tố thị trường."* | Encode causality vào model | Đã đo cái giá: bỏ feature giá quan sát kém **8% MAE** nhưng hiệu ứng cao điểm khớp thực tế | ⏸️ **Chờ mentor chọn hướng** |
| 8 | *"Khi các em trình bày được những yếu tố này as part of demo thì kết quả của mình sẽ rất đáng tin cậy."* | Đưa vào demo | App bản đồ thật, bật/tắt hiệu chỉnh thấy coverage >300k nhảy **84% → 91%** | ✅ |
| 9 | *"Còn về phần acceptance rate thì theo anh các em nên treat nó như một cái side objective. Anh sẽ gửi cho các em data bổ sung để làm bài này, tuy nhiên thì đừng đi sâu vào nó quá."* | Hạ acceptance xuống side objective | Đã dừng ở bản v1, giữ notebook trình bày | ✅ |

**8/9 xong. Còn đúng mục 7 bị chặn.**

---

## Nguyên văn toàn bộ feedback

> Tuần này anh thấy các em làm khá tốt, các em cũng bỏ ra khá nhiều effort cho các methodology
> đào sâu hơn vào uncertainty và cũng có những thông số cũng khá là meaningful.
>
> Tuy nhiên thì anh cũng có một số comment như sau:
>
> **+** Các em đưa ra các % uncertainty nhưng mà trong report các em thường average out. Thì như
> vậy theo anh nó làm mất đi độ insight. Ví dụ như uncertainty range 280k-320k cho 1 cuốc 300k
> nó cũng sẽ có độ ảnh hưởng khác nhiều so với range 30-70k cho 1 cuốc 50k á. Vì vậy nên việc
> mình present những cái số này nó khá là quan trọng. Các em có thể fill vào cái bảng này chẳng hạn
>
> **+** Cùng với comment trên thì anh nghĩ việc các em plot ra price over time với 1 đường
> predicted + vùng uncertainty và 1 đường ground truth và có annotate rush hour hay weather cũng
> sẽ meaningful hơn là các em aggregate về một vài con số. Khi mình làm bài toán pricing thì có
> những đoạn critical ví dụ như rush hour hay demand surge và đo đạc được mức độ sai số ở những
> thời điểm nhạy cảm một cách trực quan anh nghĩ khá là quan trọng. Ví dụ như 3 model này sẽ rất
> là khác nhau:
> - Một model uncertainty đều 30% so với giá predicted
> - Một model uncertainty 10% ở rush hour - 40% ở normal hour
> - Một model uncertainty 40% ở rush hour - 10% ở normal hour
>
> **+** Anh nghĩ là có insight này thì các em cũng sẽ dễ quyết định hơn là nên improve model hay
> là giữ model nhưng tìm cách giảm uncertainty. Đồng thời cũng từ insight này, việc mình forecast
> giá đối thủ mình cũng sẽ đào sâu được vào là: model mình đang fail ở đâu và làm sao để khắc
> phục thay vì là chung chung model mình chính xác tới mức nào.
>
> **+** Đồng thời thì mình cũng nên nghiên cứu kỹ hơn các yếu tố nào cấu thành 1 mức giá
> (distance, weather, rush hour, public holiday, demand-supply, etc.) và nếu mình chỉ thay đổi 1
> yếu tố nhưng fix các cái còn lại thì giá sẽ thay đổi thế nào. Ở week 1 các em phân tích impact
> của các variable rồi thì anh nghĩ đây là 1 cái natural step further. Khi mình thay đổi 1 feature
> thì price sẽ diễn biến thế nào và anh nghĩ encode được causality info này vào 1 model sẽ khá là
> tốt trong việc improve accuracy hay uncertainty. Ở các cái version pricing của bọn anh từ market
> signal multiplier đến personalized multiplier thì bọn anh đều measure price như là kết quả của
> một thay đổi của yếu tố thị trường.
>
> **+** Khi các em trình bày được những yếu tố này as part of demo thì kết quả của mình sẽ rất
> đáng tin cậy
>
> Còn về phần acceptance rate thì theo anh các em nên treat nó như một cái side objective. Anh sẽ
> gửi cho các em data bổ sung để làm bài này, tuy nhiên thì đừng đi sâu vào nó quá.

---

## Bốn câu cần hỏi mentor

| # | Câu hỏi | Chặn việc |
|---|---|---|
| **1** ⭐ | **Dữ liệu thật có mức nhiễu báo giá như bộ synthetic không?** Các chuyến giống hệt nhau vẫn lệch giá cơ bản ~18% | **Toàn bộ kế hoạch improve model** |
| **2** | Team ưu tiên **độ chính xác** hay **khả năng giải thích**? Model bỏ feature giá quan sát kém 8% MAE nhưng trả lời được what-if | Hướng đi cả tuần |
| **3** | *"Encode causality"* — ràng buộc đơn điệu, feature biến đổi, hay mô hình cấu trúc? | Mục 7 |
| **4** | Ngày lễ: bộ synthetic **không mô hình hoá** (Tết xếp 81/90 về giá). Dữ liệu thật có hiệu ứng này không? | Phần ngày lễ của mục 6 |
| **5** | Band giá chia theo mốc nào cho khớp team? Hiện tự chọn 50k/100k/150k/200k/300k | Mục 1 |

> Câu **1** giờ đáng hỏi nhất, thay chỗ câu về đánh đổi. Lý do: `tuan_4/04` cho thấy MAPE 14,65%
> **đã gần sàn của bộ dữ liệu**. Nếu dữ liệu thật cũng nhiễu như vậy thì mọi nỗ lực improve model
> là vô ích, và team nên chuyển toàn bộ công sức sang khả năng giải thích. Nếu dữ liệu thật sạch
> hơn thì toàn bộ kết luận này cần đo lại.
>
> Câu **2** vẫn quan trọng nhưng cán cân đã nghiêng: độ chính xác kịch trần ⇒ đánh đổi 8% MAE lấy
> khả năng what-if trở nên rẻ hơn nhiều so với lúc tưởng còn dư địa cải thiện.
