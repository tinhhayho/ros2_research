# Transcript thuyết trình — deck `slides/research.html` (tiếng Việt)

Kịch bản nói cho deck research 68 slide. Tổng thời lượng theo tổng các mốc *(~X phút)*
dưới đây là **~124 phút** (không tính Q&A) — deck đã lớn hơn nhiều so với bản 47 slide gốc
(thêm cụm node/executor/DDS-scope/graph, cụm VDA 5050 và cụm AUTOSAR/UDS/SOVD, +21 slide), nên buổi nói full dài hơn hẳn
bản trước; con số ~122 phút *vượt* mốc lý tưởng 75–90 phút cho một buổi nói — nếu cần ép về
khung giờ đó, hai chỗ dễ cắt nhất mà không gãy mạch là cụm "deep dive tùy chọn" ở slide
32–36 (Thor memory, đã có sẵn signpost "skip ahead" trên slide 32) và cụm fleet/AUTOSAR ở
slide 43–54 (rút còn 3–4 slide đại diện thay vì cả 12). Deck này dày thông tin — nguyên
tắc nói: **không đọc bảng**,
chỉ kể câu chuyện và chỉ tay vào 1–2 ô đắt nhất mỗi bảng; ai cần chi tiết đã có blog +
báo cáo trong repo.

Gợi ý nhịp: phần 1–2 (nền tảng) nói kỹ; phần NVIDIA/Automotive nói theo kiểu "tour có
điểm dừng"; phần fleet/AUTOSAR mới là cụm dày nhất buổi — đi chậm nhưng đừng đọc bảng;
demo cuối là cao trào — đừng để cháy giờ trước khi tới đó.

---

## Slide 1 — Robot software stacks 2026 *(~1 phút)*

Chào mọi người. Đây là kết quả đợt nghiên cứu tháng 7 của mình về phần mềm robot năm 2026
— từ robot xe, humanoid, đến tầng fleet, và cả hai nền tảng của NVIDIA.

Hai cam kết trước khi bắt đầu: một, **mọi nhận định về thế giới bên ngoài đều có nguồn,
và 14 nhận định chịu lực nhất được kiểm chứng lại độc lập tận gốc** — cuối deck có slide
chỉ ra chỗ nào kiểm chứng phát hiện sai. Hai, **mọi con số demo là số đo thật trên máy
của mình** — và cuối buổi mọi người sẽ thấy ảnh chụp thật của lần chạy đó.

## Slide 2 — Agenda *(~1 phút)*

Lộ trình tám phần: bắt đầu bằng **bản đồ** — một hình dạng stack chung cho mọi robot; rồi
soi gần ROS 2 với code thật; kiểm tra thực trạng từng mảng; tầng fleet Open-RMF **cộng cả
VDA 5050 — giao thức dây cho AMR/AGV, phần mới**; sang NVIDIA — cả Physical AI lẫn
Automotive, có mổ cả con chip Thor; automotive giờ có thêm hẳn một cụm mới: **fleet
diagnostics — UDS, AUTOSAR, SOVD**; vì sao số liệu ngành này trôi nhanh; demo thật; và
chốt bằng ý nghĩa cho team mình. Ai quan tâm mảng nào có thể đón ở phần đó. Cuối slide có
dòng giải nghĩa sẵn mấy chữ viết tắt sẽ gặp suốt buổi — AMR, AV, UDS, AUTOSAR, SOVD.

## Slide 3 — How this research was made *(~1.5 phút)*

Một phút về phương pháp, vì nó quyết định độ tin của mọi slide sau: nguồn chính thống
trước — docs chính chủ, GitHub, Hugging Face, arXiv — và **mọi nhận định bên ngoài đều có
URL nguồn** (danh sách đầy đủ nằm ở slide References cuối deck). Claim của vendor được đối
xử đúng như claim, không phải fact: chỗ nào chỉ có số marketing, slide ghi rõ ngay cạnh
con số. Và **mọi số demo đều từ lần chạy thật trên máy của mình** — không trích lại
benchmark nào mình chưa tự tái hiện. Điểm mình muốn gửi gắm: số liệu ngành này trôi rất
nhanh — slide 60 có hai ví dụ cụ thể — đừng tin slide nào không ghi nguồn, kể cả slide
của mình.

## Slide 4 — Diagram: The robot software stack *(~2.5 phút)*

Đây là phát hiện quan trọng nhất: **mọi loại robot hội tụ về cùng một hình dạng stack.**

Đọc từ dưới lên: firmware MCU chạy vòng FOC 8–32 kHz; fieldbus EtherCAT/CAN-FD 1–10 kHz;
vòng điều khiển real-time ~1 kHz trên Linux PREEMPT_RT; qua **ranh giới ROS 2** là thế giới
DDS — perception, SLAM; trên nữa là autonomy — xe thì Nav2/Autoware, humanoid thì RL policy
và VLA; trên cùng là tầng fleet.

Và để ý dòng chú thích dưới cùng — câu quan trọng nhất buổi hôm nay: **ranh giới ROS 2 là
vạch duy nhất dịch chuyển từ 2020 tới giờ; mọi thứ bên dưới nó vẫn là embedded/RTOS cổ
điển.** Làn sóng AI thay tầng planner, không thay firmware.

## Slide 5 — Diagram: Who does what *(~2 phút)*

Cùng khung đó, giờ điền việc cụ thể vào từng tầng. FOC nằm đáy; SLAM với MoveIt nằm trên
vạch ROS 2; Nav2, MPPI, policy GR00T trên cùng.

Nhìn mũi tên bên phải: từ 32 kHz dưới đáy lên 1 Hz trên đỉnh — **càng nhanh càng phải đúng
giờ thì càng xuống thấp; càng thông minh càng chịu được trễ thì càng lên cao.** Một quy tắc
đặt được mọi thứ vào chỗ của nó. Ai nhớ đúng một slide hôm nay thì nhớ slide này.

## Slide 6 — Ba quy tắc đặt tầng *(~2 phút)*

Ba hệ quả hay bị hiểu nhầm. Một: **điều khiển motor là ba vòng lồng nhau ở hai tầng** —
vòng dòng điện luôn ở MCU; còn vòng vị trí 1 kHz thì hoặc trong servo drive thông minh
(kiểu công nghiệp) hoặc trong `ros2_control` (kiểu humanoid) — chọn kiến trúc nào là quyết
định lớn nhất của team firmware robot. Hai: **FK/IK tồn tại hai lần** — bản điều khiển
1 kHz trong vòng RT, bản lập kế hoạch trăm ms trong MoveIt. Ba: **SLAM và path planning
đứng ngoài vòng torque/an toàn** — SLAM khựng thì robot tạm dừng điều hướng chứ torque
không hề hấn, *với điều kiện* tầng dưới có chức năng an toàn độc lập — đó là thứ mình
phải thiết kế vào, không phải phân tầng xong là tự có. Và lưu ý tần số là heuristic mạnh
nhất chứ không phải trục duy nhất — WCET, cô lập lỗi, chứng nhận cũng quyết định chỗ đặt.

Và dòng cuối slide: cách phân tầng này là canon của ngành từ thập niên 70–90, không phải
mình bịa — Liu & Layland, kiến trúc RCS của Albus, three-layer của Gat.

## Slide 7 — Real-time ≠ fast *(~2.5 phút)*

Slide này trả lời câu hỏi chắc chắn ai đó đang định hỏi: *"real-time gì mà có 1 kHz?"*

Thứ nhất, chữ "ROS 2" thực ra là **hai thế giới**: DDS graph — mặc định message đi qua
middleware, trễ cỡ ms và phụ thuộc cấu hình (intra-process C++ có thể né serialization;
DDS *có thể* tune deterministic được — nhưng phải tự chứng minh trên máy của mình); và
`ros2_control` — được ROS 2 cấu hình nhưng vòng nóng **bỏ qua DDS**, gọi hàm C++ trực
tiếp ở tần số mình cấu hình.

Thứ hai, nhìn bảng: real-time nghĩa là **deadline chứng minh được, không phải nhanh**.
Lưu ý con số ~50 micro giây là **số minh họa của PREEMPT_RT đã tune, không phải hằng số**
— mình chưa tự đo, cyclictest nằm trong roadmap. Với budget đó: 5% chu kỳ 1 kHz — thoải
mái; 50% chu kỳ 10 kHz — hết budget, muốn làm phải chứng minh trên target hoặc dùng
silicon chuyên dụng. 1 kHz là nơi Linux tune tốt bắt đầu thoải mái **và** vật lý hết quan
tâm — hằng số thời gian cơ khí cỡ ms rồi. Nhanh hơn nữa là việc của MCU, của anh em mình.

## Slide 8 — Hệ sinh thái ROS 2 *(~1.5 phút)*

Bản đồ repo — không đọc từng dòng, chỉ ba điểm: dòng đầu, `ros2/*` là lõi — client library,
rcl, rmw. Dòng hai, `ros2_control` — framework mà dân actuator như mình sẽ sống trong đó.
Và dòng cuối bảng phụ: tất cả **Apache/BSD, không có cổng chặn nào** — khác hẳn thế giới
automotive lát nữa. Distro mình dùng: Jazzy, LTS tới 2029.

## Slide 9 — Diagram: node, process, executor *(~2 phút)*

Trước khi xem code, phải gỡ một hiểu nhầm mà dân firmware nào cũng dính: chữ "node"
nghe y như "task" — nhưng không phải. Nhìn hình từ ngoài vào trong: hai khung lớn là
hai **OS process**. Trong mỗi process có một dải **executor** — vòng lặp sự kiện, và
chính nó sở hữu 1..N thread callback. Các ô cam mới là **node**: `/camera` với pub
`/image` và timer 30 Hz, `/detect` với sub `/image` và pub `/obstacles` — node chỉ là
một danh tính kèm các endpoint, không phải đơn vị thực thi. Nhãn xanh giữa hai node
cùng process: **intra-process (opt-in)** — truyền con trỏ, không serialization — chú ý
chữ *opt-in*, slide sau nói kỹ vì sao. Dưới đáy mỗi process là dải **DDS threads** —
I/O mạng riêng của middleware. Và thanh DDS dưới cùng — discovery + topics — là chỗ
`/obstacles` băng qua ranh giới process sang node `/planner` ở process B.

Dải ba mệnh đề cuối hình là thứ đáng chụp lại: 1 process = 1 node — kiểu cổ điển;
1 process = N node — **composition**; và **thread thuộc về EXECUTOR, không thuộc
node**. Cộng dòng chú thích về callback model: executor chạy mỗi callback đến khi
xong — không có preemption ưu tiên giữa các callback, khác hẳn task RTOS — và vòng
hard-RT sống ngoài graph, đúng bài `ros2_control` lát nữa.

## Slide 10 — Node là cái tên, không phải thread *(~2.5 phút)*

