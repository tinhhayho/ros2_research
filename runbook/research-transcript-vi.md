# Transcript thuyết trình — deck `slides/research.html` (tiếng Việt)

Kịch bản nói cho deck research 40 slide. Tổng thời lượng ~40–45 phút (không tính Q&A).
Deck này dày thông tin — nguyên tắc nói: **không đọc bảng**, chỉ kể câu chuyện và chỉ tay
vào 1–2 ô đắt nhất mỗi bảng; ai cần chi tiết đã có blog + báo cáo trong repo.

Gợi ý nhịp: phần 1–2 (nền tảng) nói kỹ; phần NVIDIA/Automotive nói theo kiểu "tour có
điểm dừng"; demo cuối là cao trào — đừng để cháy giờ trước khi tới đó.

---

## Slide 1 — Robot software stacks 2026 *(~1 phút)*

Chào mọi người. Đây là kết quả đợt nghiên cứu tháng 7 của mình về phần mềm robot năm 2026 —
từ robot xe, humanoid, đến cả hai nền tảng của NVIDIA.

Hai cam kết trước khi bắt đầu: một, **mọi nhận định về thế giới bên ngoài đều có nguồn và
đã được kiểm chứng lại tận gốc** — cuối deck có slide chỉ ra chỗ nào kiểm chứng phát hiện
sai. Hai, **mọi con số demo là số đo thật trên máy của mình** — và cuối buổi mọi người sẽ
thấy ảnh chụp thật của lần chạy đó.

## Slide 2 — Agenda *(~1 phút)*

Lộ trình tám phần: bắt đầu bằng **bản đồ** — một hình dạng stack chung cho mọi robot; rồi
soi gần ROS 2 với code thật; kiểm tra thực trạng từng mảng; tầng fleet Open-RMF; sang
NVIDIA — cả Physical AI lẫn Automotive, có mổ cả con chip Thor; phần audit; demo thật;
và chốt bằng ý nghĩa cho team mình. Ai quan tâm mảng nào có thể đón ở phần đó.

## Slide 3 — How this research was made *(~1.5 phút)*

Một phút về phương pháp, vì nó quyết định độ tin của mọi slide sau: nguồn chính thống —
docs chính chủ, GitHub, Hugging Face, arXiv — được quét theo từng đợt có ngân sách cứng.
Sau đó **14 nhận định chịu lực nhất được kiểm chứng lại độc lập bằng cách mở lại đúng
nguồn gốc**: 11 đúng, 2 sai phải sửa, 1 không kiểm chứng được. Hai cái sai đó là gì —
slide 35 sẽ khui. Điểm mình muốn gửi gắm: số liệu ngành này trôi rất nhanh, đừng tin
slide nào không ghi nguồn — kể cả slide của mình.

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
1 kHz trong vòng RT, bản lập kế hoạch trăm ms trong MoveIt. Ba: **SLAM không bao giờ
real-time** — SLAM khựng thì robot tạm dừng điều hướng chứ torque không hề hấn.

Và dòng cuối slide: cách phân tầng này là canon của ngành từ thập niên 70–90, không phải
mình bịa — Liu & Layland, kiến trúc RCS của Albus, three-layer của Gat.

## Slide 7 — Real-time ≠ fast *(~2.5 phút)*

Slide này trả lời câu hỏi chắc chắn ai đó đang định hỏi: *"real-time gì mà có 1 kHz?"*

Thứ nhất, chữ "ROS 2" thực ra là **hai thế giới**: DDS graph — mọi message qua middleware,
trễ cỡ ms; và `ros2_control` — được ROS 2 cấu hình nhưng vòng nóng **bỏ qua DDS hoàn
toàn**, gọi hàm C++ trực tiếp.

Thứ hai, nhìn bảng: real-time nghĩa là **cam kết deadline xấu nhất, không phải nhanh**.
PREEMPT_RT jitter xấu nhất ~50 micro giây — bằng 5% chu kỳ 1 kHz, ổn; nhưng bằng 50% chu
kỳ 10 kHz — vỡ. Đó là trần của Linux. 1 kHz là nơi Linux hết xấu hổ **và** vật lý hết quan
tâm — hằng số thời gian cơ khí cỡ ms rồi. Nhanh hơn nữa là việc của MCU, của anh em mình.

