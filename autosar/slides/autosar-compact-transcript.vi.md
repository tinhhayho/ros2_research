# Kịch bản thuyết trình tiếng Việt — Deck AUTOSAR 30 phút (Classic vs Adaptive)

Đây là kịch bản thuyết trình từng slide cho deck rút gọn 30 phút "AUTOSAR in 30 minutes — Classic vs Adaptive", gồm 24 slide theo đúng thứ tự. Mỗi mục ghi rõ thời lượng mục tiêu bằng đúng ngân sách giây trong say-note của slide, chia thành các khối nói có nhãn (Mở đầu / các ý / Chốt), một dòng "Chuyển slide" để bắc cầu sang slide sau, và một dòng "Lưu ý khi trình bày" ở những chỗ thật sự cần. Tổng thời lượng nói cộng dồn là khoảng 27 phút rưỡi (1648 giây), chừa lại chừng 2 tới 3 phút cho phần hỏi đáp trong khung 30 phút. Toàn bộ số liệu, ngày tháng, tên riêng và cảnh báo trung thực đều bám sát nội dung deck; các thuật ngữ kỹ thuật, tên module và tên API được giữ nguyên tiếng Anh cho đúng thói quen của kỹ sư.

---

## Slide 1 — AUTOSAR in 30 minutes — Classic vs Adaptive: what runs where

**Thời lượng mục tiêu: ~40 giây.** Slide mở màn: đặt một câu hỏi duy nhất và trấn an rằng khán giả đã có sẵn mô hình tư duy.

**Mở đầu, đặt câu hỏi (~15 giây):**
"Chào anh em. Ba mươi phút, và chỉ có một câu hỏi thôi: phần mềm AUTOSAR nào chạy trên con chip nào. Đó là toàn bộ câu chuyện hôm nay. Một tổ chức, hai nền tảng, cùng nằm trong một chiếc xe."

**Mốc phiên bản (~12 giây):**
"Mọi thứ trong deck này được đóng dấu theo bản phát hành R25-11, công bố ngày 27 tháng 11 năm 2025. Những khẳng định lấy từ bên ngoài đều có nguồn là URL, và deck đầy đủ giữ toàn bộ tài liệu tham chiếu."

**Trấn an khán giả (~13 giây):**
"Anh em đã biết MCU, biết CAN, biết một cái RTOS và biết reflash bare-metal. Vậy là anh em đã có sẵn mô hình tư duy rồi. Việc của hôm nay chỉ là gọi tên phiên bản ô tô của những thứ đó. CP là Classic Platform, AP là Adaptive Platform, hai chữ này sẽ lặp lại suốt buổi."

**Chuyển slide:**
"Trước khi vào kỹ thuật, phải trả lời một câu đã: vì sao AUTOSAR lại tồn tại."

**Lưu ý khi trình bày:** đọc "R25-11" là "R hai lăm mười một". Nói thong thả, đây là slide để khán giả ổn định chỗ ngồi.

---

## Slide 2 — Why AUTOSAR exists — one standard, many competitors

**Thời lượng mục tiêu: ~75 giây.** Slide này gieo một quy tắc kinh doanh sẽ quay lại ở cuối deck, nên phải nói cho rõ.

**Mở đầu, bản chất (~18 giây):**
"Điều đầu tiên cần gỡ hiểu nhầm: AUTOSAR là một quan hệ hợp tác phát triển toàn cầu, không phải một sản phẩm. Các cuộc bàn thảo sáng lập diễn ra năm 2002, và Development Agreement được ký vào tháng Bảy năm 2003. Hiện nay có khoảng 340 partner, chính xác là 339 vào cuối năm 2025, trải khắp ngành. Spec thì đọc miễn phí, nhưng muốn build ra sản phẩm từ nó thì phải có license."

**Mô hình trong một câu (~22 giây):**
"Toàn bộ mô hình gói gọn trong một câu từ thời sáng lập, trích Heinecke và cộng sự năm 2006: hợp tác trên tiêu chuẩn, cạnh tranh trên phần triển khai. Có một spec chung và một XML schema chung. Rồi nhiều nhà cung cấp bán stack conformant của riêng họ, tất cả cùng build ra từ cái spec đó."

**Quy tắc dự báo ai áp dụng (~25 giây):**
"Và đây là quy tắc kinh doanh dự báo được ai sẽ dùng AUTOSAR: giá trị của nó tăng theo số lượng ranh giới tổ chức mà phần mềm của anh em phải đi qua. Các Tier-1 triển khai AUTOSAR để thắng RFQ của OEM. Còn một OEM tích hợp dọc như Rivian thì bỏ qua luôn, tự xây stack của mình. Cái này có trong bài phỏng vấn trên Sonatus."

**Chốt (~10 giây):**
"Nhớ lấy quy tắc này. Nó sẽ quay lại ở slide bảng quyết định silicon và slide cây quyết định ở cuối."

**Chuyển slide:**
"Giờ vào chiếc xe thật: một xe, hai nền tảng, chạy ở đâu."

**Lưu ý khi trình bày:** nếu bị hỏi "340 hay 339?", trả lời: khoảng 340 hiện tại, con số chốt cuối 2025 là 339. Tier-1 là nhà cung cấp làm ECU cho OEM; OEM là hãng làm xe; RFQ là request for quotation.

---

## Slide 3 — One vehicle, two platforms

**Thời lượng mục tiêu: ~55 giây.** Slide khung xương: dựng thế giới quan hai nền tảng, chưa đi sâu.

**Mở đầu, hai nền tảng (~20 giây):**
"Một chiếc xe, hai nền tảng. Classic chạy trên các MCU deeply-embedded, những con vi điều khiển lo các tác vụ điều khiển nhanh. Adaptive chạy trên các SoC high-performance-compute, viết tắt là HPC, những con lo phần tính toán nặng."

**Ý cốt lõi, không phải đối thủ (~20 giây):**
"Điểm quan trọng nhất của slide này: hai cái đó không phải đối thủ của nhau. Chúng cùng tồn tại trong một chiếc xe đời 2026. Classic không bị Adaptive thay thế, và Adaptive không cố làm việc của Classic."

**Chốt, cách nối (~15 giây):**
"Chúng nối với nhau qua Ethernet và các gateway. Cả buổi hôm nay, anh em cứ giữ trong đầu bức tranh này: hai nền tảng nằm cạnh nhau trong cùng một xe."

**Chuyển slide:**
"Bắt đầu từ bên quen thuộc với dân firmware trước: Classic gói gọn trong một slide."

**Lưu ý khi trình bày:** đọc "HPC" là "H P C". Đây là slide chuyển tiếp ngắn, đừng dừng lâu.

---

## Slide 4 — Classic in one slide

**Thời lượng mục tiêu: ~70 giây.** Ba ý trụ của Classic: static, OS là kernel real-time tĩnh, và đường ASIL-D chín muồi.

**Mở đầu, mọi thứ đều static (~22 giây):**
"Classic trong một slide. Nguyên tắc số một: mọi thứ đều static và được quyết ngay lúc build. Tập task, memory map và communication matrix đều bị đóng băng trong ARXML. Rồi tool sinh tất cả những cái đó ra thành đúng một binary cho một ECU."