Diễn giải hình vừa rồi thành các luật. Một: **node = một danh tính trong graph** —
cái tên (`/camera`) cộng các endpoint của nó: publisher, subscription, service, timer,
parameter. Nó là một *object*, không phải đơn vị thực thi. Hai: **ánh xạ
process/thread hoàn toàn tự do** — 1 process = 1 node là kiểu cổ điển, demo-1 của mình
chạy đúng 5 process kiểu đó; 1 process = N node là composition. Và điểm phải nói
thật chuẩn — vì audit vừa sửa đúng chỗ này: **intra-process comms là opt-in theo từng
node** — `use_intra_process_comms(true)`, chỉ có ở rclcpp/C++, **không tự động bật khi
compose** và rclpy không có. Compose xong mà quên opt-in thì message vẫn đi đường DDS.

Ba: **thread thuộc executor, không thuộc node** — `SingleThreadedExecutor` chạy tuần
tự *mọi* callback của *mọi* node trong nó; `MultiThreadedExecutor` dùng một pool; và
DDS luôn thêm các thread I/O riêng bên dưới. Bốn: **callback không phải ISR** —
executor chạy mỗi callback đến khi hoàn thành, không có priority preemption; một
callback kẹt làm **chết đói cả executor đơn luồng** — bản đa luồng chỉ xuống cấp chứ
không chết hẳn. Hệ quả anh em đã đoán ra: vòng hard-RT không sống trong callback —
`ros2_control` chạy vòng 1 kHz trong một thread `SCHED_FIFO` thường, *ngoài* graph.

Và một con số đo thật để đóng đinh: capture của chính repo —
`docs/img/demo1_threads.txt` — cho thấy con talker C++ của demo-1, một node một
process, là **15 OS thread**: main cộng executor/rcl cộng tracing cộng hơn chục thread
`dds.*` (rmw_fastrtps_cpp, mặc định của Jazzy). Con số này thay cho một con số "5–7"
không nguồn từng suýt lên slide — đúng luật của repo: số nào lên slide cũng phải là số
đo thật.

## Slide 11 — Graph được khám phá, không phải vẽ *(~2.5 phút)*

Câu hỏi tiếp theo của dân embedded: "file wiring nằm đâu?" Trả lời: **không có** —
không GUI, không file đấu dây, không code generation. Một kết nối tồn tại vì **tên
khớp nhau**: `create_publisher("chatter")` ở một chương trình, cộng
`create_subscription("chatter")` ở chương trình khác, cộng type và QoS tương thích —
discovery bắt tay — thành một edge trong graph. Tắt process là edge của nó biến mất.
Cái `rqt_graph` mình khoe lát nữa là **máy chụp X-quang, không phải editor**.

Vậy "bó dây điện" thật nằm đâu? Hai chỗ: **tên topic trong code**, và **launch file**
— thứ khởi động các node và đấu lại dây bằng remapping
(`remappings=[('image_raw', '/front_cam/image')]`), đặt namespace, đặt parameter.

Bảng dưới slide là cú đối chiếu đắt nhất — gửi trước cho cụm AUTOSAR ở phần 6: bên
AUTOSAR Classic, kết nối khai báo trong **ARXML lúc build**, lớp **RTE sinh ra** đấu
dây — tức là sơ đồ là *đầu vào*, artifact thiết kế; bên ROS 2, kết nối là tên topic
lúc runtime, DDS discovery tự khớp — sơ đồ là *đầu ra*, một quan sát. Đổi một kết nối:
bên kia rebuild, bên này restart với remap khác. Còn GUI vẽ-rồi-chạy duy nhất trong hệ
sinh thái là Groot2 — nhưng nó sửa cái behavior tree *bên trong* một node (BT
navigator của Nav2), không phải graph giữa các node.

## Slide 12 — Diagram: DDS nối tới đâu — và dừng ở đâu *(~2 phút)*

Hình chốt cụm này: phạm vi thật của DDS. Ba kịch bản xanh phía trên: **cùng process**
— node A và node B, intra-process opt-in, truyền con trỏ, né hẳn DDS; **cùng máy** —
process với process qua shared memory hoặc loopback UDP; **khác máy** — robot với
laptop qua Ethernet, discovery bằng multicast. Dải chú thích ngay dưới là điểm ăn
tiền: **location transparency** — API pub/sub y hệt nhau trong cả ba trường hợp;
participant là các OS process có IP stack.

Rồi tới vạch đứt — **dưới vạch này không có DDS**: đất của MCU và fieldbus, nơi vòng
FOC và vòng an toàn sống — EtherCAT, CAN-FD: frame tĩnh, không có IP stack. Gương bên
xe y hệt: các zonal/body ECU trên CAN, Classic AUTOSAR signal-based.

Cây cầu bắc qua vạch là **micro-ROS**: rclc cộng client XRCE-DDS — một **library**
link thẳng vào firmware, chạy như một task trên RTOS *của bạn*; nó nói **XRCE, không
phải DDS**, với một **Agent** trên máy lớn — và chính Agent gia nhập graph thay mặt
con MCU. Footnote cuối hình cho ai theo track automotive: trên Thor, vai trò tương tự
do middleware trong guest đảm nhận — NvStreams, `ara::com` với SOME/IP hoặc DDS
binding — họ dây DDS chính là thứ AUTOSAR Adaptive chia sẻ với ROS 2, từ bản R18-03.

## Slide 13 — Diagram: graph của một robot thật *(~2 phút)*

Chốt cụm này bằng một tour topology: đây là graph của một con AMR thật, vẽ đúng kiểu
`rqt_graph` sẽ vẽ. Đọc legend trước — mỗi màu là một *loại* thành phần: box xanh =
**một node** (tự xưng tên qua discovery — không ai đấu dây cả, đúng như slide trước);
khung viền đứt = **một họ node** (Nav2); mũi tên xanh lá đơn = **topic**, mũi tên đôi =
**action** (goal cộng feedback cộng result); vạch đỏ đứt = **ranh giới RT**; dải xám =
fieldbus + firmware. Hệ màu này dùng lại y nguyên ở hình "from fleet to joint" lát nữa.

Giờ lần theo dòng dữ liệu: `/lidar_driver` fan-out topic `/scan` cho cả `/slam_toolbox`
lẫn `/amcl` — một publisher, hai subscriber, chẳng cần cấu hình gì thêm. `/imu_driver`
đẩy `/imu` vào `/ekf`; và để ý chiều ngược thú vị: `/ekf` fuse `/imu` với `/odom` —
wheel odometry — mà chính `/controller_manager` publish ngược lên. Rồi `/map`,
`/amcl_pose`, `/odometry/filtered` cùng đổ vào nhóm **Nav2**: `/bt_navigator` →
`/planner_server` → `/controller_server`, và Nav2 nhả `/cmd_vel` xuống
`/controller_manager`.

Hai điểm đắt nhất của hình. Một: tầng fleet chạm vào graph qua đúng **một cửa** —
action `/navigate_to_pose` từ `/fleet_adapter` (Open-RMF) vào `/bt_navigator`; nhớ chi
tiết này, lát tới slide 23 mình sẽ nói "RMF Core bản thân nó cũng là node" — chính là
cắm thêm box vào bức hình này. Hai: dưới `/controller_manager` graph **DỪNG** — vạch
đứt "the graph ends here": bên dưới là vòng RT 1 kHz gọi hàm trực tiếp, không topic
nào cả, rồi EtherCAT/CAN-FD xuống firmware FOC — đúng luật "hard-RT sống ngoài graph"
từ slide 10. Tên node/topic trong hình lấy từ stack wheeled-AMR thật ngoài ngành — lát nữa có
slide liệt kê đúng stack này dạng chữ; còn mini-graph tự chụp của repo nằm ở
`docs/img/demo1_node_list.txt`.

## Slide 14 — Node hoàn chỉnh 20 dòng *(~2 phút)*

Để mọi thứ bớt trừu tượng — đây là một node **hoàn chỉnh, đang chạy thật trong repo của
mình**. Hai mươi dòng Python: khai báo tên node, tạo publisher lên topic `chatter`, timer
2 Hz, xong. Không file cấu hình, không đăng ký master — `rclpy.spin()` là node sống và cả
mạng nhìn thấy nó.

Dòng lệnh bên dưới: từ bất kỳ shell nào, `ros2 topic echo /chatter` là nghe được. Và chú ý
dòng chú thích: cạnh node Python này còn một bản C++ song sinh phát cùng topic — listener
không phân biệt được hai ngôn ngữ.

## Slide 15 — hardware_interface *(~2.5 phút)*

Slide quan trọng nhất cho team mình. Đây là **cửa chính để dân firmware cắm vào robot**:
một class C++ với `on_init` — mở thiết bị CAN/EtherCAT; `read()` — đọc encoder về, mỗi chu
kỳ; `write()` — đẩy lệnh torque xuống, mỗi chu kỳ. Hết.

Ba điều phải nhớ: hai hàm đó chạy **trong thread RT 1 kHz** — cấm malloc, cấm lock, cấm
DDS; controller là plugin riêng, đổi luật điều khiển không đụng driver của bạn; và
`ros2_canopen`, `ethercat_driver_ros2` chính là class này viết sẵn — ai biết CANopen là
dùng được ngay.

## Slide 16 — Diagram: From fleet to joint *(~2.5 phút)*

Gom mọi thứ từ đầu buổi vào một bức hình, đọc từ trái sang phải là đi từ "cả tòa nhà"
xuống "một khớp" — và cùng hệ màu với slide 13: xanh = node, xám viền đứt = process, đỏ
= thread RT, vàng = hộp thư, xanh lá = topic. Trái: tầng fleet Open-RMF — giao task theo
nhịp giây/phút, chạm vào robot qua đúng một cửa là fleet adapter. Tiếp: các node autonomy
— pub/sub async qua DDS; ô "Nav2 stack" là cả một họ node (slide 13 đã mở banh nó ra), và
node thật sự phát `/cmd_vel` 20 Hz là `/controller_server`; mất gói cũng không sao.

Khối viền đứt xám là **một process duy nhất: controller_manager**. Chi tiết ít ai để ý —
và đã verify tận source code nhánh Jazzy: mỗi controller được load có **node nhỏ của
riêng nó**, `/diff_drive_controller`, `/joint_state_broadcaster`, hiện trong
`ros2 node list` cạnh `/controller_manager`, cùng chia executor của process. Subscription
`/cmd_vel` nằm trên node của diff_drive, callback chạy ở thread executor — vẫn là thế
giới "dân sự", chưa đụng gì đến real-time.

Điểm đắt nhất của hình là **ranh giới real-time — hai hộp thư màu vàng**: không có call
nào xuyên qua, chỉ có hộp thư lock-free. Lệnh đi xuống qua `RealtimeBuffer` — "lệnh mới nhất
thắng", kèm watchdog timeout: Nav2 chết là robot tự phanh. State đi lên qua
`RealtimePublisher` — phía RT chỉ try-lock rồi đi tiếp, không bao giờ chờ; một thread
thường làm "bưu tá" publish `/joint_states`. Với dân firmware: đây chính là pattern ISR
đẩy ring buffer, main loop gửi UART — đổi tên thôi.

