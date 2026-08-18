# Thử nghiệm Transformer — dự báo giá đối thủ

> Trả lời câu hỏi của anh Khoa: *"Các em đã test thử neural network transformer thử chưa?"*

---

## ✅ ĐÃ CHẠY XONG — kết quả: HOÀ

Notebook đã chạy: **`pricing-tranfomer.ipynb`** (bản tải về từ Kaggle, có đủ output).

| | Hybrid | Transformer | Chênh |
|---|---:|---:|---|
| MAE | 18.048đ | **18.008đ** | −0,22% *(transformer tốt hơn)* |
| MAPE | **14,74%** | 14,80% | +0,06 điểm *(transformer tệ hơn)* |
| R² | ~0,73 | 0,7326 | ngang |
| Tham số | — | 90.792 | |
| Train | ~9 ph CPU | ~35 ph GPU T4 | |

Từng tháng (test 864.360 chuyến):

| Tháng | MAE | MAPE | R² | n |
|---|---:|---:|---:|---:|
| 1 | 17.846đ | 14,87% | 0,7341 | 315.360 |
| 2 | 17.868đ | 14,76% | 0,7351 | 234.632 |
| 3 | 18.275đ | 14,76% | 0,7287 | 314.368 |
| **Gộp** | **18.008đ** | **14,80%** | **0,7326** | **864.360** |

⚠️ **Notebook tự kết luận *"THẮNG Hybrid 0,22%"* — đó là đọc thiếu.** Nó chỉ so MAE. Đọc cả MAPE thì
transformer tệ hơn 0,06 điểm. Hai metric đi ngược nhau nghĩa là hai model chỉ **phân bổ sai số khác
nhau** (MAE ưu ái chuyến đắt, MAPE ưu ái chuyến rẻ), không phải một cái giỏi hơn. Chênh 0,22% cũng
nằm gọn trong dải 1,9% giữa 4 thuật toán cây.

**Band `>300k` vẫn tệ nhất** (MAPE 18,06% vs 18,55% của Hybrid) — cùng một chỗ hỏng, kiến trúc khác
hẳn cũng không sửa được.

### Kết luận

> Transformer đọc thẳng chuỗi 32 báo giá **không moi thêm được thông tin nào** so với ba con số
> `mean/std/slope`. Đúng như test rẻ đã dự đoán ở dưới.
>
> **Không đưa vào pipeline** — đổi 0,22% MAE lấy một model cần GPU, gấp 4 lần thời gian train, và
> phải lưu thêm thống kê chuẩn hoá khi phục vụ.
>
> Kết quả này **củng cố** kết luận model đã chạm trần dữ liệu: nút thắt là **dữ liệu**, không phải
> sức chứa của model.

Chi tiết đầy đủ: `docs/TECH_DOC.md` §14.4.

---

## Bối cảnh: test rẻ đã dự đoán đúng kết quả này

Trước khi bro tốn công đẩy lên Kaggle, tôi đã chạy **test rẻ** trên máy — train 400.000 mẫu,
đánh giá trên **toàn bộ test tháng 3** (314.368 chuyến), baseline dùng **đủ bộ feature
production**:

| Bộ feature | MAE | MAPE |
|---|---:|---:|
| A. Chỉ feature cơ bản (không có lịch sử giá) | 19.258đ | 15,34% |
| **B. + nhóm tổng hợp** *(qs_\* và h60_\*)* — mốc | **18.407đ** | 14,81% |
| C. + chuỗi 32 báo giá thô *(bỏ nhóm tổng hợp)* | 18.397đ | 14,81% |
| D. + cả hai | 18.402đ | 14,81% |

**Đọc bảng này:**

- Lịch sử giá **có giá trị thật** — bỏ đi thì tệ hơn **4,4%**
- Nhưng **chuỗi thô và nhóm tổng hợp cho kết quả y hệt nhau** (−0,1%)
- Nhét cả hai vào **không giúp gì** (−0,0%)

