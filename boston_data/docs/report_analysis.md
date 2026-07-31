# Báo cáo Tuần 1 — Study Relation: Feature ↔ Giá & Hệ số nhân

**Dự án:** Competitor Fare Forecasting (GSM) · **Người thực hiện:** Nguyễn Đức Hiếu (S.AI.20K) · **Ngày:** 23/07/2026
**Dữ liệu:** Uber & Lyft Boston (Kaggle) — 637.322 chuyến, 18 ngày (25/11–18/12/2018)

---

**Motivation:** Trước khi build model dự đoán giá đối thủ (mục ii), cần biết **feature nào thực
sự quyết định giá và hệ số nhân**. Giả thuyết ban đầu — *giờ cao điểm đắt hơn · trung tâm đắt
hơn · thời tiết xấu đẩy giá lên* — khi đo tương quan trực tiếp đều cho **|r| < 0,05**, gần như
bằng không. Mâu thuẫn với trực giác này đặt ra câu hỏi: *các yếu tố này thật sự không ảnh
hưởng, hay cách đo đang sai?*

> **Required distinction.** Giá thô bị **`loại xe × quãng đường` chi phối 70–76%**. Mọi so sánh
> giá theo khu/giờ/thời tiết **phải kiểm soát hai yếu tố này trước** — nếu không chỉ đang đo *cơ
> cấu chuyến đi*, không phải ảnh hưởng của yếu tố cần xét. (Bằng chứng: giá TB của khu tương
> quan **r = 0,986** với quãng đường TB của khu → chênh giá giữa khu gần như hoàn toàn do độ
> dài chuyến.)

**Contribution:** Tuần này tập trung trả lời câu hỏi **"What features determine price?"** bằng
phân tích quan hệ feature ↔ giá/hệ số nhân trên bộ dữ liệu, dùng **6 phương pháp có kiểm soát**
để không tin một chỉ số đơn lẻ. Từ đó rút ra bộ feature cho model mục ii, đồng thời phát hiện
một số **nhược điểm cấu trúc của dataset** chặn trần model — phần cần trao đổi để xin bổ sung data.

---

## 0. Bối cảnh & phạm vi tuần 1

Dự án gồm ba mục:

| Mục | Nội dung |
|---|---|
| **i** | **Study relation** — các key feature (thời tiết, thời gian, vị trí…) ảnh hưởng thế nào tới **giá** và **hệ số nhân** |
| ii | Build model dự đoán **giá + hệ số nhân**, cho **quan sát trễ** của giá đối thủ + ngữ cảnh |
| iii | **Uncertainty quantification** — xuất kèm khoảng dự đoán, vd *80% PI: [17,20 · 20,60]* |

**Phân công:** Nguyễn Đức Hiếu (S.AI.20K) **focus hơn vào mục ii** — build model forecast
competitor price (Chiến support). Vì vậy ở mục i, hướng phân tích của em **tập trung trả lời
"What features determine price?"** để phục vụ trực tiếp cho việc chọn feature ở mục ii.

> **Nhiệm vụ tuần 1:** hoàn thành **data analysis cho mục i**, và nếu kịp thời gian thì build
> thử một model đơn giản cho mục ii để kiểm chứng hướng đi.

---

## 1. Phân tích relation của các key feature với giá & hệ số nhân (trên bộ dữ liệu)

### 1.1 Hướng tiếp cận

Câu hỏi trọng tâm: **feature nào quyết định giá** (và phụ: yếu tố nào quyết định hệ số nhân).
Vấn đề gặp ngay từ đầu: đo tương quan thô cho kết quả sai lệch vì **giá bị `loại xe × quãng
đường` chi phối 70–76%** — mọi yếu tố ngữ cảnh (khu, giờ, thời tiết) đều bị hai biến này lấn át.
Do đó hướng tiếp cận là:

1. **Kiểm soát `quãng đường × loại xe` trước**, rồi mới đo phần biến động còn lại thuộc về yếu
   tố cần xét (nếu không, chỉ đang đo *cơ cấu chuyến đi* chứ không phải ảnh hưởng thật).
2. **Tách riêng Uber và Lyft** — hai công thức giá khác nhau (đơn giá/dặm chênh tới 11,5%; danh
   mục dịch vụ không trùng), gộp chung sẽ làm nhiễu kết luận.