Bên phải ranh giới là vòng kín của `ros2_control`: một thread SCHED_FIFO trên
PREEMPT_RT, mỗi 1 ms làm đúng ba bước **theo thứ tự đánh số trên hình**: 1 — `read()`
chụp *toàn bộ* input (encoder trên bus → `pos[]`); 2 — `update()` cho các controller
tính (lệnh mới nhất trong hộp thư + `pos[]` → `cmd[]`); 3 — `write()` xuất *toàn bộ*
output xuống bus. Nói to điều dễ hiểu nhầm: **đây là trình tự thời gian trong một tick,
không phải chiều dữ liệu** — state đi lên qua bước 1, lệnh đi xuống qua bước 2-3; y hệt
vòng lặp MCU mình viết hàng ngày: đọc ADC → tính PID → xuất PWM, và tick chạy bất kể có
ai nghe hay không. `read()`/`write()` chính là hai method của class `MyRobot` slide
trước; controller nói chuyện với hardware bằng handle chia sẻ, không topic nào cả. Rồi
CAN-FD/EtherCAT 1–10 kHz xuống MCU firmware — FOC 8–32 kHz, thế giới của mình, không
đổi. Thước dưới cùng là ý cần chốt: **càng sang phải càng nhanh và càng deterministic —
mỗi lần đổi "chất" giao tiếp (DDS → hộp thư → fieldbus) là một lần đổi hợp đồng
timing.**

## Slide 17 — Ảnh rqt_graph thật *(~1 phút)*

Đây không phải hình vẽ — **ảnh chụp màn hình thật** từ hệ đang chạy của mình: node Python
`/talker`, node C++ `/talker_cpp`, cùng đổ vào `/listener` qua topic `/chatter`. Không ai
cấu hình gì — thuần DDS discovery. Khái niệm node/topic từ nãy giờ trông như thế này ngoài
đời.

## Slide 18 — Robot xe: phần đã ổn định *(~1.5 phút)*

Thực trạng mảng xe. AMR trong nhà: stack chuẩn đã đóng băng — `ros2_control`, slam_toolbox,
AMCL, **Nav2** — hơn trăm công ty chạy production, và chưa có planner học máy nào đuổi được
Nav2 khỏi ghế. Xe ngoài đường thì chia đôi: **Autoware** là stack mở tham chiếu cho
shuttle/bus L4; còn robotaxi thương mại — Waymo, Tesla — chạy stack độc quyền end-to-end,
không có ROS trong đó.

## Slide 19 — Diagram: ROS 2 đứng ở đâu *(~1.5 phút)*

Ba cột, ba màu, ba phán quyết: AMR/công nghiệp — **chuẩn de-facto**, xanh. Xe tự hành —
**chỉ là tham chiếu mở**, vàng. Humanoid — **gần như vắng mặt**, đỏ: Unitree có wrapper tùy
chọn, còn Tesla, Figure, 1X, Atlas đều stack riêng.

Dòng chốt bên dưới: học ROS 2 là học dòng chính công nghiệp — và tầng firmware dưới 1 kHz
thì ở đâu cũng y hệt nhau. Kỹ năng của mình chuyển được sang cả ba cột.

## Slide 20 — Humanoid: RL đã thắng *(~2 phút)*

Chuyện lớn nhất của humanoid 2024–2026: cuộc chiến locomotion đã ngã ngũ. MPC cộng
whole-body QP — dòng dõi Atlas — lùi xuống làm tầng thấp; các nền tảng mới ship **policy RL
huấn luyện trong mô phỏng, chạy 50 Hz** — kể cả Atlas điện cũng đã chuyển phe. Tầng nhiệm
vụ thì hội tụ về **VLA hai hệ**: suy luận chậm 1–10 Hz cộng action head nhanh — GR00T,
Helix, π0.5 cùng một hình dạng.

Còn dòng cuối cho anh em mình: firmware mức khớp — FOC, EtherCAT — **không đổi một ly**.

Và một cầu nối nhỏ trước khi qua hình: tất cả những gì vừa nói — GR00T, RL, VLA hai hệ —
gói gọn trong một hình chuỗi ngay sau đây; nhìn xong hình đó mình sẽ rời khỏi một robot
đơn để bước sang chuyện điều phối cả một **fleet** robot.

## Slide 21 — Diagram: từ foundation model xuống motor *(~1.5 phút)*

Chuỗi hoàn chỉnh: camera và câu lệnh vào GR00T — ~94 ms mỗi lần suy luận trên Thor, mỗi lần
nhả một **chunk** nhiều action; xuống policy toàn thân 50 Hz; xuống `ros2_control` 1 kHz;
qua EtherCAT; xuống vòng FOC 8–32 kHz. Vạch đứt giữa hình: **GPU ở trên — firmware cổ điển
ở dưới**. Stack NVIDIA dừng trên vạch 1 kHz; nửa dưới vẫn là nghề của mình.

Và đó cũng là điểm rẽ của buổi hôm nay: từ đây mình rời một robot đơn lẻ, bước sang tầng
điều phối cả một tòa nhà đầy robot — fleet.

## Slide 22 — Diagram: Open-RMF *(~1.5 phút)*

Mô hình tư duy: **đài kiểm soát không lưu cho một tòa nhà đầy robot**. Nhìn hình: RMF core
ở giữa lo lịch giao thông và phân việc; mỗi hãng robot nối vào qua một **fleet adapter**;
hạ tầng — cửa, thang máy — cũng có adapter riêng. Và ô chú thích quan trọng: mỗi robot
**giữ nguyên stack của nó** — RMF không thay Nav2, chỉ điều phối bên trên.

## Slide 23 — Open-RMF: khi nào đáng dùng *(~1.5 phút)*

Tình trạng 2026: còn sống, được OSRA chống lưng, nhánh Jazzy commit đều — nhưng deployment
thật chủ yếu là cụm Singapore: bệnh viện, sân bay. Tức là **niche nhưng có thật**. Và một
chi tiết nối thẳng về slide 11: **RMF Core bản thân nó cũng là các node ROS 2** —
scheduler, dispatcher, negotiation đến dưới dạng node cộng topic trong cùng một graph;
"cài RMF" nghĩa là launch thêm node — đến cửa và thang máy cũng gia nhập qua các adapter
node nhỏ.

Luật ngón tay cái: fleet nhiều hãng cộng hạ tầng chung — đúng bài RMF. Một robot, một hãng —
bỏ qua. Còn VDA 5050 hay được nhắc cùng: đó là **giao thức dây**, không phải bộ điều phối —
nó chạy *dưới* RMF chứ không thay RMF. Hai slide nữa mình sẽ đào sâu đúng chuẩn này.

## Slide 24 — Robot vs Core: ai làm gì *(~1.5 phút)*

Bảng phân vai — chỉ cần nhớ hàng đầu và hàng cuối: né vật cản là việc **của robot**, RMF
không bao giờ chạm sensor; và robot **không bao giờ tự nói chuyện với thang máy** — đi qua
RMF hết. Ở giữa là ba việc của Core: lịch **không-thời gian** — đặt chỗ làn đường theo thời
gian; đấu giá nhiệm vụ; và giải xung đột bằng **thương lượng trước khi robot chạm mặt nhau**.

## Slide 25 — Fleet Adapter *(~2 phút)*

Nếu team nào sau này phải tích hợp RMF thật, slide này là 80% công việc. Fleet adapter là
người phiên dịch hai chiều: nói `rmf_fleet_msgs` chuẩn với Core, nói API riêng với robot.

Ba mức tích hợp — hầu hết deployment thật dùng **Full Control**. Và đường tắt: clone
`fleet_adapter_template`, điền config.yaml, implement bốn hàm — position, battery,
navigate, stop — là xong bộ khung; robot chạy Nav2 thì dùng thẳng `free_fleet`. MiR,
Clearpath đã có adapter sẵn.

## Slide 26 — Diagram: giao diện VDA 5050 *(~2 phút)*

Trước khi vào chi tiết, một hình toàn cảnh. Trên cùng: fleet control — "master control" —
có thể là SYNAOS, Open-RMF, hay Isaac Mission Dispatch của NVIDIA. Ở giữa là MQTT broker,
bản 3.1.1 trở lên, payload JSON — đây chính là dây thật, không phải REST. Bốn topic đi
xuống robot: `order`, `instantActions`, và mới từ v3.0 là `zoneSet`; bốn topic đi lên:
`state`, `factsheet`, `connection`, `visualization`.

Giữa hình là khái niệm quan trọng nhất: một **order** là một **graph** gồm node và edge —
không phải một lệnh đơn. Master control chỉ nhả phần **base** — đoạn đã được phép chạy —
còn phần **horizon** là kế hoạch dự kiến, chưa cho phép. Cơ chế nhả base/horizon từng bước
**chính là cách VDA 5050 điều phối giao thông** — còn logic quyết định *khi nào* nhả, ai
đi trước, giải deadlock ra sao — **nằm ngoài phạm vi spec**, đó là việc của Open-RMF hay
hệ điều phối riêng.

Dưới cùng ba robot — AMR A, AMR B, AGV C — mỗi con tự khai báo mình qua **factsheet**:
hình học, tốc độ, tính năng protocol hỗ trợ. Chú thích cuối hình gói lại: v3.0.0
ra ngày 19/03/2026, do VDA + VDMA + KIT-IFL công bố; thêm robot tự hành hoàn toàn, zone
thật (BLOCKED, SPEED_LIMIT, PRIORITY…), mức lỗi CRITICAL/URGENT; nhưng vẫn không có OTA,
báo lỗi chỉ phẳng một tầng errorType/errorLevel, bảo mật giao hết cho cấu hình broker/TLS.

## Slide 27 — VDA 5050: giao thức dây cho fleet robot *(~2.5 phút)*

Đây là câu trả lời của ngành cho câu hỏi: "một fleet manager nói chuyện với robot của N
hãng khác nhau bằng cách nào?" Và giống hệt cụm automotive lát nữa — chính **VDA**, hiệp
hội công nghiệp ô tô Đức, cùng VDMA và viện KIT-IFL, đứng sau chuẩn này. Ngành robot mượn
nguyên bộ máy chuẩn hóa của ngành xe.

Bản hiện hành là **v3.0.0, ra ngày 19/03/2026** — bản "AMR release": robot tự hành hoàn
toàn (khác AGV chạy theo line/track cũ), khái niệm zone thật, hai mức lỗi CRITICAL/URGENT.
Dây truyền là MQTT 3.1.1 trở lên cộng JSON, theo scheme topic
`vda5050/v3/<manufacturer>/<serialNumber>/<topic>`. Order là graph base/horizon như slide
trước — nhắc lại vì đây chính là cơ chế traffic control, phần logic bên trong explicitly
out of scope.

