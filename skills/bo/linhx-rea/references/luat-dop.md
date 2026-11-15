# Luật & Checklist DoP cho `linhx-rea`

Tổng hợp **52 luật điện ảnh & nhiếp ảnh (DoP)** chia theo 6 trục (`anh-sang`, `ong-kinh`, `bo-cuc`, `may-di`, `mau`, `nhip`), phân loại khả năng đo kiểm tự động bằng máy (`có` / `không`), đối chiếu 8 trục **ShotBench** với `tu-vung/anh.yaml`, và bảng tra cứu nguồn gốc ở cuối tài liệu.

Khi điền `dap_an.json`:
- Nếu nhận xét của một trục vận dụng luật trong bảng này, gắn mã luật ở đầu `ghi_chu` (ví dụ: `"[AS-03] ..."`).
- Ghi tối thiểu **3 luật khớp** ở khoá gốc `"luat_khop"`: `[{"ma": "AS-03", "vi_sao": "...", "moc": {"x": 0.45, "y": 0.32}}]`.

---

## 1. Trục `anh-sang` (Ánh sáng — 10 luật)

| Mã | Đo được bằng máy? | Luật viết lại |
|---|---|---|
| `AS-01` | không | Mọi nguồn sáng nhân tạo đặt thêm phải gắn với một nguồn phát hợp lý trong bối cảnh (cửa sổ, đèn dầu, ngọn lửa) để giữ tính thuyết phục tự sự [nguồn: deakins-forum] |
| `AS-02` | có | Ưu tiên hút bớt ánh sáng dội thừa bằng mảng đen (negative fill) để gọt khối gương mặt và tăng tỷ lệ tương phản sáng–tối thay vì chồng thêm đèn phụ [nguồn: deakins-forum] |
| `AS-03` | có | Khi dùng đèn bàn hay đèn đạo cụ trong khung (practical), bổ sung một nguồn phản xạ mềm cùng hướng và cùng nhiệt màu ngoài khung để mở rộng dải chuyển sáng trên da mặt [nguồn: team-deakins-ep04] |
| `AS-04` | có | Giữ một hướng bóng đổ chủ đạo duy nhất trong cảnh bằng cách tối giản số lượng đèn chính, tránh nhiều bóng chồng chéo làm nát hình khối [nguồn: team-deakins-ep09] |
| `AS-05` | có | Khi quay bằng tường LED hoặc nguồn sáng đặt gần chủ thể, phải kiểm tra độ tụt sáng nhanh theo định luật nghịch đảo bình phương để tiền cảnh không sáng chênh giả tạo so với hậu cảnh [nguồn: team-deakins-ep29] |
| `AS-06` | có | Dưới nắng gắt trên đỉnh đầu nơi sa mạc, đặt nhân vật ngược sáng (backlight) và tận dụng mặt cát/đất sáng làm tấm hắt sáng tự nhiên để khử hốc mắt tối sâu [nguồn: asc-fraser-dune] |
| `AS-07` | có | Tránh quay ngoại cảnh thiên nhiên vào khung giờ mặt trời đứng bóng làm phẳng khối, trừ khi nghi lễ văn hóa hoặc ý đồ kịch bản cố tình đòi hỏi mặt trời thiên đỉnh [nguồn: asc-lubezki-revenant] |
| `AS-08` | có | Khi quay đêm bằng lửa trại hoặc đèn dầu, lót một nền sáng dimmer ổn định cường độ thấp và chắn bớt ánh trăng/ánh sáng môi trường thừa để giữ độ sâu vùng tối [nguồn: asc-lubezki-revenant] |
| `AS-09` | có | Chiếu sáng vào gò má quay xa máy (short lighting) hoặc góc chếch 45 độ tạo tam giác sáng ngược dưới mắt (Rembrandt) để tăng chiều sâu khối 3D thay vì đánh bẹt trực diện [nguồn: sb-lighting-setups] |
| `AS-10` | có | Chủ động dìm phơi sáng xuống vùng tối (underexposure) kết hợp nguồn ngược sáng diện tích lớn để biến chủ thể tiền cảnh thành bóng sẫm giàu sức nặng tâm lý [nguồn: asc-young-arrival] |