**OS là kernel real-time tĩnh (~20 giây):**
"OS ở đây là một kernel real-time tĩnh. Toàn bộ task được chốt lúc build, lịch ưu tiên cố định, không có heap, giống một RTOS cấu hình tĩnh mà bạn đã quen nhưng chặt hơn. Nó được đóng gói thành các Scalability Class từ SC1 đến SC4, các class cao thêm dần phần bảo vệ timing và bảo vệ bộ nhớ."

**Đường ASIL-D chín muồi (~20 giây):**
"Và Classic nắm con đường ASIL-D đã chín muồi. Tính tất định của nó đến từ chính việc mọi thứ đều static. Bản triển khai AUTOSAR đầu tiên được chứng nhận theo ISO 26262 lên tới mức ASIL D xuất hiện năm 2016. Cụ thể là Vector MICROSAR Safe, do exida chứng nhận."

**Chốt (~8 giây):**
"Static, OS là kernel real-time tĩnh, và ASIL-D chín. Ba trụ đó là toàn bộ tinh thần của Classic."

**Chuyển slide:**
"Slide sau tôi sẽ chỉ một cái mẹo. Đây là ý tưởng thật sự mới với dân bare-metal."

**Lưu ý khi trình bày:** chỉ vào hình stack Classic khi nói "một binary cho một ECU". ASIL đọc là "A-SIL", các mức QM nhỏ hơn A, B, C, D theo ISO 26262.

---

## Slide 5 — The relocation trick — why an SWC relocates across ECUs without a code change

**Thời lượng mục tiêu: ~75 giây.** Slide "aha moment" cho dân firmware: nêu vấn đề trước, rồi mới tiết lộ cơ chế.

**Mở đầu, tạo móc (~10 giây):**
"Slide trước tôi có hứa một cái mẹo. Đây là ý tưởng thật sự mới nếu anh em quen làm bare-metal: di dời một software component từ ECU này sang ECU khác mà không sửa một dòng code nào của nó."

**Cơ chế, phần một: VFB (~20 giây):**
"Bí quyết nằm ở chỗ các software component không bao giờ gọi thẳng nhau, và cũng không bao giờ gọi bus hay driver. Chúng chỉ nói chuyện qua một thứ gọi là Virtual Functional Bus, bằng ba hàm: Rte_Write, Rte_Read và Rte_Call. Trong code của component không hề có chữ CAN, không có SPI, không có tên ECU nào cả."

**Cơ chế, phần hai: RTE sinh theo deployment (~30 giây):**
"Vậy ai quyết định dữ liệu thật sự đi đâu? Là RTE, và RTE được sinh ra theo từng deployment. Anh em nhìn hình: bên trên là hai component nói chuyện trên VFB, bên dưới là khi chúng được gán vào ECU thật. Nếu hai component nằm cùng một ECU, tool sinh RTE thành một cú copy buffer nội bộ. Nếu chúng nằm trên hai ECU khác nhau, tool sinh RTE thành một message COM đi ra CAN hoặc Ethernet. Code của component giữ nguyên trong cả hai trường hợp."

**Chốt (~15 giây):**
"Cho nên khi di dời component, thứ duy nhất thay đổi là code mà generator phát ra. Bare-metal không có thứ gì tương đương cả."

**Chuyển slide:**
"Giờ mình đi xuống một tầng: khi tín hiệu thật sự phải ra dây, Classic đóng gói nó như thế nào."

**Lưu ý khi trình bày:** nói chậm hơn các slide khác vì đây là khái niệm nền cho phần ara::com của Adaptive. Nếu bị hỏi "giống HAL hay dependency injection?": giống về tinh thần, nhưng đây là code-gen lúc build cho cả kiến trúc xe, không phải lookup lúc runtime, nên không trả giá hiệu năng.

---

## Slide 6 — CP comms + diagnostics in 60 seconds

**Thời lượng mục tiêu: ~75 giây.** Ba khối đều nhau: comm matrix, tách hai module chẩn đoán, và reflash.

**Mở đầu, communication matrix (~27 giây):**
"Classic comm và diagnostics trong sáu mươi giây. Communication dùng một communication matrix đóng băng, hay còn gọi là K-matrix. Nó là signal-oriented, không phải service-oriented. Nó cố định mọi frame, mọi signal, mọi bên gửi và bên nhận ngay lúc build. Module COM đóng gói các signal vào các I-PDU rồi bắn ra CAN, LIN, FlexRay hoặc Ethernet. Toàn bộ được sinh static, nên anh em chứng minh được nó ngay ở khâu tích hợp."

**Ý dễ sai nhất: DEM tính, DCM định dạng (~30 giây):**
"Chẩn đoán tách thành hai module, và đây là chỗ người ta hay nhầm nhất, phải nắm cho đúng. DEM là bên tính. Nó là cơ sở dữ liệu bộ nhớ lỗi, làm debounce kết quả của các monitor và duy trì cái UDS status byte cho từng DTC. Còn DCM là bên định dạng. Nó là một UDS server được sinh ra, đọc từ DEM và nói chuyện với máy tester. DCM không tự tính gì về lỗi cả."

**Reflash quen thuộc (~18 giây):**
"Và reflash thì chính là cái bootloader anh em đã biết. Các dịch vụ UDS 0x34, 0x36 và 0x37, tức RequestDownload, TransferData và RequestTransferExit, nạp lại nguyên cả ECU thông qua bootloader."

**Chuyển slide:**
"Đến đây là hết phần Classic. Câu hỏi tiếp theo: tại sao lại cần một nền tảng thứ hai?"

**Lưu ý khi trình bày:** nhấn mạnh câu "DEM tính, DCM định dạng", đây là điểm dễ hỏi. I-PDU đọc là "I P D U". Nếu bị hỏi FlexRay: nói ngắn là bus tất định tốc độ cao, nay đang giảm dần.

---

## Slide 7 — Why Adaptive exists

**Thời lượng mục tiêu: ~85 giây.** Slide bản lề: điểm mạnh của CP hóa thành giới hạn, và câu định nghĩa AP phải nói thật chính xác.

**Mở đầu, điểm mạnh thành giới hạn (~40 giây):**
"Vì sao lại cần nền tảng thứ hai. Chính những điểm mạnh của Classic lại hóa thành giới hạn. Nó có một communication matrix static, không có service discovery lúc runtime. Nó không có dynamic deployment, và chỉ có OTA của function ở mức hạn chế. Phần BSW của nó thì C-centric và không có heap. Cộng lại, Classic không thể chứa các stack C++ lớn, luôn thay đổi, và các stack perception."

**Câu trả lời của AUTOSAR (~33 giây):**
"Câu trả lời của AUTOSAR là một nền tảng thứ hai: một service platform trên POSIX. Và câu này phải nói cho thật chính xác. Adaptive là middleware và các service nằm trên một POSIX OS. Nó không phải một OS mới. Các Adaptive Application chỉ là các process POSIX bình thường, viết bằng C++ và link với ARA."