Zone đáng nói kỹ vì đây là chỗ nhiều bài viết public sai: BLOCKED, LINE_GUIDED, RELEASE,
COORDINATED_REPLANNING, SPEED_LIMIT, ACTION, cộng PRIORITY, PENALTY, DIRECTED, BIDIRECTED
— danh sách dài, nhưng **không có "charging zone"** — mở thẳng spec ra đếm số lần xuất
hiện: zero. Sạc thật là một cặp action `startCharging`/`stopCharging`, không phải zone
type.

Giới hạn spec tự khai: không có OTA — chỉ có `updateCertificate` xoay vòng chứng chỉ TLS,
không cập nhật firmware; chẩn đoán chỉ phẳng một tầng errorType/errorLevel — không có gì
gần với chiều sâu của UDS mà mình học ở cụm automotive tiếp theo; bảo mật là việc của cấu
hình broker/TLS; an toàn là việc của ISO 3691-4, một chuẩn khác hẳn.

Vùng phủ sóng: mạnh nhất ở châu Âu — hệ sinh thái SYNAOS gồm KUKA, Omron, SEW, STILL, MiR;
cộng Bosch Rexroth, DS Automotion; Bắc Mỹ cũng có chỗ đứng thật — OTTO của Rockwell có
chứng nhận VDA 5050 riêng; châu Á thì còn rời rạc. Và điểm nối lại toàn bộ buổi: **Open-RMF
có thể điều khiển robot ngay trên VDA 5050** — qua `vda5050_connector`, MiR ship sẵn
adapter, Isaac Mission Dispatch của NVIDIA cũng nói được giao thức này. VDA 5050 không
thay RMF — nó là lớp dây bên dưới RMF, đúng như mình đã nói ở slide Open-RMF.

## Slide 28 — Diagram: ba máy tính NVIDIA *(~1.5 phút)*

Sang NVIDIA. Họ đóng khung robotics thành **ba máy tính**: TRAIN trên DGX — nơi Cosmos và
GR00T ra đời; SIMULATE trên máy trạm RTX — Isaac Sim, Isaac Lab, dữ liệu tổng hợp; DEPLOY
trên Jetson Thor gắn trong robot. Và mũi tên vòng dưới đáy — dữ liệu hiện trường quay về
train: **data flywheel**, bánh đà dữ liệu. Ai nắm bánh đà, người đó nắm cuộc chơi — đó là
chiến lược thật sự của NVIDIA.

## Slide 29 — NVIDIA: cái gì có thật *(~2 phút)*

Bảng kiểm kê hiện trạng — ba dòng đáng chỉ tay: **Cosmos 3** — world model hợp nhất, ra tháng
5/2026, license Linux Foundation. **GR00T N1.7** — VLA cho robot, tháng 4/2026, và chú ý:
backbone của nó **chính là Cosmos** — hai sản phẩm một dòng máu. Dòng Jetson Thor: MIG chia
được **2** phân vùng — con số này hay bị đồn là 7; số 2 mới là số trong tài liệu JetPack
(slide 60 kể tiếp chuyện số liệu trôi).

Câu chốt dưới bảng: **mở có tầng lớp** — weights và code mở, nhưng tất cả khóa vào
CUDA/TensorRT. Không có đường chạy CPU.

## Slide 30 — Diagram: bên trong Thor (bản vẽ) *(~1.5 phút)*

Mổ con chip. GPU Blackwell 2.560 nhân CUDA bên trái với vạch MIG chia đôi; CPU 14 nhân
Neoverse bên phải; và điểm trả lời câu hỏi "CPU nối GPU bằng gì" — **không có đường riêng
nào cả**: cả hai treo trên Memory Control Fabric, chung 128 GB RAM hợp nhất. Với dân
embedded: nghĩ như một con MCU khổng lồ — mọi thứ chung một bus bộ nhớ.

## Slide 31 — Block diagram chính chủ NVIDIA *(~1.5 phút)*

Còn đây là **hình gốc của chính NVIDIA** — không phải mình vẽ. Đối chiếu được với slide
trước. Nhưng chú ý cảnh báo màu đỏ dưới caption: hình chính chủ này vẽ block **SPE/RTOS —
mà staff NVIDIA sau đó xác nhận không tồn tại trong silicon**. Bài học: đến diagram chính
chủ của hãng cũng phải đối chiếu lại. Chi tiết ở slide sau.

## Slide 32 — Các MCU ẩn trong Thor *(~2.5 phút)*

Signpost nhanh trước khi vào: năm slide tiếp — từ MCU ẩn tới bộ nhớ Thor — là một **deep
dive tùy chọn**. Ai đang gấp giờ có thể nhảy thẳng tới "Robotics vs automotive". Còn ai ở
lại thì đây là câu hỏi anh em hay hỏi nhất: bên trong SoC đó có bao nhiêu MCU, chạy
firmware gì?

Bảng đã kiểm chứng: BPMP lo boot và nguồn, PSC lo bảo mật, RCE/DCE lo camera và hiển thị —
tất cả là **blob đóng, ký số**. Dòng đỏ quan trọng nhất: **SPE — con MCU always-on mà thời
Orin mình được tự viết firmware FreeRTOS lên — đã bị xóa khỏi Thor**, không có SDK thay
thế. Và FSI — đảo an toàn — **chỉ có trên bản DRIVE/IGX, không có trên Jetson**.

Hệ quả cho firmware engineer, đóng khung dưới slide: trong Jetson Thor **không còn nhân
RTOS nào cho mình lập trình** — code real-time hoặc lên PREEMPT_RT, hoặc ra MCU ngoài qua
fieldbus. Đúng kiến trúc cascade từ slide 4.

## Slide 33 — Thor memory: một pool 273 GB/s, không HBM *(~2 phút)*

Bốn slide tiếp theo đi sâu về **bộ nhớ Thor** — từng số trong đây đều được đối chiếu
trực tiếp với datasheet và docs chính chủ của NVIDIA.

Điểm chính: cả CPU, GPU lẫn accelerator **dùng chung một pool LPDDR5X duy nhất** sau
Unified Coherency Fabric — không có HBM ở bất kỳ SKU nào, đó là cái giá của 130 W. Đọc
bảng theo cột: T5000 128 GB, T4000 và DRIVE Thor 64 GB, nhưng **băng thông giữ nguyên
273 GB/s** trên cả ba — bus 256-bit, 4.266 MHz. Cache thì NVIDIA có công bố đàng hoàng:
L1 64+64 KB, L2 1 MB mỗi nhân, và **16 MB system cache dùng chung** — báo cáo gốc nói
"không có số liệu SRAM" là sai.

Câu đóng khung đáng nhớ: workload bị nghẽn bộ nhớ **xuống cấp ít hơn** trên SKU nhỏ so
với khoảng cách TFLOPS — vì băng thông y hệt nhau. Chú ý thêm: mốc "40 W" chỉ có trên
trang marketing, datasheet không có — mình ghi rõ trong gloss.

## Slide 34 — Full coherence và cú lật khuyến nghị allocator *(~2.5 phút)*

Đây là slide đáng tiền nhất cụm này. Orin chỉ có **I/O coherency một chiều**: GPU đọc được
cache CPU, chiều ngược lại thì không. Thor là Tegra đầu tiên có **Sysmem Full Coherency**
— hai chiều, phần cứng tự quản.

Và vì thế lời khuyên allocator **lật ngược**: báo cáo bên ngoài khuyên dùng
`cudaMallocManaged` "cho latency thấp" — docs NVIDIA nói ngược lại. Trên Thor + CUDA 13.0,
allocation managed **không được cache trên GPU**; còn bộ nhớ pageable/host-registered đi
qua đường coherence mới thì — trích nguyên văn — *"can outperform both Pinned memory or
Unified memory"*. Tức là đường nhanh nhất cho handoff perception (GPU) → planning (CPU)
bây giờ là… `malloc` thường. Nếu team chỉ nhớ một điều từ cụm memory này thì nhớ dòng đó.

## Slide 35 — Unified memory: folklore dGPU vs thực tế trên Thor *(~2.5 phút)*

Có một báo cáo bên ngoài thứ hai giải thích *cơ chế* unified memory của Thor — và nó dùng
toàn từ vựng của GPU rời. Slide này là bảng đối chiếu sau khi kiểm chứng.

Đi từng dòng: **"driver migrate page khi cần" — không có gì để migrate**, mọi allocator
đều nằm trên cùng một LPDDR5X, từ "migration" không hề xuất hiện trong docs Tegra; khác
nhau chỉ là ai cache và ai giữ coherence. **"Oversubscription"** — khái niệm của dGPU
(GPU pool nhỏ hơn RAM host), một pool 128 GB thì không có ranh giới nào để vượt, giới
hạn thật là chia ngân sách với OS. **"Không có ATS, coherence yếu hơn GH200"** — ngược:
GPU của Thor đọc pageable memory *qua chính page table của host*, coherence không thua
gì; cái GH200 hơn thật là **quy mô** — 480 GB + HBM qua link 900 GB/s. **"Tune bằng
cudaMemAdvise + prefetch to device"** — `cudaMemAdvise` không có trong docs Tegra, còn
prefetch thì Thor là Tegra đầu tiên hỗ trợ nhưng làm gì có "device pool" để đưa data về.

Câu chốt đóng khung: lời khuyên nào nhắc *migration, oversubscription, preferred
location* là viết cho GPU rời — trên Thor toàn bộ cuộc chơi là **chọn allocator** (slide
trước). Ghi chú nhỏ ở gloss: kể cả với dGPU, gọi là "software migration" cũng sai — từ
Pascal đã là hardware page-fault engine.

## Slide 36 — 273 GB/s là ngân sách: chọn model theo băng thông *(~2.5 phút)*

So với server: H100 (HBM3) 3,35 TB/s, H200 (HBM3e) 4,8, B200 xấp xỉ 8 — Thor kém 12–30
lần. Với decode tự hồi quy, **mỗi token phải đọc lại toàn bộ trọng số**, nên nghẽn là ở
băng thông chứ không phải TOPS.

Bảng roofline — nói rõ với anh em đây là **số suy ra từ công thức, chưa phải đo thật**:
10 tỷ tham số ở FP4 là trần ~55 token/giây; 20 tỷ ở FP8 chỉ còn ~14. Thực tế đạt 60–80%
trần. Đây chính là lý do model VLA cho edge quẩn quanh 2–10 tỷ tham số, và vì sao FP4
trên Thor quan trọng hơn trên H100.

Cuối slide có một nuance cho ai hay so với server: câu "unified memory trên server chậm"
đã lỗi thời — GH200/GB200 nối CPU-GPU bằng **NVLink-C2C coherent 900 GB/s**. Thor là cùng
một ý tưởng, ở mức điện edge. Số liệu gốc và nguồn từng dòng nằm trong ghi chú research
của repo (`research/jetson-thor-memory-2026-07.md`) nếu ai muốn tự soát lại.

## Slide 37 — Diagram: One silicon, two worlds *(~1.5 phút)*