---

## 2. Trục `ong-kinh` (Ống kính & Quang học — 9 luật)

| Mã | Đo được bằng máy? | Luật viết lại |
|---|---|---|
| `OK-01` | không | Chọn tiêu cự chính là quyết định đặt vị trí đứng tâm lý của khán giả đối với nhân vật chứ không đơn thuần là thu hẹp hay mở rộng khung nhìn [nguồn: deakins-forum] |
| `OK-02` | có | Ưu tiên dải tiêu cự trung bình tự nhiên (32mm–65mm tùy khổ cảm biến) và khép khẩu vùng tối ưu T4–T5.6 khi cần giữ tỷ lệ gương mặt trung thực, không biến dạng rìa [nguồn: deakins-forum] |
| `OK-03` | có | Dùng ống kính góc rộng lấy nét cực gần trên cảm biến khổ lớn để vừa áp sát biểu cảm nhân vật ở tiền cảnh vừa giữ trọn bối cảnh hùng vĩ không bị xóa mù phía sau [nguồn: asc-lubezki-revenant] |
| `OK-04` | có | Khai thác trường ảnh cực mỏng của khổ phim/cảm biến lớn (như IMAX 65mm) ở cự ly cận cảnh để tách đôi mắt nhân vật khỏi hậu cảnh và kéo người xem vào dòng nội tâm [nguồn: asc-hoytema-oppenheimer] |
| `OK-05` | có | Trong cú máy dài phải chuyển nét liên tục từ tiền cảnh sang hậu cảnh, chọn hệ thấu kính triệt tiêu hiện tượng thở tiêu cự (zero focus breathing) để khung hình không co giật [nguồn: asc-deakins-1917] |
| `OK-06` | không | Có thể đan xen có chủ đích hai họ ống kính khác cá tính (như ống hiện đại sắc nét và ống cổ mềm) ngay trong cùng cảnh để dịch chuyển ngầm cảm nhận khách quan–chủ quan [nguồn: asc-young-arrival] |
| `OK-07` | có | Can thiệp lớp tráng phủ (detuning) hoặc dùng thấu kính cổ như Petzval tạo bokeh xoáy và flare ấm nhằm khử vẻ sắc lạnh điện tử khi quay phim bối cảnh lịch sử [nguồn: asc-prieto-kotfm] |
| `OK-08` | không | Tách biệt ngôn ngữ thấu kính theo không gian tâm lý: dùng anamorphic cho cảnh nội tâm gần gũi và ống kính cầu (spherical) mở hết chiều cao khung cho đại cảnh choáng ngợp [nguồn: asc-fraser-dune] |
| `OK-09` | có | Phân biệt tiêu cự qua dấu hiệu hình học: ống kính siêu rộng gây giãn phối cảnh và cong biên, còn ống kính tele dài nén phẳng khoảng cách tiền cảnh–hậu cảnh [nguồn: shotbench-arxiv] |

---

## 3. Trục `bo-cuc` (Bố cục & Đóng khung — 9 luật)

