# TÀI LIỆU GIỚI THIỆU DỰ ÁN (INTERN)
## Nghiên cứu Định giá XanhSM — Tổng quan Dự án Cấp cao

**Hệ số nhân thị trường, tối đa hóa lợi nhuận, và định giá cá nhân hóa**

Dự án xây dựng một quyết định định giá theo nhiều tầng: **trước tiên** ổn định thị trường địa phương, **sau đó** bổ sung một hiệu chỉnh GMV-kỳ-vọng có kiểm soát, và **cuối cùng** áp một lớp cá nhân hóa (wrapper) ở cấp báo giá với biên độ bị giới hạn.

*Tổng quan dự án: 20 tháng 7 năm 2026 — Được biên soạn như một phần giới thiệu khái niệm độc lập, tự chứa.*

> **Lưu ý thuật ngữ (người dịch bổ sung để bạn dễ theo dõi):**
> - **GMV** (Gross Merchandise Value): tổng giá trị giao dịch — ở đây hiểu là tổng doanh thu cước dự kiến.
> - **Quote / báo giá**: một lần hệ thống báo giá cho một chuyến đi cụ thể.
> - **Bucket**: một "nhóm" thị trường cục bộ theo thời gian (và thường là theo khu vực), ký hiệu chỉ số *t*.
> - **Multiplier / hệ số nhân**: hệ số nhân lên giá cước cơ sở (ví dụ giá tăng khi cầu vượt cung).
> - **Wrapper / lớp bao**: hệ số điều chỉnh nhỏ, nằm quanh giá trị 1, áp lên trên giá tham chiếu chung.

---

## Mục lục

1. Vấn đề chúng ta đang giải quyết
2. Hệ số nhân thị trường (Market multiplier)
3. Tối đa hóa lợi nhuận (Profit maximization)
4. Lớp phản ứng giá cá nhân hóa (Personalized price-response layer)

---

## 1. Vấn đề chúng ta đang giải quyết

Hệ số nhân cuối cùng phải trả lời được ba câu hỏi:

1. Trạng thái cung–cầu địa phương hiện tại **đòi hỏi** mức giá nào?
2. Một dịch chuyển nhỏ quanh mức giá thị trường đó có **cải thiện GMV kỳ vọng** không?
3. Riêng báo giá cụ thể này được kỳ vọng sẽ **phản ứng thế nào** với dịch chuyển đó?

Ba câu hỏi này vận hành ở các cấp độ khác nhau, nên thuật toán giữ chúng ở **các tầng riêng biệt** và chỉ **kết hợp đầu ra của chúng ở bước cuối cùng**:

**Hệ số nhân cuối cùng**

$$m^{final}_{t,u} = p^{\star}_{t,u}\left[\, m^{market}_t + G_t(\alpha Z_t) \,\right] \tag{1}$$

Trong đó $m^{market}_t$ là hệ số nhân thị trường cho bucket $t$; $Z_t$ là tín hiệu GMV-kỳ-vọng cục bộ; $\alpha$ chuyển tín hiệu đó sang đơn vị hệ số nhân; và $G_t$ **chặn hoặc cho đi qua** cú "nudge" (điều chỉnh nhẹ) lợi nhuận thu được. Lớp bao (wrapper) $p^{\star}_{t,u}$ là đặc thù cho từng báo giá và luôn giữ **gần bằng 1**.

Phép **cộng** bên trong dấu ngoặc vuông là có chủ đích: áp lực thị trường và áp lực lợi nhuận trước tiên hình thành **một mức giá tham chiếu chung**. Phép **nhân** được áp *sau đó*, để phần cá nhân hóa vẫn chỉ là một **điều chỉnh cục bộ** quanh mức tham chiếu ấy, chứ không phải là vật thay thế cho bộ điều khiển thị trường.

---

## 2. Hệ số nhân thị trường (Market multiplier)

Tầng thị trường tạo ra **một** hệ số nhân cho một bucket thị trường cục bộ tại thời điểm $t$. Gọi $d_t$ và $s_t$ lần lượt là tín hiệu **cầu** và **cung** của bucket đó. Chênh lệch mức độ hiện tại giữa chúng là:

$$\ell_t = d_t - s_t \tag{2}$$

$\ell_t > 0$ nghĩa là cầu vượt cung; $\ell_t < 0$ nghĩa là bucket đang **dư cung** so với cầu. Số hạng này mô tả **trạng thái thị trường hiện tại**, nhưng chưa cho biết trạng thái đó đang mạnh lên hay đang dịu đi.

Để nắm bắt **chuyển động**, ta định nghĩa mức thay đổi của cầu tương đối so với mức thay đổi của cung:

$$q_t = (d_t - d_{t-1}) - (s_t - s_{t-1}) \tag{3}$$

$q_t > 0$ nghĩa là áp lực đang dịch chuyển **về phía khan hiếm** (thiếu xe). $q_t < 0$ nghĩa là áp lực đang dịch chuyển **về phía giảm nhẹ** (bớt căng). Dùng đồng thời cả $\ell_t$ và $q_t$ giúp **tách biệt** mức mất cân bằng hiện tại với **hướng di chuyển** của nó.

Các thay đổi thô rất bất ổn định, nên tín hiệu chuyển động được **làm mượt** qua hai bước:

$$q^{med}_t = \text{median}(q_{t-W+1}, \ldots, q_t) \tag{4}$$

$$\tilde{q}_t = \rho\, q^{med}_t + (1 - \rho)\,\tilde{q}_{t-1} \tag{5}$$

Ở đây $W$ là cửa sổ trượt (rolling window), và $\rho \in (0, 1]$ điều khiển tốc độ phản ứng của giá trị đã làm mượt. **Trung vị (median)** loại bỏ các đột biến (spike) đơn lẻ trong cửa sổ; sau đó **trung bình mũ (exponential average)** ngăn tín hiệu còn lại thay đổi quá đột ngột giữa các lần cập nhật.

Tín hiệu chuyển động đã làm mượt được **giới hạn (clip)** trước khi đưa vào bộ điều khiển:

$$g_t = \text{clip}(\tilde{q}_t, -c, c), \qquad \text{clip}(x, a, b) = \min\{\max\{x, a\}, b\} \tag{6}$$

Hằng số $c > 0$ là **độ lớn chuyển động tối đa** mà bộ điều khiển được phép sử dụng. Việc clip giúp ngăn một khoảng thời gian bất thường tạo ra một thay đổi giá quá lớn.

Điều chỉnh thị trường là:

$$\Delta^{market}_t = \eta_1\, g_t\, \ell_t + \eta_2\, \ell_t \tag{7}$$

trong đó $\eta_1$ điều khiển **tương tác** giữa mức mất cân bằng và chuyển động, còn $\eta_2$ điều khiển **phản ứng trực tiếp** với mức mất cân bằng. Số hạng thứ nhất trở nên mạnh khi tình trạng khan hiếm và chuyển động xấu đi **cộng hưởng** với nhau. Số hạng thứ hai vẫn hoạt động khi thị trường mất cân bằng nhưng tín hiệu chuyển động lại nhỏ. Giữ lại cả hai số hạng giúp tránh việc **một tình trạng khan hiếm âm thầm nhưng dai dẳng bị bỏ sót**.

Cuối cùng, áp điều chỉnh này lên hệ số nhân cơ sở đầu vào:

$$m^{market}_t = \text{clip}\!\left(\, m^{base}_t \left[1 + \Delta^{market}_t\right],\; m_{min},\; m_{max} \,\right) \tag{8}$$

Ở đây $m^{base}_t$ là hệ số nhân đi vào tầng thị trường, và $m_{min}$, $m_{max}$ là các **ngưỡng vận hành**. Đầu ra là một hệ số nhân thị trường $m^{market}_t$ đã bị giới hạn, **được dùng chung** cho mọi báo giá trong bucket.

> **Vì sao thiết kế như vậy.** Bộ điều khiển phản ứng với **cả mức độ lẫn chuyển động** của áp lực thị trường, trong khi việc làm mượt và clip giới hạn mức độ mà các đầu vào nhiễu có thể làm thay đổi giá trong một lần cập nhật.

---

## 3. Tối đa hóa lợi nhuận (Profit maximization)

Tầng thị trường được thiết kế nhằm hướng tới **cân bằng**. Tầng lợi nhuận đặt một câu hỏi hẹp hơn: quanh mức $m^{market}_t$, liệu một dịch chuyển nhỏ **lên hoặc xuống** có cải thiện GMV kỳ vọng không? Nó trả lời ở cấp bucket và chỉ đóng góp một **cú nudge có kiểm soát**.

Với báo giá $i$, gọi $x_i$ là ngữ cảnh (context) của nó, $m^{ref}_i$ là hệ số nhân tham chiếu, và $m$ là một hệ số nhân ứng viên. Gọi $p^{book}_{i,0}$ là **xác suất đặt xe đã hiệu chỉnh** tại mức tham chiếu. Xác suất đặt xe của ứng viên là:

$$\hat{p}^{book}_i(m) = \text{clip}\!\left[\, p^{book}_{i,0}\, \exp\!\left(-\epsilon_i \log\frac{m}{m^{ref}_i}\right),\; p_{min},\; p_{max} \,\right] \tag{9}$$