**Chốt, chỉ vào hình (~12 giây):**
"Anh em nhìn hình stack Adaptive: bên dưới là POSIX OS có sẵn, bên trên là lớp ARA và các ứng dụng. AUTOSAR không thay OS, họ đặt một tầng service lên trên OS."

**Chuyển slide:**
"Nhưng không phải OS nào cũng đỡ được Adaptive. Có một lằn ranh cứng chọn kernel cho anh em."

**Lưu ý khi trình bày:** câu "nó không phải một OS mới" là câu hay bị hiểu sai nhất về AP, hãy nhấn. ARA đọc là "A R A", viết tắt AUTOSAR Runtime for Adaptive Applications.

---

## Slide 8 — AP runs only on a POSIX OS — the line that picks your kernel

**Thời lượng mục tiêu: ~70 giây.** Slide phân loại kernel. Đừng đọc hết bảng; nêu đúng hai yêu cầu của spec rồi chia hai nhóm.

**Mở đầu, hai yêu cầu của spec (~28 giây):**
"Đây là lằn ranh kiến trúc cứng nhất. Spec bắt buộc điều này. Ứng dụng phải lập trình theo POSIX PSE51 cộng với C++ Standard Library. Cái này nằm trong AP_SWS_OperatingSystemInterface, Doc 719, requirement RS_OSI_00100, tên là POSIX PSE51 Compliance. Nhưng chưa đủ. Nền tảng bên dưới còn phải là một OS multi-process có MMU. Đó là yêu cầu virtual-memory của spec, SWS_OSI_01010, đòi mỗi Process phải chạy trong không gian địa chỉ ảo riêng, bởi vì Execution Management sinh ra các process theo manifest."

**Chia hai nhóm, bên đỡ được (~22 giây):**
"Hai yêu cầu đó phân loại mọi kernel thành hai nhóm. Bên đỡ được AP, cặp production là QNX và Linux. QNX Neutrino là default production, POSIX đầy đủ, từng được chứng nhận PSE52 hồi khoảng 2008, và ASIL-D đến qua QNX OS for Safety. Linux và AGL thì POSIX-conformant nhưng chưa được chứng nhận chính thức, dùng cho dev và bản QM. Nhóm capable-class còn có Green Hills INTEGRITY, PikeOS và VxWorks."

**Bên không đỡ được (~15 giây):**
"Bên không đỡ được AP là tất cả những gì có task model: FreeRTOS, README của chính nó nói một app POSIX 'cannot be ported... using only this wrapper'; SAFERTOS thì không có POSIX, nó là một static safety RTOS, chỉ một image tĩnh duy nhất; Zephyr và NuttX là các RTOS lớp MCU; và AUTOSAR OS, vốn là kernel real-time tĩnh của Classic."

**Chốt, một câu test (~5 giây):**
"Test chỉ một câu: OS này có nói PSE51 và có chạy được process cô lập bằng MMU không? Cả hai đều có thì mới đỡ được AP."

**Chuyển slide:**
"Trên cái POSIX OS đó, AP dựng lên các functional cluster. Ta xem thẳng từ spec."

**Lưu ý khi trình bày:** đừng đọc từng dòng bảng, khán giả tự đọc được; chỉ nêu cặp production QNX/Linux và một câu test. Nếu bị hỏi vì sao NuttX không tính: nó có bản MMU kernel build tùy chọn nhưng không có fork/exec, vẫn là lớp MCU.

---

## Slide 9 — The functional clusters — straight from the spec

**Thời lượng mục tiêu: ~70 giây.** Slide bản đồ. Đọc như tấm bản đồ, không phải checklist; chỉ chốt bốn cluster.

**Mở đầu, đọc như bản đồ (~20 giây):**
"Đây là nền tảng Adaptive lấy thẳng từ spec, một hình không chỉnh sửa. Nguồn là AP_EXP_PlatformDesign, R25-11, Figure 4.1. Anh em hãy đọc nó như một tấm bản đồ, không phải một checklist. R25-11 định nghĩa 20 functional cluster. Đừng cố đọc hết cả hai mươi."

**Bốn cluster mang cả câu chuyện (~40 giây):**
"Chỉ cần chỉ vào bốn cái. Communication Management, tức ara::com, lo phần giao tiếp. Execution Management, tức ara::exec, lo phần khởi chạy và quản lý vòng đời process. Diagnostic Management, tức ara::diag, lo chẩn đoán. Và Update and Config Management, tức ara::ucm, lo cập nhật. Bốn cluster đó mang phần còn lại của cả buổi nói. Còn khoảng mười sáu cluster kia nằm ngoài phạm vi hôm nay."

**Chốt (~10 giây):**
"Nên khi nhìn tấm bản đồ này, mắt anh em chỉ cần bám bốn ô: com, exec, diag, ucm."

**Chuyển slide:**
"Bắt đầu từ cái quan trọng nhất và cũng quen nhất với dân middleware: ara::com."

**Lưu ý khi trình bày:** thật sự chỉ tay vào bốn ô trên hình khi gọi tên. "functional cluster" giữ nguyên tiếng Anh. Đọc "ara::com" là "a-ra com".

---

## Slide 10 — `ara::com` — one API, swappable bindings

**Thời lượng mục tiêu: ~80 giây.** Slide API cốt lõi của AP; điểm rút ra là API độc lập giao thức, binding thay được bên dưới.

**Mở đầu, một API proxy/skeleton (~24 giây):**
"ara::com là một API duy nhất, độc lập với giao thức, dựng trên mô hình proxy/skeleton. Ứng dụng viết code theo API đó thôi. Còn integrator mới là người chọn wire binding, và họ chọn trong manifest, không phải trong code."

**Ba binding chuẩn (~28 giây):**
"Có ba binding được chuẩn hóa: SOME/IP, Signal-Based và DDS. Riêng DDS đã có mặt từ bản R18-03. Anh em nhìn hình: cùng một API ở trên, bên dưới là các binding thay thế cho nhau. Ngoài ba cái chuẩn đó, Local IPC là thực tế bên trong một máy. Nhưng Local IPC là mức implementation, không phải một giao thức chuẩn hóa giữa các nhà cung cấp."

**Ý chuyển giao được (~20 giây):**
"Ý cần mang về: API thì độc lập giao thức, còn binding thì thay được ở bên dưới. Đúng y như rmw của ROS 2 chạy trên DDS. Ai từng làm ROS 2 sẽ thấy quen ngay."

**Chốt (~8 giây):**
"Một API, nhiều binding, chọn lúc tích hợp chứ không phải lúc code. Đó là toàn bộ tinh thần ara::com."

**Chuyển slide:**
"Đủ lý thuyết rồi. Giờ mở ba repo thật ra đọc, bắt đầu từ một stack Classic viết bằng C."

**Lưu ý khi trình bày:** nếu khán giả có nền ROS 2, so sánh rmw sẽ ăn ngay; nếu không, bỏ qua vế đó cũng được. Đọc "SOME/IP" là "sâm-ai-pi", "DDS" là "D D S".

---

## Slide 11 — Inside the repo 1/3: `Fang717/arccore-core-21`