3. **Đối chiếu chéo nhiều phương pháp**, không kết luận dựa trên một chỉ số.

### 1.2 Phương pháp thực hiện

| Phương pháp | Ý nghĩa (đo được gì) | Điểm mù cần lưu ý |
|---|---|---|
| Pearson / Spearman | Quan hệ tuyến tính / đơn điệu | Mù với quan hệ răng cưa (như giờ trong ngày) |
| Mutual Information | Quan hệ phi tuyến bất kỳ | Không cho biết chiều tác động |
| **Correlation ratio (η)** | Sức mạnh giải thích của **biến phân loại** (khu, giờ, thời tiết) | Bị thổi phồng nếu quá nhiều nhóm |
| Permutation importance | Feature mà **model thực sự** dùng | Bị chia phiếu khi feature trùng lặp |
| SHAP | Đóng góp từng dòng, có chiều | Chậm; lệch khi feature tương quan |
| **Hồi quy có kiểm soát** | **Hiệu ứng thuần** của từng yếu tố, tính bằng % sau khi trừ các yếu tố khác | Giả định dạng hàm |

> **Ý nghĩa của cách phối hợp:** dùng η + hồi quy kiểm soát làm *xương sống* (vì phần lớn
> feature là phân loại và quan hệ phi tuyến), rồi lấy các phương pháp còn lại để **kiểm chứng
> chéo**. Ví dụ `moonPhase` xếp hạng cao ở cả MI lẫn permutation nhưng vẫn là rác — chỉ lộ ra
> khi kiểm tra "proxy ngày" (1 giá trị/ngày). Không phương pháp đơn lẻ nào bắt được điều này.

---

## 2. Phân tích từng key feature với giá & hệ số nhân (trên bộ dữ liệu)

Ba nhóm feature ngữ cảnh được phân tích theo cùng một mạch: **cách phân tích → kết luận ảnh
hưởng tới giá và tới hệ số nhân → giải thích vì sao trong bộ dữ liệu yếu tố này lại ảnh hưởng
như vậy**. Nhắc lại: giá đo trên từng chuyến (đã kiểm soát quãng đường); hệ số nhân đo trên Lyft
ở cấp thị trường.

### 2.1 🕐 Thời gian (time)

**Cách phân tích.** Xem giá TB và tỷ lệ surge theo `hour_local` (0–23), theo thứ / cuối tuần;
kiểm tra dạng quan hệ (đơn điệu hay răng cưa); tách hai chiều *tần suất* (bao nhiêu % chuyến bị
surge) vs *cường độ* (khi surge thì mạnh bao nhiêu). Trực quan bằng biểu đồ quãng đường → giá tô
màu theo giờ (nếu giờ ảnh hưởng, chấm giờ cao điểm phải nằm cao hơn ở cùng quãng đường).

**Kết luận ảnh hưởng.**
- **→ Giá:** ảnh hưởng **rất yếu** — sau kiểm soát, biên độ giá theo giờ chỉ **0,58 điểm %**;
  trên biểu đồ quãng đường→giá, màu (giờ) trộn đều theo chiều dọc → giờ gần như không nâng/hạ giá.
  Giả thuyết "giờ cao điểm làm giá tăng" **bị bác bỏ với giá** trên bộ này.
- **→ Hệ số nhân:** ảnh hưởng **yếu nhưng có thật**, chỉ lên *thời điểm* xảy ra surge — tỷ lệ
  surge dao động **5,91% → 8,03% (1,36×)**, giờ cao điểm 8, 15, 17, 19, 21, 22; nhưng giờ **không**
  làm surge mạnh hơn (cường độ chỉ 1,04×).

**Vì sao trong bộ dữ liệu thời gian lại ảnh hưởng yếu như vậy?** Vì **số chuyến xe được lưu lại
ở các khung giờ gần như bằng nhau, ở mọi khu vực** → phân phối chuyến theo giờ **không phản ánh
được nhu cầu tại giờ cao điểm**. Bằng chứng:

| Phép đo | Giá trị | Ý nghĩa |
|---|---|---|
| CV số bản ghi theo giờ | **0,074** | Số chuyến gần như bằng nhau ở mọi khung giờ |
| CV số bản ghi theo (khu × giờ) | **0,081** | Trong từng khu, các giờ cũng đồng đều |
| Corr(số chuyến, tỷ lệ surge) | **0,015** | Số chuyến gần như độc lập với áp lực cầu |