⇒ Nhóm tổng hợp `mean/std/slope` + giá quan sát gần nhất đã là **thống kê đủ** cho chuỗi.
Không còn thông tin nào trong chuỗi thô mà chúng chưa nắm được.

**Transformer đọc chuỗi sẽ không có gì mới để đọc.** Nếu LightGBM — vốn rất mạnh với dữ liệu
bảng — không moi được gì từ 32 giá lag, khả năng transformer moi được là rất thấp.

### Đã chạy — và test rẻ dự đoán đúng

Test rẻ nói *"chuỗi thô không thêm gì so với nhóm tổng hợp"*. Chạy đầy đủ trên 864.360 chuyến test
xác nhận: MAE −0,22%, MAPE +0,06 điểm — hoà.

Vẫn đáng chạy, vì trả lời *"bọn em đã thử, đây là số"* mạnh hơn nhiều so với *"bọn em suy luận là
không đáng"*. Và kết quả hoà cũng là kết quả có giá trị: nó chốt được rằng model đã chạm trần dữ
liệu bằng một kiến trúc hoàn toàn khác.

---

## Có gì trong thư mục này

```
transformer/
├── README.md                    file này
├── kaggle_transformer.ipynb     notebook để đẩy lên Kaggle
└── du_lieu/                     175 MB — đẩy lên làm Kaggle Dataset
    ├── mau.parquet              6.897.051 mẫu · 155 MB
    ├── bao_gia.parquet          1.724.714 báo giá · 20 MB
    └── meta.json                mã hoá danh mục, mô tả cột
```

### Dữ liệu có đủ không

**Đủ số dòng:** `mau.parquet` giữ nguyên toàn bộ 6.897.051 dòng của `hcm_train_ready.parquet` —
cả 4 mức lag, cả 4 split (train 4.641.799 · calibration 615.908 · test 864.360 ·
validation 774.984).

**Cột thì lọc:** lấy 28/72 cột. Bỏ 44 cột **không nằm trong bộ feature production** — 19 cột thời
tiết chi tiết (nhiệt độ, độ ẩm, gió, áp suất...), toạ độ, hex id, `history_60m_price_min/max`.
Model hiện tại chỉ dùng `weather_main` chứ không dùng 19 cột thời tiết kia.

Nhóm tổng hợp trong `mau.parquet` **khớp đúng `B_NUM` + `M_NUM`** của pipeline production, nên
baseline ở bước 2 là so sánh công bằng với model thật.

### Vì sao tách làm hai bảng

`mau.parquet` là **bài toán dự đoán** — mỗi dòng một chuyến cần đoán giá.
`bao_gia.parquet` là **dòng chảy báo giá** — dùng để tra cứu chuỗi K báo giá gần nhất.

Cách này nhẹ hơn nhiều so với nhúng sẵn chuỗi vào từng dòng: 6,9M × 32 bước × 7 feature × 4 byte
= **6,2 GB**. Tách ra chỉ còn **150 MB**.

Notebook dựng chuỗi bằng `searchsorted` — chạy mất **1 giây**.

---

## Các bước đẩy lên Kaggle

### 1. Tạo Dataset

1. Vào <https://www.kaggle.com/datasets> → **New Dataset**
2. Kéo thả **cả 3 file** trong `du_lieu/` vào
3. Đặt tên: `hcm-gia-doi-thu-chuoi`
4. Chọn **Private** (dữ liệu synthetic của công ty)
5. **Create** — chờ upload ~150 MB

### 2. Tạo Notebook

1. Vào <https://www.kaggle.com/code> → **New Notebook**
2. **File → Import Notebook** → chọn `kaggle_transformer.ipynb`
3. Bên phải: **Add Input** → **Datasets** → chọn dataset vừa tạo
4. Bên phải: **Settings → Accelerator → GPU T4 x2** (hoặc P100)
5. **Run All**

> Notebook tự dò đường dẫn trong `/kaggle/input/`, không cần sửa gì.

### 3. Thời gian dự kiến