**Thời lượng mục tiêu: ~65 giây.** Slide repo đầu tiên: giới thiệu cấu trúc, rồi nói thẳng phần provenance đáng ngờ.

**Mở đầu, đây là gì (~14 giây):**
"Đây là repo đầu tiên trong ba repo đáng đọc, một stack Classic Platform viết bằng C. Nó là Arctic Core, một stack basic-software đầy đủ của một vendor. README của nó tự mô tả: 'Arctic Core is an open-source implementation of the AUTOSAR (Automotive Open System Architecture) standard, designed for the development of automotive Electronic Control Units (ECUs).'"

**Cấu trúc cây thư mục (~26 giây):**
"Nhìn cây thư mục. Thư mục core/communication chứa chuỗi giao tiếp: Com, PduR tức PDU router, CanIf tức CAN interface, CanTp tức transport protocol, và SoAd, kèm luôn một stack TCP/IP nhẹ là lwip-2.0.3. Thư mục core/system chứa OS kernel real-time tĩnh cùng các service hệ thống EcuM, BswM, SchM. Thư mục core/diagnostic chứa ba module UDS là Dem, Dcm, Det. Các module tự đóng dấu AUTOSAR 4.0.3 trong release macro, ví dụ Com.h đặt COM_AR_RELEASE thành 4/0/3. Phần hỗ trợ phần cứng rất rộng, các port MCU nằm dưới core/mcal/arch."

**Phần trung thực, cảnh báo provenance (~22 giây):**
"Giờ tới phần trung thực, phải nói thẳng. Đây là một bản re-upload ẩn danh, người dùng GitHub tên Fang717, của một snapshot vendor thời thương mại, Arctic Core phiên bản 21.0.0. Nó không có lịch sử phát triển thật. Toàn bộ 8.481 file mã nguồn được thêm trong đúng một commit 'Initial commit' hồi tháng Sáu năm 2024, và không có commit nào sau đó động vào code. README nói GPL-2.0, nhưng không có file LICENSE ở gốc, GitHub API báo không có license, còn header từng file lại mang một notice kép: hoặc là commercial ArcCore license, hoặc là GPL version 2. Bản thân code cũng cũ. Copyright từng file ghi năm 2013 và 2014, nên dù nhãn là 21.0.0 và upload năm 2024, đây vẫn là code thời AUTOSAR 4.0.3."

**Chốt (~3 giây):**
"Đọc nó để thấy hình dạng của một stack Classic thật, đừng đọc để đưa vào production."

**Chuyển slide:**
"Giờ mở đúng hai hàm trong stack này ra xem code Classic viết bằng C trông thế nào."

**Lưu ý khi trình bày:** commit gắn với repo này là 7874929. Cảnh báo provenance là bắt buộc phải nói, không được lướt qua. Nếu bị hỏi "dùng được không?": đọc để học kiến trúc thì tốt, không dùng cho sản phẩm.

---

## Slide 12 — The code 1/3: Classic AUTOSAR in C

**Thời lượng mục tiêu: ~65 giây.** Slide code. Đi theo đúng thứ tự "What to notice", gọi đúng tên định danh.

**Mở đầu, hàm Com_SendSignal (~30 giây):**
"Đây là hai hàm thật lấy từ stack Arctic Core. Hàm đầu là Com_SendSignal, chính là dịch vụ COM mà một task gọi để publish một application signal, rồi COM sau đó đóng nó vào một I-PDU trên bus. Để ý: nó trả về kiểu uint8 do vendor typedef, và nhận vào Com_SignalIdType, không phải kiểu C trần, nhờ vậy module hành xử giống hệt nhau trên mọi MCU. Trước khi làm bất cứ việc gì, nó kiểm tra module đã init chưa, bằng điều kiện COM_INIT khác Com_GetStatus. Nếu chưa, nó báo một development-time error qua DET, bằng DET_REPORTERROR, và trả về mã COM_SERVICE_NOT_AVAILABLE, thay vì đụng vào config chưa khởi tạo. Cái comment gắn thẻ @req COM334 nối đúng dòng này tới một điều khoản đánh số trong spec COM của AUTOSAR, và mức truy vết requirement-to-code đó chạy xuyên suốt cả stack."

**Component chỉ nói qua RTE (~35 giây):**
"Đoạn thứ hai là một application software component, và nó không bao giờ gọi thẳng basic software. Nó chỉ dùng các hàm Rte_ được sinh ra. Rte_IRead và Rte_IWrite di chuyển dữ liệu port: ở đây Rte_IWrite_SwcWriterRunnable_SenderPort_data1 ghi ra, còn Rte_IRead_SwcWriterRunnable_InputPort_data1 đọc vào. Còn Rte_Call gọi một client-server operation, ở đây là Rte_Call_Blinker_Write. Nhờ vậy component độc lập hoàn toàn với phần cứng và với bus. Ngay cả việc xin đánh thức mạng cũng làm qua RTE: hàm SwcWriterInit xin full communication từ module ComM, bằng Rte_IWrite_Init_ComMControl_requestedMode với tham số COMM_FULL_COMMUNICATION. Những cái tên Rte_ dài dằng dặc đó do RTE generator sinh ra từ cấu hình ECU, không ai gõ tay cả. Đó chính là cốt lõi của phong cách Classic hướng cấu hình."

**Chuyển slide:**
"Cùng ý tưởng đó, nhưng ở một stack Classic khác, viết lại từ đầu bởi một người."

**Lưu ý khi trình bày:** đọc "@req COM334" là "req COM ba ba bốn". Đây là slide code, chỉ tay theo từng dòng khi gọi tên hàm. Nếu bị hỏi tên Rte_ sao dài vậy: vì generator ghép tên runnable, tên port và tên phần tử dữ liệu vào làm một.

---

## Slide 13 — Inside the repo 2/3: `autoas/as`

**Thời lượng mục tiêu: ~65 giây.** Slide repo thứ hai: một stack viết từ đầu bởi một người, kèm cảnh báo license mâu thuẫn.

**Mở đầu, khác gì repo trước (~16 giây):**
"Repo thứ hai là autoas trên as, một stack Classic rất khác. Chỗ Arctic Core là bản re-upload ẩn danh của một snapshot thương mại, thì cái này được viết từ đầu bởi đúng một người, là một stack basic-software Classic AUTOSAR 4.4, chủ yếu bằng C, các module nằm dưới infras. README của tác giả nói thẳng: 'This project is only free to be used for evaluation and study purpose, all of the BSWs are developed by me alone according to AUTOSAR 4.4.'"

**Phạm vi và tooling (~33 giây):**
"Phạm vi khá rộng: chuỗi communication gồm Com, PduR, CanIf, CanTp, và cả SomeIp lẫn Sd tức service discovery, LinIf; phần diagnostic gồm Dcm, Dem, Det; các memory service NvM, Fee, Ea; crypto là Csm; các driver MCAL như Can, Dio, Fls, Lin, Port; và một OS kernel real-time tĩnh với task, alarm, counter, resource nằm dưới infras/system/kernel/os. Khác với một stack trần, cái này còn có tooling desktop đi kèm. tools/generator là bộ sinh cấu hình bằng Python cho từng module, kiểu Com.py, Dcm.py, CanTp.py và chừng bốn chục cái nữa. tools/asone là một công cụ đồ họa QT cho Com, Dcm và flash loader. Nó còn có một bootloader và các trình mô phỏng bus CAN hoặc LIN qua socket IP. Cả cây build bằng SCons."