| Mã | Đo được bằng máy? | Luật viết lại |
|---|---|---|
| `BC-01` | không | Khước từ những khung hình đẹp phô trương tự tách khỏi mạch truyện; bố cục tốt phải dẫn mắt khán giả thẳng vào tâm điểm kịch tính mà không lộ bàn tay sắp đặt [nguồn: deakins-forum] |
| `BC-02` | có | Tận dụng khung cửa, rèm che, gương soi và vật cản tiền cảnh trong không gian hẹp để tạo bố cục khung trong khung, đặt người xem vào vị thế quan sát thầm lặng [nguồn: doyle-interview] |
| `BC-03` | có | Phá vỡ quy tắc chừa khoảng nhìn rộng (look room) bằng bố cục lệch phía hẹp (`Short side`) khi nhân vật nhìn sát vào mép khung gần nhất để gợi sự bế tắc hoặc cô lập [nguồn: shotbench-arxiv] |
| `BC-04` | có | Phân biệt rạch ròi ranh giới cắt cơ thể giữa các cỡ cảnh liền kề: `Medium Wide` cắt từ đầu gối, `Medium` cắt từ thắt lưng, còn `Medium Close-Up` cắt từ ngực/vai trở lên [nguồn: shotbench-arxiv] |
| `BC-05` | có | Tránh đặt đường biên khung cắt ngang đúng khớp xương tự nhiên (mắt cá, đầu gối, cổ tay, cằm); luôn dịch đường cắt lên giữa đùi, eo hoặc ngực để hình thể tự nhiên [nguồn: sb-shot-size] |
| `BC-06` | có | Đặt nhân vật cực nhỏ trong đại cảnh (`Extreme Wide Shot`) trước khối kiến trúc hoặc thiên nhiên khổng lồ để lượng hóa sự cô độc và chênh lệch quyền lực không gian [nguồn: sb-shot-size] |
| `BC-07` | có | Phân biệt bố cục đặt tâm (`Center`), đối xứng gương (`Symmetrical`) với bố cục cân bằng bất đối xứng (`Balanced`) nơi nhiều chủ thể rải đều giữ thăng bằng thị giác [nguồn: shotbench-arxiv] |
| `BC-08` | có | Kiểm soát cao độ đặt máy: góc máy thấp (`Low angle`) nâng vị thế hoặc đè nặng trần không gian, góc cao/đỉnh đầu (`High angle`/`Overhead`) thu nhỏ và bóc trần sơ đồ vị trí chủ thể [nguồn: shotbench-arxiv] |
| `BC-09` | không | Vị trí đặt máy và phương án đánh đèn phải được chốt đồng thời như một bài toán duy nhất vì dịch góc máy vài tấc đã làm thay đổi hoàn toàn phản xạ sáng trên mặt diễn viên [nguồn: team-deakins-ep29] |

---

## 4. Trục `may-di` (Chuyển động máy — 9 luật)

| Mã | Đo được bằng máy? | Luật viết lại |
|---|---|---|
| `MD-01` | không | Luôn thử dàn dựng cảnh hoàn toàn trên máy tĩnh trước; chỉ cho máy di chuyển khi hành động hoặc biến chuyển tâm lý nhân vật thực sự đòi hỏi [nguồn: deakins-forum] |
| `MD-02` | có | Phân biệt tiến/lùi thân máy (`Push in`/`Pull out`) với phóng/thu tiêu cự (`Zoom in`/`Zoom out`) thông qua độ trượt thị sai (parallax) giữa tiền cảnh và hậu cảnh [nguồn: shotbench-arxiv] |
| `MD-03` | có | Không nhầm lẫn xoay trục dọc tại chỗ (`Tilt up`/`Tilt down` — không đổi độ cao mắt máy) với nâng/hạ toàn bộ thân máy (`Boom`/`Pedestal` — dịch chuyển độ cao vật lý và đường chân trời) [nguồn: shotbench-arxiv] |
| `MD-04` | có | Kết hợp đẩy máy tiến vào đồng thời zoom rộng ra (`Dolly zoom`) để giữ nguyên cỡ nhân vật nhưng kéo giãn hậu cảnh đột ngột khi diễn tả cơn choáng váng nhận thức [nguồn: sb-camera-movement] |
| `MD-05` | không | Trong phim giả một cú máy liên tục, ưu tiên hệ ổn định mượt (gimbal/crane/dolly) thay vì rung cầm tay toàn tập để máy có thể lùi về trạng thái tĩnh lặng quan sát khi nhịp phim lắng xuống [nguồn: asc-deakins-1917] |
| `MD-06` | có | Dùng chuyển động trượt ngang song song (`Truck`) đồng tốc với bước đi nhân vật để giữ cỡ cảnh ổn định trong khi hậu cảnh trôi ngang tạo dòng chảy năng lượng [nguồn: sb-camera-movement] |
| `MD-07` | có | Dùng thân máy nhỏ gọn bám sát diễn viên qua hành lang hẹp trong cú máy dài để chuyển mượt giữa góc nhìn chủ quan (POV) và góc quan sát khách quan mà không cần cắt cảnh [nguồn: asc-lubezki-revenant] |
| `MD-08` | có | Sử dụng quỹ đạo lượn cung tròn (`Arc`) bao quanh chủ thể để xoáy hậu cảnh và cô lập khoảnh khắc cao trào cảm xúc hoặc đối đầu trực diện [nguồn: sb-camera-movement] |
| `MD-09` | có | Dùng máy cầm tay kết hợp tốc độ màn trập chậm để tạo vệt nhòe chuyển động (motion blur) khi cần truyền tải sự hỗn loạn, bốc đồng của đô thị [nguồn: doyle-interview] |

