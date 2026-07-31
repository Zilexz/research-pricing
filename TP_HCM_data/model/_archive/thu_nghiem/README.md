# Các thử nghiệm đã hoàn thành

Các notebook trong thư mục này **đã chạy xong, kết quả đã ghi vào báo cáo tuần 2 (mục 5)**.
Giữ lại để đối chiếu/tái kiểm chứng, không nằm trong pipeline chính.

| File | Nội dung | Kết quả |
|---|---|---|
| `train_hybrid_base_v2.ipynb` | Thêm 4 feature tốc độ/đơn giá của chuyến quan sát gần nhất | Importance ≈ 0, không cải thiện |
| `chuan_bi_du_lieu_v2.ipynb` | Bản chuẩn bị dữ liệu kèm 4 feature trên | (đi kèm file trên) |
| `train_allfeatures_weighted.ipynb` | Ném hết 49 cột + `feature_weights` ưu tiên | Chênh 6 VND (full 6,9M dòng) |
| `train_nn_multitask.ipynb` | Neural Network 1 thân 2 đầu ra + feature gate | Thua GBM ở cả 2 target |
| `train_finetune_optuna.ipynb` | Optuna 9 tham số × 40 trial × 3 tháng | Chênh **+2 VND** |

→ Kết luận chung: **MAE ~15.000 VND là sàn nhiễu của dữ liệu**, không phải model chưa tối ưu.