**Phần trung thực, license mâu thuẫn (~16 giây):**
"Phần cần nói thẳng. Đây là dự án của một người. Lịch sử chỉ có một maintainer, và README nói các module 'developed by me alone'. Cái nhãn AUTOSAR 4.4 là tuyên bố của tác giả, không phải kết quả được kiểm chứng hay chứng nhận, nên hãy coi là AUTOSAR-style chứ không phải compliant. License cũng tự mâu thuẫn bên trong. File LICENSE khai dual GPLv3 hoặc commercial, trong khi README lại giới hạn chỉ cho evaluation và study, còn GitHub thì báo license là 'Other'. Một số nhánh vẫn còn dở dang."

**Chuyển slide:**
"Mở code ra: cùng một hàm Com_SendSignal, nhưng viết lại độc lập, cộng một lát cắt trong OS kernel."

**Lưu ý khi trình bày:** commit là bfe1805. Sự mâu thuẫn license là điểm bắt buộc nói, đừng bỏ. Nếu bị hỏi có chạy trên xe thật không: không, đây là học thuật, coi như AUTOSAR-style.

---

## Slide 14 — The code 2/3: `autoas/as`

**Thời lượng mục tiêu: ~65 giây.** Slide code. Hàm COM viết lại độc lập, và lát cắt priority-ceiling trong GetResource.

**Mở đầu, cùng hàm, tác giả khác (~30 giây):**
"Cùng ý tưởng, nhưng ở stack viết từ đầu. Hàm đầu vẫn là Com_SendSignal, nhưng viết độc lập. Vì là một dịch vụ AUTOSAR public, nó trả về Std_ReturnType, tức hợp đồng chuẩn E_OK hoặc E_NOT_OK, và nó đặt biến ret thành lỗi trước, cụ thể là E_NOT_OK, để người gọi thấy lỗi trừ khi cú gửi thật sự thành công. Ba dòng DET_VALIDATE là các development-error guard của Classic, cả ba gắn service id của COM là 0x0A. Chúng lần lượt loại module chưa init, qua điều kiện NULL khác COM_CONFIG trả COM_E_UNINIT; loại signal id vượt phạm vi, qua SignalId nhỏ hơn COM_CONFIG->numOfSignals trả COM_E_PARAM; và loại con trỏ dữ liệu NULL, trả COM_E_PARAM_POINTER. Vướng cái nào là return sớm cái đó. Rồi signal được tra theo index từ một bảng cấu hình chỉ đọc được sinh ra, là COM_CONFIG->SignalConfigs. Lại đúng cái pattern hướng cấu hình."

**Lát cắt priority-ceiling trong GetResource (~35 giây):**
"Đoạn thứ hai là một lát cắt bên trong hàm GetResource của OS kernel, và nó chính là priority-ceiling protocol. Khi nhận một resource, priority của task đang chạy được nâng lên tới cái ceiling được cấu hình static của resource đó: nếu RunningVar->priority nhỏ hơn ResourceConstArray[ResID].ceilPrio thì gán priority bằng ceilPrio. Đây là cách kernel ngăn priority inversion và deadlock mà không hề block lúc runtime. Priority cũ và resource đang giữ trước đó được lưu lại trước, qua prevPrio và prevRes, để các cặp resource lồng nhau tháo ra như một ngăn xếp, đúng kiểu last-in first-out. Cả đoạn cập nhật này chạy bên trong EnterCritical và ExitCritical với interrupt bị mask, vì nó thay đổi trạng thái scheduler dùng chung, và nó chỉ áp dụng trong ngữ cảnh task, qua điều kiện TCL_TASK bằng CallLevel, chứ không trong một interrupt handler."

**Chuyển slide:**
"Đó là hết bên Classic. Giờ sang repo thứ ba, một codebase dạy học của Adaptive."

**Lưu ý khi trình bày:** đọc "0x0A" là "không x không A". "priority ceiling" giữ nguyên tiếng Anh. Nếu bị hỏi vì sao không block: vì ceiling đã tính sẵn static, chỉ cần nâng priority là đủ chặn inversion.

---

## Slide 15 — Inside the repo 3/3: `langroodi/Adaptive-AUTOSAR`

**Thời lượng mục tiêu: ~65 giây.** Slide repo Adaptive: codebase dạy học, chỉ đường đọc, kèm hai giới hạn trung thực.

**Mở đầu, bắt đầu từ README (~18 giây):**
"Đây là repo thứ ba đáng bỏ thời gian, langroodi trên Adaptive-AUTOSAR, và đây là codebase dạy học. README nói rõ mục tiêu: 'The goal of this project is to implement the interfaces defined by the standard for educational purposes.' Bắt đầu từ README, nó nói trong một đoạn dự án là gì, và liệt kê đúng các lệnh build, test, run."

**Đường đọc code (~29 giây):**
"Rồi mở main.cpp. Nó chỉ khoảng năm mươi lăm dòng: nó dựng Execution Management, chạy một polling loop, và truyền vào các manifest. File header cần nghiền ngẫm là execution_client.h. Nó cho thấy một app báo trạng thái của mình lên Execution Management, và các private member để lộ ra rằng cú gọi đó thật ra là một SOME/IP RPC, chứ không phải một ara::com proxy được sinh ra. CMakeLists.txt thì ghim C++14, kéo về GoogleTest, và định nghĩa executable cùng hai test target. Dưới src/ara có bảy interface cluster của AP: com, core, diag, exec, cùng log, phm, sm. Để chạy: cấu hình và build bằng CMake với GCC hoặc Clang, chạy unit test bằng ctest, rồi khởi động bằng cách truyền vào bốn file manifest .arxml."

**Hai giới hạn trung thực (~18 giây):**
"Hai giới hạn cần nói thẳng. Một, demo không chạy offline. Nó cần một Volvo API key, một OAuth 2.0 token và mạng thật để gọi Volvo Extended Vehicle REST API. Hai, code dừng ở mức SOME/IP transport, không có facade Proxy/Skeleton của ara::com được sinh ra. Và nó đang ngủ đông, commit mã nguồn cuối cùng là ngày 22 tháng Sáu năm 2023. License là MIT. Đọc nó để thấy hình dạng, đừng đọc để đưa vào production."

**Chuyển slide:**
"Mở đúng hai đoạn C++ trong repo này ra xem lớp platform của Adaptive được ghép lại thế nào."

**Lưu ý khi trình bày:** commit là 866d158. Đọc "OAuth" là "âu-thò". Nếu bị hỏi sao demo cần Volvo: vì nó minh họa gọi ra một backend xe thật, không phải mô phỏng thuần.

---

## Slide 16 — The code 3/3: `langroodi/Adaptive-AUTOSAR`

**Thời lượng mục tiêu: ~65 giây.** Slide code C++. Hình dạng lớp RpcClient, rồi cách ghép Execution Management.

