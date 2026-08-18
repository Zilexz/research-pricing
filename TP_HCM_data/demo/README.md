# Demo — mô phỏng dự báo giá đối thủ trên bản đồ

Bản demo trực quan để trình bày với người ngoài nhóm kỹ thuật. Chạy tập test qua model
và mô phỏng từng chuyến trên bản đồ thật khu Phú Mỹ Hưng, Quận 7.

## Cách mở

**Nháy đúp vào `index.html`.** Không cần cài gì, không cần chạy server — dữ liệu đã nhúng
sẵn trong file.

> ⚠️ **Cần mạng** để tải nền bản đồ (OpenStreetMap qua CARTO) và thư viện Leaflet.
> Không có mạng thì mọi thứ vẫn chạy, chỉ mất nền bản đồ.

Giao diện chiếm trọn một màn hình, không cuộn. Chiều cao bản đồ, biểu đồ và nhật ký **co theo
chiều cao cửa sổ**, nên màn hình 768px hay 1080px đều nhìn đủ ba khu. Đã kiểm từ 620px trở lên.
Nếu cửa sổ hẹp dưới 1200px thì bố cục tự xếp dọc và cả trang chuyển sang cuộn.

## Có gì trên màn hình

| Khu vực | Nội dung |
|---|---|
| **Bản đồ** (trên trái) | 3 vùng nét đứt · nhiều xe chạy song song · vệt đường giữ lại 14 chuyến gần nhất, xanh = trúng khoảng, đỏ = trượt |
| **Ba bảng biểu đồ** (dưới trái) | Chuyển bằng tab. Xem mục dưới |
| **Chuyến đang theo dõi** (phải) | Giá dự đoán · thanh khoảng tin cậy · giá thật hiện khi xe tới nơi |
| **Dải thống kê** (phải) | Coverage · giá sai TB · độ rộng khoảng · trượt lên/xuống · đối chiếu baseline |
| **Nhật ký** (dải ngang dưới cùng) | 80 chuyến gần nhất, 11 cột |

## Ba bảng biểu đồ

Khu biểu đồ dưới bản đồ có **ba tab**, mỗi tab trả lời một câu hỏi khác nhau. Mọi biểu đồ cập
nhật trực tiếp theo từng chuyến chạy xong, và vẽ lại từ đầu khi đổi cấu hình.

Chú giải màu nằm ngay bên phải thanh tab, đổi theo tab đang mở.

### Tab 1 — Dự đoán giá

| Biểu đồ | Câu hỏi | Cách đọc |
|---|---|---|
| **Tán xạ dự đoán vs thật** | Dự đoán có sát giá thật không? | Mỗi chấm là một chuyến. Trục ngang = giá dự đoán, trục dọc = giá thật. **Càng bám đường chéo càng đúng.** Chấm đỏ = rơi ngoài khoảng |
| **Phân bố sai số** | Sai lệch tập trung ở đâu? | Cột chồng: xanh = nằm trong khoảng, đỏ = nằm ngoài. Lệch sang **phải** nghĩa là dự đoán cao hơn giá thật |
| **Model vs baseline** | Hơn cách làm ngây thơ bao nhiêu? | Hai đường sai số tích luỹ: xanh = model, xám đứt = persistence (lấy luôn giá quan sát gần nhất). Vùng xanh nhạt giữa hai đường là phần model ăn được |

> Bản trước dùng **đường nối 70 chuyến liên tiếp** — cách mã hoá đó sai, vì mỗi chuyến một tuyến
> một quãng đường khác nhau, nối lại thành đường gấp khúc không mang thông tin gì. Và hai biểu đồ
> "lệch %" với "lệch đồng" nói **cùng một chuyện** hai lần.

### Tab 2 — Sai lệch theo bối cảnh