Nguyên nhân gốc: dữ liệu là **lịch crawl API cố định** (thu giá đều đặn), không phải log đặt xe
thật — số bản ghi phản ánh *tần suất thu thập*, không phản ánh *có bao nhiêu người muốn đi*. Do
đó "giờ cao điểm" (vốn thể hiện qua lượng cầu tăng vọt) **không có cách nào hiện ra trong giá**.

![Số chuyến theo giờ gần như phẳng, trong khi tỷ lệ surge có đỉnh giờ cao điểm](fig_time_demand.png)

*Hình 1 — Trái: số bản ghi theo giờ gần như phẳng (CV=0,074). Phải: tỷ lệ surge theo giờ lại có
đỉnh rõ (giờ cao điểm). Hai đường không khớp nhau → số chuyến trong dataset không đo được nhu cầu.*

### 2.2 📍 Vị trí (location)

**Cách phân tích.** Xếp hạng 12 khu theo giá TB; vẽ chân dung từng khu (quãng đường × giá, tách
Uber/Lyft); so **premium thật** sau khi kiểm soát quãng đường; đo η của khu với tỷ lệ surge và
tách hai chiều tần suất vs cường độ theo khu.

**Kết luận ảnh hưởng.**
- **→ Giá:** ảnh hưởng **yếu và gián tiếp** — xếp hạng giá thô cho Boston University đắt nhất
  (18,86 USD), Haymarket Square rẻ nhất (13,58 USD), nhưng **giá TB của khu tương quan r = 0,986
  với quãng đường TB của khu** → chênh gần như hoàn toàn do độ dài chuyến. Sau kiểm soát, biên độ
  chênh thật giữa 12 khu chỉ còn **~15 điểm %**.
- **→ Hệ số nhân:** **mạnh nhất** trong các feature (η = 0,152) — chênh **7,4×** giữa Back Bay
  (11,19%) và North End (1,52%); tần suất & cường độ đi cùng nhau theo khu (r = 0,954). Đáng chú
  ý: **trung tâm không hề surge nhiều hơn** (5,73%) so với khu ngoại vi/đại học (10,10%).

**Vì sao trong bộ dữ liệu vị trí ảnh hưởng ít tới giá nhưng nhiều tới surge?** Vì **vùng thu thập
quá hẹp** — 12 khu đều nằm trong lõi trung tâm Boston (bao lồi **6,7 km²**, bán kính ~5 km, đều
là khu mật độ cao). Khi mọi điểm đón đều "cùng một kiểu" trung tâm, **cơ cấu giá giữa chúng gần
như đồng nhất** → ảnh hưởng của vị trí lên *giá* bị nén xuống chỉ còn 14–17% (và phần lớn là do
quãng đường). Nhưng với *surge*, mỗi khu vẫn có mức khan hiếm xe nội tại khác nhau (Back Bay đông
đúc vs North End yên tĩnh) → vị trí vẫn là tín hiệu mạnh nhất. Kết luận về giá vì thế **chỉ đúng
với phạm vi nội đô hẹp này**, không mở rộng cho sân bay / liên quận xa / ngoại ô.

### 2.3 🌦️ Thời tiết (weather)

**Cách phân tích.** Gộp các kiểu thời tiết theo `short_summary` (Clear, Rain, Foggy, Drizzle…);
so giá TB (trong cùng dải quãng đường) và tỷ lệ surge giữa các nhóm; **kiểm tra số ngày** mỗi
kiểu thời tiết xuất hiện để đánh giá độ tin cậy.

**Kết luận ảnh hưởng.**
- **→ Giá:** **không đo được ảnh hưởng đáng tin** — biên độ giá giữa 9 kiểu thời tiết chỉ **1,3–1,6%**.
- **→ Hệ số nhân:** tương tự, η chỉ **0,010**, biên độ tỷ lệ surge ~1,25× — không đáng kể.

**Vì sao trong bộ dữ liệu thời tiết gần như không đo được?** Hai lý do:
1. **Thiếu số ngày mưa để tách tín hiệu.** `Drizzle` chỉ xuất hiện **2 ngày**, `Rain`/`Foggy`
   **3 ngày** trong 18 ngày → biến thời tiết **lẫn hoàn toàn với hiệu ứng ngày** (không tách được
   đâu là do mưa, đâu là do đặc điểm riêng của đúng ngày đó).