**Mở đầu, lớp RpcClient (~30 giây):**
"Giờ là cùng lớp platform đó trong repo dạy học Adaptive. Đoạn đầu là hình dạng của một class. RpcClient là client SOME/IP kiểu request-and-response trừu tượng, mà toàn bộ phần wiring được dựng lên trên nó. Cái HandlerType public chỉ là một std::function nhận vào một message đã giải mã, kiểu SomeIpRpcMessage. Trạng thái private là hai map, khóa theo một service và method id đóng gói lại thành uint32_t: một map là mSessionIds theo dõi session id theo từng method, một map là mHandlers giữ các handler phản hồi đã đăng ký. Class này cố tình transport-agnostic, nên một subclass cụ thể như SocketRpcClient mới cung cấp phần gửi thật sự."

**Ghép Execution Management (~28 giây):**
"Đoạn thứ hai là điểm vào của Execution Management. Một SocketRpcServer cụ thể được dựng từ cấu hình RPC đã parse: địa chỉ ipAddress, cổng portNumber và protocolVersion. Rồi cái server đó được truyền bằng con trỏ vào một ara::exec::ExecutionServer, nên execution server chỉ nói chuyện với client thông qua lớp trừu tượng SOME/IP RPC. Những dòng cuối nạp các function-group state và trạng thái ban đầu từ mô hình ARXML, qua hàm fillStates. Cái phong cách hướng cấu hình, model-first đó chạy xuyên suốt cả codebase."

**Chốt (~7 giây):**
"Để ý điểm chung: config đến từ ARXML, còn giao tiếp thì đi qua một lớp RPC trừu tượng thay được bên dưới. Y hệt tinh thần ara::com ở slide trước."

**Chuyển slide:**
"Còn một mảnh nữa: đâu là bề mặt do chính spec đặt tên, và ranh giới trung thực của cả buổi khảo sát code."

**Lưu ý khi trình bày:** đọc "RPC" là "R P C". Nếu bị hỏi vì sao dùng con trỏ: để execution server không phụ thuộc loại transport cụ thể, chỉ thấy giao diện abstract.

---

## Slide 17 — The shape of the code — real ara:: from public repos

**Thời lượng mục tiêu: ~58 giây.** Slide chốt phần code: bề mặt spec đặt tên, cách AP báo lỗi, và ranh giới trung thực về CAPI.

**Mở đầu, bề mặt chuẩn hóa (~16 giây):**
"Đây là hình dạng của code ara:: thật từ một repo công khai. Bắt đầu từ bề mặt được chuẩn hóa. Spec đặt tên cho API gửi event của ara::com: Send của một sample type, và Send của một ara::com::SampleAllocateePtr. Cái này nằm trong AP_SWS_CommunicationManagement, R25-11, mục 8.4.2.2.2. Đó là hợp đồng mà các vendor phải hiện thực."

**Cách AP báo lỗi (~22 giây):**
"Giờ nhìn code. Hàm ReportExecutionState trả về một ara::core::Result của void, chứ không ném exception. Adaptive báo lỗi bằng một giá trị trả về, không phải bằng exception ném ra. Và đây là hợp đồng mà mọi Adaptive Application đều phải hiện thực, để Execution Management biết nó đã đạt trạng thái kRunning. Bên phía ara::com, vòng đời offer của skeleton cũng được spec đặt tên: OfferService và StopOfferService trên class ServiceSkeleton, theo SWS_CM_00101 và SWS_CM_00111, cùng tài liệu đó. Nhắc lại lưu ý học thuật: repo C++ này ngủ đông từ ngày 22 tháng Sáu năm 2023, tức đã im lặng 3 năm, nên đọc để thấy hình dạng, đừng đọc cho production."

**Ranh giới trung thực (~20 giây):**
"Và đây là ranh giới trung thực cho cả buổi khảo sát code. Các khối xây dựng và code dạy học thì mở. Nhưng một stack AP hoàn chỉnh, conformant, mã nguồn mở thì không tồn tại. Bản hiện thực chính thức hoàn chỉnh duy nhất, tên là CAPI, bị giới hạn chỉ cho các partner của AUTOSAR."

**Chuyển slide:**
"Đủ code rồi. Giờ đặt Classic và Adaptive cạnh nhau trong một bảng, theo bảy hàng."

**Lưu ý khi trình bày:** đọc "CAPI" là "cáp-pi", viết tắt Common Adaptive Platform Implementation. Câu "một stack AP hoàn chỉnh mã nguồn mở thì không tồn tại" là điểm chốt trung thực, hãy nói rõ ràng.

---

## Slide 18 — CP vs AP — the split that matters

**Thời lượng mục tiêu: ~75 giây.** Slide bảng bảy hàng. Đọc theo cặp đối chiếu, giữ nhịp, đừng sa đà một hàng.

**Mở đầu, ba hàng đầu (~28 giây):**
"Đây là bảng phân định quan trọng nhất, gồm bảy hàng. Hàng Target: một bên là MCU deeply-embedded như Infineon AURIX, NXP S32K, Renesas RH850; bên kia là HPC SoC như NVIDIA Orin và Thor, Qualcomm, NXP S32G, Renesas R-Car. Hàng OS: một bên là AUTOSAR OS, một kernel real-time tĩnh, các class SC1 tới SC4, không MMU; bên kia không phải một OS mới, mà là một OS Interface trên POSIX PSE51, chạy trên Linux, QNX hoặc PikeOS. Hàng Model: một bên fully static, C, các hàm Rte_Read/Write/Call được sinh ra, một binary; bên kia dynamic, C++14, các namespace ara::, manifest bind trễ, có discovery và start/stop lúc runtime."

**Bốn hàng sau (~35 giây):**
"Hàng Comms: một bên signal-oriented, COM đóng signal vào I-PDU trên CAN, LIN, FlexRay hoặc Ethernet; bên kia service-oriented, ara::com proxy/skeleton trên SOME/IP hoặc DDS. Hàng Diagnostics: một bên là DCM cộng DEM, UDS trên DoCAN hoặc DoIP; bên kia là một cluster DM tức ara::diag, vừa là UDS server vừa có SOVD, và DoIP là transport chuẩn hóa duy nhất, tuy cho phép transport tùy biến. Hàng Updates: một bên reflash nguyên cả ECU qua bootloader và UDS, tức 0x34, 0x36, 0x37; bên kia là UCM, cài hoặc cập nhật từng Software Cluster riêng lẻ, OTA-native. Hàng Safety: một bên ISO 26262 chín muồi lên tới ASIL D, bản đầu tiên được chứng nhận năm 2016; bên kia 'up to ASIL D' trên giấy, thực tế khó hơn, hiện ASIL-B đang ship, còn ASIL-D đang trên đường."

**Chốt, CP không chỉ có CAN (~12 giây):**
"Một điểm hay bị hiểu lầm: Classic không phải chỉ có CAN. Một SOME/IP Transformer chuẩn hóa đã có từ bản 4.2.1, tháng Mười năm 2014, nhiều năm trước cả bản phát hành đầu tiên của Adaptive."