## Slide 8 — Hệ sinh thái ROS 2 *(~1.5 phút)*

Bản đồ repo — không đọc từng dòng, chỉ ba điểm: dòng đầu, `ros2/*` là lõi — client library,
rcl, rmw. Dòng hai, `ros2_control` — framework mà dân actuator như mình sẽ sống trong đó.
Và dòng cuối bảng phụ: tất cả **Apache/BSD, không có cổng chặn nào** — khác hẳn thế giới
automotive lát nữa. Distro mình dùng: Jazzy, LTS tới 2029.

## Slide 9 — Node hoàn chỉnh 20 dòng *(~2 phút)*

Để mọi thứ bớt trừu tượng — đây là một node **hoàn chỉnh, đang chạy thật trong repo của
mình**. Hai mươi dòng Python: khai báo tên node, tạo publisher lên topic `chatter`, timer
2 Hz, xong. Không file cấu hình, không đăng ký master — `rclpy.spin()` là node sống và cả
mạng nhìn thấy nó.

Dòng lệnh bên dưới: từ bất kỳ shell nào, `ros2 topic echo /chatter` là nghe được. Và chú ý
dòng chú thích: cạnh node Python này còn một bản C++ song sinh phát cùng topic — listener
không phân biệt được hai ngôn ngữ.

## Slide 10 — hardware_interface *(~2.5 phút)*

Slide quan trọng nhất cho team mình. Đây là **cửa chính để dân firmware cắm vào robot**:
một class C++ với `on_init` — mở thiết bị CAN/EtherCAT; `read()` — đọc encoder về, mỗi chu
kỳ; `write()` — đẩy lệnh torque xuống, mỗi chu kỳ. Hết.

Ba điều phải nhớ: hai hàm đó chạy **trong thread RT 1 kHz** — cấm malloc, cấm lock, cấm
DDS; controller là plugin riêng, đổi luật điều khiển không đụng driver của bạn; và
`ros2_canopen`, `ethercat_driver_ros2` chính là class này viết sẵn — ai biết CANopen là
dùng được ngay.

## Slide 11 — Ảnh rqt_graph thật *(~1 phút)*

Đây không phải hình vẽ — **ảnh chụp màn hình thật** từ hệ đang chạy của mình: node Python
`/talker`, node C++ `/talker_cpp`, cùng đổ vào `/listener` qua topic `/chatter`. Không ai
cấu hình gì — thuần DDS discovery. Khái niệm node/topic từ nãy giờ trông như thế này ngoài
đời.

## Slide 12 — Robot xe: phần đã ổn định *(~1.5 phút)*

Thực trạng mảng xe. AMR trong nhà: stack chuẩn đã đóng băng — `ros2_control`, slam_toolbox,
AMCL, **Nav2** — hơn trăm công ty chạy production, và chưa có planner học máy nào đuổi được
Nav2 khỏi ghế. Xe ngoài đường thì chia đôi: **Autoware** là stack mở tham chiếu cho
shuttle/bus L4; còn robotaxi thương mại — Waymo, Tesla — chạy stack độc quyền end-to-end,
không có ROS trong đó.

## Slide 13 — Diagram: ROS 2 đứng ở đâu *(~1.5 phút)*

Ba cột, ba màu, ba phán quyết: AMR/công nghiệp — **chuẩn de-facto**, xanh. Xe tự hành —
**chỉ là tham chiếu mở**, vàng. Humanoid — **gần như vắng mặt**, đỏ: Unitree có wrapper tùy
chọn, còn Tesla, Figure, 1X, Atlas đều stack riêng.

Dòng chốt bên dưới: học ROS 2 là học dòng chính công nghiệp — và tầng firmware dưới 1 kHz
thì ở đâu cũng y hệt nhau. Kỹ năng của mình chuyển được sang cả ba cột.