---

## 5. Trục `mau` (Màu sắc & Chất liệu — 8 luật)

| Mã | Đo được bằng máy? | Luật viết lại |
|---|---|---|
| `MAU-01` | không | Tiết chế những màu mang tải trọng văn hóa mạnh (như sắc đỏ Á Đông) để khi tung vào rèm cửa hay trang phục, màu sắc lập tức trở thành sự kiện tâm lý tự sự [nguồn: doyle-interview] |
| `MAU-02` | có | Giữ nguyên sự pha trộn nhiệt màu tự nhiên giữa nguồn sáng ấm gần (lửa, đèn dây tóc) và vùng tối lạnh xa (ánh trăng, trời đêm) thay vì cân bằng trắng phẳng đồng nhất [nguồn: team-deakins-ep09] |
| `MAU-03` | có | Dùng cặp màu bổ túc đối đỉnh 180 độ trên vòng màu (điển hình Cam ấm – Xanh cổ vịt lạnh) để tách hẳn sắc da chủ thể khỏi nền cảnh và đẩy mạnh xung đột thị giác [nguồn: sb-color] |
| `MAU-04` | có | Dùng bảng màu đơn sắc (`Monochromatic`) hoặc tương đồng liền kề (`Analogous`) với độ bão hòa kiểm soát chặt để dìm khung hình vào một trạng thái cảm xúc đồng nhất [nguồn: sb-color] |
| `MAU-05` | có | Cài một điểm nhấn màu nghịch âm lạc tông (`Discordant accent`) vào giữa khung hình đơn sắc hoặc trầm đục để cưỡng bức ánh nhìn người xem khóa vào chi tiết then chốt [nguồn: sb-color] |
| `MAU-06` | không | Khi cần tách rạch ròi tuyến truyện chủ quan giàu cảm xúc khỏi tuyến tư liệu khách quan lịch sử, đối lập trực tiếp phim màu với phim đen trắng hạt thực [nguồn: asc-hoytema-oppenheimer] |
| `MAU-07` | không | Dám hạ bão hòa và để tông da nhân vật tái lạnh theo sự suy kiệt tâm lý thay vì luôn gò màu da về chuẩn hồng hào thương mại trong khâu chỉnh màu [nguồn: asc-young-arrival] |
| `MAU-08` | có | Khử độ gắt kỹ thuật số bằng quy trình in ra phim nhựa rồi quét ngược lại (`film-out`) hoặc LUT mô phỏng ảnh cổ (Autochrome/Kodachrome) để tạo hạt phim và quầng sáng hữu cơ [nguồn: asc-fraser-dune] |

---

## 6. Trục `nhip` (Nhịp điệu thị giác & Dựng cảnh trong khung — 7 luật)

