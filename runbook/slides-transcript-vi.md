# Transcript thuyết trình — deck `slides/slides.html` (tiếng Việt)

Kịch bản nói cho từng slide, viết theo văn nói tự nhiên. Tổng thời lượng ~20–25 phút
(gồm 3 demo live). Chỗ có `[DEMO]` là thao tác trên terminal — lệnh chính xác và output
kỳ vọng nằm trong `runbook/live-demo-runbook.md`. Trước buổi present: chạy `./run.sh test`
để chắc cả 3 demo xanh, và mở sẵn `docs/03-qos.md`, `docs/05-rmw.md` trong tab.

---

## Slide 1 — ROS 2 for embedded engineers *(~1 phút)*

Chào mọi người. Hôm nay mình giới thiệu ROS 2 — nhưng không phải kiểu lý thuyết suông.
Toàn bộ buổi này chạy quanh ba demo thật trên máy mình, chạy trong Docker, và **mọi con số
trên slide đều lấy từ lần chạy thật** — không có số nào chép từ tài liệu marketing.

Tinh thần của buổi này nằm ngay trên slide: *see it, run it, swap it* — nhìn thấy nó chạy,
tự chạy được, và swap được cả tầng middleware bên dưới.

## Slide 2 — Why ROS 2? *(~2 phút)*

Vì sao dân embedded như team mình nên quan tâm ROS 2?

Ý tưởng cốt lõi: thay vì viết một firmware to đùng, ta xây hệ thống từ nhiều **process nhỏ
gọi là node**, nói chuyện với nhau qua mạng. Và điểm khác biệt lớn nhất so với mọi framework
khác: **không có master trung tâm** — các node tự tìm thấy nhau, ngang hàng.

Với anh em firmware, cứ map thế này cho dễ:
- **Topic** giống broadcast frame trên bus — ai muốn nghe thì nghe.
- **Service** giống một transaction đọc/ghi register — hỏi một câu, nhận một câu trả lời.
- **Action** giống một lệnh DMA hay motor move dài — chạy lâu, có báo tiến độ, hủy được.
- Và **QoS** — quality of service — giống các trade-off reliability/timing khi mình chọn
  cấu hình bus.

Điểm cuối: tầng truyền dẫn bên dưới là một **HAL swap được** — đổi cả network stack bằng
một biến môi trường, không recompile. Lát nữa demo 3 mình chứng minh câu này.

## Slide 3 — ROS 1 vs ROS 2 *(~1.5 phút)*

Nhiều người từng nghe ROS 1. Khác biệt quan trọng nhất nằm ở dòng đầu bảng: ROS 1 có
`roscore` — một master trung tâm, chết là cả hệ chết. ROS 2 **bỏ hẳn master**, discovery
phân tán qua DDS.

Dòng hai: ROS 1 dùng giao thức tự chế TCPROS; ROS 2 đứng trên **DDS/RTPS** — chuẩn công
nghiệp đã dùng trong quốc phòng, y tế — hoặc Zenoh, và cắm qua lớp `rmw` nên đổi vendor được.

Với mình, dòng đáng chú ý nhất cho team embedded là dòng cuối: ROS 2 có **micro-ROS** chạy
được trên MCU — ROS 1 chưa bao giờ xuống được tầng đó. Cuối buổi mình nói thêm.

## Slide 4 — Diagram kiến trúc layer cake *(~2 phút)*

Đây là bức tranh quan trọng nhất buổi hôm nay. Đọc từ trên xuống:

Code của mình viết bằng **rclpy** (Python) hoặc **rclcpp** (C++) — hai client library. Cả
hai gọi xuống **rcl** — lớp C chung. Rồi tới lớp thú vị nhất: **rmw** — ROS middleware
interface. Nó chính là một **HAL đúng nghĩa** — giống như mình viết driver trên HAL của ST
hay NXP: code ở trên không cần biết bên dưới là Fast DDS, Cyclone DDS hay Zenoh.

Nhớ callout bên phải: đổi middleware là **zero recompiles** — chỉ đổi một biến môi trường.
Ai từng phải port firmware giữa hai dòng chip sẽ hiểu giá trị của câu này.

## Slide 5 — Diagram discovery *(~1.5 phút)*

Bên trái là thế giới cũ: mọi node đăng ký qua master. Master chết — cả hệ tê liệt.
Single point of failure kinh điển.

Bên phải là ROS 2: các node **tự multicast tìm nhau**, hình thành mesh ngang hàng. Giống
enumerate endpoint trên bus — thiết bị cắm vào tự khai báo, không cần ai cấp phát.