## Slide 14 — Humanoid: RL đã thắng *(~2 phút)*

Chuyện lớn nhất của humanoid 2024–2026: cuộc chiến locomotion đã ngã ngũ. MPC cộng
whole-body QP — dòng dõi Atlas — lùi xuống làm tầng thấp; các nền tảng mới ship **policy RL
huấn luyện trong mô phỏng, chạy 50 Hz** — kể cả Atlas điện cũng đã chuyển phe. Tầng nhiệm
vụ thì hội tụ về **VLA hai hệ**: suy luận chậm 1–10 Hz cộng action head nhanh — GR00T,
Helix, π0.5 cùng một hình dạng.

Còn dòng cuối cho anh em mình: firmware mức khớp — FOC, EtherCAT — **không đổi một ly**.

## Slide 15 — Diagram: Open-RMF *(~1.5 phút)*

Sang tầng fleet. Mô hình tư duy: **đài kiểm soát không lưu cho một tòa nhà đầy robot**.
Nhìn hình: RMF core ở giữa lo lịch giao thông và phân việc; mỗi hãng robot nối vào qua một
**fleet adapter**; hạ tầng — cửa, thang máy — cũng có adapter riêng. Và ô chú thích quan
trọng: mỗi robot **giữ nguyên stack của nó** — RMF không thay Nav2, chỉ điều phối bên trên.

## Slide 16 — Open-RMF: khi nào đáng dùng *(~1.5 phút)*

Tình trạng 2026: còn sống, được OSRA chống lưng, nhánh Jazzy commit đều — nhưng deployment
thật chủ yếu là cụm Singapore: bệnh viện, sân bay. Tức là **niche nhưng có thật**.

Luật ngón tay cái: fleet nhiều hãng cộng hạ tầng chung — đúng bài RMF. Một robot, một hãng —
bỏ qua. Còn VDA 5050 hay được nhắc cùng: đó là **giao thức dây**, không phải bộ điều phối —
nó chạy *dưới* RMF chứ không thay RMF.

## Slide 17 — Robot vs Core: ai làm gì *(~1.5 phút)*

Bảng phân vai — chỉ cần nhớ hàng đầu và hàng cuối: né vật cản là việc **của robot**, RMF
không bao giờ chạm sensor; và robot **không bao giờ tự nói chuyện với thang máy** — đi qua
RMF hết. Ở giữa là ba việc của Core: lịch **không-thời gian** — đặt chỗ làn đường theo thời
gian; đấu giá nhiệm vụ; và giải xung đột bằng **thương lượng trước khi robot chạm mặt nhau**.

## Slide 18 — Fleet Adapter *(~2 phút)*

Nếu team nào sau này phải tích hợp RMF thật, slide này là 80% công việc. Fleet adapter là
người phiên dịch hai chiều: nói `rmf_fleet_msgs` chuẩn với Core, nói API riêng với robot.

Ba mức tích hợp — hầu hết deployment thật dùng **Full Control**. Và đường tắt: clone
`fleet_adapter_template`, điền config.yaml, implement bốn hàm — position, battery,
navigate, stop — là xong bộ khung; robot chạy Nav2 thì dùng thẳng `free_fleet`. MiR,
Clearpath đã có adapter sẵn.

## Slide 19 — Diagram: ba máy tính NVIDIA *(~1.5 phút)*

Sang NVIDIA. Họ đóng khung robotics thành **ba máy tính**: TRAIN trên DGX — nơi Cosmos và
GR00T ra đời; SIMULATE trên máy trạm RTX — Isaac Sim, Isaac Lab, dữ liệu tổng hợp; DEPLOY
trên Jetson Thor gắn trong robot. Và mũi tên vòng dưới đáy — dữ liệu hiện trường quay về
train: **data flywheel**, bánh đà dữ liệu. Ai nắm bánh đà, người đó nắm cuộc chơi — đó là
chiến lược thật sự của NVIDIA.

## Slide 20 — NVIDIA: cái gì có thật *(~2 phút)*