**Chuyển slide:**
"Bảng cho thấy sự khác biệt. Slide sau cho thấy vì sao hai cái vẫn phải sống chung."

**Lưu ý khi trình bày:** giữ nhịp đều, mỗi hàng chỉ một hơi. "SOVD" đọc "S O V D", là Service-Oriented Vehicle Diagnostics. Nếu bị hỏi ASIL-D của AP: chưa có middleware AP nào được chứng nhận end-to-end ASIL-D tính tới giữa 2026, ASIL-D nằm ở OS như QNX cộng hypervisor cộng safety case của vendor.

---

## Slide 19 — Coexistence — AP plans, CP keeps the wheels

**Thời lượng mục tiêu: ~75 giây.** Slide hình từ spec. Chỉ vào hai region và các mũi tên bypass; chốt bằng câu spec.

**Mở đầu, Region A (~22 giây):**
"Sống chung, lấy thẳng từ spec: một hình, hai nền tảng. Nguồn là AP_EXP_PlatformDesign, R25-11, Figure 3.2. Region A, cái tag màu xanh dương, là Adaptive Platform trên máy tính hiệu năng cao. Đây là bên tính toán mức cao. Nó cảm nhận môi trường, tài xế và trạng thái xe. Nó hợp nhất chúng thành một environment and state model duy nhất. Rồi nó chạy maneuver và trajectory planning, tức lập kế hoạch động tác và quỹ đạo."

**Region C (~20 giây):**
"Region C, các ô bên trái và dọc phía dưới với tag màu xanh mòng két, là bên Classic Platform. Đây là bên điều khiển nhanh. Nó gom các ô sensor input: camera, radar, lidar, rồi inertial, odometry, GPS, rồi C2C và C2I tức car-to-car và car-to-infrastructure. Nó cũng giữ ô trajectory-control cùng safety-function ở dưới cùng."

**Điểm mấu chốt, mũi tên bypass (~23 giây):**
"Giờ tới điểm quan trọng nhất. Anh em nhìn các mũi tên đi ra từ các ô sensor. Một số chạy lên perception ở Region A. Nhưng một số chạy thẳng xuống safety function, và chúng bypass hẳn Region A. Bên safety giữ nguồn sensor feed riêng của nó. Cho nên đường an toàn không phụ thuộc vào đường lập kế hoạch. Nếu HPC sập, bánh xe vẫn an toàn."

**Chốt, câu của spec (~10 giây):**
"Và spec nói thẳng: AP 'will not replace CP'. Hai nền tảng 'interact ... to form an integrated system', theo mục 3.4. Một xe software-defined đời mới chạy cả hai nền tảng cùng lúc, nối bằng Ethernet và gateway. Sống chung là kiến trúc được thiết kế, không phải gánh nặng di sản."

**Chuyển slide:**
"Vậy chọn cái nào cho con silicon của anh em? Có một bảng mua sắm trả lời hết."

**Lưu ý khi trình bày:** thật sự chỉ tay vào các mũi tên bypass, đây là ý hình ảnh mạnh nhất của slide. Nếu bị hỏi safety island có trên hình không: hình này ở mức logic, chi tiết silicon nằm ở slide bảng quyết định kế tiếp.

---

## Slide 20 — Which stack on which silicon — the decision map

**Thời lượng mục tiêu: ~85 giây.** Slide bảng mua sắm: cả deck trong một bảng. Cho khán giả tìm hàng silicon của họ.

**Mở đầu, cách dùng bảng (~10 giây):**
"Đây là cả deck gói trong một bảng mua sắm. Nó cho thấy cái gì chạy ở đâu, và ai bán nó. Việc của anh em rất đơn giản: tìm đúng hàng silicon của mình."

**Đi qua năm hàng (~55 giây):**
"Hàng A-core SoC, như DRIVE Orin và Thor guest, NXP S32G và S32N, hoặc R-Car: chạy QNX hoặc Linux cộng một stack AP; hoặc chạy một middleware không phải AUTOSAR, tức con đường Rivian. Về nhà cung cấp AP có Vector, Elektrobit với corbos, ETAS RTA-VRTE, và Qorix. OS bên dưới là một hạng mục mua sắm riêng. Hàng safety island trên chính SoC, là lockstep Cortex-R52 như Thor FSI: chạy firmware an toàn của vendor, cộng một Vector FSI reference integration trên Thor. Nhà cung cấp là NVIDIA FSI firmware và Vector. Lưu ý: bản reference MICROSAR Classic lên tới ASIL-D của Vector nhắm vào con companion MCU, không phải cái island. Hàng companion hoặc safety MCU, như RH850 đời Thor, AURIX đời Orin: chạy Classic; nhà cung cấp là Vector AFW cùng bản reference integration của NVIDIA. Hàng zonal hoặc domain MCU, như NXP S32Z và S32E, AURIX, RH850: chạy Classic; nhà cung cấp là các stack Classic của Tier-1, kiểu MICROSAR hay lớp EB tresos. Hàng small edge ECU, lớp S32K: chạy Classic hoặc bare-metal trên RTOS; nhà cung cấp là stack Tier-1 hoặc tự làm in-house."

**Chốt, quy tắc kinh doanh (~20 giây):**
"Bên dưới tất cả là quy tắc kinh doanh ta đã gặp ở đầu buổi: giá trị AUTOSAR tăng theo số ranh giới tổ chức mà phần mềm phải đi qua. Các OEM tích hợp dọc như Rivian bỏ qua nó. Còn các Tier-1 thì triển khai nó để thắng RFQ của OEM."

**Chuyển slide:**
"Đó là bên trong xe theo góc silicon. Giờ nhìn dòng chảy chẩn đoán từ backend xuống tận từng nhánh."

**Lưu ý khi trình bày:** đây là slide "chụp ảnh màn hình" cho manager, cứ mời khán giả tìm hàng của họ trước khi anh em đọc. "FSI" đọc "F S I", Functional Safety Island. Các ô vendor chỉ là ví dụ, không phải danh sách thị trường đầy đủ.

---

## Slide 21 — Fleet and diagnostics in one picture

**Thời lượng mục tiêu: ~75 giây.** Slide sơ đồ: ngoài xe và trong xe, và ranh giới UDS không bao giờ ra internet.

**Mở đầu, ngoài xe (~30 giây):**
"Đây là fleet và diagnostics gói trong một bức tranh. Nhìn từ ngoài xe trước. Backend nói SOVD, tức REST và JSON trên HTTPS, cộng thêm MQTT telemetry. Nó không bao giờ dùng raw UDS. Điểm vào của chiếc xe là TCU."

**Trong xe (~35 giây):**
"Nhìn vào trong xe. Central gateway là một DoIP router kiêm firewall. Nó định tuyến DoIP và UDS trên backbone. Nó re-transport từ DoIP xuống DoCAN để đi tới các nhánh Classic. Và đây là ranh giới quan trọng nhất của slide: raw UDS không bao giờ bị phơi ra internet. Backend chỉ nói ngôn ngữ web an toàn, còn gateway mới là chỗ dịch xuống UDS bên trong xe."