2. **Thiếu hai mắt xích trung gian.** Ngoài đời thời tiết tác động tới giá qua *(a)* cung–cầu
   (mưa → cung < cầu → surge ↑) và *(b)* thời lượng (mưa → tắc đường → thời gian ↑ → cước ↑). Bộ
   Boston **không có** cả tín hiệu cung–cầu lẫn cột thời lượng, nên hai đường ảnh hưởng này bị đứt.

> ⚠️ Đây **không** phải bằng chứng "thời tiết vô hại". Trên dữ liệu GSM (khí hậu Việt Nam, mùa
> mưa rõ, có đủ cung–cầu & thời lượng), ảnh hưởng của thời tiết **phải được đánh giá lại**.

---

## 3. Tổng hợp: feature nào quyết định giá, feature nào quyết định hệ số nhân

### 3.1 Kết quả phân tích — feature nào quyết định GIÁ

Thước đo: **% phổ giá mà mỗi yếu tố giải thích được, sau khi đã kiểm soát quãng đường**.

| Nhóm yếu tố | → GIÁ (% phổ giá, sau kiểm soát) | Diễn giải trên bộ dữ liệu hiện tại |
|---|---|---|
| 🚗 **Loại xe (`name`)** | **70–76%** | Yếu tố quyết định áp đảo — bậc giá của hạng xe |
| 📏 **Quãng đường (`distance`)** | *(kiểm soát nền)* | Cùng `name` đã cho R² 0,90–0,95; là trục giá cơ sở |
| 📍 Khu vực đón (`source`) | 14–17% | Sau kiểm soát chỉ còn ~15 điểm % chênh thật giữa 12 khu |
| 📍 Điểm đến (`destination`) | 12–16% | Tương tự khu đón |
| 🕐 Giờ (`hour_local`) | ~5% (biên độ **0,58 điểm %**) | Ảnh hưởng tới giá **rất yếu** |
| 🌦️ Thời tiết | ~5% | Biên độ 1,3–1,6%; còn lẫn với hiệu ứng ngày |
| 📅 Thứ / cuối tuần | ~3% | Không đáng kể |

**Kết quả:** trên bộ dữ liệu này, **giá gần như được quyết định hoàn toàn bởi thuộc tính chuyến
đi (loại xe + quãng đường)**. Các yếu tố ngữ cảnh (khu vực, giờ, thời tiết) đóng góp rất ít vào
giá — khác hẳn các giả thiết ban đầu là các key feature (giờ cao điểm, vị trí, thời tiết) sẽ có
tác động vào sự thay đổi về giá của các cuốc xe.

### 3.2 Kết quả phụ — feature nào quyết định HỆ SỐ NHÂN

(Chỉ đo được trên Lyft; Uber toàn bộ `surge=1.0`.) Thước đo: η trên bảng cấp thị trường.

| Nhóm yếu tố | → HỆ SỐ NHÂN (η) | Diễn giải |
|---|---|---|
| 📍 **Khu vực đón** | **0,152** ⭐ | Mạnh nhất — chênh **7,4×** giữa Back Bay (11,19%) và North End (1,52%) tỷ lệ surge |
| 📍 Điểm đến | 0,019 | Yếu |
| 🕐 Giờ | 0,011 | Tác động lên *tần suất* surge (1,28×) nhưng không lên *cường độ* (1,04×) |
| 🌦️ Thời tiết | 0,010 | Không đo được đáng tin (lẫn hiệu ứng ngày) |

**Đọc kết quả:** hệ số nhân do **bối cảnh thị trường (vị trí)** quyết định là chính, nhưng
**không dai dẳng** (giờ trước có surge chỉ làm tăng 1,27× khả năng giờ này surge) — trái ngược
với giá vốn rất dai dẳng (r=0,903). Đây là tín hiệu sớm cho thấy hệ số nhân **khó dự đoán** bằng
lag, cần tín hiệu cung–cầu thời gian thực (làm rõ ở mục ii/iii).

### 3.3 Chốt lại

> **Giá và hệ số nhân do hai nhóm yếu tố khác nhau quyết định:** giá ← *thuộc tính chuyến đi*
> (loại xe + quãng đường); hệ số nhân ← *bối cảnh thị trường* (vị trí). → **Phải tách thành hai
> model, hai bộ feature** cho mục ii.