Bảng kiểm kê đã audit — ba dòng đáng chỉ tay: **Cosmos 3** — world model hợp nhất, ra tháng
5/2026, license Linux Foundation. **GR00T N1.7** — VLA cho robot, tháng 4/2026, và chú ý:
backbone của nó **chính là Cosmos** — hai sản phẩm một dòng máu. Dòng Jetson Thor: MIG chia
được **2** phân vùng — con số này từng bị đồn là 7, audit mới lòi ra.

Câu chốt dưới bảng: **mở có tầng lớp** — weights và code mở, nhưng tất cả khóa vào
CUDA/TensorRT. Không có đường chạy CPU.

## Slide 21 — Diagram: bên trong Thor (bản vẽ) *(~1.5 phút)*

Mổ con chip. GPU Blackwell 2.560 nhân CUDA bên trái với vạch MIG chia đôi; CPU 14 nhân
Neoverse bên phải; và điểm trả lời câu hỏi "CPU nối GPU bằng gì" — **không có đường riêng
nào cả**: cả hai treo trên Memory Control Fabric, chung 128 GB RAM hợp nhất. Với dân
embedded: nghĩ như một con MCU khổng lồ — mọi thứ chung một bus bộ nhớ.

## Slide 22 — Block diagram chính chủ NVIDIA *(~1.5 phút)*

Còn đây là **hình gốc của chính NVIDIA** — không phải mình vẽ. Đối chiếu được với slide
trước. Nhưng chú ý cảnh báo màu đỏ dưới caption: hình chính chủ này vẽ block **SPE/RTOS —
mà staff NVIDIA sau đó xác nhận không tồn tại trong silicon**. Bài học: đến diagram của
hãng cũng phải audit. Chi tiết ở slide sau.

## Slide 23 — Các MCU ẩn trong Thor *(~2.5 phút)*

Câu hỏi anh em hay hỏi nhất: bên trong SoC đó có bao nhiêu MCU, chạy firmware gì?

Bảng đã kiểm chứng: BPMP lo boot và nguồn, PSC lo bảo mật, RCE/DCE lo camera và hiển thị —
tất cả là **blob đóng, ký số**. Dòng đỏ quan trọng nhất: **SPE — con MCU always-on mà thời
Orin mình được tự viết firmware FreeRTOS lên — đã bị xóa khỏi Thor**, không có SDK thay
thế. Và FSI — đảo an toàn — **chỉ có trên bản DRIVE/IGX, không có trên Jetson**.

Hệ quả cho firmware engineer, đóng khung dưới slide: trong Jetson Thor **không còn nhân
RTOS nào cho mình lập trình** — code real-time hoặc lên PREEMPT_RT, hoặc ra MCU ngoài qua
fieldbus. Đúng kiến trúc cascade từ slide 4.

## Slide 24 — Diagram: từ foundation model xuống motor *(~1.5 phút)*

Chuỗi hoàn chỉnh: camera và câu lệnh vào GR00T — ~94 ms mỗi lần suy luận trên Thor, mỗi lần
nhả một **chunk** nhiều action; xuống policy toàn thân 50 Hz; xuống `ros2_control` 1 kHz;
qua EtherCAT; xuống vòng FOC 8–32 kHz. Vạch đứt giữa hình: **GPU ở trên — firmware cổ điển
ở dưới**. Stack NVIDIA dừng trên vạch 1 kHz; nửa dưới vẫn là nghề của mình.

## Slide 25 — Diagram: One silicon, two worlds *(~1.5 phút)*

Giờ đặt hai nền tảng NVIDIA cạnh nhau. Trái: robot — ROS 2, Ubuntu, GR00T mở, devkit
3.499 đô mua thoải mái. Phải: xe — DriveWorks, QNX cộng Linux, Alpamayo bị khóa license,
devkit phải xin qua chương trình riêng. Giữa: phần chung — **cùng die Thor, cùng não
Cosmos, cùng TensorRT**. Cùng silicon, hai thế giới — vì sao? Ba slide nữa trả lời.