| Bước | Thời gian |
|---|---|
| 1 — Dựng chuỗi | ~2 phút |
| 2 — Test rẻ (LightGBM) | ~10 phút |
| 3 — Transformer (3 tháng × 8 epoch) | ~60 phút |

Kaggle cho **30 giờ GPU/tuần**, session tối đa **12 tiếng** — thừa sức.

---

## Notebook làm gì

### Bước 1 — Dựng chuỗi

Với mỗi mẫu, tìm K báo giá gần nhất **trước mốc cắt** bằng `searchsorted`.

> **Chống rò rỉ dữ liệu:** chỉ lấy báo giá có `ts <= cutoff`, trong đó
> `cutoff = target_timestamp − lag`. Notebook có `assert` kiểm điều này — nếu sai thì dừng ngay,
> không train ra kết quả đẹp giả.

### Bước 2 — Test rẻ, 4 cấu hình

So LightGBM với: không lịch sử · 3 con số tổng hợp · chuỗi thô · cả hai.
Đây là **chốt chặn** — nếu chuỗi không thêm gì thì dừng, khỏi tốn 2 ngày dựng transformer.

### Bước 3 — Transformer

```
CHUỖI K×7 → Linear → + positional → TransformerEncoder ×2, 4 head → mean pool
                                                                        │
TĨNH (embedding danh mục + 12 feature số) ──────────────────────────────┤
                                                                        ▼
                                                            MLP → 2 đầu ra
                                                    log(giá cơ bản) · hệ số nhân
```

Khoảng **90.000 tham số**. Dự đoán hai đầu ra rồi nhân lại giống kiến trúc Hybrid, train **riêng
từng tháng** (lịch sử giá reset theo tháng, gộp lại là rò rỉ).

---

## Mốc phải vượt

| Model | MAE | MAPE |
|---|---:|---:|
| Persistence | 33.683đ | — |
| Dự đoán giá trực tiếp (GBM) | 18.834đ | — |
| **Hybrid** (giá cơ bản × hệ số nhân) | **18.048đ** | **14,74%** |

Transformer phải xuống dưới **18.048đ** mới có giá trị thực tế.

→ **Đạt 18.008đ** — vượt mốc MAE nhưng thua ở MAPE. Xem mục đầu file.

---

## Kết quả hoà — vẫn phải ghi vào báo cáo

Kết quả hoà ở đây **không phải thất bại**, nó chốt được một chuyện quan trọng:

> Model đã chạm trần **của bộ dữ liệu này**. Việc tiếp theo phải là **thêm nguồn dữ liệu mới**,
> không phải đổi kiến trúc.

Điều này khớp với những gì đã đo trước đó:

| Đã thử | Kết quả |
|---|---|
| 4 thuật toán (XGBoost / LightGBM / HistGB / GAM) | Chênh nhau 1,9% |
| Neural network multi-task (MLP) | Thua GBM |
| Optuna 40 trial × 3 tháng | +2 VND |
| Ném hết 49 cột + feature weights | 6 VND |
| **Transformer đọc chuỗi** | **MAE −0,22% · MAPE +0,06 điểm — hoà** |

Ghi rõ để sau này không ai phải thử lại.

---

## Nếu muốn thử thêm trước khi kết luận

| Thử | Đổi gì | Đáng thử? |
|---|---|---|
| Bỏ `h60_*` khỏi feature tĩnh | Ép model phải dùng chuỗi | ⭐ đáng nhất — đã có sẵn ở cấu hình C bước 2 |
| `K = 64` | Phủ hết 60 phút thay vì ~23 phút | Vừa |
| `d = 128`, `n_lop = 4` | Model to hơn | Thấp — dữ liệu là nút thắt, không phải sức chứa model |
| `epochs = 20` | Train lâu hơn | Thấp |

---

## Sinh lại dữ liệu

Nếu model được train lại, chạy `dong_goi_kaggle.py` (thư mục tạm của phiên làm việc) để sinh lại
`du_lieu/` rồi upload phiên bản mới lên Kaggle.