| Mã | Đo được bằng máy? | Luật viết lại |
|---|---|---|
| `NH-01` | có | Trong cú máy dài nối qua nhiều bối cảnh ngoại trời, khóa đồng bộ mật độ mây tản sáng (`Overcast`) để giữ nhịp sắc độ liền mạch không bị gãy khi ghép cắt ẩn [nguồn: asc-deakins-1917] |
| `NH-02` | có | Dùng nguồn sáng động thực tế trong cảnh (như pháo sáng trôi trên cáp, đèn tàu hỏa lướt qua) để bóng đổ quét biến thiên liên tục, tạo nhịp thị giác ngay trong một cú máy không cắt [nguồn: asc-deakins-1917] |
| `NH-03` | không | Đối lập nhịp dolly trượt ngang chậm lặp đi lặp lại qua các khung cửa hẹp (nén cảm xúc) với nhịp cắt gấp cầm tay (bùng nổ năng lượng) tùy theo trạng thái nội tâm phim [nguồn: doyle-interview] |
| `NH-04` | có | Điều phối trình tự cỡ cảnh từ đại cảnh mở không gian (`EWS`/`WS`) thu dần vào cận cảnh (`MCU`/`CU`/`ECU`) để tăng dần nhịp căng thẳng và độ tập trung cảm xúc [nguồn: sb-shot-size] |
| `NH-05` | có | Thiết kế sự tiến hóa bảng màu xuyên suốt thời lượng phim (transitional palette — từ ấm tươi sang lạnh bạc màu) để phản chiếu nhịp lão hóa hoặc suy sụp của nhân vật [nguồn: asc-prieto-kotfm] |
| `NH-06` | có | Kết nối toàn bộ đèn trường quay vào bàn dimmer riêng để điều biến cường độ sáng mượt theo nhịp bước chân diễn viên đi qua các vùng sáng–tối trong phòng [nguồn: asc-young-arrival] |
| `NH-07` | có | Trong cảnh video, chỉ gán nhãn chuyển động máy tại đúng khoảng thời gian (timestamp interval) có vận động chủ đích rõ rệt, loại bỏ dao động rung ngẫu nhiên không mang nhịp tự sự [nguồn: shotbench-github] |

---

## 7. Đối chiếu 8 trục ShotBench với `tu-vung/anh.yaml`

### 7.1. Bảng 8 trục và 67 nhãn chuẩn của ShotBench [nguồn: shotbench-arxiv, shotbench-github]

| STT | Mã | Tên trục ShotBench | Số nhãn | Danh sách nhãn đầy đủ |
|---|---|---|---|---|
| 1 | `SS` | **Shot Size** (Cỡ cảnh) | 7 | `Extreme Wide`, `Wide`, `Medium Wide`, `Medium`, `Medium Close Up`, `Close Up`, `Extreme Close Up` |
| 2 | `SF` | **Shot Framing** (Cách đóng khung chủ thể) | 7 | `Single`, `2 shot`, `3 shot`, `Group shot`, `Insert`, `Establishing shot`, `Over the shoulder` |
| 3 | `CA` | **Camera Angle** (Góc đặt máy tĩnh) | 5 | `Aerial`, `Overhead`, `High angle`, `Low angle`, `Dutch angle` |
| 4 | `LS` | **Lens Size** (Tiêu cự / Phối cảnh ống kính) | 4 | `Ultra Wide&Fisheye`, `Wide`, `Medium`, `Long Lens` |
| 5 | `LT` | **Lighting Type** (Loại nguồn sáng) | 12 | `Daylight`, `Artificial light`, `Mixed light`, `Firelight`, `Overcast`, `Practical light`, `Sunny`, `Moonlight`, `Fluorescent`, `HMI`, `Tungsten`, `LED` |
| 6 | `LC` | **Lighting Condition** (Hướng & Tương phản sáng) | 10 | `Side light`, `Backlight`, `High contrast`, `Silhouette`, `Edge light`, `Underlight`, `Top light`, `Hard light`, `Soft light`, `Low contrast` |
| 7 | `SC` | **Shot Composition** (Bố cục cân bằng khung) | 6 | `Center`, `Balanced`, `Symmetrical`, `Right heavy`, `Left heavy`, `Short side` |
| 8 | `CM` | **Camera Movement** (Chuyển động máy — video) | 16 | `Push in`, `Pull out`, `Boom up`, `Boom down`, `Pan left`, `Pan right`, `Tilt up`, `Tilt down`, `Zoom in`, `Zoom out`, `Static`, `Move to the right`, `Move to the left`, `Arc`, `Camera roll`, `Dolly zoom` |

### 7.2. Đối chiếu chi tiết với 17 trục của `tu-vung/anh.yaml`