Giờ đặt hai nền tảng NVIDIA cạnh nhau. Trái: robot — ROS 2, Ubuntu, GR00T mở, devkit
3.499 đô mua thoải mái. Phải: xe — DriveWorks, QNX cộng Linux, Alpamayo bị khóa license,
devkit phải xin qua chương trình riêng. Giữa: phần chung — **cùng die Thor, cùng não
Cosmos, cùng TensorRT**. Cùng silicon, hai thế giới — vì sao? Ba slide nữa trả lời.

## Slide 38 — Cùng silicon, khác luật: góc nhìn software *(~2.5 phút)*

Bảng so sánh — hàng đáng giá nhất là hàng cuối: robotics phát hành theo **ngày**, automotive
theo **quý và năm** — vì mỗi bản phát hành bên xe kèm một hồ sơ an toàn. Hàng middleware
cũng đáng nói: robotics có ROS 2 chung cả ngành; xe thì **không có "ROS của xe"** — mỗi
hãng tự xây trên DriveWorks. Đó là lý do kỹ năng ROS 2 chuyển việc dễ, kỹ năng automotive
gắn với quy trình.

Một hàng nữa đáng dừng lại: hàng OS. Automotive ghi "DriveOS 7: hypervisor → QNX hoặc
Linux guest cộng service VM" — có dấu sao, vì đây là chỗ tài liệu chính chủ của NVIDIA
**tự mâu thuẫn với nhau**: SDK công khai nói thẳng *"Multiple Guest OS are not
supported… you can run QNX or Linux, but not both."* — chỉ có cấu hình dual-QNX được tài
liệu hóa, và chỉ trên Orin, không phải Thor. Bức tranh quen thuộc "QNX cộng Linux chạy
song song" là khung hình ở mức platform/marketing; "multiple OS domains" hóa ra nghĩa là
**một guest OS cộng các service VM riêng của NVIDIA** (BPMP, bảo mật, display, chia sẻ
GPU) — không phải hai hệ điều hành khách chạy đồng thời. Hình sau sẽ vẽ lại đúng con số
này, và Alpamayo — mô hình lái xe của NVIDIA — có slide riêng ở cuối phần automotive.

## Slide 39 — Diagram: DriveOS chia đôi phần mềm *(~2.5 phút)*

Kiến trúc bên xe: hypervisor Type-1 chia SoC thành hai máy ảo cách ly phần cứng. Giải
thích nhanh cho ai chưa quen: **Type-1 nghĩa là hypervisor chạy thẳng trên phần cứng,
boot lên trước tiên, không có OS nào bên dưới** — hình dung nó như một RTOS tối giản mà
"task" của nó là nguyên các hệ điều hành. Ba hệ quả: Linux panic thì QNX không hề hấn
(không có OS chung nào để chết lây); hypervisor chỉ vài chục nghìn dòng nên audit/chứng
nhận được — khác hẳn kiểu VirtualBox chạy trên một host OS hàng chục triệu dòng; và nó
tự chia CPU tĩnh cho từng VM nên VM an toàn giữ được deadline.

Trái — **QNX, RTOS thương mại đã pre-cert ASIL-D**: watchdog, I/O xe, logic
fail-operational. Phải — Linux: CUDA, DriveWorks, stack AI. Mũi tên giữa hai bên là
triết lý cả kiến trúc: **"AI đề xuất — bên đã chứng nhận giám sát."** So với robotics ở
ô cam: một Ubuntu duy nhất, không có partition nào được chứng nhận.

Và đúng như vừa nhắc ở slide trước: hình này giờ có thêm một dòng chú thích — bản SDK
công khai chỉ chạy **một guest tại một thời điểm**, "QNX hoặc Linux, không phải cả hai";
cấu hình duy nhất chạy hai guest đồng thời được tài liệu hóa là **dual-QNX, và chỉ trên
Orin**. Nên đọc hình này như khung kiến trúc/triết lý — "một bên đề xuất, một bên giám
sát" — chứ chưa phải bằng chứng cho một Thor thật đang chạy song song QNX và Linux.

## Slide 40 — Diagram: Automotive software stack (DRIVE Thor) *(~2.5 phút)*

Slide 4 mình có stack của robot — đây là **bản đối xứng cho xe**, cùng hình dạng để so
sánh từng tầng, và trả lời luôn câu hỏi "AUTOSAR nằm đâu trong stack NVIDIA".

Đọc từ dưới lên như bên robot: đáy là **các ECU trên xe** — MCU zonal/domain và safety
MCU trên board — đây là **đất của AUTOSAR Classic**, stack tĩnh, kernel real-time ưu tiên cố định. Bằng chứng cụ
thể: firmware safety MCU trên board NVIDIA tên là **AFW — AUTOSAR firmware của Vector**;
thế hệ Orin là AURIX, sang Thor đổi sang **Renesas RH850** — đổi vendor, kiểm chứng từ
docs và forum flash. Nối ECU với máy tính AD là hàng **mạng trong xe** — chính là hàng
fieldbus của bên robot: backbone automotive Ethernet tới 10 Gbps có TSN, còn CAN-FD,
LIN, FlexRay là nhánh legacy. Lên trên: Thor SoC với đảo an toàn FSI; **DriveOS 7** — hypervisor
Type-1 chia QNX ASIL-D và Linux như slide trước; vạch middleware — NvStreams của NVIDIA,
còn **SOME/IP và DDS là của AUTOSAR Adaptive mang vào**; DriveWorks SDK; và trên cùng,
cạnh stack AV của OEM, là ô nét đứt **AUTOSAR Adaptive** — `ara::com`, POSIX/C++, do
Tier-1 cung cấp (Vector MICROSAR, EB corbos) — **không phải IP của NVIDIA**, NVIDIA chỉ
tuyên bố "hỗ trợ đầy đủ".

Hai điểm gửi anh em: một, so với bên robot thì vạch dịch chuyển ở đây không phải DDS mà
là **ranh giới hypervisor/ASIL**. Hai, chi tiết thú vị nhất: AUTOSAR Adaptive có **DDS
binding từ bản 18-03** — nghĩa là một ECU Adaptive và một node ROS 2 nói cùng một họ
giao thức; hai thế giới tưởng xa nhau lại chung dây điện. Mercedes MB.OS là ví dụ thật:
Linux + QNX tự xây, AUTOSAR dùng chọn lọc qua Vector.

## Slide 41 — Bảng chứng nhận: ai cert cái gì *(~2.5 phút)*

Slide này quan trọng vì ngôn từ trong ngành này rất dễ đánh lừa. Bảng trên — **đã chứng
nhận xong**: DriveOS 5.2 đạt ASIL-B năm 2022; DriveOS 6.0 đạt **ASIL-D tháng 1/2025 — nhưng
trên Orin, không phải Thor**; hai chứng nhận quy trình; QNX mang cert riêng vào devkit.
TÜV SÜD, TÜV Rheinland — các tổ chức chứng nhận độc lập của Đức — là người ký.

Đoạn dưới — chữ NVIDIA **cố tình dùng yếu hơn**: Thor mới chỉ "assessed", IGX mới chỉ
"capable". Và dòng đậm cuối: **phía robotics — Jetson, Isaac, GR00T — zero chứng nhận.**
"Certified" và "assessed" cách nhau một trời một vực — đọc spec nhớ soi chữ này.

## Slide 42 — DRIVE Thor: từng phần kiếm ASIL thế nào *(~2.5 phút)*

Vậy cụ thể làm sao ra được ASIL-D? Không phải rắc bụi tiên lên sản phẩm — từng lớp một:
**FSI** — bốn cụm Cortex-R52 chạy lockstep, hai nhân chạy y hệt từng chu kỳ, lệch là báo
lỗi — trọng tài cô lập vật lý. Hơn **22 nghìn cơ chế tự chẩn đoán** rải khắp SoC. Còn lớp
phân vùng phần mềm cụ thể là: hypervisor Type-1 giữ guest **QNX đã cert ASIL-D** cách ly
phần cứng khỏi stack AI QM — và nhắc lại đúng caveat vừa nói: bức tranh "QNX cộng Linux"
là khung platform, **SDK công khai chỉ chạy một guest tại một thời điểm**. Phần mềm thì
**ASIL decomposition**: stack AI giữ mức QM — không claim an toàn gì — còn stack cổ
điển đã cert giám sát nó; *hệ thống* đạt ASIL-D bằng dư thừa, **không phải bằng cách chứng
nhận một mạng neural** — điều đó chưa ai làm được. Ngoài SoC còn một MCU trọng tài cầm
watchdog và quyền cắt nguồn.

Câu đóng khung là bài học mang về cho robot: **cô lập não an toàn, để AI ở QM, giao kill
switch cho một core nhỏ đã cert.** Pattern này sẽ thành luật của robotics sớm thôi.

## Slide 43 — Fleet management — chuẩn cũ, lên thêm một tầng *(~2 phút)*

Rời automotive certification, mình mở một cụm hoàn toàn mới: quản lý cả một **fleet** xe
— robotaxi, xe tải, xe giao hàng — hàng nghìn chiếc mà không ai chạm tay vào được. Bốn
việc phải làm: **remote diagnostics** — đọc mã lỗi từ xa mà không cần lôi xe vào xưởng;
**predictive maintenance** — bắt được pin, phanh, sensor đang trôi khỏi ngưỡng trước khi
hỏng; **OTA update** — vá phần mềm không cần triệu hồi; và **health telemetry** — dòng dữ
liệu liên tục nuôi hai việc trên.

Ba chuẩn làm việc này trung lập với mọi hãng: **UDS (ISO 14229)** — một ngôn ngữ chẩn đoán
mọi ECU đều nói, bất kể hãng nào; **AUTOSAR** — kiến trúc phần mềm quyết định chẩn đoán
nằm ở đâu trong stack; và **SOVD (ISO 17978, mới ra 2026)** — lớp REST/JSON hướng ra
cloud nằm trên UDS.

Dòng gloss dưới slide giờ làm việc khác: giải nghĩa nhanh năm chữ viết tắt sẽ theo mình
suốt cụm — OTA, ECU, UDS, AUTOSAR, SOVD — mỗi cái đều có slide riêng ngay sau đây, nên
không cần nhớ hết ngay bây giờ.

## Slide 44 — Diagram: AUTOSAR Classic *(~2 phút)*

Đi từ trên xuống đúng như hình vẽ. Trên cùng là Application Layer — các **SWC**, Software
Component: door control, torque request, cả bộ cung cấp dữ liệu chẩn đoán — mỗi SWC là
một khối code cô lập. Ngay dưới là **RTE**, Runtime Environment — lớp glue **sinh tự
động**, là giao diện duy nhất mà SWC nhìn thấy: SWC nói chuyện qua *port*, không bao giờ
gọi địa chỉ trực tiếp. Xuống nữa là **BSW**, Basic Software — Services Layer với AUTOSAR
OS, COM, NvM, WdgM, và hai module mình sẽ quay lại ở slide sau: **DCM + DEM**, chẩn đoán
UDS. Dưới BSW là ECU Abstraction Layer — che đi cách board được đấu dây — rồi tới **MCAL**,
Microcontroller Abstraction Layer: driver CAN/LIN/ETH, ADC, PWM, watchdog — nói với dân
firmware thì MCAL gần như HAL của vendor mà anh em đã quen. Có một làn tắt gọi là **CDD**,
Complex Device Driver, cho driver nào không vừa khuôn BSW. Đáy cùng là con MCU thật —
Renesas RH850, Infineon AURIX, NXP S32K.