## Slide 26 — Cùng silicon, khác luật: góc nhìn software *(~2 phút)*

Bảng so sánh — hàng đáng giá nhất là hàng cuối: robotics phát hành theo **ngày**, automotive
theo **quý và năm** — vì mỗi bản phát hành bên xe kèm một hồ sơ an toàn. Hàng middleware
cũng đáng nói: robotics có ROS 2 chung cả ngành; xe thì **không có "ROS của xe"** — mỗi
hãng tự xây trên DriveWorks. Đó là lý do kỹ năng ROS 2 chuyển việc dễ, kỹ năng automotive
gắn với quy trình.

## Slide 27 — Diagram: DriveOS chia đôi phần mềm *(~2 phút)*

Kiến trúc bên xe: hypervisor Type-1 chia SoC thành hai máy ảo cách ly phần cứng. Trái —
**QNX, RTOS thương mại đã pre-cert ASIL-D**: watchdog, I/O xe, logic fail-operational.
Phải — Linux: CUDA, DriveWorks, stack AI. Mũi tên giữa hai bên là triết lý cả kiến trúc:
**"AI đề xuất — bên đã chứng nhận giám sát."** So với robotics ở ô cam: một Ubuntu duy
nhất, không có partition nào được chứng nhận.

## Slide 28 — Bảng chứng nhận: ai cert cái gì *(~2.5 phút)*

Slide này quan trọng vì ngôn từ trong ngành này rất dễ đánh lừa. Bảng trên — **đã chứng
nhận xong**: DriveOS 5.2 đạt ASIL-B năm 2022; DriveOS 6.0 đạt **ASIL-D tháng 1/2025 — nhưng
trên Orin, không phải Thor**; hai chứng nhận quy trình; QNX mang cert riêng vào devkit.
TÜV SÜD, TÜV Rheinland — các tổ chức chứng nhận độc lập của Đức — là người ký.

Đoạn dưới — chữ NVIDIA **cố tình dùng yếu hơn**: Thor mới chỉ "assessed", IGX mới chỉ
"capable". Và dòng đậm cuối: **phía robotics — Jetson, Isaac, GR00T — zero chứng nhận.**
"Certified" và "assessed" cách nhau một trời một vực — đọc spec nhớ soi chữ này.

## Slide 29 — DRIVE Thor: từng phần kiếm ASIL thế nào *(~2.5 phút)*

Vậy cụ thể làm sao ra được ASIL-D? Không phải rắc bụi tiên lên sản phẩm — từng lớp một:
**FSI** — bốn cụm Cortex-R52 chạy lockstep, hai nhân chạy y hệt từng chu kỳ, lệch là báo
lỗi — trọng tài cô lập vật lý. Hơn **22 nghìn cơ chế tự chẩn đoán** rải khắp SoC. Phần mềm
thì **ASIL decomposition**: stack AI giữ mức QM — không claim an toàn gì — còn stack cổ
điển đã cert giám sát nó; *hệ thống* đạt ASIL-D bằng dư thừa, **không phải bằng cách chứng
nhận một mạng neural** — điều đó chưa ai làm được. Ngoài SoC còn một MCU trọng tài cầm
watchdog và quyền cắt nguồn.

Câu đóng khung là bài học mang về cho robot: **cô lập não an toàn, để AI ở QM, giao kill
switch cho một core nhỏ đã cert.** Pattern này sẽ thành luật của robotics sớm thôi.

## Slide 30 — Alpamayo *(~2 phút)*

Người anh em lái xe của GR00T. NVIDIA gọi tiến hóa phần mềm xe là AV 1.0 module hóa →
2.0 end-to-end → **3.0 VLA biết suy luận** — Alpamayo là canh bạc 3.0, ra CES tháng 1/2026.

Bảng so với GR00T — hai dòng đắt nhất: **backbone cùng là Cosmos** — bằng chứng kỹ thuật
mạnh nhất rằng robot và xe đang chung não; và dòng cuối — **trust model**: GR00T được tin
điều khiển robot trực tiếp, Alpamayo thì **không bao giờ một mình** — luôn có stack cổ điển
đã cert kèm sát. Cùng công nghệ, khác chế độ trách nhiệm.