Bộ từ vựng `tu-vung/anh.yaml` hiện gồm **17 trục** (10 trục đọc hình ảnh + 7 thành phần thị giác Bruce Block: `khong_gian`, `duong_net`, `hinh_khoi`, `sac_do`, `mau`, `chuyen_dong`, `nhip`):

1. **Trùng khớp trực tiếp**:
   - **`Lighting Condition (LC)` ↔ `anh_sang_huong` + `anh_sang_cung_mem` + `sac_do`**: `anh.yaml` tách `LC` thành 3 trục trực giao (`anh_sang_huong`: `ngang_trai`, `ngang_phai`, `nguoc_sang_vien`, `dinh_chieu_xuong`, `duoi_hat_len`, `thuan_truoc`, `chech_trai`, `chech_phai`; `anh_sang_cung_mem`: `cung_gat`, `vua_ro_khoi`, `mem_khuech_tan`, `phang_khong_bong`; `sac_do`: `tuong_phan` / `tuong_dong`). Nhãn `Silhouette` tổ hợp từ `nguoc_sang_vien` + `sac_do: tuong_phan`.
   - **`Shot Composition (SC)` ↔ `duong_dan_mat` + toạ độ `moc` (`[x, y]` / lưới 3×3 `A1..C3`)**: `Center` / `Symmetrical` khớp `phan_bo_tinh_tam`; `Left heavy` / `Right heavy` suy từ hoành độ `x` của `moc`, nhưng chưa có nhãn tường minh cho `Short side` và `Balanced`.
2. **Trùng gián tiếp một phần**:
   - **`Lighting Type (LT)` ↔ `nhiet_mau` + `anh_sang_cung_mem`**: đo được hệ quả thị giác (`nong_am`, `lanh_tram`, `tuong_phan_nong_lanh`, `cung_gat`, `mem_khuech_tan`), chưa tách nguồn phát vật lý (`Practical light`, `Daylight`, `Tungsten`, `Fluorescent`, `HMI`, `LED`).
   - **`Shot Framing (SF)` ↔ `chu_the_chinh` + `chu_the_phu`**: có `chan_dung_nguoi`, `nhom_nguoi`, `vat_the_dao_cu`, `tien_canh_che_mo`, chưa tách chi tiết `2 shot`, `3 shot`, `Over the shoulder`, `Establishing shot`.
   - **`Lens Size (LS)` ↔ `khong_gian` + `bieu_tuong: hinh_hoc_bien_dang`**: phản ánh gián tiếp chiều sâu/biến dạng, chưa có trục tiêu cự quang học và độ sâu trường ảnh (DOF).
3. **Nhóm trục ShotBench có mà `anh.yaml` đang thiếu**:
   - **`Shot Size (SS)`**: chưa có trục cỡ cảnh (`EWS`, `WS`, `MWS`, `MS`, `MCU`, `CU`, `ECU`).
   - **`Camera Angle (CA)`**: chưa có trục góc đặt máy theo chiều đứng và độ nghiêng (`Low angle`, `High angle`, `Eye level`, `Overhead`, `Aerial`, `Dutch angle`).
   - **`Camera Movement (CM)`**: dành cho video (`rea-video`), cần tách 3 cơ chế tịnh tiến có thị sai (`Push/Pull`, `Truck`, `Boom`, `Arc`), xoay trục không thị sai (`Pan`, `Tilt`, `Roll`) và biến thiên tiêu cự (`Zoom`, `Dolly zoom`).
4. **Nhóm trục `anh.yaml` có mà ShotBench thiếu**:
   - Neo toạ độ bằng chứng `moc`, nhiệt màu & quan hệ màu (`nhiet_mau`, `mau`), chất liệu bề mặt (`chat_lieu`), đường dẫn mắt chi tiết (`duong_dan_mat`), biểu tượng (`bieu_tuong`), cảm xúc (`cam_xuc`), phong cách (`phong_cach`) và nhịp điệu thị giác (`nhip`).

---

## 8. Bảng nguồn tham chiếu