Và để ý thêm: `ROS_DOMAIN_ID` — hai domain khác nhau là hai thế giới cách ly hoàn toàn,
kể cả chung một dây mạng. Lát demo 3 mình chứng minh bằng số.

## Slide 6 — Diagram ba kiểu giao tiếp *(~1.5 phút)*

Ba cột này là ba pattern giao tiếp — và anh em sẽ thấy nó quen thuộc:

Cột một, **Topic** — pub/sub liên tục, một chiều, nhiều người nghe. Dòng dữ liệu sensor.
Cột hai, **Service** — request/reply. Gọi một hàm ở process khác.
Cột ba, **Action** — nhiệm vụ dài: gửi goal, nhận feedback liên tục, cuối cùng nhận result,
và hủy giữa chừng được.

Firmware mapping: broadcast frame — register transaction — DMA transfer có progress.
Demo ngay bây giờ sẽ chạy cả ba trên một hệ thật.

## Slide 7 — Demo 1: pub/sub + service + action *(~3 phút, live)*

`[DEMO]` — gõ `./run.sh demo-1` rồi nói trong lúc nó chạy:

Cái đang chạy là **năm process riêng biệt**: một talker Python, một talker C++, một
listener, một service server, một action server. Không ai cấu hình ai — chúng tự tìm nhau.

Khi output hiện, chỉ vào từng dòng:
- `node list` đủ 5 node — không có master nào đứng giữa.
- Dòng `/chatter` — chú ý message `"Hello from C++ (rclcpp)"` lẫn message Python trên
  **cùng một topic**: hai ngôn ngữ, một bus, listener không phân biệt được.
- Service: `AddTwoInts(2, 3)` trả về `sum=5` — một transaction gọn.
- Action Fibonacci: feedback nhảy `[0,1,1]` → `[0,1,1,2]` → … rồi result + SUCCEEDED —
  đúng pattern DMA-có-progress mình vừa nói.

Chốt: dòng cuối `Demo 1 acceptance PASSED` — đây là test tự động, không phải mình canh tay.

## Slide 8 — Diagram QoS RxO *(~1.5 phút)*

Trước demo 2, cần một khái niệm: **QoS phải khớp hai đầu** — luật Request-versus-Offered.
Publisher *offer* một mức chất lượng, subscriber *request* một mức. Subscriber đòi cao hơn
mức publisher offer → **không có kết nối nào cả**. Không phải chậm, không phải lỗi — mà là
**im lặng, zero message**.

Giống như một bên nói UART có parity, một bên đòi CRC đầy đủ — không bắt tay được thì thôi.
Điểm dễ ăn đòn nhất khi mới làm ROS 2 đấy.

## Slide 9 — Demo 2: QoS kết quả thật *(~3 phút, live)*

`[DEMO]` — gõ `./run.sh demo-2`, mở `docs/03-qos.md` khi xong:

Bảng này sinh tự động từ lần chạy vừa rồi. Ba dòng:
- `best_effort` → `reliable`: **0 message** — đúng luật RxO vừa nói. Một publisher kiểu
  sensor best-effort không giao được gì cho subscriber đòi reliable.
- Chiều ngược lại `reliable` → `best_effort`: **20/20** — offer cao hơn request thì OK.
- Durability lệch nhau (`volatile` → `transient_local`): lại **0**.

Điều đáng quý: nó **không im lặng hoàn toàn** — RMW log một dòng warning incompatible QoS.
Nhưng nếu không biết trước luật này, bạn sẽ mất một buổi debug "sao topic không có data".

Còn dòng cuối — `transient_local` latching: subscriber vào muộn vẫn nhận được message cũ,
giống đọc lại register cuối cùng thay vì chờ frame mới.

## Slide 10 — Diagram RTPS = ARQ *(~1.5 phút)*

Nhìn vào bên dưới của chữ "reliable": nó không có phép màu nào cả. RTPS chạy trên UDP và tự
làm reliability bằng **HEARTBEAT / ACKNACK / resend** — chính là **ARQ sliding window** mà
anh em nào làm giao thức đều từng viết. Sequence number, gap detection, retransmit — đủ bộ.

Điểm mình muốn chốt: ROS 2 không phải hộp đen. Dưới mọi topic "reliable" là một cơ chế mà
người làm firmware đọc phát hiểu ngay.

## Slide 11 — Diagram RMW swap *(~1 phút)*

Giờ tới lời hứa ở slide 2: đổi cả middleware bằng một biến môi trường. Cùng một binary,
`RMW_IMPLEMENTATION=rmw_fastrtps_cpp` hay `rmw_cyclonedds_cpp` hay `rmw_zenoh_cpp` — không
build lại gì hết.