Ba điều đóng khung: một binary, một ECU, hard real-time; mọi thứ được cấu hình tĩnh lúc
build qua **ARXML** — không có gì tự khám phá lúc chạy; và AUTOSAR OS không phải hàng tự
chế — nó là một kernel real-time tĩnh, ưu tiên cố định, có thêm bảo vệ bộ nhớ và thời gian,
và multicore qua các scalability class SC1–SC4.

## Slide 45 — Diagram: AUTOSAR Adaptive *(~2 phút)*

Bản đối xứng cho máy tính lớn. Điểm đầu tiên phải nói rõ: **Adaptive không phải một hệ
điều hành** — nó là middleware chạy TRÊN một OS POSIX, QNX hoặc Linux; app thấy profile
**PSE51**, còn dịch vụ nền tảng có thể dùng full POSIX.

Trên hình: Adaptive Applications — process C++14, mỗi app thuộc về một **Software
Cluster** — đơn vị cập nhật *và* chẩn đoán, nhớ từ này vì nó quay lại ở UCM. Bên dưới là
**ARA**, AUTOSAR Runtime for Adaptive, chia thành các cụm namespace `ara::`: `ara::com` —
giao tiếp qua SOME/IP hoặc DDS binding; `ara::diag` — chính là DM, chẩn đoán UDS nhưng
chỉ qua DoIP; `ara::ucm` — update; `ara::exec` — vòng đời tiến trình; `ara::per` —
persistency; `ara::log`.

Hai điểm ghim lại: một, đây là mô hình service-oriented — app tìm dịch vụ lúc chạy qua
discovery — nhưng **production build khóa discovery lại và giới hạn cấp phát động chỉ ở
lúc khởi động**, không để nó chạy hoang trong xe thật. Hai, target là SoC hiệu năng cao —
lớp Thor, các HPC domain/zonal — khác hẳn MCU nhỏ của Classic.

## Slide 46 — Classic vs Adaptive: đặt cạnh nhau *(~2.5 phút)*

Giờ đặt hai bảng cạnh nhau. Đọc theo hàng, không đọc hết ô: OS — Classic là AUTOSAR OS;
Adaptive là POSIX, app thấy PSE51. Model — Classic tĩnh, dây hết lúc build qua
ARXML; Adaptive service-oriented nhưng production pin cứng lại. Diagnostics — Classic
dùng DCM+DEM là BSW module; Adaptive dùng DM qua `ara::diag`, và DM **chỉ đi DoIP**,
không có đường CAN. Updates — Classic reflash toàn bộ qua bootloader bằng UDS
0x34/0x36/0x37; Adaptive update theo từng Software Cluster qua UCM. Và cả hai **cùng tồn
tại trên một chiếc xe**: Classic trên các MCU, Adaptive trên các máy tính lớn.

Hai hàng đáng nói nhất — vì có hai mẩu folklore dai dẳng cần đính chính: hàng comms — ai đó nói
"Classic không làm được Ethernet" là **sai**, SOME/IP Transformer đã chuẩn hóa trong
Classic **4.2.1 từ 2016** — trước cả bản đầu tiên của Adaptive (R17-03, 3/2017) một năm;
Classic vẫn có
CAN/LIN/FlexRay nhưng Ethernet/SOME/IP đã ở đó từ lâu. Hàng safety — ai đó nói "Adaptive
là hạng an toàn thấp" cũng sai: Vector đã ship MICROSAR Adaptive Safe ở **ASIL-B**, và
các chương trình ASIL-D đang chạy — kể cả Wind River được TÜV SÜD đánh giá (từ 2019) là
"ASIL-D-suitable".

## Slide 47 — Diagram: UDS diagnostic stack *(~2 phút)*

Đi từ trên xuống. Trên cùng: diagnostic client — tester ở xưởng, hoặc backend fleet đi qua
gateway. Ngay dưới là chính **UDS, ISO 14229** — một tầng application, và chú ý: nó không
quan tâm đi trên dây nào. Xuống một tầng là hai đường vận chuyển: **DoCAN** — CanTp, ISO
15765-2, chạy trên CAN/CAN-FD; và **DoIP**, ISO 13400, chạy trên automotive Ethernet. Rồi
hình rẽ hai nhánh xuống hai loại ECU: bên trái là ECU Classic — DCM lo dispatch/session/
security, DEM giữ DTC và freeze frame, SWC cung cấp dữ liệu; bên phải là máy Adaptive — DM
(`ara::diag`) chỉ nói DoIP, một diagnostic server riêng cho mỗi Software Cluster, app
Adaptive cung cấp dữ liệu.

Dòng chú thích dưới hình là câu quan trọng nhất slide: **cùng một chuỗi byte request chạy
trên cả hai** — `22 F1 90` đọc VIN y hệt nhau, dù là ECU thân xe nhỏ xíu qua CAN hay máy
tính trung tâm qua Ethernet. Một ngôn ngữ, hai đường dây, hai nền tảng.

## Slide 48 — UDS services a fleet actually uses *(~2 phút)*

Bảng service ID — chỉ tay vào vài dòng thật sự dùng trong vận hành fleet, không đọc hết:
`0x10` mở phiên chẩn đoán mở rộng hoặc lập trình; `0x27` SecurityAccess — bắt tay seed-key
trước khi đụng vào cái gì nhạy cảm; `0x22` đọc DID — `0xF190` chính là VIN, cộng version,
tình trạng sensor; `0x19` đọc DTC — mã lỗi kèm freeze frame; `0x31` chạy routine —
self-test, calibrate, hoặc xóa vùng nhớ trước khi flash.

Bốn service flash: `0x34` RequestDownload, `0x35` RequestUpload, `0x36` TransferData,
`0x37` RequestTransferExit — mình cố tình đọc đủ bộ bốn vì **các bài viết ngoài kia rất
hay quên `0x35`**, chỉ nhớ ba trong bốn.

Dòng cuối, dễ hiểu lầm nhất: `0x2A` ReadDataByPeriodicIdentifier — đọc định kỳ, nghe như
telemetry nhưng **không phải**: nó bị giới hạn trong một phiên, phải poll theo thời gian,
và không gian DID chỉ có 0xF2xx — dòng dữ liệu liên tục thật của fleet chạy trên một
pipeline telematics riêng (MQTT hay giao thức riêng), UDS vẫn chỉ là giao thức chẩn đoán.

## Slide 49 — Diagram: fleet UDS end-to-end *(~2 phút)*

Bức tranh trung thực nhất cụm này. Từ trên: fleet backend — kho telemetry, predictive
maintenance, chiến dịch OTA. Hai đường ra khỏi backend: một đường telemetry liên tục qua
MQTT/giao thức telematics riêng; một đường diagnostics qua **SOVD** — REST/HTTP cộng
JSON, ISO 17978:2026. Và dòng chữ đậm ngay giữa hình: **UDS thô không bao giờ lộ ra
internet**.

Xuống xe: TCU — modem 4G/5G, chấm dứt kết nối cloud bằng TLS và chứng chỉ. Rồi tới
**central gateway** — vừa là DoIP gateway vừa là firewall, đây mới là chốt chặn bảo mật
thật sự: nó dịch request từ ngoài thành UDS trong xe. Từ gateway tỏa ra backbone Ethernet
nói DoIP/UDS cộng SOME/IP, và các nhánh CAN/CAN-FD nói CanTp/UDS xuống HPC (chạy DM của
Adaptive, UCM cài OTA) và các ECU zonal/domain, ECU đời cũ (chạy DCM+DEM của Classic).

Chú thích cuối hình lặp lại điều mình vừa nói ở slide trước: `0x2A` có thật, nhưng
telemetry liên tục là việc của pipeline riêng.

## Slide 50 — Diagram: fleet management on DRIVE Thor *(~2.5 phút)*

Đây là hình trả lời câu hỏi "quản lý fleet chạm vào một chiếc xe Thor bằng đường nào" —
chỉ vẽ những gì có tài liệu chứng minh. Đi
từ trên: fleet backend giống hình trước — OTA, telemetry, API SOVD/telematics. Rồi TCU +
central gateway — chú ý dòng ghi chú nghiêng bên cạnh: đây là **hai ECU tách biệt**, không phải Thor, và
**Thor không có vai trò gateway nào được tài liệu hóa**. Từ gateway, đường DoIP/UDS đi vào
mạng trong xe rồi tới board DRIVE AGX Thor.

Trên board, hai vùng tách biệt hoàn toàn: bên trái là **Thor SoC** — bên trong chỉ có
**một guest OS VM** (SDK công khai: một guest, không phải cả hai), chạy stack AV của OEM,
DriveWorks, và AUTOSAR Adaptive dưới dạng lớp Tier-1 — Vector MICROSAR hoặc EB corbos —
với DM (`ara::diag`, UDS qua DoIP, một server mỗi Software Cluster) và UCM (cài OTA từng
Software Cluster). Việc này chạy trên DriveOS 7 — hypervisor Type-1 cộng các service VM
của chính NVIDIA (storage, display, chia sẻ GPU). Cạnh Thor SoC, tách rời hoàn toàn, là
FSI — cụm lockstep Cortex-R52, silicon riêng, không phải partition của hypervisor.

Bên phải board là vùng **Classic AUTOSAR đất thật** — không phải VM: companion MCU
Renesas RH850 chạy MICROSAR Classic (AFW) với DCM+DEM, kết nối với Thor SoC qua một
**giao diện độc quyền UDP over Ethernet** — không phải DoIP.

Dòng chú thích dưới cùng tóm lại: **đã tài liệu hóa** — DM+UCM sống trong guest, Classic
sống trên companion MCU — **không có vai trò fleet-gateway, không có phân vùng Classic-ECU
ảo nào trên Thor**. Hai dòng cuối hình là bảng giải nghĩa viết tắt (TCU, DoIP, DM/UCM,
DCM+DEM, FSI, AFW, SOVD) — hình này dày chữ viết tắt nhất deck nên để sẵn cho khán giả.

## Slide 51 — Fleet reality check *(~2 phút)*

Chốt cụm bằng bảng đối chiếu: cái gì có tài liệu, cái gì chỉ là lời đồn.