Bốn biểu đồ cột, cùng một cách đọc: mỗi cột là sai số trung bình của một nhóm, **vạch đứt ngang
là sai số chung** của toàn bộ chuyến đã chạy. Cột **xanh** là quanh mức chung, cột **đỏ** là tệ
hơn mức chung trên 12% — đó là chỗ model đang yếu.

| Chia theo | Nhóm |
|---|---|
| Mức giá | 6 band, từ `<50k` đến `>300k` |
| Khung giờ | 0–5 · 6–9 · 10–12 · 13–16 · 17–19 · 20–23 (giờ Việt Nam) |
| Quãng đường | `<2` · 2–5 · 5–8 · 8–12 · `>12` km |
| Thời tiết | Quang · Mây · Mưa · Khác |

Nhóm chưa đủ **5 chuyến** hiện thành vạch xám nhạt, không ghi số — quá ít mẫu thì mọi kết luận
đều là nhiễu.

Đây là bảng trả lời câu *model đang sai ở đâu, sai nhiều chỗ nào và ít chỗ nào*. Cho chạy ở nhóm
`đại diện` tới ~200 chuyến rồi đọc: quãng đường tách nhóm rõ hơn hẳn khung giờ.

### Tab 3 — Khoảng tin cậy

| Biểu đồ | Cách đọc |
|---|---|
| **Coverage hội tụ** | Coverage tích luỹ tiến dần về vạch xanh (mức đã hứa). Dải xanh nhạt là sai số lấy mẫu, **co dần** khi số chuyến tăng — không phải dải ±3 điểm cố định. Chỉ vẽ từ chuyến thứ 20 trở đi: dưới ngưỡng đó coverage là nhiễu thuần, vẽ vào chỉ làm bẹp phần còn lại của đường |
| **Coverage theo mức giá** | Cột đo **lệch so với mức đã hứa**, không phải từ 0. Xanh = đúng lời hứa trong phạm vi sai số mẫu · đỏ = hụt · cam = thừa (khoảng rộng quá) |
| **Khoảng rộng bao nhiêu** | Cột cam = `±q%` của từng band, số xám dưới cột = độ rộng tuyệt đối theo đồng |
| **Coverage theo bối cảnh** | Bốn ô cao điểm × mưa — đúng hai chiều mentor hỏi. Đọc giống biểu đồ coverage theo mức giá |

Hai biểu đồ coverage cố tình vẽ lệch quanh mức đã hứa thay vì từ 0: nếu vẽ từ 0 thì mọi cột đều
~90% và nhìn y hệt nhau, đúng cái bẫy "trung bình che mất chi tiết" mà tab này sinh ra để phá.

Thanh khoảng cho thấy đúng thứ đang bán: **cận dưới — dự đoán — cận trên**, rồi vạch đen
là giá thật khi tới nơi. Xanh nghĩa là nằm trong khoảng, đỏ là ra ngoài.

Thẻ bên phải theo dõi **một** xe tại một thời điểm. Khi xe đó tới nơi, kết quả giữ trên màn
hình 1,5 giây rồi thẻ chuyển sang xe kế. Các xe còn lại vẫn chạy và vẫn được tính vào thống kê.

## Điểm đón/trả ngẫu nhiên trong vùng

Mỗi chuyến sinh một điểm đón và một điểm trả **ngẫu nhiên trong bán kính 620 m** quanh mỗi khu
(vòng nét đứt trên bản đồ), rải đều trên mặt đĩa.

> ⚠️ Đây **chỉ để nhìn cho sinh động**. Dữ liệu gốc chỉ có 3 toạ độ cố định, nên quãng đường,
> thời lượng và giá **không đổi** theo vị trí rải. Nói rõ chỗ này nếu bị hỏi — đừng để người
> xem tưởng model dự đoán được theo từng địa chỉ.

Điểm rải dùng ngẫu nhiên **có hạt giống** theo số thứ tự chuyến, nên chạy lại vẫn ra đúng vị
trí cũ.

## Điều khiển

