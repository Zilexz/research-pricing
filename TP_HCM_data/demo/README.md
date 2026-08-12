# Demo — mô phỏng dự báo giá đối thủ trên bản đồ

Bản demo trực quan để trình bày với người ngoài nhóm kỹ thuật. Chạy tập test qua model
và mô phỏng từng chuyến trên bản đồ thật khu Phú Mỹ Hưng, Quận 7.

## Cách mở

**Nháy đúp vào `index.html`.** Không cần cài gì, không cần chạy server — dữ liệu đã nhúng
sẵn trong file.

> ⚠️ **Cần mạng** để tải nền bản đồ (OpenStreetMap qua CARTO) và thư viện Leaflet.
> Không có mạng thì mọi thứ vẫn chạy, chỉ mất nền bản đồ.

## Có gì trên màn hình

| Khu vực | Nội dung |
|---|---|
| **Bản đồ** (trên trái) | 3 vùng nét đứt · nhiều xe chạy song song · vệt đường giữ lại 14 chuyến gần nhất, xanh = trúng khoảng, đỏ = trượt |
| **Ba biểu đồ** (dưới trái) | Xem mục dưới |
| **Chuyến đang theo dõi** (phải) | Giá dự đoán · thanh khoảng tin cậy · giá thật hiện khi xe tới nơi |
| **Dải thống kê** (phải) | Coverage · giá sai TB · độ rộng khoảng · trượt lên/xuống |
| **Nhật ký** (dải ngang dưới cùng) | 80 chuyến gần nhất, 11 cột |

## Ba biểu đồ — mỗi cái trả lời một câu

| Biểu đồ | Câu hỏi | Cách đọc |
|---|---|---|
| **Tán xạ dự đoán vs thật** | Dự đoán có sát giá thật không? | Mỗi chấm là một chuyến. Trục ngang = giá dự đoán, trục dọc = giá thật. **Càng bám đường chéo càng đúng.** Chấm đỏ = rơi ngoài khoảng |
| **Phân bố sai số** | Sai lệch tập trung ở đâu? | Cột chồng: xanh = nằm trong khoảng, đỏ = nằm ngoài. Lệch sang **phải** nghĩa là dự đoán cao hơn giá thật |
| **Coverage hội tụ** | Lời hứa có giữ được không? | Coverage tích luỹ tiến dần về vạch xanh (mức danh mục). Dải xanh nhạt = ±3 điểm |

> Bản trước dùng **đường nối 70 chuyến liên tiếp** — cách mã hoá đó sai, vì mỗi chuyến một tuyến
> một quãng đường khác nhau, nối lại thành đường gấp khúc không mang thông tin gì. Và hai biểu đồ
> "lệch %" với "lệch đồng" nói **cùng một chuyện** hai lần.

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

Dải thống kê bên phải lặp lại bốn số đó kèm độ rộng khoảng trung bình và tỷ lệ trượt lên/xuống.

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

Bước 3 → 4 là phần đáng cho xem nhất.

## Dữ liệu

| File | Nội dung |
|---|---|
| `du_lieu/chuyen.json` | 900 chuyến đại diện + 327 chuyến >300k, lấy từ **tập test** |
| `du_lieu/cauhinh.json` | Tham số `q` cho 3 mức × 6 band, hiệu chỉnh trên tập calibration |

Mỗi chuyến gồm: thời điểm · loại xe · thời tiết · điểm đón/trả · quãng đường · thời lượng ·
giá dự đoán · **giá thật** · giá cơ bản · hệ số nhân.

**Tập test chưa từng được dùng để huấn luyện hay hiệu chỉnh** — nên mọi con số trên màn hình
là dự đoán thật sự, không phải model đọc lại bài.

Mẫu 900 chuyến lấy phân tầng theo giờ × tuyến (mỗi ô tối đa 5 chuyến) nên trải đủ 24 giờ và
cả 9 tuyến. Nhóm >300k lấy **toàn bộ**, không lấy mẫu.

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