Cột "đã tài liệu hóa": một gateway/TCU duy nhất chấm dứt kết nối cloud, UDS thô
không bao giờ chạm internet; SOVD giờ là ISO 17978:2026 — REST/JSON cho cả HPC lẫn ECU
cũ, và ngay trong spec Adaptive, DM đã cài sẵn ASAM SOVD cạnh ISO 14229; và vECU Classic
dưới hypervisor **là chuyện có thật** — nhưng ở EB corbos và COQOS (giờ thuộc Qualcomm từ
tháng 6/2024), danh sách SoC hỗ trợ của COQOS không có NVIDIA.

Cột "thổi phồng — mâu thuẫn với SDK công khai 7.0.3 của Thor": claim "nhiều phân
vùng Classic-AUTOSAR ảo trên Thor" — nguyên văn SDK: *"Multiple Guest OS are not
supported. In addition, you can run QNX or Linux, but not both."*; claim "Thor là gateway
UDS/DoIP của fleet" — zero tài liệu, đường SoC-tới-MCU là giao diện UDP độc quyền; claim
"FSI là một partition hypervisor" — FSI là silicon lockstep tách rời.

Và một trích dẫn chính chủ đáng nhớ: Vector, 25/8/2025, xác nhận trực tiếp — MICROSAR
Classic là "reference integration" cho **FSI và companion MCU**, "lên tới ASIL-D"; còn
MICROSAR Adaptive thì "có thể bật trên nền tảng NVIDIA DRIVE AGX" — đó mới là chỗ AUTOSAR
thật sự đứng trên một chiếc xe chạy Thor.

## Slide 52 — Diagram: E/E architecture consolidation *(~1.5 phút)*

Vì sao fleet management dễ hơn theo thời gian — nhìn ba giai đoạn trên hình. 2000 thập
niên: hàng trăm ECU, mỗi cái một chức năng, dây CAN điểm-nối-điểm — chẩn đoán là cắm vào
cổng OBD, nói chuyện với từng ECU một. 2015–2022: domain controller — powertrain, body,
chassis, infotainment — nhóm chức năng lại, gateway route giữa các bus. Và bây giờ, kiến
trúc SDV: zonal cộng central — một vài central computer HPC chạy AV/AD, Adaptive AUTOSAR,
OTA; các zonal ECU chỉ còn nhóm theo **vị trí vật lý** trên xe, nối bằng Ethernet backbone
TSN, còn phần mềm được gom về trung tâm.

Dòng chú thích dưới hình là lý do cả cụm fleet này tồn tại được: ít hộp hơn để flash, một
gateway để bảo mật, một chỗ để gom dữ liệu sức khỏe, và OTA theo từng software cluster
thay vì reflash từng ECU. Số liệu "trên 100 ECU xuống dưới chục" là con số ngành đưa ra,
không phải con số đo được.

Cuối hình có dòng giải nghĩa viết tắt nếu khán giả cần: DC = domain controller;
FL/FR/RL/RR = bốn góc xe (trước/sau — trái/phải); HPC = high-performance computer;
AV/AD = autonomous vehicle / automated driving (stack tự lái); OTA = over-the-air update;
TSN = time-sensitive networking.

## Slide 53 — Diagram: fleet standards map *(~2 phút)*

Đặt hai cột song song — robot bên trái, xe bên phải — bốn hàng chức năng. Fleet
orchestration: robot có VDA 5050 (dây) cộng Open-RMF (điều phối) cộng MassRobotics (chia
sẻ trạng thái); xe thì **không có chuẩn nào** — dispatch vẫn độc quyền theo từng operator.
Cloud diagnostics API: robot dựa vào nền tảng thương mại như InOrbit, Formant — trên thực
tế chứ không phải chuẩn; xe có hẳn SOVD, ISO 17978. Software update: robot dùng tool chứ
không chuẩn — Mender, RAUC, SWUpdate; xe có UDS flash cộng UCM theo từng Software Cluster,
được chuẩn hóa. Platform architecture: robot có ROS 2 — de-facto nhưng mở; xe có AUTOSAR
Classic+Adaptive — chuẩn an toàn ISO 26262.

Dòng chú thích cuối là insight thật của cả bức tranh: **mỗi bên chuẩn hóa đúng cái
tầng bên kia bỏ ngỏ** — và cả hai đều thiếu một thứ: chưa ai có chuẩn discovery ngữ nghĩa
kiểu "DID cho khả năng cảm biến" — factsheet của VDA 5050 chỉ tả hình học và protocol,
không tả robot "nhìn thấy gì".

## Slide 54 — Two fleets, two standard stacks *(~2 phút)*

Gói cụm fleet lại bằng đúng cái bất đối xứng ở hình trước, rồi điểm mấy chỗ bài viết
public hay trượt khỏi spec — tất cả đã đối chiếu trực tiếp với spec.

Thứ nhất: VDA 5050 v3.0 là bản hiện hành — ra ngày **19/03/2026** — mà phần lớn bài viết
public vẫn mô tả bản 2.x cũ. Thứ hai: "vùng sạc" — **không tồn tại** trong danh sách zone
type của spec, sạc là một cặp action `startCharging`/`stopCharging`. Thứ ba, cú thổi
phồng lớn nhất: "Redfish cộng PICMG IoT.x đang được đẩy mạnh cho fleet robot" — **không
có tài liệu nào** chứng minh, hai chuẩn có thật nhưng chẳng liên quan gì tới AMR, bị khâu
lại thành một xu hướng không tồn tại. Và những mảnh CÓ thật mà bài viết hay bỏ sót:
MassRobotics (chia sẻ trạng thái, bổ trợ), OPC 40010 (giám sát tài sản), RMF chạy trên
VDA 5050 (tích hợp đang ship).

Bài học đóng khung ở gloss: **bài viết public thường đúng về bản thân các chuẩn, nhưng
sai về xu hướng kiến trúc mà họ tự suy ra từ chuẩn** — tin phần đầu, kiểm phần sau.

## Slide 55 — Alpamayo *(~2 phút)*

Người anh em lái xe của GR00T. NVIDIA gọi tiến hóa phần mềm xe là AV 1.0 module hóa →
2.0 end-to-end → **3.0 VLA biết suy luận** — Alpamayo là canh bạc 3.0, ra CES tháng 1/2026.

Bảng so với GR00T — hai dòng đắt nhất: **backbone cùng là Cosmos** — bằng chứng kỹ thuật
mạnh nhất rằng robot và xe đang chung não; và dòng cuối — **trust model**: GR00T được tin
điều khiển robot trực tiếp, Alpamayo thì **không bao giờ một mình** — luôn có stack cổ điển
đã cert kèm sát. Cùng công nghệ, khác chế độ trách nhiệm.

## Slide 56 — Diagram: DRIVE Hyperion 10 *(~1.5 phút)*

Đây là kiến trúc sensor tham chiếu **có thật** của NVIDIA — 14 camera, 9 radar, 1 lidar,
12 ultrasonic, 2 con Thor bên trong; hình chiếc xe là minh họa của mình, còn cấu hình
sensor là spec công bố. Điểm đáng ngẫm ở footnote: **một bộ sensor cố định, chứng nhận một
lần, nhân bản cho trăm nghìn xe** — ngược hẳn robotics, nơi mỗi con robot tự chọn sensor.
Chuẩn hóa là cái giá và cũng là sức mạnh của certification.

## Slide 57 — Ảnh devkit thật *(~30 giây)*

Phần cứng bằng xương bằng thịt — ảnh chính chủ devkit DRIVE AGX Thor: SoC giữa board, card
dọc, 16 cổng camera GMSL. Không có giá niêm yết — muốn mua phải vào chương trình developer
của NVIDIA. So với con Jetson 3.499 đô đặt hàng là ship.

## Slide 58 — Automotive ships *(~1.5 phút)*

Nó có bán được thật không? Có, nhưng nói mốc cho chuẩn: **CLA sản xuất hàng loạt từ tháng
6/2025** — xe MB.OS đầu tiên; còn stack lái enhanced-L2 do NVIDIA cung cấp ("L2++" là cách
gọi của ngành, không phải bậc SAE) dự kiến **rollout ở Mỹ trước cuối 2026** — dual-stack
đúng kiến trúc slide 39. **Uber ký chạy robotaxi 28 thành phố đến 2028**, và mục tiêu trăm
nghìn xe L4 là "tăng dần, bắt đầu từ 2027" chứ không phải xong trước 2028. Doanh thu
automotive của NVIDIA: 2,3 tỷ đô một năm — nghe to nhưng chỉ ~1% doanh thu NVIDIA.

Câu đóng khung: robotics ship **thí nghiệm hàng tuần**, automotive ship **sản phẩm chứng
nhận hàng năm** — trên cùng một con chip.

## Slide 59 — Chọn phe nào? *(~2 phút)*

Câu hỏi cá nhân nhất buổi: embedded software engineer nên theo bên nào? Việc hàng ngày hai
bên khác hẳn — bên robot: viết hardware_interface, driver CAN, tune PREEMPT_RT, ship hàng
tuần; bên xe: MISRA, truy vết requirement, WCET, ký safety case, ship hàng năm nhưng chữ ký
của bạn là thứ máy không thay được.

Nhưng dòng đậm giữa slide mới là ý chính: **phần giao nhau chính là cái nghề** — real-time,
fieldbus, ranh giới an toàn, đưa AI xuống silicon — hai bên cần y hệt nhau. Kết luận đóng
khung: **học trên Physical AI** vì rẻ và mở — GR00T chạy ngay trên bàn mình rồi — **giữ khả
năng đọc ISO 26262**. Khi robotics có luật riêng — và tín hiệu đã rõ — kỹ sư song ngữ được
trả giá cao nhất.

## Slide 60 — Số liệu trôi: luôn mở lại nguồn gốc *(~2 phút)*

Như đã hứa ở slide 3 — hai ví dụ vì sao đừng tin số liệu truyền tay. Hai con số nghe rất
kêu vẫn đang lan truyền trong các bài viết: "MIG trên Thor chia 7 phân vùng" — tài liệu
JetPack nói **2**; và bộ số benchmark GR00T TensorRT "117 xuống 92 ms, so với RTX 5090" —
số trong tài liệu NVIDIA là **144,9 xuống 93,8 ms**, và GPU so sánh thật là RTX Pro 5000 /
H100 — sai cả số lẫn GPU. Cả hai đều "hợp lý đến mức không ai buồn nghi".

Bài học một câu cho team: **số liệu Physical AI trôi rất nhanh — release ra hàng tháng,
bài viết không đuổi kịp. Mở lại nguồn gốc trước khi con số đi vào design doc, hay slide.**

## Slide 61 — Live demo: GR00T trên một GPU desktop *(~2.5 phút)*

Cao trào: mình chạy **thật** GR00T N1.7 — 3 tỷ tham số — zero-shot trên card RTX 5070 Ti
16 GB, dữ liệu mẫu từ repo public của NVIDIA.