**Độ co giãn (elasticity)** $\epsilon_i \geq 0$ điều khiển mức độ phản ứng của báo giá $i$ trước một thay đổi giá tương đối. Khi $m = m^{ref}_i$, số hạng mũ bằng 1 và xác suất giữ nguyên ở giá trị tham chiếu. Khi $m$ tăng vượt mức tham chiếu, số hạng này giảm xuống dưới 1 và xác suất đặt xe **giảm**. Hai ngưỡng $p_{min}$ và $p_{max}$ ngăn một phản ứng cực đoan chi phối toàn bộ phép tính giá trị.

Gọi xác suất **hoàn thành** chuyến là:

$$\hat{p}^{complete}_i = \hat{P}(\text{complete} \mid \text{booked},\, x_i) \tag{10}$$

Xác suất này được **giữ cố định** trong khi thuật toán thăm dò một dịch chuyển giá cục bộ nhỏ. Nếu $b_i$ là **giá cước cơ sở không tăng giá (non-surge base fare)**, thì GMV kỳ vọng của báo giá $i$ dưới ứng viên $m$ là:

$$\hat{V}_i(m) = \hat{p}^{book}_i(m)\, \hat{p}^{complete}_i\, b_i\, m \tag{11}$$

Bốn thừa số có vai trò rõ ràng: **xác suất đặt xe** quyết định liệu một đơn có bắt đầu hay không; **xác suất hoàn thành** quyết định liệu nó có kết thúc hay không; $b_i$ đặt thang giá cước; và $m$ áp mức giá ứng viên.

Với các báo giá $Q_t$ trong bucket $t$, tổng hợp giá trị các báo giá:

$$F_t(m) = \sum_{i \in Q_t} \hat{V}_i(m) \tag{12}$$

Như vậy $F_t(m)$ là **GMV kỳ vọng của bucket** nếu hệ số nhân ứng viên là $m$. Tầng này cần **hướng cải thiện** quanh hệ số nhân hiện tại, chứ không phải một cực trị toàn cục. Do đó nó thăm dò hai điểm lân cận:

$$F'_t(m_t) \approx \frac{F_t(m_t + h) - F_t(m_t - h)}{2h} \tag{13}$$

Ở đây $h > 0$ là **bước thăm dò** nhỏ. Sai phân đối xứng (symmetric difference) dùng dịch chuyển lên và xuống bằng nhau, nên tín hiệu mô tả **độ dốc cục bộ** quanh $m_t$ thay vì thiên vị sẵn về một hướng.

Chuyển độ dốc đó thành một tín hiệu **tương đối, bị giới hạn**:

$$Z_t = \text{clip}\!\left(\frac{m_t\, F'_t(m_t)}{|F_t(m_t)| + \varepsilon_F},\; -z_{max},\; z_{max}\right) \tag{14}$$

Tử số $m_t F'_t(m_t)$ biểu diễn mức thay đổi trên **thang hệ số nhân tương đối**. Việc chia cho $|F_t(m_t)| + \varepsilon_F$ **loại bỏ thang GMV tuyệt đối** của bucket; $\varepsilon_F > 0$ giữ cho tỉ số ổn định khi GMV kỳ vọng nhỏ. Cuối cùng, $z_{max}$ **giới hạn cường độ** của tín hiệu. $Z_t > 0$ nghiêng về một mức tăng nhỏ, $Z_t < 0$ nghiêng về một mức giảm nhỏ, và giá trị gần 0 nghĩa là đường cong GMV-kỳ-vọng đang **phẳng** cục bộ.

Tín hiệu lợi nhuận chỉ đi vào thuật toán cuối cùng thông qua một **cổng an toàn (safety gate)**. Gọi $\gamma_t \in \{0, 1\}$ cho biết cổng có **mở** hay không, và định nghĩa:

$$G_t(x) = \gamma_t x, \qquad \Delta m^{profit}_t = G_t(\alpha Z_t) = \gamma_t\, \alpha\, Z_t \tag{15}$$

Thang $\alpha$ chuyển $Z_t$ (không thứ nguyên) sang **đơn vị hệ số nhân**. Cổng **chỉ mở khi** đường-đã-điều-chỉnh-lợi-nhuận vẫn còn **đủ gần** đường-chỉ-thị-trường; một số điều kiện vận hành nhất định cũng có thể **đóng** nó lại. Thiết kế này cho phép GMV kỳ vọng hiệu chỉnh mức giá thị trường **mà không** để số hạng lợi nhuận chiếm quyền kiểm soát hành vi cân bằng thị trường.

> **Đầu vào và đầu ra.** Tầng này nhận: ngữ cảnh các báo giá, các ước lượng đặt xe và hoàn thành, giá cước cơ sở, hệ số nhân tham chiếu, và bước thăm dò $h$. Nó trả về: tín hiệu cấp bucket $Z_t$ và cú nudge đã qua cổng $\Delta m^{profit}_t$.

---

## 4. Lớp phản ứng giá cá nhân hóa (Personalized price-response layer)

Hai tầng đầu tiên tạo ra một **giá tham chiếu chung của hệ thống**:

$$\bar{m}_t = \text{clip}\!\left(\, m^{market}_t + G_t(\alpha Z_t),\; m_{min},\; m_{max} \,\right) \tag{16}$$

Tầng cá nhân hóa **không xây dựng lại** mức tham chiếu này. Nó chỉ **ước lượng** một báo giá cụ thể có khả năng phản ứng thế nào với một dịch chuyển nhỏ quanh mức tham chiếu đó.

Gọi $X$ là ngữ cảnh cố định của báo giá và $m$ là một hệ số nhân ứng viên. Đo ứng viên như một **dịch chuyển log tương đối** so với mức tham chiếu:

$$r = \log\frac{m}{\bar{m}_t} \tag{17}$$

Mức tham chiếu có $r = 0$, một mức tăng có $r > 0$, và một mức giảm có $r < 0$. Việc dùng dịch chuyển tương đối cho phép **cùng một bộ hàm phản ứng** mô tả các thay đổi quanh những mức hệ số nhân thị trường khác nhau.

Giả sử có $K$ **lớp phản ứng giá trơn (smooth price-response classes)** $f_1(r), \ldots, f_K(r)$. Ngữ cảnh báo giá tạo ra các **trọng số lớp không âm**:

$$w_k(X) \geq 0, \qquad \sum_{k=1}^{K} w_k(X) = 1 \tag{18}$$

Hàm phản ứng đặc thù theo ngữ cảnh là:

$$R(r \mid X) = \sum_{k=1}^{K} w_k(X)\, f_k(r) \tag{19}$$

Mỗi $f_k$ đại diện cho **một dạng phản ứng lặp lại**; $w_k(X)$ cho biết dạng đó **khớp** với ngữ cảnh báo giá đến mức nào. Các trọng số hoạt động như một **phân loại mềm (soft classification)**: một báo giá có thể **nằm giữa** các lớp phản ứng thay vì bị ép vào một nhãn cứng. Vì $R$ là một tổ hợp tuyến tính của các hàm trơn, nên phản ứng kết quả cũng thay đổi **trơn tru** theo giá và theo các ngữ cảnh lân cận.

Ở mức tổng quát, cộng phản ứng giá này vào **điểm số đặt xe nền (baseline booking score)** của báo giá:

$$\hat{P}(\text{book} \mid X, m) = \text{sigmoid}\!\left(\, b(X) + R\!\left(\log\frac{m}{\bar{m}_t} \,\middle|\, X\right) \right) \tag{20}$$

Ở đây $b(X)$ biểu diễn **ý định đặt xe (booking intent)** tại mức giá tham chiếu, còn $R$ chỉ **thay đổi** ý định đó khi giá dịch chuyển ra xa mức tham chiếu. Việc tách hai số hạng giúp giữ **hành vi cầu nền** tách biệt với **độ nhạy về giá**.

Chính sách định giá so sánh các dịch chuyển nhỏ, bị giới hạn quanh $\bar{m}_t$ và chọn ra một lớp bao $p^{\star}_{t,u}$ **gần 1**. Hệ số nhân báo giá cuối cùng là:

$$m^{final}_{t,u} = p^{\star}_{t,u}\, \bar{m}_t \tag{21}$$

Một wrapper **nhỏ hơn 1** kéo báo giá **xuống** dưới mức tham chiếu chung; wrapper **lớn hơn 1** đẩy nó **lên**; và $p^{\star}_{t,u} = 1$ giữ nguyên mức tham chiếu. **Ý tưởng nghiên cứu ổn định** ở đây là *tổ hợp các lớp phản ứng phụ thuộc vào ngữ cảnh*. Còn định nghĩa cụ thể của các lớp, quy trình huấn luyện, và quy tắc chọn wrapper **chưa được cố định** trong bản tổng quan này.

Thay Phương trình (16) vào Phương trình (21) cho ta cấu trúc hoàn chỉnh trong Phương trình (1): **tầng thị trường** đặt điểm neo, **tầng lợi nhuận** cung cấp một hiệu chỉnh đã qua cổng, và **tầng cá nhân hóa** áp một lớp bao cục bộ ở cấp báo giá.

---

*— Hết —*