## Slide 31 — Diagram: DRIVE Hyperion 10 *(~1.5 phút)*

Đây là kiến trúc sensor tham chiếu **có thật** của NVIDIA — 14 camera, 9 radar, 1 lidar,
12 ultrasonic, 2 con Thor bên trong; hình chiếc xe là minh họa của mình, còn cấu hình
sensor là spec công bố. Điểm đáng ngẫm ở footnote: **một bộ sensor cố định, chứng nhận một
lần, nhân bản cho trăm nghìn xe** — ngược hẳn robotics, nơi mỗi con robot tự chọn sensor.
Chuẩn hóa là cái giá và cũng là sức mạnh của certification.

## Slide 32 — Ảnh devkit thật *(~30 giây)*

Phần cứng bằng xương bằng thịt — ảnh chính chủ devkit DRIVE AGX Thor: SoC giữa board, card
dọc, 16 cổng camera GMSL. Không có giá niêm yết — muốn mua phải vào chương trình developer
của NVIDIA. So với con Jetson 3.499 đô đặt hàng là ship.

## Slide 33 — Automotive ships *(~1.5 phút)*

Nó có bán được thật không? Có: **Mercedes CLA sản xuất từ quý 1 năm nay** — dual-stack đúng
kiến trúc slide 27, bán ở mức L2++. **Uber ký chạy robotaxi 28 thành phố đến 2028, mục tiêu
trăm nghìn xe L4.** Doanh thu automotive của NVIDIA: 2,3 tỷ đô một năm — nghe to nhưng chỉ
~1% doanh thu NVIDIA.

Câu đóng khung: robotics ship **thí nghiệm hàng tuần**, automotive ship **sản phẩm chứng
nhận hàng năm** — trên cùng một con chip.

## Slide 34 — Chọn phe nào? *(~2 phút)*

Câu hỏi cá nhân nhất buổi: embedded software engineer nên theo bên nào? Việc hàng ngày hai
bên khác hẳn — bên robot: viết hardware_interface, driver CAN, tune PREEMPT_RT, ship hàng
tuần; bên xe: MISRA, truy vết requirement, WCET, ký safety case, ship hàng năm nhưng chữ ký
của bạn là thứ máy không thay được.

Nhưng dòng đậm giữa slide mới là ý chính: **phần giao nhau chính là cái nghề** — real-time,
fieldbus, ranh giới an toàn, đưa AI xuống silicon — hai bên cần y hệt nhau. Kết luận đóng
khung: **học trên Physical AI** vì rẻ và mở — GR00T chạy ngay trên bàn mình rồi — **giữ khả
năng đọc ISO 26262**. Khi robotics có luật riêng — và tín hiệu đã rõ — kỹ sư song ngữ được
trả giá cao nhất.

## Slide 35 — Trust, but audit *(~1.5 phút)*

Như đã hứa ở slide 3 — kiểm chứng bắt được gì? Hai nhận định nghe rất kêu và **sai**: "MIG
trên Thor chia 7 phân vùng" — thực tế là **2**; và bộ số benchmark TensorRT lan truyền —
sai cả số lẫn GPU so sánh, số thật là 144,9 xuống 93,8 ms. Cả hai đều "hợp lý đến mức không
ai buồn nghi".

Bài học một câu: **số liệu Physical AI trôi rất nhanh — mở lại nguồn gốc trước khi con số
lên slide.** Deck này được viết đúng bằng quy tắc đó.

## Slide 36 — Live demo: GR00T trên một GPU desktop *(~2.5 phút)*

Cao trào: mình chạy **thật** GR00T N1.7 — 3 tỷ tham số — zero-shot trên card RTX 5070 Ti
16 GB, dữ liệu mẫu từ repo public của NVIDIA.