Nhưng chú ý phần màu đỏ: Fast DDS và Cyclone nói chuyện được với nhau vì chung wire
protocol RTPS. Zenoh thì **khác wire protocol** — không interop với DDS. Swap được không có
nghĩa là trộn được. Demo chứng minh ngay.

## Slide 12 — Demo 3: swap + interop kết quả thật *(~3 phút, live)*

`[DEMO]` — gõ `./run.sh demo-3`, mở `docs/05-rmw.md`:

Bốn dòng kết quả, đọc từ trên xuống:
- Cùng binary chạy trên **cả ba middleware**: 8/8/8 message — mỗi cặp cùng loại đều thông.
- Fast DDS ↔ Cyclone: **8** — hai vendor khác nhau, chung RTPS, nói chuyện bình thường.
  Đây là giá trị của chuẩn mở.
- Fast DDS → Zenoh: **0** — khác wire protocol, đúng như slide trước cảnh báo.
- Domain 42 → domain 99: **0** — đổi một số là cách ly tuyệt đối. Chạy nhiều robot trong
  một lab không giẫm chân nhau là nhờ cái này.

## Slide 13 — Diagram turtlesim graph *(~1 phút)*

Trước khi kết, một demo cho vui mắt — vì nãy giờ toàn terminal. Diagram này là graph thật
của turtlesim: node `teleop` phát topic `/turtle1/cmd_vel`, node `turtlesim` nhận và trả
`/turtle1/pose`, kèm mấy service như `/spawn`, `/clear`.

## Slide 14 — Visual demos *(~2 phút, live nếu còn thời gian)*

`[DEMO nếu còn giờ]` — `./run.sh viz` — một con rùa hiện lên, lái bằng phím mũi tên. Mở
terminal thứ hai chạy `./run.sh rqt` — thấy **graph sống**: đúng cái diagram slide trước,
nhưng đang nhúc nhích theo phím bấm của mình.

Câu chốt cho phần này: mọi khái niệm trừu tượng nãy giờ — node, topic, service — giờ là
thứ nhìn thấy được, sờ được. Anh em về chạy lại chỉ cần Docker, không cần cài ROS.

## Slide 15 — Diagram micro-ROS *(~1.5 phút)*

Câu hỏi chắc chắn có người đang định hỏi: "chạy được trên MCU không?"

**micro-ROS**: client rút gọn chạy trên FreeRTOS/Zephyr/NuttX, nói chuyện với một **agent**
bên Linux qua giao thức DDS-XRCE — nhẹ đủ cho serial hoặc UDP. Nhìn từ phía ROS 2, con MCU
hiện ra như một node bình thường: cũng topic, cũng service.

Đây là appendix — chưa phải demo hôm nay — nhưng là hướng nghiên cứu tiếp theo của mình,
và là chỗ kỹ năng firmware của team mình ăn tiền nhất.

## Slide 16 — Takeaways *(~1.5 phút)*

Năm điều mang về:

Một — ROS 2 là hệ phân tán **không master**, QoS cấu hình theo từng stream.
Hai — ba pattern giao tiếp: **topic / service / action** = stream / RPC / long task.
Ba — **QoS phải khớp hai đầu**, và khi không khớp nó có cảnh báo — nhưng phải biết mà nhìn.
Bốn — **RMW là một cái HAL**: swap Fast DDS / Cyclone / Zenoh bằng một biến env.
Năm — **micro-ROS** kéo được mô hình này xuống MCU.

Và dòng cuối slide là bài tập về nhà, một dòng lệnh duy nhất:
`./run.sh build && ./run.sh demo-1 && ./run.sh viz` — máy nào có Docker là chạy.
Cảm ơn mọi người — giờ ai muốn lái thử con rùa thì lên đây.

---

## Ghi chú phòng thân (nếu bị hỏi xoáy)

- **"Discovery chậm/thiếu node?"** — daemon cache đang race; đợi vài giây, script demo đã
  tự poll. (Chi tiết: mục panic trong `live-demo-runbook.md`.)
- **"Số 20 message ở đâu ra?"** — publisher 5 Hz × subscriber chạy 4 giây = 20. Số thật,
  sinh tự động vào `docs/03-qos.md`.
- **"Zenoh 0 message có phải lỗi không?"** — không, là thiết kế: khác wire protocol. Còn
  zenoh↔zenoh vẫn 8/8 (cần router `rmf_zenohd` — script tự bật).
- **"Sao không benchmark hiệu năng?"** — buổi này dạy khái niệm bằng kết quả thật; benchmark
  latency/jitter là bước nghiên cứu tiếp (đã nằm trong roadmap).