**Chốt (~10 giây):**
"Nên nhớ hai lớp: bên ngoài là SOVD và MQTT trên web, bên trong là DoIP xuống DoCAN, và một firewall chặn giữa. UDS ở lại trong xe."

**Chuyển slide:**
"Giờ gộp tất cả lại thành một cây quyết định: làm sao chọn stack cho một ECU cụ thể."

**Lưu ý khi trình bày:** đọc "DoIP" là "đu-ai-pi", "DoCAN" là "đu-can". Điểm bảo mật "raw UDS không bao giờ ra internet" đáng nhấn, đây là câu manager và security hay hỏi.

---

## Slide 22 — Choosing your stack — the decision tree

**Thời lượng mục tiêu: ~95 giây.** Slide dài nhất: cây quyết định. Đi theo hai câu hỏi, nhánh MCU trước, rồi HPC, rồi bằng chứng.

**Mở đầu, hai câu hỏi (~12 giây):**
"Hai câu hỏi là chọn được stack, và ở nhánh MCU thì ngã rẽ đầu tiên là safety. Câu một: function này chạy ở đâu? Nếu là một MCU deeply-embedded, thì câu hai là: ECU này phải mang mức safety nào, và khách hàng là ai?"

**Nhánh MCU, bán cho OEM (~18 giây):**
"Nếu nó mang một mức ASIL và anh em bán cho một OEM, thì lựa chọn coi như đã được quyết sẵn. RFQ đòi AUTOSAR cộng bằng chứng ASIL, nên anh em mua Classic với một base đã được chứng nhận trước, ví dụ MICROSAR Safe."

**Nhánh MCU, sản phẩm của chính mình (~25 giây):**
"Nếu nó mang một mức ASIL nhưng là sản phẩm của chính anh em, thì có hai lựa chọn đều trung thực. Một, vẫn mua Classic, để lấy base đã chứng nhận, driver của vendor, và các module đã giải sẵn. Hai, lấy một RTOS không phải AUTOSAR nhưng đã được chứng nhận, ví dụ SAFERTOS, rồi tự gánh toàn bộ safety case ISO 26262. Đó chính là con đường Rivian, và nó cần một đội safety thật sự. Còn nếu ECU chỉ là QM, không cần chứng nhận, thì dùng gì cũng được."

**Nhánh HPC (~22 giây):**
"Sang nhánh HPC. Câu chuyện safety ở đây nằm trong OS đã chứng nhận, trong hypervisor, trong safety island, và trong companion MCU, mà con companion MCU đó thì chạy Classic. Cho nên câu hỏi còn lại trên HPC chỉ là về khả năng liên thông giữa các nhà cung cấp. Mua một stack AP nếu anh em cần các endpoint chuẩn hóa. Ngược lại thì dùng S-CORE, hoặc tự xây."

**Chốt, bằng chứng (~18 giây):**
"Thanh màu cam vẫn giữ nguyên: mọi kết cục đều đáp ứng cùng các hợp đồng fleet như nhau. Bằng chứng cho việc tự xây vẫn chạy được: Tesla fleet-telemetry cho thấy chiếc xe đóng vai client, đẩy protobuf qua WebSocket cộng mTLS. Trong đường đó không có SOME/IP, không có DDS, không có DoIP. Và Rivian nói thẳng: 'We don't use any of the industry offerings such as AUTOSAR.' Bỏ AUTOSAR chỉ đánh mất các endpoint dựng sẵn bên trong xe, chứ không hề mất khả năng kết nối tới fleet."

**Chuyển slide:**
"Gói tất cả lại thành ba điều mang về."

**Lưu ý khi trình bày:** đây là slide dày nhất, giữ nhịp và bám sơ đồ. "S-CORE" đọc "S core". Nếu bị hỏi Tesla có AUTOSAR không: ở đường fleet-telemetry thì không, họ dùng protobuf trên WebSocket và mTLS.

---

## Slide 23 — Three takeaways

**Thời lượng mục tiêu: ~65 giây.** Slide chốt: ba điều gọn, nhấn từng ý một.

**Mở đầu, takeaway một (~22 giây):**
"Ba điều mang về. Một: AUTOSAR là một chuẩn của chuỗi cung ứng. Giá trị của nó tăng theo số ranh giới tổ chức mà phần mềm của anh em phải đi qua. Và nhớ kỹ điều này: ASIL đến từ ISO 26262, không phải từ AUTOSAR."

**Takeaway hai (~25 giây):**
"Hai: hai nền tảng, sống chung theo thiết kế. Classic là static, có một con đường ISO 26262 chín muồi lên tới ASIL D, bản đầu tiên được chứng nhận năm 2016, và nó chạy trên MCU. Adaptive là một service platform trên POSIX, và nó chạy trên HPC. Đây là một hệ thống phân cấp được thiết kế, không phải gánh nặng di sản."

**Takeaway ba (~15 giây):**
"Ba: tìm đúng hàng silicon của anh em trên bảng quyết định. Tìm ra rồi thì anh em biết ngay stack nào, biết câu hỏi về OS, và biết ai bán nó."

**Chốt (~3 giây):**
"Ba câu đó là toàn bộ ba mươi phút vừa rồi."

**Chuyển slide:**
"Slide cuối: đi sâu ở đâu, và mời anh em đặt câu hỏi."

**Lưu ý khi trình bày:** đây là ba câu để khán giả chép lại, nói chậm và tách bạch từng ý. Câu "ASIL đến từ ISO 26262, không phải từ AUTOSAR" là thông điệp đáng nhớ nhất, hãy nhấn.

---

## Slide 24 — Q&A — and where to dig deeper

**Thời lượng mục tiêu: ~35 giây.** Slide đóng: chỉ nguồn đào sâu, ghi chú license, rồi mở hỏi đáp.

**Mở đầu, ba nguồn đào sâu (~20 giây):**
"Muốn đi sâu hơn thì có ba chỗ. Deck đầy đủ 73 slide nằm ở autosar/slides/autosar-deck.md, nó mở rộng từng điểm hôm nay kèm tài liệu tham chiếu gốc. Bản mirror spec cục bộ nằm ở autosar/specs, giữ đủ 35 file PDF của R25-11, gồm Foundation, Classic và Adaptive. Còn các tài liệu nghiên cứu và blog thì nằm dưới autosar, chia theo Classic, Adaptive, và Classic-vs-Adaptive."

**Ghi chú license và mở hỏi đáp (~15 giây):**
"Một ghi chú về bản quyền: các hình lấy từ spec được tái hiện nguyên bản, không chỉnh sửa, thuộc bản quyền AUTOSAR R25-11. Còn các sơ đồ đã điều chỉnh thì được vẽ lại theo các hình được trích dẫn, không sao chép trực tiếp từ artwork của spec. Xin cảm ơn anh em. Giờ mình sang phần câu hỏi."

**Lưu ý khi trình bày:** đây là chỗ dừng để nhận câu hỏi, đã chừa khoảng 2 tới 3 phút cuối khung 30 phút. Nếu một câu hỏi cần chi tiết sâu, chỉ khán giả tới đúng slide trong deck 73 slide thay vì trả lời dài tại chỗ.