| Nút | Ý nghĩa |
|---|---|
| **▶ Chạy liên tục** | Thả xe mới cho tới khi chạm mốc dừng hoặc bấm tạm dừng |
| **⏭ Một chuyến** | Chỉ thả thêm đúng một xe rồi thôi |
| **↺ Đặt lại** | Xoá sạch thống kê, bản đồ và nhật ký |
| **Tốc độ** | 1× đến 8× — thời gian bay tỷ lệ với thời lượng chuyến thật |
| **Số xe** | 1 / 4 / 8 xe chạy cùng lúc |
| **Dừng sau** | 50 / 200 / hết mẫu / không dừng |
| **Độ tin cậy** | 70 / 80 / 90% — hạ mức thì khoảng hẹp lại nhưng trượt nhiều hơn |
| **Hiệu chỉnh** | `q chung` (một tỷ lệ cho mọi chuyến) ↔ `theo band giá` (Mondrian) |
| **Nhóm chuyến** | `đại diện` (900 chuyến ngẫu nhiên) ↔ `chỉ chuyến >300k` (toàn bộ 327 chuyến) |

**Mặc định dừng sau 200 chuyến** rồi in tổng kết. Bấm ▶ lần nữa thì chạy tiếp thêm 200 chuyến.
Chọn `không dừng` nếu muốn để chạy nền lúc thuyết trình.

Đổi **độ tin cậy**, **hiệu chỉnh**, **nhóm chuyến** hoặc **mốc dừng** sẽ xoá thống kê và bắt
đầu lại — vì trộn hai cấu hình vào cùng một con số coverage là vô nghĩa.

## Đọc số ở đâu

Bốn chỉ số quan trọng nằm ngay **thanh trên cùng**, luôn nhìn thấy dù cuộn thế nào:

| Chip | Nghĩa |
|---|---|
| Đang chạy **N** xe | Số xe đang trên đường |
| Đã xong **N / M** | Tiến độ so với mốc dừng |
| Coverage **x%** | Tỷ lệ giá thật rơi trong khoảng — so với danh mục đang chọn |
| Giá sai TB **x%** | Trung bình `|dự đoán − thật| / thật` |

Dải thống kê bên phải lặp lại bốn số đó kèm độ rộng khoảng trung bình, tỷ lệ trượt lên/xuống, và
một dòng đối chiếu với **baseline persistence** — cách làm ngây thơ nhất là lấy luôn giá quan sát
gần nhất làm dự báo. Con số "tốt hơn x%" là lý do model tồn tại; nếu nó tụt về 0 thì model không
đáng chạy.

**Nhật ký** ở dải ngang dưới cùng, 11 cột:

| Cột | Nội dung |
|---|---|
| ● | Xanh = trúng khoảng · đỏ = trượt |
| Giờ · Tuyến · Km | Bối cảnh chuyến |
| Bối cảnh | Loại xe · thời tiết · có phải cao điểm không |
| Giá cơ bản × hệ số | Phân rã theo kiến trúc Hybrid |
| Dự đoán · Khoảng tin cậy · Giá thật | Ba con số cần so |
| Lệch | `+` = dự đoán **cao hơn** giá thật, tô đỏ khi vượt 15% |
| Kết quả | `trong khoảng` · `vượt trên` · `thấp hơn` |

## Kịch bản nên demo

**1. Cho chạy ở mặc định** (đại diện · 90% · theo band). Sau ~40 chuyến, coverage sẽ hội tụ
quanh 90%. Ý: *model không chỉ đoán một con số, nó nói luôn mình chắc chắn tới đâu — và lời
hứa đó giữ được.*

**2. Hạ độ tin cậy xuống 70%.** Khoảng hẹp đi rõ rệt, nhưng cứ 10 chuyến thì 3 chuyến ra ngoài.
Ý: *đây là nút đánh đổi, không phải nút cải thiện.*

**3. Chuyển sang `chỉ chuyến >300k`, để `q chung`.** Coverage rơi xuống **~84%** dù danh mục
là 90%. Ý: *con số trung bình che mất chuyện nhóm khách đắt tiền nhất bị phục vụ tệ nhất.*