Bảng số đo thật: VRAM đỉnh **7,5 trên 16 GB** — không tràn; **106 ms mỗi lần gọi**; mỗi lần
nhả chunk 8 action nên thông lượng ~**75 action mỗi giây** — thừa cho robot thật; load model
20 giây từ cache. Mọi thứ đều public — weights trên Hugging Face, script trên GitHub — team
mình tải về chạy lại được nguyên xi.

Điểm kỹ thuật đáng nhớ: **action chunking** — 9 lần suy luận mỗi giây thành 75 lệnh mỗi
giây. Đó là mánh khiến foundation model điều khiển nổi robot.

## Slide 37 — Ảnh chụp lần chạy *(~30 giây)*

Và đây — ảnh chụp thật terminal lúc chạy: lệnh, MSE hai quỹ đạo, thống kê latency, dòng
Done. Không phải mock-up. Ai muốn xem log gốc thì nó nằm trong repo.

## Slide 38 — Ý nghĩa cho team embedded *(~2 phút)*

Gom cả buổi thành bốn gạch đầu dòng: một — **tầng dưới 1 kHz không đổi**, đó là lãnh thổ
mình, mọi stack đều cần nó. Hai — đường nhanh nhất vào robotics cho dân embedded:
**ros2_control cộng EtherCAT/CANopen cộng PREEMPT_RT** — không phải đi học train model.
Ba — học **giao diện** của tầng ML: policy ăn gì nhả gì ở nhịp nào — nội tạng của nó để
sau. Bốn — an toàn luôn nằm **cạnh** compute, trên PLC hay MCU safety-rated — không Jetson
nào, không stack ROS nào được chứng nhận cả.

## Slide 39 — Roadmap + takeaways *(~1.5 phút)*

Việc tiếp theo của repo, theo thứ tự đáng làm: demo `ros2_control`; Gazebo; micro-ROS cộng
CANopen trên vcan; đo PREEMPT_RT bằng cyclictest; demo Open-RMF; cuối cùng mới tới track
NVIDIA. Toàn việc chạm tay được, mỗi mục một buổi chiều.

Bảy takeaway đã nằm trên slide — mình chỉ đọc một: **robot và xe chung một bộ não; thứ chia
đôi hai thế giới là chứng nhận, không phải công nghệ.**

## Slide 40 — References *(~30 giây)*

Toàn bộ nguồn — chia ba nhóm, kèm ghi chú số demo là của mình đo. Hai bài blog trên
Confluence có bản văn xuôi đầy đủ của deck này — một bản primer 10 phút cho người mới, một
bản deep-dive. Cảm ơn mọi người — câu hỏi?

---

## Phòng thân Q&A (các câu dễ bị hỏi)

- **"1 kHz sao gọi là real-time?"** — real-time = cam kết deadline, không phải nhanh; jitter
  PREEMPT_RT ~50 µs = 5% chu kỳ 1 kHz; nhanh hơn là việc của MCU (slide 7 có bảng).
- **"Số 22.000 cơ chế chẩn đoán lấy đâu ra?"** — nguồn thứ cấp, đã ghi chú thận trọng ngay
  trên slide 29; con số chưa đối chiếu được trang chính chủ.
- **"RH850 hay AURIX trên board DRIVE?"** — bằng chứng công khai thế hệ Thor chỉ về RH850
  (docs + forum flash); thời Orin là AURIX; Infineon vẫn PR chung chung — đã đánh dấu "cần
  xác nhận thêm" trong báo cáo.
- **"GR00T chạy 16 GB thật không? Fine-tune được không?"** — inference: thật, 7,5 GB đỉnh,
  ảnh slide 37. Fine-tune: khuyến nghị ≥40 GB VRAM — máy mình không đủ, cần GPU lớn/cloud.
- **"Sao không thấy Apollo/Baidu, Mobileye?"** — phạm vi đợt này là hệ sinh thái NVIDIA và
  stack mở; các stack độc quyền khác nằm ngoài scope, có thể là đợt research sau.
- **"Cosmos 3 tải về chạy được không?"** — bản Nano 16B cần ~32 GB VRAM (BF16) — quá cỡ
  card mình; đó là lý do demo chọn GR00T 3B.