| Mã nguồn | Tác giả | Tiêu đề | URL |
|---|---|---|---|
| `deakins-forum` | Roger Deakins, ASC, BSC | Cinematography advice & Outdoor Lighting Principles (Roger A. Deakins Forum) | https://www.rogerdeakins.com/forums/topic/cinematography-advice/ |
| `team-deakins-ep04` | Roger Deakins & James Deakins | Team Deakins Podcast Ep. 4: Practical Lighting | https://teamdeakins.libsyn.com/practical-lighting |
| `team-deakins-ep09` | Roger Deakins & James Deakins | Team Deakins Podcast Ep. 9: Learning Lighting | https://teamdeakins.libsyn.com/learning-lighting |
| `team-deakins-ep29` | Roger Deakins, James Deakins & Greig Fraser | Team Deakins Podcast Ep. 29: Greig Fraser – Cinematographer | https://teamdeakins.libsyn.com/greig-fraser-cinematographer |
| `asc-lubezki-revenant` | Ron Prince / Emmanuel Lubezki, ASC, AMC | Grizzly adventure: Emmanuel Lubezki AMC ASC, The Revenant | https://britishcinematographer.co.uk/emmanuel-lubezki-amcasc-the-revenant/ |
| `asc-hoytema-oppenheimer` | British Cinematographer / Hoyte van Hoytema, ASC, FSF, NSC | Hoyte van Hoytema ASC NSC FSF / Oppenheimer | https://britishcinematographer.co.uk/hoyte-van-hoytema-asc-nsc-fsf-oppenheimer/ |
| `asc-fraser-dune` | Jay Holben, Mandy Walker & British Cinematographer / Greig Fraser, ASC, ACS | ASC Clubhouse Conversations — Dune & Greig Fraser ACS ASC / Dune | https://theasc.com/blogs/blog/clubhouse-conversations-dune |
| `asc-deakins-1917` | Ron Prince / Roger Deakins, CBE, BSC, ASC | Roger Deakins CBE BSC ASC \| 1917 | https://britishcinematographer.co.uk/roger-deakins-cbe-bsc-asc-1917/ |
| `asc-young-arrival` | British Cinematographer / Bradford Young, ASC | Bradford Young ASC / Arrival | https://britishcinematographer.co.uk/bradford-young-asc-arrival/ |
| `asc-prieto-kotfm` | The ASC / Kodak / MPA The Credits / Rodrigo Prieto, ASC, AMC | Rodrigo Prieto ASC AMC on The Irishman & Killers of the Flower Moon | https://theasc.com/blogs/blog/the-irishman-rodrigo-prieto-asc-amc-pt4 |
| `doyle-interview` | Vicente Rodriguez-Ortega / Christopher Doyle, HKSC | Zen Palette: An Interview with Christopher Doyle (Reverse Shot) | https://reverseshot.org/interviews/entry/216/christopher_doyle |
| `shotbench-arxiv` | Hongbo Liu, Jingwen He et al. | ShotBench: Expert-Level Cinematic Understanding in Vision-Language Models | https://arxiv.org/abs/2506.21356 |
| `shotbench-github` | Vchitect (Hongbo Liu, Jingwen He et al.) | Vchitect/ShotBench GitHub Repository README & Project Page | https://github.com/Vchitect/ShotBench |
| `sb-shot-size` | SC Lannom (StudioBinder) | Guide to Camera Shots: Every Shot Size Explained | https://www.studiobinder.com/blog/ultimate-guide-to-camera-shots/ |
| `sb-camera-movement` | StudioBinder Team | Camera Movements in Film — Ultimate Guide | https://www.studiobinder.com/blog/types-of-camera-movements-in-film/ |
| `sb-lighting-setups` | StudioBinder Team | Film Lighting Techniques — The Ultimate Guide | https://www.studiobinder.com/blog/film-lighting-techniques/ |
| `sb-color` | Matthew Vasiliauskas (StudioBinder) | How to Use Color in Film: 50+ Movie Color Palettes | https://www.studiobinder.com/blog/how-to-use-color-in-film/ |