**4. Vẫn nhóm đó, bấm sang `theo band giá`.** Coverage bật lên **~91%**. Ý: *sửa được mà
không cần train lại model — chỉ cần hiệu chỉnh riêng cho từng nhóm giá.*

Bước 3 → 4 là phần đáng cho xem nhất. Mở tab **Khoảng tin cậy** trong lúc bấm qua lại thì thấy
luôn cái giá phải trả: cột `>300k` ở biểu đồ độ rộng nhảy từ **±30,1%** lên **±41,0%**. Coverage
không tự nhiên mà có — nó đổi bằng khoảng rộng hơn.

**5. Về nhóm `đại diện`, chạy ~200 chuyến, mở tab `Sai lệch theo bối cảnh`.** Bốn biểu đồ cột
cho thấy sai số tách nhóm rất rõ theo **quãng đường** và **mức giá**, gần như không tách theo
**khung giờ**. Ý: *model không yếu vào giờ cao điểm như trực giác — nó yếu ở chuyến dài và chuyến
đắt.* Đây là kết quả chính của tuần 4, và demo dựng lại được nó ngay trước mặt người xem.

## Dữ liệu

| File | Nội dung |
|---|---|
| `du_lieu/chuyen.json` | 900 chuyến đại diện + 327 chuyến >300k, lấy từ **tập test** |
| `du_lieu/cauhinh.json` | Tham số `q` cho 3 mức × 6 band, hiệu chỉnh trên tập calibration |

Mỗi chuyến gồm: thời điểm · loại xe · thời tiết · điểm đón/trả · quãng đường · thời lượng ·
giá dự đoán · **giá thật** · giá cơ bản · hệ số nhân · **dự báo persistence** (dùng cho biểu đồ
đối chiếu baseline).

**Tập test chưa từng được dùng để huấn luyện hay hiệu chỉnh** — nên mọi con số trên màn hình
là dự đoán thật sự, không phải model đọc lại bài.

Mẫu 900 chuyến lấy phân tầng theo giờ × tuyến (mỗi ô tối đa 5 chuyến) nên trải đủ 24 giờ và
cả 9 tuyến. Nhóm >300k lấy **toàn bộ**, không lấy mẫu.

## Ảnh chạy thử

`anh_chay_thu/` là ảnh chụp màn hình của một lượt chạy thật (Chromium, 1920×800), dùng để đối
chiếu khi nghi demo hiển thị sai:

| Ảnh | Cấu hình |
|---|---|
| `01_tab_du_doan_gia` · `02_tab_sai_lech` · `03_tab_tin_cay` | đại diện · 90% · theo band · 200 chuyến |
| `04_dat_q_chung` → `05_dat_theo_band` | `>300k`, bước 3 → 4 của kịch bản |
| `06_muc_70` | đại diện · 70% |

## Sinh lại dữ liệu

Hai script trong thư mục tạm của phiên làm việc:
`xuat_demo.py` (đọc parquet → JSON) rồi `gen_demo_html.py` (nhúng JSON vào HTML).

Cần chạy lại khi model được train lại — nếu không, demo sẽ hiển thị dự đoán cũ.

## Hạn chế cần nói trước nếu bị hỏi

| | |
|---|---|
| Điểm đón/trả **rải ngẫu nhiên** trong vùng | Chỉ để nhìn — quãng đường và giá lấy từ dữ liệu gốc, không tính lại theo toạ độ rải |
| Đường đi là **đường cong nội suy**, không phải lộ trình thật | Dữ liệu chỉ có điểm đầu/cuối, không có polyline |
| Chỉ **3 khu vực** | Dữ liệu tổng hợp chỉ phát sinh quanh 3 điểm này |
| Thời gian chạy **không theo tỷ lệ thật** | Đã nén lại để xem được nhiều chuyến trong ít phút |