Bảng số đo thật — nói rõ là **hai lần chạy riêng biệt**: lần A là lần đầu tiên, cache
lạnh — load 94,6 giây, trung bình 107,7 ms mỗi lần gọi; lần B cache ấm — load 20,5 giây,
106,4 ms (ảnh slide sau chính là lần B). VRAM đỉnh **7,5 trên 16 GB** — không tràn. Mỗi
lần gọi nhả **8 action step tương lai** — quy ra ~75 step sinh ra mỗi giây, nhưng nhấn
mạnh: đó là **thông lượng tính toán, không phải nhịp lệnh robot thực thi**. Còn hai con số
MSE là **sai số dự đoán open-loop trên 2 quỹ đạo mẫu — không phải "độ chính xác" hoàn thành
task**. Mọi thứ đều public — weights trên Hugging Face, script trên GitHub — team mình tải
về chạy lại được nguyên xi.

Điểm kỹ thuật đáng nhớ: **action chunking** — 9 lần suy luận mỗi giây nhưng mỗi lần nhả 8
step, nên vẫn đủ nhịp lệnh cho robot thật; còn thực thi bao nhiêu step trước khi replan là
lựa chọn lúc deploy.

## Slide 62 — Ảnh chụp lần chạy *(~30 giây)*

Và đây — ảnh chụp thật terminal lúc chạy: lệnh, MSE hai quỹ đạo, thống kê latency, dòng
Done. Không phải mock-up. Ai muốn xem log gốc thì nó nằm trong repo.

## Slide 63 — Ý nghĩa cho team embedded *(~2 phút)*

Gom cả buổi thành bốn gạch đầu dòng: một — **tầng dưới 1 kHz không đổi**, đó là lãnh thổ
mình, mọi stack đều cần nó. Hai — đường nhanh nhất vào robotics cho dân embedded:
**ros2_control cộng EtherCAT/CANopen cộng PREEMPT_RT** — không phải đi học train model.
Ba — học **giao diện** của tầng ML: policy ăn gì nhả gì ở nhịp nào — nội tạng của nó để
sau. Bốn — an toàn luôn nằm **cạnh** compute, trên PLC hay MCU safety-rated — tính đến
07/2026 chưa Jetson robotics nào, chưa stack ROS nào có chứng nhận hoàn tất.

## Slide 64 — Roadmap + takeaways *(~1.5 phút)*

Việc tiếp theo của repo, theo thứ tự đáng làm: demo `ros2_control`; Gazebo; micro-ROS cộng
CANopen trên vcan; đo PREEMPT_RT bằng cyclictest; demo Open-RMF; cuối cùng mới tới track
NVIDIA. Toàn việc chạm tay được, mỗi mục một buổi chiều.

Bảy takeaway đã nằm trên slide — mình chỉ đọc một: **robot và xe chung một dòng model
(Cosmos-Reason); thứ chia đôi hai thế giới là chứng nhận, không phải công nghệ.**

## Slide 65 — Glossary 1/3: robotics & software *(~20 giây)*

Ba slide tra cứu cho người mới — **không đọc, mọi người chụp lại là được**. Slide này là
toàn bộ từ viết tắt phía robotics: ROS 2, DDS, QoS, FOC, SLAM, VLA, WCET… mỗi từ một
dòng giải nghĩa. Trong lúc thuyết trình nếu ai lạc ở từ nào thì ba slide này là phao.

## Slide 66 — Glossary 2/3: silicon, memory & automotive *(~20 giây)*

Nửa còn lại: phần cứng và automotive — LPDDR5X, HBM, MIG, UVM/ATS, rồi cụm chứng nhận
ASIL/SEooC/TÜV, và cụm AUTOSAR CP/AP, SOME/IP, TSN. Điểm nhấn duy nhất đáng nói miệng:
ASIL đọc từ thấp lên cao là QM rồi A tới D — deck này dùng thang đó liên tục. Còn muốn
đào sâu nội bộ AUTOSAR với UDS thì có slide 3/3 ngay sau — đây mới là bản rút gọn.

## Slide 67 — Glossary 3/3: AUTOSAR & vehicle diagnostics *(~20 giây)*

Slide tra cứu thứ ba, dành riêng cho cụm AUTOSAR/UDS vừa học: SWC, RTE, BSW, MCAL, CDD ở
nửa Classic; ARA, `ara::`, PSE51, Software Cluster ở nửa Adaptive; rồi UDS, SID, DTC/DID,
DoCAN/DoIP, DCM/DEM, DM/UCM, SOVD, và cả VDA 5050/AGV/MQTT/base-horizon phía robot. Không
đọc — chụp lại khi cần.

## Slide 67 — References *(~30 giây)*

Toàn bộ nguồn — chia **bốn nhóm** (mới thêm nhóm Fleet/diagnostics cho cụm
AUTOSAR/UDS/VDA 5050), kèm ghi chú số demo là của mình đo. Hai bài blog trên Confluence có
bản văn xuôi đầy đủ của deck này — một bản primer 10 phút cho người mới, một bản
deep-dive. Cảm ơn mọi người — câu hỏi?

---

## Phòng thân Q&A (các câu dễ bị hỏi)

- **"1 kHz sao gọi là real-time?"** — real-time = deadline chứng minh được, không phải
  nhanh; jitter PREEMPT_RT ~50 µs là số minh họa đã tune (mình chưa tự đo — cyclictest nằm
  trong roadmap) = 5% chu kỳ 1 kHz; nhanh hơn phải chứng minh trên target hoặc dùng MCU
  (slide 7 có bảng).
- **"DDS không real-time à?"** — nói chuẩn: graph ROS 2 *mặc định* không phải ranh giới
  hard-RT; bản thân DDS được thiết kế cho hệ real-time phân tán và tune deterministic
  được — có bài realtime_proposal trên design.ros2.org; intra-process còn né được
  serialization. Cái mình khuyên là đừng đặt topic hop vào đường torque nếu chưa đo.
- **"MSE 0.003 nghĩa là robot làm được việc?"** — không; đó là sai số dự đoán open-loop
  trên 2 quỹ đạo mẫu, không nói gì về tỉ lệ hoàn thành task khi robot chạy closed-loop.
- **"Số 22.000 cơ chế chẩn đoán lấy đâu ra?"** — nguồn thứ cấp, đã ghi chú thận trọng ngay
  trên slide 42; con số chưa đối chiếu được trang chính chủ.
- **"RH850 hay AURIX trên board DRIVE?"** — bằng chứng công khai thế hệ Thor chỉ về RH850
  (docs + forum flash); thời Orin là AURIX; Infineon vẫn PR chung chung — đã đánh dấu "cần
  xác nhận thêm" trong báo cáo.
- **"GR00T chạy 16 GB thật không? Fine-tune được không?"** — inference: thật, 7,5 GB đỉnh,
  ảnh slide 62. Fine-tune: khuyến nghị ≥40 GB VRAM — máy mình không đủ, cần GPU lớn/cloud.
- **"Sao không thấy Apollo/Baidu, Mobileye?"** — phạm vi đợt này là hệ sinh thái NVIDIA và
  stack mở; các stack độc quyền khác nằm ngoài scope, có thể là đợt research sau.
- **"Cosmos 3 tải về chạy được không?"** — bản Nano 16B cần ~32 GB VRAM (BF16) — quá cỡ
  card mình; đó là lý do demo chọn GR00T 3B.
- **"VDA 5050 có thay được Open-RMF không?"** — không, khác lớp: VDA 5050 là **wire
  protocol** (MQTT + JSON, order/state/factsheet), Open-RMF là **coordinator** (lịch
  không-thời gian, đấu giá nhiệm vụ, giải xung đột). RMF có thể *chạy trên* VDA 5050 qua
  `vda5050_connector` — chuyện có thật, MiR ship sẵn adapter. Bản thân VDA 5050 cũng
  không làm traffic logic: spec tự khai routing/deadlock resolution là ngoài phạm vi.
- **"Sao không chạy Classic AUTOSAR trong VM trên Thor?"** — mẫu hình "Classic vECU dưới
  hypervisor" có thật, nhưng ở EB corbos Hypervisor và COQOS (nay thuộc Qualcomm từ
  6/2024) — danh sách SoC của COQOS (Qualcomm, NXP, Renesas, TI, Samsung) không có
  NVIDIA. Trên Thor, không có tài liệu nào cho thấy Classic chạy như guest của
  hypervisor; Classic sống trên companion MCU thật — Renesas RH850 — theo đúng xác nhận
  của Vector.
- **"UDS có dùng làm telemetry được không?"** — về mặt kỹ thuật `0x2A` (đọc định kỳ) tồn
  tại và chạy được qua DoIP, nhưng nó bị giới hạn trong một phiên, phải poll theo thời
  gian, không gian DID hẹp (0xF2xx) — không phải kênh streaming. Fleet thật dùng pipeline
  telematics riêng (MQTT/proprietary) cho dữ liệu liên tục, và UDS thô **không bao giờ**
  lộ ra internet — gateway/TCU luôn là chốt dịch.
- **"Deck nói một guest OS mà hình vẽ hai VM — mâu thuẫn?"** — đã đối chiếu kỹ: luật chính
  xác là "không trộn guest", không phải "chỉ một guest duy nhất" — DriveOS hỗ trợ ba cấu
  hình: Linux đơn, QNX đơn, hoặc **dual-QNX** (hai VM QNX) — không có cấu hình QNX+Linux
  đồng thời nào được tài liệu hóa, kể cả trên Thor lẫn thế hệ Orin trước đó. "Multiple OS
  domains" của NVIDIA nghĩa là guest(s) cộng các service VM riêng (BPMP, bảo mật,
  display, chia sẻ GPU) — không phải hai OS khách chạy song song. Không có nguồn OEM nào
  công khai xác nhận QNX + Linux cùng chạy trên một Thor.
- **"Redfish/PICMG có phải hướng tương lai cho robot fleet?"** — audit không tìm thấy tài
  liệu nào ghép hai chuẩn này với AMR/robot fleet. Redfish là chuẩn quản lý server/BMC
  của DMTF; PICMG IoT.1 là data model cảm biến nhà máy, phần mở rộng Redfish còn "work in
  progress". Hai chuẩn có thật, nhưng bị một báo cáo bên ngoài khâu lại thành một xu
  hướng không hề tồn tại — đã gạch khỏi deck.
- **"SOVD có thay UDS không?"** — không, ASAM nói rõ SOVD "được phát triển để cùng tồn
  tại, không phải thay thế UDS". SOVD là lớp REST/JSON hướng cloud, đứng trên UDS và có
  thể front cả ECU cũ; UDS vẫn là ngôn ngữ chẩn đoán trong xe. AUTOSAR Adaptive còn cài
  sẵn cả hai — DM nói ISO 14229 lẫn ASAM SOVD.
- **"Compose nhiều node vào một process là tự động được zero-copy à?"** — không;
  intra-process comms là **opt-in theo từng node** — `use_intra_process_comms(true)`,
  và chỉ có ở rclcpp/C++ (rclpy không có). Composition mà không opt-in thì message
  giữa hai node cùng process vẫn đi qua DDS như thường; compose chỉ tiết kiệm
  process/discovery, còn zero-copy phải tự bật.
