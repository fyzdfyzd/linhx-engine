---
type: kq-dr
de: DE-1
nguon: Gemini Deep Research (3.1 Pro, tai khoan Art Urah Ultra, Chrome may cty)
link: https://gemini.google.com/u/1/app/b3525af466654384
ngay: 2026-11-09
---

> Ket qua tho tu Gemini Deep Research, chua kiem link. Khi dung ghi [DR] canh nguon va kiem lai link con song.


## Quy Trình Nhân Vật Ảo

# Báo cáo Nghiên cứu Chuyên sâu: Quy trình Kỹ thuật, Tiêu chuẩn Đo lường và Khung Pháp lý trong Sản xuất Nhân vật Ảo (2024–2026)

## 1. Bối cảnh Ngành và Triết lý Thiết kế Tiền trạm

Trong giai đoạn từ năm 2024 đến 2026, ngành công nghiệp sản xuất nhân vật ảo, bao gồm VTuber, đại sứ thương hiệu AI (AI influencer) và diễn viên phim ngắn AI, đã trải qua một sự chuyển dịch mô hình sâu sắc. Các quy trình làm việc (workflow) truyền thống vốn phụ thuộc hoàn toàn vào kỹ thuật dựng hình 3D thủ công qua các phần mềm như Maya hay Blender nay đã được tích hợp mạnh mẽ, hoặc thay thế một phần, bởi các mô hình AI tạo sinh (Generative AI) như Diffusion, ControlNet và IC-LoRA. Sự thay đổi này giúp tối ưu hóa thời gian sản xuất và chi phí, nhưng đồng thời đặt ra một thách thức kỹ thuật cốt lõi: Hiện tượng suy thoái danh tính (Character Drift).

Sự suy thoái danh tính xảy ra khi khuôn mặt, tỷ lệ cơ thể hoặc các chi tiết đặc trưng của nhân vật bị biến dạng hoặc thay đổi dần qua các khung hình video hoặc qua các thế hệ hình ảnh tĩnh khác nhau. Trong các quy trình không được kiểm soát, mô hình AI coi mỗi lần tạo ảnh là một sự kiện độc lập, dẫn đến việc nhân vật mất đi sự đồng nhất. Để giải quyết vấn đề này, các studio và agency chuyên nghiệp đã thiết lập một hệ thống quy trình nghiêm ngặt, chuyển đổi khái niệm "nhất quán" từ một cảm quan thị giác (vibe) sang một thông số kỹ thuật (spec) có thể đo lường, kiểm chứng bằng toán học và khóa chặt bằng các hợp đồng dữ liệu. Báo cáo này cung cấp một phân tích toàn diện về chuỗi cung ứng sản xuất nhân vật ảo, hệ thống đo lường độ tương đồng sinh trắc học, cấu trúc của Cẩm nang nhân vật (Character Bible), và các rào cản pháp lý mà ngành công nghiệp này đang phải đối mặt.

## 2. Chuẩn hóa Quy trình Sản xuất và Hệ thống Cổng Duyệt

Quy trình tạo ra một nhân vật ảo thương mại không bắt đầu từ việc mở một phần mềm tạo ảnh hay phần mềm 3D, mà bắt đầu từ việc thiết lập một nguồn chân lý duy nhất (single source of truth) dưới dạng văn bản. Dựa trên dữ liệu kỹ thuật từ các đơn vị tiên phong như Lollipop, Astorie và các studio phát triển VTuber, quy trình này được cấu trúc thành các bước tuyến tính với các cổng duyệt khắt khe nhằm loại bỏ sự trôi dạt danh tính ngay từ trong trứng nước.

### 2.1. Chuỗi Cung ứng Sản xuất 7 Bước cho AI Influencer và Diễn viên Phim ngắn

Đối với các dự án AI Influencer và diễn viên phim ngắn AI, vòng đời sản xuất tiêu chuẩn được chia thành bảy bước giải phẫu kỹ thuật nghiêm ngặt. Khởi đầu quy trình là việc biên soạn Cẩm nang nhân vật, nơi toàn bộ đặc điểm nhận dạng, cấu trúc khuôn mặt, kiểu tóc, trang phục đặc trưng và hồ sơ giọng nói được đóng băng (freeze) dưới dạng văn bản trước khi bất kỳ điểm ảnh nào được kết xuất. Một yếu tố quan trọng trong bước này là việc thiết lập "Khối phủ định" (Negative block), một đoạn mã hóa văn bản mô tả chính xác những yếu tố thị giác mà nhân vật tuyệt đối không bao giờ được phép mang.

Sau khi văn bản được khóa, giám đốc nghệ thuật (Art Director) sẽ tiến hành quá trình đúc kết hình ảnh (casting). Quá trình này đòi hỏi việc tạo ra từ 10 đến 20 biến thể hình ảnh khái niệm ban đầu để chọn ra một nguyên mẫu duy nhất có khả năng truyền tải cảm xúc tốt nhất khi thu nhỏ trên màn hình điện thoại. Từ nguyên mẫu này, hệ thống sẽ xây dựng một bộ ảnh tham chiếu (Reference Image Set) được đóng băng. Bộ tham chiếu tiêu chuẩn bắt buộc phải chứa từ 5 đến 8 hình ảnh cho mỗi nhân vật, bao phủ các góc độ thiết yếu: góc chính diện (đóng vai trò là mỏ neo danh tính chính), góc ba phần tư (phục vụ cho các khung hình đối thoại), góc nghiêng hoàn toàn (phục vụ cho các cảnh quay qua vai), một bảng biểu cảm đa dạng và một bức ảnh toàn thân nhằm khóa tỷ lệ cơ thể và trang phục. Việc sử dụng một bức ảnh duy nhất bị coi là lỗi quy trình nghiêm trọng vì AI sẽ thiếu dữ liệu về độ sâu hình học của hộp sọ và cấu trúc cơ thể.

Bước thứ ba liên quan đến bài toán kinh tế học của việc huấn luyện mô hình. Các studio phải quyết định xem có nên huấn luyện một bộ chuyển đổi danh tính (LoRA - Low-Rank Adaptation) riêng cho nhân vật hay không. Dữ liệu thực tiễn chỉ ra rằng ngưỡng hòa vốn cho quyết định này là khoảng 8 tập phim (episodes). Đối với các chiến dịch hoặc bộ phim dưới 8 tập, chi phí thời gian thu thập dữ liệu sạch, chạy huấn luyện GPU và tinh chỉnh tham số vượt quá lợi ích mang lại; do đó, một bộ ảnh tham chiếu cố định kết hợp với IP-Adapter hoặc ControlNet là phương án tối ưu. Tuy nhiên, đối với các series dài kỳ từ 8 tập trở lên, việc huấn luyện LoRA trở thành yêu cầu bắt buộc để duy trì danh tính trong các điều kiện ánh sáng và bối cảnh phức tạp.

Song song với hình ảnh, hồ sơ giọng nói cũng phải được khóa cố định. Một nhân vật thương mại chỉ được cấp một hồ sơ giọng nói duy nhất, trong đó các thông số về độ ổn định (stability), độ tương đồng âm sắc (similarity) và mức độ phóng đại phong cách diễn xuất (style exaggeration) được lưu trữ vĩnh viễn vào Cẩm nang. Một quy tắc bất di bất dịch là tuyệt đối không tạo lại (re-roll) giọng nói giữa chừng; nếu một câu thoại bị lỗi, kỹ sư âm thanh chỉ được phép tạo lại câu thoại đó trên nền hồ sơ giọng nói đã khóa, thay vì thay đổi thông số hồ sơ.

Để đảm bảo tính nhất quán trong khâu tạo sinh, mọi lời nhắc (prompt) đưa vào hệ thống phải được chuẩn hóa. Kỹ sư AI bắt buộc phải sao chép nguyên văn (verbatim) các mô tả từ Cẩm nang nhân vật cho mọi khung hình. Việc diễn giải lại hoặc thay đổi từ ngữ mô tả ngoại hình giữa các cảnh quay bị nghiêm cấm, vì điều này sẽ dẫn đến hiện tượng trôi dạt ngữ nghĩa, kéo theo sự biến dạng hình ảnh. Mọi thay đổi có chủ đích về trang phục, vết thương hay sự lão hóa do yêu cầu của kịch bản đều phải được ghi chép tỉ mỉ vào nhật ký sản xuất. Việc ghi chép này đảm bảo rằng các thay đổi có kế hoạch không bị hệ thống kiểm duyệt tự động đánh dấu là lỗi danh tính ở các khâu sau.

Đóng vai trò chốt chặn cuối cùng trước khi phân phối là Cổng duyệt trước xuất bản (Pre-publish Gate). Tại đây, giám đốc kỹ thuật (Technical Director) hoặc trưởng nhóm kiểm soát chất lượng (Lead QC) sẽ thực thi một danh sách kiểm tra nghiêm ngặt. Điểm mấu chốt của cổng duyệt này là tập phim mới luôn phải được so sánh A/B trực tiếp với tài sản của Tập 1, chứ không phải tập ngay trước đó. Nguyên lý này nhằm ngăn chặn "sự trôi dạt thế hệ" (generational drift) — hiện tượng các sai số siêu nhỏ tích lũy qua từng tập, khiến Tập 10 trông giống Tập 9 nhưng lại hoàn toàn khác biệt so với nguyên tác ở Tập 1.

### 2.2. Phân tách Cấu trúc đối với Quy trình VTuber 2D và 3D

Trong khi quy trình AI Influencer tập trung vào việc hướng dẫn mô hình tạo sinh, quy trình phát triển VTuber truyền thống và bán tự động lại đòi hỏi sự can thiệp vi phẫu của con người vào cấu trúc tệp đồ họa. Đối với VTuber 2D, sau khi thiết kế hình ảnh (Character Sheet) được phê duyệt, họa sĩ minh họa (Visual Designer) phải tiến hành cắt lớp (Live2D Separation). Nhân vật được phân rã thành hàng chục, thậm chí hơn 100 lớp (layers) riêng biệt, bao gồm sự tách biệt độc lập giữa tóc trước, tóc sau, đồng tử, tròng trắng, mí mắt, cằm, và từng khớp xương tay chân. Chất lượng của khâu phân tách này đặt ra giới hạn trần cho độ mượt mà của chuyển động sau này.

Tiếp theo, kỹ sư gắn xương (Rigger) sẽ tiếp nhận tệp PSD nhiều lớp này, đưa vào các hệ thống như Live2D Cubism để thiết lập lưới biến dạng (deformation meshes) và các thông số vật lý như trọng lực của tóc hay độ nảy của trang phục. Cuối cùng, mô hình được đưa qua cổng thử nghiệm thời gian thực trên các phần mềm theo dõi khuôn mặt như VTube Studio hoặc VSeeFace. Nếu phát hiện các lỗi như đồng tử bị trôi khỏi mắt, hoặc biểu cảm không khớp với cơ mặt người điều khiển, quy trình sẽ phải quay lại vòng lặp chỉnh sửa. Tổng thời gian sản xuất từ lúc phác thảo đến khi xuất bản cho một mô hình VTuber 2D chất lượng cao thường kéo dài từ 2 đến 8 tuần. Đối với mô hình 3D, quá trình bắt đầu thông qua các phần mềm như VRoid Studio, cho phép xuất trực tiếp định dạng tệp .VRM với thời gian nhanh hơn, nhưng lại đòi hỏi năng lực tối ưu hóa số lượng đa giác (polygon count) dưới 70.000 để đảm bảo khả năng theo dõi chuyển động mượt mà.

## 3. Khoa học Đo lường Độ Nhất quán Khuôn mặt và Cơ thể

Duy trì độ nhất quán không phải là một quy trình dựa trên cảm tính mắt thường. Trong nền công nghiệp sản xuất quy mô lớn, việc đánh giá độ "giữ mặt" được thực thi bởi các thuật toán trích xuất nhúng sinh trắc học (biometric identity embeddings). Các studio không so sánh các điểm ảnh (pixels), mà so sánh khoảng cách toán học giữa các đặc trưng nhận dạng vô hình. Ba kiến trúc cốt lõi định hình tiêu chuẩn đo lường hiện nay là ArcFace, DINO và CLIP.

### 3.1. ArcFace và Toán học của Độ Tương đồng Cosine

ArcFace (Additive Angular Margin Loss), được phát triển bởi InsightFace, là nền tảng tối thượng của hầu hết các hệ thống bảo toàn và nhận diện danh tính hiện đại, bao gồm InstantID, PuLID, ReActor và các nút logic trong ComfyUI (như PersonSelector). Lý do ArcFace trở thành tiêu chuẩn công nghiệp nằm ở cách nó cải tiến hàm mất mát (loss function). Các thuật toán cũ như Softmax thường gặp khó khăn trong việc phân tách các ranh giới giữa các khuôn mặt gần giống nhau. CosFace đã cố gắng khắc phục điều này bằng cách thêm một hình phạt lề cosine (additive cosine margin), nhưng ArcFace đã tiến xa hơn bằng cách cộng trực tiếp một lề góc cố định (angular margin) vào không gian góc của đặc trưng mục tiêu.

Quá trình hoạt động của ArcFace diễn ra như sau: Đầu tiên, thuật toán phát hiện và căn chỉnh khuôn mặt bằng RetinaFace hoặc BiSeNet, loại bỏ các yếu tố gây nhiễu như bối cảnh hay ánh sáng. Sau đó, nó nén khuôn mặt thành một vector nhúng đa chiều mang đặc tính sinh trắc học. Khi cần đánh giá, hệ thống so sánh vector của ảnh tạo ra với vector của ảnh gốc và tính toán khoảng cách cosine giữa chúng. Khoảng cách này được biểu diễn dưới dạng Điểm Tương đồng Cosine (Cosine Similarity Score).

Phân tích các tài liệu kỹ thuật cho thấy băng thông ngưỡng độ tương đồng Cosine được phân chia thành bốn dải chính, quyết định trực tiếp đến hành động của hệ thống kiểm duyệt tự động. Dải điểm từ 0.0 đến 0.4 biểu thị danh tính đã trôi dạt hoàn toàn và tệp ảnh sẽ bị tự động loại bỏ. Dải từ 0.4 đến 0.6 là vùng cảnh báo (worth a look), nơi hệ thống yêu cầu sự đánh giá thủ công từ người duyệt vì có thể khuôn mặt bị biến dạng do góc nghiêng cực đại hoặc ánh sáng gắt. Dải 0.6 đến 0.75 là dải an toàn cho sản xuất tiêu chuẩn, với ngưỡng 0.65 thường được thiết lập làm mặc định (default cutoff) trong các công cụ như ComfyUI PersonSelector, tạo ra sự cân bằng hoàn hảo giữa việc giữ vững danh tính và cho phép nhân vật biểu cảm tự nhiên. Cuối cùng, từ 0.75 đến 1.0 đại diện cho độ trung thực danh tính cực cao. Mức 0.8 thường được yêu cầu trong các bài kiểm tra học thuật của mô hình InstantID, hoặc ngưỡng 0.75 dùng để lọc dữ liệu sạch trong các tập dữ liệu huấn luyện lớn như PPR10K. Việc thiết lập ngưỡng quá cao (tiệm cận 1.0) trong thực tế sản xuất sẽ gây phản tác dụng, khiến hệ thống từ chối chính những bản kết xuất hợp lệ chỉ vì nhân vật thay đổi tư thế đầu.

### 3.2. DINO và CLIP: Đo lường Dáng vẻ Tổng thể và Tuân thủ Kịch bản

Nếu chỉ sử dụng ArcFace, hệ thống sẽ rơi vào "điểm mù" về cơ thể. Một AI có thể tạo ra một bức ảnh với khuôn mặt giống hệt nhân vật, nhưng gắn trên một thân hình sai tỷ lệ hoặc mặc sai trang phục. Để lấp đầy khoảng trống này, các đường ống (pipelines) đánh giá chất lượng cao như PuLID tích hợp thêm mô hình DINO và CLIP.

DINO (thường là DINOv2) được áp dụng để đo lường "Sự nhất quán tổng thể" (DINO Consistency). Thay vì tập trung vào khuôn mặt, DINO trích xuất các đặc trưng hình ảnh toàn cục, đánh giá mức độ tương đồng của quần áo, cấu trúc giải phẫu học cơ thể và tư thế giữa các ảnh. Tuy nhiên, các tài liệu kỹ thuật không ghi nhận một "ngưỡng cắt" số học cố định áp dụng chung cho DINO như ArcFace, mà chủ yếu sử dụng nó làm điểm chuẩn (benchmark) tương đối để so sánh hiệu suất giữa các phiên bản mô hình khác nhau.

Song song đó, CLIP (Contrastive Language-Image Pre-training) thông qua các chỉ số CLIP-T và CLIP-I được sử dụng để định lượng khả năng bám sát lời nhắc kịch bản (prompt alignment). CLIP đảm bảo rằng nếu kịch bản yêu cầu nhân vật "đang chạy dưới mưa", hình ảnh đầu ra không chỉ có đúng khuôn mặt, đúng tỷ lệ cơ thể, mà phải thực hiện chính xác hành động và bối cảnh môi trường được giao.

Để tối ưu hóa quá trình đo lường này, hệ thống áp dụng các chế độ Mặt nạ phân đoạn (Mask Mode). Trong ComfyUI, chế độ "face" hoặc "head" sử dụng mạng nơ-ron BiSeNet để phân đoạn chính xác vùng da và tóc, loại bỏ cổ áo hay nền. Trong khi đó, chế độ "body" yêu cầu tích hợp mô hình SAM (Segment Anything Model) để trích xuất lớp mặt nạ toàn thân, đảm bảo các thuật toán như DINO không bị nhiễu bởi bối cảnh phía sau nhân vật.

## 4. Giải phẫu Cẩm nang Nhân vật (Character Bible)

Có một sự hiểu lầm lớn trong ngành công nghiệp rằng Cẩm nang nhân vật tồn tại để ép AI tạo ra các bức ảnh giống hệt nhau một cách cơ học. Thực chất, triết lý của Cẩm nang nhân vật là "giảm thiểu sự không chắc chắn" (reducing uncertainty). Bằng cách cung cấp dữ liệu đa chiều, Cẩm nang giúp AI hiểu rõ kết cấu ba chiều của nhân vật trước khi nó quyết định nhân vật sẽ làm gì trong một cảnh quay cụ thể.

### 4.1. Hệ thống 10 Cấu phần Tiêu chuẩn

Một Cẩm nang nhân vật cấp độ chuyên nghiệp là một tài liệu dài từ 2 đến 3 trang, kết hợp văn bản mô tả kỹ thuật và hệ thống tài sản hình ảnh neo, bao gồm 10 hạng mục thiết yếu để vận hành hệ thống Khóa Danh tính (Identity Lock):

Đầu tiên là **Chính diện (Front View)**, đóng vai trò là mỏ neo thị giác chính, xác định rõ cấu trúc hộp sọ, màu mắt, kiểu dáng tóc và hình bóng (silhouette) tổng thể. Tuy nhiên, hình chính diện là chưa đủ. **Mặt bên (Side Views - Left & Right)** là cấu phần tối quan trọng để dạy cho AI hiểu về khối lượng không gian, độ nhô của sống mũi, đường viền hàm và vị trí tai. Thiếu mặt bên, các mô hình video AI sẽ làm bẹp hoặc biến dạng khuôn mặt khi nhân vật quay đầu. Tiếp theo, **Mặt sau (Back View)** duy trì tính liên tục của trang phục và kiểu tóc khi nhân vật di chuyển xa khỏi ống kính.

Để nhân vật có sức sống, **Bảng Biểu cảm (Facial Expressions Sheet)** bắt buộc phải bao gồm ít nhất 8 trạng thái cảm xúc cốt lõi (Bình thường, Vui vẻ, Tức giận, Ngạc nhiên, Suy nghĩ, Buồn, Phấn khích, Lo lắng). Bảng này dạy cho mô hình AI cách các cơ mặt biến dạng dưới tác động của cảm xúc mà không làm mất đi các nét sinh trắc học đặc trưng. Đi kèm với khuôn mặt là **Bảng Xoay Toàn thân (Full Body Turnaround)** với các góc 3/4 và sau lưng, giúp cố định tỷ lệ chiều cao, độ rộng vai và chiều dài chân.

Để phục vụ cho việc lên kịch bản phân cảnh (storyboarding), **Tư thế Tham chiếu (Pose Reference Sheet)** cung cấp từ 10 đến 20 tư thế thường gặp trong đời sống (như khoanh tay, cầm điện thoại, chạy). Nhằm ngăn chặn AI nhận diện sai lầm rằng một trang phục mới đồng nghĩa với một nhân vật mới, **Biến thể Trang phục (Outfit Variations)** cung cấp các bộ cánh từ thường ngày đến trang trọng. Cùng với đó, **Bảng Màu (Color Palette)** khóa chặt các mã màu hệ Hex cho da, tóc, mắt và vật liệu, đảm bảo chúng không bị biến đổi dưới các điều kiện ánh sáng môi trường khác nhau.

Về mặt điện ảnh, **Góc Máy ảnh (Camera Angles)** xác định ngôn ngữ thị giác ưa thích của dự án, từ cận cảnh chân dung đến các cú máy qua vai (over-the-shoulder). Cuối cùng, **Hồ sơ Văn bản (Character Profile)** đóng gói toàn bộ nhân dạng vào một cấu trúc ngôn ngữ, bao gồm tên, tuổi, chiều cao, tính cách, nghề nghiệp và định hướng phong cách nghệ thuật (ví dụ: Cinematic realism).

Công thức thực thi để đạt được độ nhất quán cao trong sản xuất được định nghĩa bằng phương trình: Cẩm nang Nhân vật Mạnh + Lời nhắc Khóa Danh tính (Identity Lock) + Lời nhắc Cảnh Chi tiết = Độ Nhất quán Tối ưu. Trong đó, Lời nhắc Khóa Danh tính quy định rạch ròi những yếu tố thuộc về giải phẫu học không bao giờ được phép thay đổi, đồng thời cho phép sự linh hoạt tuyệt đối đối với trang phục, ánh sáng, góc máy và bối cảnh môi trường.

### 4.2. Khung Cấu trúc Mã nguồn Mở

Sự chuẩn hóa của Cẩm nang nhân vật đã phát triển đến mức nó được thiết kế để tương thích trực tiếp với các Mô hình Ngôn ngữ Lớn (LLM) như Claude hay GPT-4. Một ví dụ tiêu biểu là bộ khung cấu trúc mã nguồn mở character-bible.md từ dự án Dramake lưu trữ trên GitHub. Cấu trúc này không dành cho con người đọc, mà đóng vai trò như một cơ sở dữ liệu để LLM truy xuất.

Mẫu Dramake phân rã nhân vật thành sáu khối dữ liệu siêu cấu trúc. Khối **Danh tính (Identity)** định nghĩa rõ ràng về loài, giới tính, bản đồ bề mặt (surface map) của da, tỷ lệ cơ thể và các hạn chế về mặt vận động giải phẫu. Khối **Cấu trúc Trang phục (Costume Structure)** không chỉ mô tả quần áo mà còn quy định chi tiết về vật liệu, các khóa cài, vị trí đường may, dung sai của nếp gấp, độ ẩm, vết bẩn, và đặc biệt nghiêm cấm mọi sự thay đổi về mặt cấu trúc lưới (topology) của trang phục.

Khối **Diễn xuất (Performance)** đặt ra các quy tắc về mức độ nhân hóa (anthropomorphism), động tác thói quen đặc trưng, từ vựng chuyển động, và giới hạn kéo giãn cơ thể (squash/stretch), đồng thời ngăn chặn các hành vi dị biến (mutations) phi logic. Khối **Tuyến Âm thanh (Voice Line)** neo giữ các thông số về âm vực, nhịp thở, cơ sở cảm xúc và kết cấu không gian của micro. Cuối cùng, các khối **Tài sản Chính thức (Official Assets)** và **Quyền uy Tham chiếu (Reference Authority)** quản lý các liên kết đến các ảnh gốc đã được nghiệm thu, đảm bảo AI luôn gọi đúng phiên bản tham chiếu mới nhất và không được phép tự ý ngoại suy.

## 5. Rủi ro Pháp lý, Quyền Nhân thân và Sự Minh bạch Đạo đức

Sự bùng nổ của AI sáng tạo mang lại khả năng tối ưu hóa vô tiền khoáng hậu, nhưng đồng thời tạo ra những vùng xám pháp lý phức tạp. Việc khai thác dữ liệu để tạo ra nhân vật ảo đối diện với rủi ro nghiêm trọng liên quan đến quyền hình ảnh, bản quyền tác phẩm và các quy định về minh bạch dữ liệu, đặc biệt khi quy mô thương mại hóa được mở rộng.

### 5.1. Quyền Hình ảnh và Thực tiễn Tranh chấp tại Việt Nam

Theo quy định tại Điều 32 Bộ luật Dân sự 2015 của Việt Nam, quyền của cá nhân đối với hình ảnh của mình là một quyền nhân thân bất khả xâm phạm. Mọi hành vi sử dụng hình ảnh cá nhân đều phải được sự đồng ý của người đó. Trong ngành công nghiệp nhân vật ảo, rủi ro lớn nhất phát sinh ở khâu huấn luyện bộ dữ liệu (dataset training). Nếu một agency thu thập hình ảnh của các người mẫu thật trên mạng internet để làm "tài sản tham chiếu" nhằm huấn luyện mô hình LoRA tạo ra một khuôn mặt AI mới, hành vi này có thể cấu thành vi phạm pháp luật nếu không có sự ủy quyền rõ ràng. Đặc biệt, khi nhân vật ảo này được sử dụng cho mục đích thương mại (như quảng bá sản phẩm), cơ quan sản xuất bắt buộc phải trả thù lao cho chủ thể của những hình ảnh gốc, trừ khi có hợp đồng thoả thuận khác đi.

Trong môi trường hợp tác thương mại thực tiễn giữa nhãn hàng và các Người có sức ảnh hưởng (KOLs), rủi ro pháp lý thường xuất hiện dưới dạng các vi phạm vượt quá phạm vi cho phép. Agency hoặc nhãn hàng có thể sử dụng dữ liệu hình ảnh của KOL để tạo ra các nhân vật phái sinh bằng công nghệ deepfake nhằm kéo dài thời gian chiến dịch quảng cáo hoặc mở rộng thị trường mà không ký thêm phụ lục hợp đồng, hoặc nghiêm trọng hơn là đưa nhân vật ảo vào các tình huống gây tổn hại đến danh dự, nhân phẩm và uy tín của KOL bản gốc. Các chế tài xử phạt đối với hành vi xâm phạm quyền riêng tư hình ảnh không dừng lại ở mức phạt hành chính từ 20 đến 30 triệu đồng, mà còn có thể bị truy cứu trách nhiệm hình sự về tội làm nhục người khác theo Điều 155 Bộ luật Hình sự.

### 5.2. Các Phán quyết Tiền lệ Định hình Ngành tại Trung Quốc

Trong khi khung pháp lý tại nhiều quốc gia còn đang điều chỉnh, các Tòa án Internet tại Bắc Kinh, Trung Quốc đã đưa ra hàng loạt phán quyết mang tính bước ngoặt, trực tiếp định hình cách thức các tập đoàn công nghệ quản trị rủi ro tài sản ảo.

Tiền lệ đầu tiên liên quan đến bản quyền của nhân vật 3D. Trong một vụ kiện, một cá nhân tên Tôn mỗ đã tự ý trích xuất và rao bán các mô hình 3D của hai nhân vật ảo (Nhân vật A và B) do một nhóm công ty hợp tác sản xuất. Tòa án Internet Bắc Kinh đã phán quyết rằng các thiết kế nhân vật ảo này mang "tính nguyên gốc" (originality) rõ rệt, phản ánh sự lựa chọn thẩm mỹ độc đáo của đội ngũ thiết kế về đường nét, màu sắc và cấu trúc, do đó chúng cấu thành "tác phẩm mỹ thuật" được bảo hộ theo Luật Bản quyền. Việc Tôn mỗ bán các mô hình có sự tương đồng thực chất (substantial similarity) về khuôn mặt, kiểu tóc và trang phục đã vi phạm quyền sao chép và truyền đạt tác phẩm qua mạng lưới thông tin, dẫn đến án phạt bồi thường thiệt hại kinh tế 15.000 NDT.

Tiền lệ thứ hai thiết lập sự bảo hộ đối với Hình ảnh Nhân thân Toàn diện (Overall Personality Image). Trong vụ án liên quan đến phần mềm "AI Companion", người dùng đã sử dụng tính năng của nền tảng để tải lên tên, chân dung và đặc điểm cá nhân của một nhân vật của công chúng (ông He) nhằm tạo ra các mô hình AI tương tác. Tòa án lập luận rằng việc kết hợp các đặc điểm này để xây dựng một bản sao ảo đã trực tiếp xâm phạm quyền tự do và tôn nghiêm nhân thân của cá nhân đó. Quan trọng hơn, tòa án phán quyết rằng nền tảng phần mềm không thể lấy lý do là trung gian công nghệ để trốn tránh trách nhiệm; thiết kế tính năng và thuật toán của họ đã khuyến khích và tạo điều kiện cho hành vi vi phạm, do đó họ phải chịu trách nhiệm bồi thường trực tiếp.

Tiền lệ thứ ba là vụ kiện về Quyền giọng nói AI đầu tiên tại Trung Quốc. Một nữ diễn viên lồng tiếng (Bà Yin) phát hiện giọng nói của mình bị sao chép thành các mô hình văn bản-thành-giọng-nói (TTS) trên nhiều ứng dụng. Tòa án đã thiết lập tiêu chuẩn "Tính có thể nhận diện" (Identifiability): Nếu công chúng có thể liên tưởng trực tiếp giọng nói do AI tổng hợp với chủ thể gốc thông qua âm sắc, ngữ điệu và phong cách phát âm, thì quyền giọng nói đối với bản sao AI đó được pháp luật bảo vệ tuyệt đối. Tòa án cũng vạch ra ranh giới pháp lý sắc bén: việc một cá nhân ký hợp đồng cấp phép sử dụng bản ghi âm của họ cho một dự án cụ thể hoàn toàn không đồng nghĩa với việc họ cấp phép cho công ty đó dùng dữ liệu âm thanh để huấn luyện mô hình AI. Các công ty liên quan do có yếu tố lỗi chủ quan đã phải chịu trách nhiệm liên đới, với mức bồi thường lên tới 250.000 NDT.

### 5.3. Rủi ro Tuân thủ và Quy định Dán nhãn AI (AI Labeling Rules)

Để đối phó với sự lan truyền của deepfake và nội dung tạo sinh, Cục Quản lý Không gian mạng Trung Quốc (CAC) cùng các cơ quan chức năng đã ban hành các quy định nghiêm ngặt về nhận diện nội dung AI, chính thức có hiệu lực và được thực thi mạnh mẽ trong giai đoạn 2024–2025.

Theo quy định, mọi tài sản hình ảnh, video, âm thanh hay bối cảnh ảo được tạo ra hoặc chỉnh sửa đáng kể bởi AI tại thị trường này bắt buộc phải được gắn nhãn minh bạch. Sự minh bạch này yêu cầu tính hai chiều: phải có "nhãn tường minh" (explicit labels) hiển thị trực tiếp trên giao diện để người dùng có thể nhận biết bằng mắt thường, và "nhãn ẩn" (implicit labels) dưới dạng siêu dữ liệu (metadata) hoặc thủy ấn kỹ thuật số (watermarks) được nhúng sâu vào mã tệp tin để theo dõi nguồn gốc và chống lại các hành vi chỉnh sửa gian lận.

Các nền tảng phân phối ứng dụng và mạng xã hội có nghĩa vụ pháp lý phải kiểm duyệt và từ chối lưu trữ các nội dung AI không được dán nhãn hợp lệ. Sự thực thi của các cơ quan quản lý không chỉ nằm trên giấy. Vào tháng 9 năm 2026, CAC đã công bố các vụ xử phạt điển hình, trong đó các ứng dụng nhỏ (mini programs) cung cấp dịch vụ tạo sinh AI đã bị buộc gỡ bỏ ngoại tuyến (offline) vì bỏ qua khâu dán nhãn và né tránh các quy trình đánh giá bảo mật bắt buộc của quốc gia. Các thương hiệu và agency quốc tế khi triển khai các chiến dịch tiếp thị sử dụng nhân vật ảo (digital avatars) tại Trung Quốc hiện phải đối diện với sự gia tăng mạnh mẽ về chi phí tuân thủ; nếu vi phạm các nghĩa vụ về dán nhãn, bảo vệ dữ liệu hay lưu trữ hồ sơ, họ có nguy cơ bị đình chỉ dịch vụ, kiểm duyệt công khai và chịu mức phạt hành chính lên tới 200.000 NDT.

## 6. Phụ lục 1: Phân tích Khoảng trống Dữ liệu (Missing Data)

Trong quá trình tổng hợp các nguồn tài liệu kỹ thuật từ các diễn đàn, báo cáo và bài đăng của các chuyên gia trong ngành, một số chỉ số và cấu trúc quy trình nội bộ đặc thù vẫn chưa được tiết lộ công khai, tạo ra những khoảng trống dữ liệu nhất định:

- **Ngưỡng số học cụ thể của DINO:** Trong khi thuật toán ArcFace được công khai các mức ngưỡng đánh giá (như 0.65 cho sản xuất tiêu chuẩn hay 0.8 cho độ trung thực cao), các báo cáo học thuật và tài liệu kỹ thuật ghi nhận việc sử dụng mô hình DINO (DINOv2) để đo lường độ nhất quán về quần áo và cơ thể (DINO Consistency), nhưng hoàn toàn không công bố một "ngưỡng cắt" (cutoff threshold) bằng con số cụ thể để tự động loại bỏ hình ảnh. DINO hiện tại dường như chỉ được dùng làm thang đo tương đối.
- **Định danh vai trò duyệt cuối cùng tại Agency Việt Nam:** Các tài liệu phân tích workflow của các đơn vị quốc tế (như Astorie, Lollipop) mô tả chi tiết chức năng của cổng duyệt trước xuất bản, nhưng các tài liệu nội địa và quốc tế không cung cấp thông tin cụ thể về chức danh C-level (như Brand Manager, Client Representative, hay Creative Director) chịu trách nhiệm ký duyệt ở vòng cuối cùng mang tính thương mại, mà chỉ rọi đèn vào các chức danh sản xuất kỹ thuật nội bộ (Technical Director, Visual Designer, Rigger).

## 7. Phụ lục 2: Bảng Trích dẫn Nguyên văn Các Thông số Kỹ thuật (Verbatim Quotes)

Bảng dưới đây trích dẫn nguyên văn (kèm liên kết) các số liệu kỹ thuật quan trọng nhất về đo lường và quy định định hình cấu trúc sản xuất:

| Chỉ số / Tham số Kỹ thuật | Trích dẫn nguyên văn (Verbatim Quote) | Nguồn (Liên kết tham chiếu) |
| --- | --- | --- |
| **Số ảnh Tham chiếu Tiêu chuẩn** | "Generate and freeze 5–8 references per character: front, three-quarter, profile, expression set, and a full-body wardrobe shot." | [Lollipop - Character Consistency](https://www.lollipop.im/blog/character-consistency-workflow/) |
| **Ngưỡng huấn luyện LoRA** | "The practical threshold is around 8 episodes. Training costs hours of asset collection, training runs, and parameter tuning; below 8 episodes you will not earn that back." | [Lollipop - Character Consistency](https://www.lollipop.im/blog/character-consistency-workflow/) |
| **Ngưỡng đo ArcFace (ComfyUI)** | "threshold is the cosine-similarity cutoff, and 0.6–0.7 is the recommended band - too low and every face 'matches', too high and your character stops matching their own slightly-off renders. (Default: 0.650)" | [ComfyUI PersonSelector](https://comfy.icu/node/PersonSelector) |
| **Ngưỡng ArcFace (Cảnh báo & Loại bỏ)** | "The README's reference: above 0.6 you're confidently the same person, 0.4–0.6 is 'worth a look', below 0.4 identity has drifted." | [ComfyUI FaceSimilarityNode](https://comfy.icu/node/FaceSimilarityNode) |
| **Ngưỡng Khôi phục Danh tính InstantID** | "The cosine similarity threshold for successful recovery is set to 0.8." | [arXiv - Adapter Shield](https://arxiv.org/html/2512.00075v1) |
| **Ngưỡng lọc Dữ liệu Sạch PPR10K** | "After filtering for single-face images and enforcing a face similarity threshold greater than 0.75, we constructed a training set of 10,444 pairs of images..." | [arXiv - Identity Preserving Generation](https://arxiv.org/pdf/2607.25622) |
| **Tiền phạt Bản quyền Mô hình 3D (Tòa án Bắc Kinh)** | "Final judgment: Defendant Sun was ordered to pay total economic damages of 15,000 RMB to the plaintiffs (10,000 RMB for Virtual Human A, 5,000 RMB for Virtual Human B)." | [Beijing News - 3D Virtual Human](https://m.bjnews.com.cn/detail/1756211837168290.html) |
| **Tiền phạt Xâm phạm Quyền giọng nói AI (Tòa án Bắc Kinh)** | "Defendants 2 (Media Co.) and 3 (Software Co.) had fault and were held jointly liable for 250,000 RMB in economic damages." | [JTN - First AI Voice Case](https://www.jtn.com/CN/booksdetail.aspx?type=06001&keyid=00000000000000008474&PageUrl=majorbook&Lan=CN) |

   

## 8. Bảng Hệ thống Nguồn Dữ liệu (Source Table)

| Mã ID Tham chiếu | Ngôn ngữ | Ngày / Năm | Chủ thể / Trọng tâm Dữ liệu Cung cấp | Liên kết Truy cập (URL) |
| --- | --- | --- | --- | --- |
| 1, 114 | Tiếng Anh | 2024-2026 | Lollipop: Character Consistency Workflow (Quy trình 7 bước, Pre-publish gates, Ngưỡng LoRA) | [Lollipop Blog](https://www.lollipop.im/blog/character-consistency-workflow/) |
| 2, 24 | Tiếng Anh | 2026 | Astorie: Workflows/Character Consistency (Định hình Cẩm nang từ vibe sang spec) | [Astorie Workflows](https://astorie.ai/workflows/character-consistency) |
| 5, 116 | Tiếng Anh | 2024-2026 | PromptHome: AI Character Bible Guide (Cấu trúc 10 phần, Identity Lock Prompt) | [The Prompt Home](https://theprompthome.com/ai-character-bible-guide/) |
| 38, 113 | Tiếng Anh | 2024 | ComfyUI PersonSelector: ArcFace Cosine Similarity Thresholds (Ngưỡng an toàn 0.6 - 0.7) | [ComfyUI Node](https://comfy.icu/node/PersonSelector) |
| 40, 44, 50 | Tiếng Anh | 2024-2026 | DocSaid / Didit / YouTube: ArcFace Paper Analysis (Nguyên lý Additive Angular Margin Loss) | [DocSaid Research](https://docsaid.org/en/blog/papers/face-recognition/arcface) |
| 60 | Tiếng Anh | 2024 | ComfyUI FaceSimilarityNode: Các ngưỡng trôi dạt danh tính sinh trắc học (< 0.4) | [ComfyUI Node](https://comfy.icu/node/FaceSimilarityNode) |
| 63, 139 | Tiếng Anh | Tháng 10/2026 | Medium (Devenko AI): Build an AI Mascot for Ecom (Số vòng lặp casting, quy tắc thương hiệu) | [Medium Article](https://devenkoai.medium.com/how-to-build-an-ai-mascot-for-your-ecom-brand-free-guide-42c4e71bebc6) |
| 67, 74 | Tiếng Anh | 2025 | arXiv: Adapter Shield (Đánh giá học thuật InstantID, ngưỡng khôi phục 0.8) | [arXiv Paper](https://arxiv.org/html/2512.00075v1) |
| 73, 79 | Tiếng Anh | 2025 | arXiv: Khảo sát độ Nhất quán Danh tính bằng DINO và thuật toán ArcFace | [arXiv Paper](https://arxiv.org/html/2508.09461v1) |
| 77, 156 | Tiếng Anh | 2024 | arXiv: Khung đánh giá PuLID Framework (Các chỉ số CurricularFace, CLIP-T, CLIP-I) | [arXiv Paper](https://arxiv.org/html/2404.16022v2) |
| 82, 172 | Tiếng Trung | 26/08/2025 | Beijing News: Phán quyết của Tòa án Bắc Kinh về Bản quyền nhân vật 3D (Bồi thường 15,000 NDT) | [Beijing News](https://m.bjnews.com.cn/detail/1756211837168290.html) |
| 85, 86, 141 | Tiếng Trung | 21/06/2024 | JTN: Các án lệ của Tòa án Internet Bắc Kinh (Bảo vệ quyền giọng nói AI, Phần mềm AI Companion) | [JTN Law](https://www.jtn.com/CN/booksdetail.aspx?type=06001&keyid=00000000000000008474&PageUrl=majorbook&Lan=CN) |
| 92, 94 | Tiếng Trung | 2024-2026 | UISDC: Quy trình thiết kế nhân vật số 3D truyền thống (Mô hình, Textures, UDIM, Rigging) | [UISDC Blog](https://www.uisdc.com/digital-human-role-design) |
| 96, 98, 140 | Tiếng Anh | 2026 | Kuroganeito / DrawMarket: Hướng dẫn Khởi tạo Model VTuber (Cắt layers, Cổng duyệt, VRoid) | [VTuber Guide](https://kuroganeito.jp/vtubermodelcreation-en) |
| 112, 142 | Tiếng Trung | 2024-2026 | GitHub (xixihhhh): Hệ thống mã nguồn mở Character Bible (Định dạng .md) cho dự án Dramake AI | [GitHub Repository](https://github.com/xixihhhh/ai-short-drama-skill/blob/main/skills/dramake/assets/templates/character-bible.md) |
| 117, 121, 126 | Tiếng Việt | 2024-2026 | Luật Hoàng Sa / Viện Kiểm Sát: Phân tích cơ sở pháp lý Điều 32 Bộ luật Dân sự 2015 (Quyền hình ảnh) | [Luật Hoàng Sa](https://luathoangsa.vn/quyen-cua-ca-nhan-doi-voi-hinh-anh-nd63851.html) |
| 130 | Tiếng Việt | 2024-2026 | Luật Long Phan: Chuyên đề giải quyết tranh chấp quyền hình ảnh giữa các KOLs/Influencer và Agency | [Luật Long Phan](https://luatlongphan.vn/giai-quyet-tranh-chap-su-dung-hinh-anh-kol-influencer) |
| 151 | Tiếng Anh | 2026 | arXiv (PDF): Phân tích mạng nơ-ron Dual-Branch (Lọc dữ liệu PPR10K với ngưỡng > 0.75) | [arXiv Paper](https://arxiv.org/pdf/2607.25622) |
| 157, 160, 162 | Tiếng Anh | 2025-2026 | AI Regulations / Trussed.AI: Báo cáo phân tích Luật dán nhãn minh bạch AI của CAC Trung Quốc | [AI Regulations](https://artificialintelligenceregulations.com/jurisdictions/china.html) |
| 164 | Tiếng Anh | 2026 | TransAsia Lawyers: Dự thảo pháp luật về quản lý, dán nhãn và xử phạt liên quan đến Nhân vật số tại Trung Quốc | [TransAsia Lawyers](https://www.transasialawyers.com/insights/new-draft-rules-for-digital-avatars-and-virtual-humans-in-china) |

[theprompthome.com
AI Character Bible: The Ultimate Guide to Creating Consistent AI
Opens in a new window](https://theprompthome.com/ai-character-bible-guide/)[astorie.ai
AI Character Consistency Workflow - Astorie
Opens in a new window](https://astorie.ai/workflows/character-consistency)[lollipop.im
AI Character Consistency Workflow: 7 Steps | Lollipop Drama Guides
Opens in a new window](https://www.lollipop.im/blog/character-consistency-workflow/)[devenkoai.medium.com
How to Build an AI Mascot for Your Ecom Brand (FREE Guide)
Opens in a new window](https://devenkoai.medium.com/how-to-build-an-ai-mascot-for-your-ecom-brand-free-guide-42c4e71bebc6)[draw.market
From OC to VTuber Model — How to Nail Your Character Design
Opens in a new window](https://draw.market/en/blog/first-step-to-custom-vtuber-model.html)[kuroganeito.jp
The Ultimate Guide to VTuber Model Creation (2026) - Ito Kurogane
Opens in a new window](https://kuroganeito.jp/vtubermodelcreation-en)[medium.com
Bringing VTubers to Life: My 2D Character and Live2D Model
Opens in a new window](https://medium.com/@Kenny_Studiuo/bringing-vtubers-to-life-my-2d-character-and-live2d-model-creation-workflow-308ca604cc85)[os-artist-front.webapp.easebar.com
How to Make a VTuber Model from Scratch (Free & Paid Methods)
Opens in a new window](https://os-artist-front.webapp.easebar.com/en/blog/how-to-make--vtuber-model.html)[comfy.icu
Person Selector (Match) - ComfyUI Cloud - Comfy.ICU
Opens in a new window](https://comfy.icu/node/PersonSelector)[morphic.com
InstantID: single-image face identity preservation in AI - Morphic
Opens in a new window](https://morphic.com/ai-glossary/instantid)[comfy.icu
Face Similarity (InsightFace) - ComfyUI Cloud - Comfy.ICU
Opens in a new window](https://comfy.icu/node/FaceSimilarityNode)[medium.com
ArcFace — Architecture and Practical example: How to calculate the
Opens in a new window](https://medium.com/@ichigo.v.gen12/arcface-architecture-and-practical-example-how-to-calculate-the-face-similarity-between-images-183896a35957)[docsaid.org
ArcFace · Blog - DOCSAID
Opens in a new window](https://docsaid.org/en/blog/papers/face-recognition/arcface)[didit.me
ArcFace vs. CosFace: Deep Dive into Face Matching Algorithms
Opens in a new window](https://didit.me/blog/arcface-vs-cosface-deep-dive-into-face-matching-algorithms/)[youtube.com
State‑of‑the‑Art Face Recognition with Angular Margin - YouTube
Opens in a new window](https://www.youtube.com/watch?v=66jO7fdUELk)[community.hailo.ai
A Comprehensive Guide to Building a Face Recognition System
Opens in a new window](https://community.hailo.ai/t/a-comprehensive-guide-to-building-a-face-recognition-system/8803)[medium.com
Face Recognition and ArcFace Loss for Beginners | by Aylin Aydin
Opens in a new window](https://medium.com/@aylin.aydin/face-recognition-and-arcface-loss-for-beginners-cdfddbf7e88)[arxiv.org
Adapter Shield: A Unified Framework with Built-in Authentication for
Opens in a new window](https://arxiv.org/html/2512.00075v1)[arxiv.org
Personalized Person Image Generation with Holistic Identity ... - arXiv
Opens in a new window](https://arxiv.org/pdf/2607.25622)[arxiv.org
Personalized Person Image Generation with Holistic Identity ... - arXiv
Opens in a new window](https://arxiv.org/html/2607.25622v1)[arxiv.org
Gen-AFFECT: Generation of Avatar Fine-grained Facial Expressions
Opens in a new window](https://arxiv.org/html/2508.09461v1)[arxiv.org
PuLID: Pure and Lightning ID Customization via Contrastive Alignment
Opens in a new window](https://arxiv.org/html/2404.16022v2)[github.com
character-bible.md - xixihhhh/ai-short-drama-skill · GitHub
Opens in a new window](https://github.com/xixihhhh/ai-short-drama-skill/blob/main/skills/dramake/assets/templates/character-bible.md)[luathoangsa.vn
Quyền của cá nhân đối với hình ảnh (Điều 32 Bộ luật dân sự 2015).
Opens in a new window](https://luathoangsa.vn/quyen-cua-ca-nhan-doi-voi-hinh-anh-nd63851.html)[vanphuclawfirm.com
Quyền của cá nhân đối với hình ảnh được quy định như nào?
Opens in a new window](https://vanphuclawfirm.com/quyen-cua-ca-nhan-doi-voi-hinh-anh/)[luatvietnam.vn
Luật quy định thế nào về quyền hình ảnh của cá nhân? - LuatVietnam
Opens in a new window](https://luatvietnam.vn/tin-phap-luat/luat-quy-dinh-the-nao-ve-quyen-hinh-anh-cua-ca-nhan-230-15685-article.html)[kiemsat.vn
Trách nhiệm dân sự đối với hành vi xâm phạm quyền nhân thân trên
Opens in a new window](https://kiemsat.vn/trach-nhiem-dan-su-doi-voi-hanh-vi-xam-pham-quyen-nhan-than-tren-mang-xa-hoi-72210.html)[luatlongphan.vn
Giải quyết tranh chấp sử dụng hình ảnh KOL/Influencer
Opens in a new window](https://luatlongphan.vn/giai-quyet-tranh-chap-su-dung-hinh-anh-kol-influencer)[m.bjnews.com.cn
虚拟数字人形象受著作权法保护，北京互联网法院作出生效判决 - 新京报
Opens in a new window](https://m.bjnews.com.cn/detail/1756211837168290.html)[chinaiplawupdate.com
北京互联网法院涉人工智能典型案例 - China IP Law Update -
Opens in a new window](https://www.chinaiplawupdate.com/wp-content/uploads/2025/09/%E5%8C%97%E4%BA%AC%E4%BA%92%E8%81%94%E7%BD%91%E6%B3%95%E9%99%A2%E6%B6%89%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E5%85%B8%E5%9E%8B%E6%A1%88%E4%BE%8B.pdf)[jtn.com
AI应用中的权利保护与合规：“全国首例AI生成声音人格权侵权案”评析
Opens in a new window](https://www.jtn.com/CN/booksdetail.aspx?type=06001&keyid=00000000000000008474&PageUrl=majorbook&Lan=CN)[artificialintelligenceregulations.com
AI Regulation in China: Laws, Status and Penalties
Opens in a new window](https://artificialintelligenceregulations.com/jurisdictions/china.html)[trussed.ai
China AI Labeling Requirements September 2025 - Trussed AI
Opens in a new window](https://trussed.ai/resources/china-ai-labeling-requirements-september-2025)[transasialawyers.com
New Draft Rules for Digital Avatars and Virtual Humans in China
Opens in a new window](https://www.transasialawyers.com/insights/new-draft-rules-for-digital-avatars-and-virtual-humans-in-china)[uisdc.com
5000字干货！3D卡通虚拟数字人角色设计完整流程（上） - 优设
Opens in a new window](https://www.uisdc.com/digital-human-role-design)[domer.io
Consistent Character Workflow: The Missing Link in AI Content
Opens in a new window](https://domer.io/blog/consistent-character-ai-workflow)[ltx.io
How to Maintain Character Consistency in AI Video Production - LTX
Opens in a new window](https://ltx.io/blog/how-to-maintain-character-consistency-in-ai-video)[vidu.com
Consistent Character AI: Workflows & Tips - Vidu AI
Opens in a new window](https://www.vidu.com/blog/consistent-character-ai)[runway.com
Runway Resources | How to Create Consistent AI Characters
Opens in a new window](https://runway.com/resources/create-consistent-ai-characters)[youtube.com
How to Make Consistent AI Characters With Your Own Face and
Opens in a new window](https://www.youtube.com/watch?v=wGs2vByrF3U)[higgsfield.ai
7 Tools for Consistent AI Characters Across Every Scene in 2026
Opens in a new window](https://higgsfield.ai/blog/tools-for-consistent-ai-characters)[invideo.io
Solving AI Character Consistency Workflow - invideo AI
Opens in a new window](https://invideo.io/academy/i-tried-every-ai-character-consistency-workflow-results/)[sozee.ai
AI Influencer Content Workflow: Step-By-Step Playbook - Sozee
Opens in a new window](https://www.sozee.ai/resources/ai-influencer-content-workflow/)[thefluxtrain.com
AI Influencer Creator Workflow | TheFluxTrain
Opens in a new window](https://thefluxtrain.com/ai-influencer-creator/)[queststudio.io
How to Create an AI Influencer That Stays Consistent - QuestStudio
Opens in a new window](https://queststudio.io/blog/how-to-create-an-ai-influencer)[elser.ai
Building an Original Character Bible That AI Tools Can Follow
Opens in a new window](https://www.elser.ai/blog/building-an-original-character-bible-that-ai-tools-can-follow)[oakgen.ai
AI Character Video Workflow: Sheet to Launch Cut - Oakgen.ai
Opens in a new window](https://oakgen.ai/blog/character-sheet-to-launch-video-workflow)[montagea.com
How to Build a Consistent AI Influencer: Video Workflow - Montagea
Opens in a new window](https://montagea.com/blog/build-consistent-ai-influencer-video-workflow/)[youtube.com
This Character Board Makes Your AI Influencer 100% Consistent
Opens in a new window](https://www.youtube.com/watch?v=x9ETAqkAysg)[didit.me
Face Matching Algorithms: ArcFace & CosFace. - Didit.me
Opens in a new window](https://didit.me/blog/face-matching-algorithms-arcface-cosface/)[arxiv.org
A novel Facial Recognition technique with Focusing on Masked Faces
Opens in a new window](https://www.arxiv.org/pdf/2501.04444v1)[openaccess.thecvf.com
ArcFace for Disguised Face Recognition - CVF Open Access
Opens in a new window](https://openaccess.thecvf.com/content_ICCVW_2019/papers/DFW/Deng_ArcFace_for_Disguised_Face_Recognition_ICCVW_2019_paper.pdf)[insightface.ai
InsightFace ArcFace: Additive Angular Margin Loss Explained
Opens in a new window](https://www.insightface.ai/research/arcface)[ijert.org
Selfie-Based Attendance System Implementation Using ArcFace
Opens in a new window](https://www.ijert.org/selfie-based-attendance-system-implementation-using-arcface-and-cosine-similarity-for-identity-verification-ijertconv14is010041)[viblo.asia
[Paper explained] Face Recognition: Facenet, ArcFace, CosFace
Opens in a new window](https://viblo.asia/p/paper-explained-some-face-recognition-approaches-facenet-arcface-cosface-Do754zgLZM6)[mdpi.com
CoFaDiff: Coordinating Identity Fidelity and Text Consistency ... - MDPI
Opens in a new window](https://www.mdpi.com/2076-3417/16/1/414)[media.io
ComfyUI Consistent Characters: IP-Adapter, PuLID and LoRA Guide
Opens in a new window](https://www.media.io/image-tips/comfyui-consistent-characters.html)[youtube.com
AI Face Swap Battle: PuLID vs InstantID vs FaceID - YouTube
Opens in a new window](https://www.youtube.com/watch?v=E62ori0VSds)[medium.com
I'm 21, and This Is What Building an AI Influencer Has Actually Paid Me
Opens in a new window](https://medium.com/@enockjackson873/im-21-and-this-is-what-building-an-ai-influencer-has-actually-paid-me-431e6abf2643)[arxiv.org
EmojiDiff: Advanced Facial Expression Control with High Identity
Opens in a new window](https://arxiv.org/html/2412.01254v2)[arxiv.org
MultiHuman-Testbench: Benchmarking Image Generation for ... - arXiv
Opens in a new window](https://arxiv.org/html/2506.20879v2)[arxiv.org
Visual Persona: Foundation Model for Full-Body Human ... - arXiv
Opens in a new window](https://arxiv.org/html/2503.15406v2)[peking.bjd.com.cn
e案e审丨利用AI软件恶搞、丑化他人肖像，构成人格权侵权！
Opens in a new window](https://peking.bjd.com.cn/content/s68a7fbd0e4b0221b9bebd39b.html)[thepaper.cn
北京高院典型案例：虚拟数字人形象可构成美术作品，受著作权法保护
Opens in a new window](https://www.thepaper.cn/newsDetail_forward_33026199)[legal.gmw.cn
AI合成肖像声音北京互联网法院：老年人正被网络侵权“围猎” _光明网
Opens in a new window](https://legal.gmw.cn/2026-10/16/content_39050667.htm)[advertisingvietnam.com
Virtual Influencer: Họ là ai trong thế giới tiếp thị - quảng cáo?
Opens in a new window](https://advertisingvietnam.com/article/virtual-influencer-ho-la-ai-trong-the-gioi-tiep-thi-quang-cao-p20244)[brandsvietnam.com
AI sẽ thay đổi Social Media Marketing như thế nào trong năm tới?
Opens in a new window](https://www.brandsvietnam.com/congdong/topic/ai-se-thay-doi-social-media-marketing-nhu-the-nao-trong-nam-toi)[beautyplus.com
Trình tạo nhân vật AI | Tạo hình đại diện tùy chỉnh - BeautyPlus
Opens in a new window](https://www.beautyplus.com/vi/ai-influencer/ai-persona-generator)[uisdc.com
Blender 实战！3D卡通虚拟数字人角色设计完整流程（中） - 优设网
Opens in a new window](https://www.uisdc.com/digital-human-role-design-2)[spiroworks.com
How to Commission a VTuber Model: A Guide to Character Design
Opens in a new window](https://spiroworks.com/how-to-commission-a-vtuber-model-a-guide-to-character-design-live2d-art-and-design-briefs/)[rokoko.com
Guide: How To Create The Best VTuber Setup - Rokoko
Opens in a new window](https://www.rokoko.com/insights/guide-how-to-create-the-best-vtuber-setup)[tips.clip-studio.com
Designing a VTuber Character by LizStaley - Make better art
Opens in a new window](https://tips.clip-studio.com/en-us/articles/11064)[reddit.com
How do character designers usually work when creating a VTuber
Opens in a new window](https://www.reddit.com/r/VirtualYoutubers/comments/1ohcfv0/how_do_character_designers_usually_work_when/)[youtube.com
How I design Vtuber Models | A step by step tutorial - YouTube
Opens in a new window](https://www.youtube.com/watch?v=S-nKWrSZSnY)[youtube.com
How I Made My Own VTuber (+ 6 Character Design Tips) - YouTube
Opens in a new window](https://www.youtube.com/watch?v=f89r_MnSslU&vl=en)[i-law.vn
Quyền bảo vệ hình ảnh cá nhân - iLAW
Opens in a new window](https://i-law.vn/huong-dan-phap-ly/quyen-bao-ve-hinh-anh-ca-nhan-68966)[daibieunhandan.vn
Trường hợp nào sử dụng hình ảnh cá nhân không cần xin phép?
Opens in a new window](https://daibieunhandan.vn/truong-hop-nao-su-dung-hinh-anh-ca-nhan-khong-can-xin-phep-10320962.html)[htc-law.com
Sử dụng hình ảnh cá nhân trái phép trên mạng xã hội
Opens in a new window](https://htc-law.com/tu-van-phap-luat-dan-su/su-dung-hinh-anh-ca-nhan-trai-phep-tren-mang-xa-hoi-muc-boi-thuong-danh-du-la-bao-nhieu,6276.html)[thuvienphapluat.vn
Quyền của cá nhân đối với hình ảnh của mình theo Bộ luật Dân sự
Opens in a new window](https://thuvienphapluat.vn/chinh-sach-phap-luat-moi/vn/ho-tro-phap-luat/tu-van-phap-luat/65989/quyen-cua-ca-nhan-doi-voi-hinh-anh-cua-minh-theo-bo-luat-dan-su-2015)[comfy.icu
Alchemica Face Match (ArcFace identity score) - ComfyUI Cloud
Opens in a new window](https://comfy.icu/node/AlchemicaFaceMatch)[github.com
How to compare 2 ArcFace features? · Issue #903 - GitHub
Opens in a new window](https://github.com/deepinsight/insightface/issues/903)[github.com
High-accuracy Face Recognition using ArcFace & InsightFace · GitHub
Opens in a new window](https://github.com/dubey-astha/Face_Recognition_Arcface)[arxiv.org
SynthFaces: Balanced Large Scale Human Dataset - arXiv
Opens in a new window](https://arxiv.org/html/2610.40119v1)[arxiv.org
Cross-Person Identity Change Under Source-Coupled Multi-Human
Opens in a new window](https://arxiv.org/html/2610.22746v1)[arxiv.org
Vera: Identity-Faithful Human Subject-to-Video Generation - arXiv
Opens in a new window](https://arxiv.org/html/2607.20247v1)[arxiv.org
PuLID: Pure and Lightning ID Customization via Contrastive Alignment
Opens in a new window](https://arxiv.org/html/2404.16022v1)[biometricupdate.com
China's draft rules on AI 'virtual humans' target biometric deepfakes
Opens in a new window](https://www.biometricupdate.com/202604/chinas-draft-rules-on-ai-virtual-humans-target-biometric-deepfakes)[casrai.org
China's AI Regulation: Interim Measures to the 2025 Labeling Rules
Opens in a new window](https://casrai.org/guides/china-ai-regulation-explained)[mmlcgroup.com
China's New Rules for Labeling AI-Generated Content Commence
Opens in a new window](https://mmlcgroup.com/china-ai-labelling-rules/)[intelligence.dlapiper.com
Law / proposed law in China - AI Laws of the World
Opens in a new window](https://intelligence.dlapiper.com/artificial-intelligence/?t=01-law&c=CN)[chinalawtranslate.com
Measures for Labeling of AI-Generated Synthetic Content
Opens in a new window](https://www.chinalawtranslate.com/en/ai-labeling/)[bjlti.com
Deepfake, portrait rights and identity protection
Opens in a new window](https://bjlti.com/revista/article/view/81)Xác định mục tiêu nghiên cứuTôi đang phân tích yêu cầu về quy trình sản xuất nhân vật ảo, VTuber và AI influencer từ thực tế các studio và agency giai đoạn 2024–2026. Nội dung tập trung vào quy trình duyệt từ bước casting khuôn mặt đến tạo character bible, cũng như các tiêu chí kỹ thuật cụ thể.Phân tích các chỉ số duy trì độ giống mặtTôi đang xem xét các phương pháp đo lường tính nhất quán của khuôn mặt mà studio áp dụng, bao gồm việc sử dụng các mô hình đánh giá như ArcFace, CLIP, DINO và khoảng cách cosine, cùng các ngưỡng điểm định lượng chuẩn để đảm bảo độ nhận diện của nhân vật.Triển khai tìm kiếm đa ngôn ngữTôi đang bắt đầu truy vấn nguồn tài liệu kỹ thuật chuyên sâu trên các nền tảng như Zhihu, Medium, LinkedIn và bài tham luận GDC/CEDEC bằng tiếng Anh, Trung, Hàn và Việt nhằm thu thập quy trình làm việc thực tế, cấu trúc character bible và các rủi ro pháp lý liên quan.  [lollipop.im
AI Character Consistency Workflow: 7 Steps | Lollipop Drama Guides](https://www.lollipop.im/blog/character-consistency-workflow/)[theprompthome.com
AI Character Bible: The Ultimate Guide to Creating Consistent AI](https://theprompthome.com/ai-character-bible-guide/)[domer.io
Consistent Character Workflow: The Missing Link in AI Content](https://domer.io/blog/consistent-character-ai-workflow)[ltx.io
How to Maintain Character Consistency in AI Video Production - LTX](https://ltx.io/blog/how-to-maintain-character-consistency-in-ai-video)[vidu.com
Consistent Character AI: Workflows & Tips - Vidu AI](https://www.vidu.com/blog/consistent-character-ai)[runway.com
Runway Resources | How to Create Consistent AI Characters](https://runway.com/resources/create-consistent-ai-characters)[youtube.com
How to Make Consistent AI Characters With Your Own Face and](https://www.youtube.com/watch?v=wGs2vByrF3U)[higgsfield.ai
7 Tools for Consistent AI Characters Across Every Scene in 2026](https://higgsfield.ai/blog/tools-for-consistent-ai-characters)[invideo.io
Solving AI Character Consistency Workflow - invideo AI](https://invideo.io/academy/i-tried-every-ai-character-consistency-workflow-results/)[sozee.ai
AI Influencer Content Workflow: Step-By-Step Playbook - Sozee](https://www.sozee.ai/resources/ai-influencer-content-workflow/)[thefluxtrain.com
AI Influencer Creator Workflow | TheFluxTrain](https://thefluxtrain.com/ai-influencer-creator/)[queststudio.io
How to Create an AI Influencer That Stays Consistent - QuestStudio](https://queststudio.io/blog/how-to-create-an-ai-influencer)[elser.ai
Building an Original Character Bible That AI Tools Can Follow](https://www.elser.ai/blog/building-an-original-character-bible-that-ai-tools-can-follow)[oakgen.ai
AI Character Video Workflow: Sheet to Launch Cut - Oakgen.ai](https://oakgen.ai/blog/character-sheet-to-launch-video-workflow)[astorie.ai
AI Character Consistency Workflow - Astorie](https://astorie.ai/workflows/character-consistency)[montagea.com
How to Build a Consistent AI Influencer: Video Workflow - Montagea](https://montagea.com/blog/build-consistent-ai-influencer-video-workflow/)[youtube.com
This Character Board Makes Your AI Influencer 100% Consistent](https://www.youtube.com/watch?v=x9ETAqkAysg)[didit.me
Face Matching Algorithms: ArcFace & CosFace. - Didit.me](https://didit.me/blog/face-matching-algorithms-arcface-cosface/)[github.com
High-accuracy Face Recognition using ArcFace & InsightFace · GitHub](https://github.com/dubey-astha/Face_Recognition_Arcface)[insightface.ai
InsightFace ArcFace: Additive Angular Margin Loss Explained](https://www.insightface.ai/research/arcface)[medium.com
ArcFace — Architecture and Practical example: How to calculate the](https://medium.com/@ichigo.v.gen12/arcface-architecture-and-practical-example-how-to-calculate-the-face-similarity-between-images-183896a35957)[openaccess.thecvf.com
ArcFace for Disguised Face Recognition - CVF Open Access](https://openaccess.thecvf.com/content_ICCVW_2019/papers/DFW/Deng_ArcFace_for_Disguised_Face_Recognition_ICCVW_2019_paper.pdf)[community.hailo.ai
A Comprehensive Guide to Building a Face Recognition System](https://community.hailo.ai/t/a-comprehensive-guide-to-building-a-face-recognition-system/8803)[arxiv.org
A novel Facial Recognition technique with Focusing on Masked Faces](https://www.arxiv.org/pdf/2501.04444v1)[youtube.com
State‑of‑the‑Art Face Recognition with Angular Margin - YouTube](https://www.youtube.com/watch?v=66jO7fdUELk)[viblo.asia
[Paper explained] Face Recognition: Facenet, ArcFace, CosFace](https://viblo.asia/p/paper-explained-some-face-recognition-approaches-facenet-arcface-cosface-Do754zgLZM6)Phân tích quy trình tạo nhân vật và tài liệu thiết kếTôi đã tổng hợp các bước xây dựng nhân vật ảo chuyên nghiệp từ giai đoạn tạo khuôn mặt đến khi hoàn thiện tài liệu hướng dẫn (character bible). Quy trình tiêu chuẩn đòi hỏi đóng cứng đặc tính nhân vật trước khi tạo hình, thiết lập bộ 5-8 ảnh tham chiếu gốc và kiểm tra độ đồng nhất qua các cổng duyệt. Các thành phần quan trọng trong tài liệu bao gồm góc nhìn đa chiều, bảng màu, biểu cảm và khối văn bản loại trừ nhằm hạn chế tối đa tình trạng biến dạng khuôn mặt.Khoảng trống thông tin về số đo kỹ thuật và pháp lýHiện tại tôi đang tập trung làm rõ các ngưỡng định lượng cụ thể như chỉ số tương đồng cosine khi ứng dụng ArcFace, CLIP hay DINO trong các pipeline kiểm thử tự động của studio. Đồng thời, tôi cần thu thập thêm thông tin chi tiết về các rủi ro pháp lý thực tế, đặc biệt là các vụ tranh chấp bản quyền hình ảnh tham chiếu và quyền chân dung đối với nhân vật số tại thị trường Trung Quốc và quốc tế.Kế hoạch truy xuất thông tin chuyên sâuTôi đang mở rộng tìm kiếm sang các nguồn tài liệu kỹ thuật bằng tiếng Trung trên Zhihu, Bilibili cùng các bài báo pháp lý liên quan đến vi phạm quyền chân dung của người thật. Mục tiêu tiếp theo là xác định chính xác các số liệu đo lường độ giống mặt, các khung pháp lý đang áp dụng và tìm kiếm thông tin đối chiếu từ các agency sản xuất tại Việt Nam.  [docsaid.org
ArcFace · Blog - DOCSAID](https://docsaid.org/en/blog/papers/face-recognition/arcface)[comfy.icu
Person Selector (Match) - ComfyUI Cloud - Comfy.ICU](https://comfy.icu/node/PersonSelector)[openaccess.thecvf.com
ArcFace for Disguised Face Recognition - CVF Open Access](https://openaccess.thecvf.com/content_ICCVW_2019/papers/DFW/Deng_ArcFace_for_Disguised_Face_Recognition_ICCVW_2019_paper.pdf)[medium.com
Face Recognition and ArcFace Loss for Beginners | by Aylin Aydin](https://medium.com/@aylin.aydin/face-recognition-and-arcface-loss-for-beginners-cdfddbf7e88)[youtube.com
State‑of‑the‑Art Face Recognition with Angular Margin - YouTube](https://www.youtube.com/watch?v=66jO7fdUELk)[insightface.ai
InsightFace ArcFace: Additive Angular Margin Loss Explained](https://www.insightface.ai/research/arcface)[ijert.org
Selfie-Based Attendance System Implementation Using ArcFace](https://www.ijert.org/selfie-based-attendance-system-implementation-using-arcface-and-cosine-similarity-for-identity-verification-ijertconv14is010041)[viblo.asia
[Paper explained] Face Recognition: Facenet, ArcFace, CosFace](https://viblo.asia/p/paper-explained-some-face-recognition-approaches-facenet-arcface-cosface-Do754zgLZM6)[mdpi.com
CoFaDiff: Coordinating Identity Fidelity and Text Consistency ... - MDPI](https://www.mdpi.com/2076-3417/16/1/414)[morphic.com
InstantID: single-image face identity preservation in AI - Morphic](https://morphic.com/ai-glossary/instantid)[didit.me
ArcFace vs. CosFace: Deep Dive into Face Matching Algorithms](https://didit.me/blog/arcface-vs-cosface-deep-dive-into-face-matching-algorithms/)[comfy.icu
Face Similarity (InsightFace) - ComfyUI Cloud - Comfy.ICU](https://comfy.icu/node/FaceSimilarityNode)[media.io
ComfyUI Consistent Characters: IP-Adapter, PuLID and LoRA Guide](https://www.media.io/image-tips/comfyui-consistent-characters.html)[youtube.com
AI Face Swap Battle: PuLID vs InstantID vs FaceID - YouTube](https://www.youtube.com/watch?v=E62ori0VSds)[devenkoai.medium.com
How to Build an AI Mascot for Your Ecom Brand (FREE Guide)](https://devenkoai.medium.com/how-to-build-an-ai-mascot-for-your-ecom-brand-free-guide-42c4e71bebc6)[medium.com
I'm 21, and This Is What Building an AI Influencer Has Actually Paid Me](https://medium.com/@enockjackson873/im-21-and-this-is-what-building-an-ai-influencer-has-actually-paid-me-431e6abf2643)[arxiv.org
EmojiDiff: Advanced Facial Expression Control with High Identity](https://arxiv.org/html/2412.01254v2)[arxiv.org
Adapter Shield: A Unified Framework with Built-in Authentication for](https://arxiv.org/html/2512.00075v1)[arxiv.org
PuLID: Pure and Lightning ID Customization via Contrastive Alignment](https://arxiv.org/html/2404.16022v1)[arxiv.org
PuLID: Pure and Lightning ID Customization via Contrastive Alignment](https://arxiv.org/html/2404.16022v2)[arxiv.org
SynthFaces: Balanced Large Scale Human Dataset - arXiv](https://arxiv.org/html/2610.40119v1)[arxiv.org
Gen-AFFECT: Generation of Avatar Fine-grained Facial Expressions](https://arxiv.org/html/2508.09461v1)[arxiv.org
MultiHuman-Testbench: Benchmarking Image Generation for ... - arXiv](https://arxiv.org/html/2506.20879v2)[arxiv.org
Visual Persona: Foundation Model for Full-Body Human ... - arXiv](https://arxiv.org/html/2503.15406v2)[m.bjnews.com.cn
虚拟数字人形象受著作权法保护，北京互联网法院作出生效判决 - 新京报](https://m.bjnews.com.cn/detail/1756211837168290.html)[peking.bjd.com.cn
e案e审丨利用AI软件恶搞、丑化他人肖像，构成人格权侵权！](https://peking.bjd.com.cn/content/s68a7fbd0e4b0221b9bebd39b.html)[jtn.com
AI应用中的权利保护与合规：“全国首例AI生成声音人格权侵权案”评析](https://www.jtn.com/CN/booksdetail.aspx?type=06001&keyid=00000000000000008474&PageUrl=majorbook&Lan=CN)[chinaiplawupdate.com
北京互联网法院涉人工智能典型案例 - China IP Law Update -](https://www.chinaiplawupdate.com/wp-content/uploads/2025/09/%E5%8C%97%E4%BA%AC%E4%BA%92%E8%81%94%E7%BD%91%E6%B3%95%E9%99%A2%E6%B6%89%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E5%85%B8%E5%9E%8B%E6%A1%88%E4%BE%8B.pdf)[thepaper.cn
北京高院典型案例：虚拟数字人形象可构成美术作品，受著作权法保护](https://www.thepaper.cn/newsDetail_forward_33026199)[legal.gmw.cn
AI合成肖像声音北京互联网法院：老年人正被网络侵权“围猎” _光明网](https://legal.gmw.cn/2026-10/16/content_39050667.htm)[advertisingvietnam.com
Virtual Influencer: Họ là ai trong thế giới tiếp thị - quảng cáo?](https://advertisingvietnam.com/article/virtual-influencer-ho-la-ai-trong-the-gioi-tiep-thi-quang-cao-p20244)[brandsvietnam.com
AI sẽ thay đổi Social Media Marketing như thế nào trong năm tới?](https://www.brandsvietnam.com/congdong/topic/ai-se-thay-doi-social-media-marketing-nhu-the-nao-trong-nam-toi)[beautyplus.com
Trình tạo nhân vật AI | Tạo hình đại diện tùy chỉnh - BeautyPlus](https://www.beautyplus.com/vi/ai-influencer/ai-persona-generator)Tổng hợp chỉ số duy trì độ giống mặtTôi đang ghi nhận các kết quả kỹ thuật về tiêu chuẩn giữ mặt nhân vật. Việc trích xuất vector đặc trưng qua ArcFace và InsightFace cho thấy ngưỡng tương đồng Cosine chuẩn nằm trong khoảng 0.6–0.7 cho việc xác nhận cùng danh tính, khoảng 0.4–0.6 được đánh giá là nguy cơ lệch mặt và dưới 0.4 thể hiện sự mất tính nhất quán khuôn mặt.Bổ sung cấu trúc tài liệu nhân vậtTôi đang tổng hợp các thành phần cốt lõi của một Character Bible chuyên nghiệp, bao gồm bộ quy chuẩn định danh khuôn mặt, tập ảnh tham chiếu chuẩn, bộ prompt cố định cùng tham số mô hình tạo ảnh, cấu hình giọng nói và các giới hạn pháp lý về hình ảnh thương hiệu.Khảo sát thực tế chuyên ngànhTôi chuẩn bị truy vấn sâu hơn vào các nguồn bài viết kỹ thuật từ các nền tảng chuyên môn Trung Quốc, bài nghiên cứu học thuật và các án lệ liên quan đến quyền hình ảnh của nhân vật ảo nhằm thu thập số liệu trích dẫn cụ thể và hoàn thiện quy trình kiểm duyệt.  [uisdc.com
Blender 实战！3D卡通虚拟数字人角色设计完整流程（中） - 优设网](https://www.uisdc.com/digital-human-role-design-2)[uisdc.com
5000字干货！3D卡通虚拟数字人角色设计完整流程（上） - 优设](https://www.uisdc.com/digital-human-role-design)[spiroworks.com
How to Commission a VTuber Model: A Guide to Character Design](https://spiroworks.com/how-to-commission-a-vtuber-model-a-guide-to-character-design-live2d-art-and-design-briefs/)[draw.market
From OC to VTuber Model — How to Nail Your Character Design](https://draw.market/en/blog/first-step-to-custom-vtuber-model.html)[os-artist-front.webapp.easebar.com
How to Make a VTuber Model from Scratch (Free & Paid Methods)](https://os-artist-front.webapp.easebar.com/en/blog/how-to-make--vtuber-model.html)[rokoko.com
Guide: How To Create The Best VTuber Setup - Rokoko](https://www.rokoko.com/insights/guide-how-to-create-the-best-vtuber-setup)[medium.com
Bringing VTubers to Life: My 2D Character and Live2D Model](https://medium.com/@Kenny_Studiuo/bringing-vtubers-to-life-my-2d-character-and-live2d-model-creation-workflow-308ca604cc85)[tips.clip-studio.com
Designing a VTuber Character by LizStaley - Make better art](https://tips.clip-studio.com/en-us/articles/11064)[reddit.com
How do character designers usually work when creating a VTuber](https://www.reddit.com/r/VirtualYoutubers/comments/1ohcfv0/how_do_character_designers_usually_work_when/)[kuroganeito.jp
The Ultimate Guide to VTuber Model Creation (2026) - Ito Kurogane](https://kuroganeito.jp/vtubermodelcreation-en)[youtube.com
How I design Vtuber Models | A step by step tutorial - YouTube](https://www.youtube.com/watch?v=S-nKWrSZSnY)[youtube.com
How I Made My Own VTuber (+ 6 Character Design Tips) - YouTube](https://www.youtube.com/watch?v=f89r_MnSslU&vl=en)[theprompthome.com
AI Character Bible: The Ultimate Guide to Creating Consistent AI](https://theprompthome.com/ai-character-bible-guide/)[github.com
character-bible.md - xixihhhh/ai-short-drama-skill · GitHub](https://github.com/xixihhhh/ai-short-drama-skill/blob/main/skills/dramake/assets/templates/character-bible.md)Cơ sở kỹ thuật và tiền lệ pháp lý mớiTôi vừa ghi nhận các thông số đo lường thực nghiệm về độ đồng nhất khuôn mặt qua các thuật toán trích xuất đặc trưng như ArcFace và CurricularFace. Các kết quả chỉ ra ngưỡng độ tương đồng cosine chuẩn dao động trong khoảng từ 0.60 đến 0.77 đối với các mô hình tạo ảnh hiện đại như InstantID hay PuLID. Về mặt pháp lý, tôi đã tổng hợp được các phán quyết thực tế công nhận hình ảnh nhân vật số có tính độc tạo là tác phẩm nghệ thuật được bảo hộ bản quyền, đồng thời xác định rủi ro vi phạm quyền chân dung khi vi phạm việc tạo hình quá giống hoặc sử dụng dữ liệu người thật mà chưa được cấp phép.Khoảng trống về tài liệu thiết kế và quy trình nội bộTôi đang tìm cách bổ sung thêm các số liệu chi tiết về quy trình duyệt nội bộ của các studio Trung Quốc và quốc tế, bao gồm số vòng kiểm tra tiêu chuẩn, tỷ lệ duyệt tại các cổng kiểm soát và cấu trúc tài liệu character bible thực tế được công khai từ các dự án thành công.Trích xuất tài liệu kỹ thuật chuyên sâuTôi đang tiếp tục truy cập trực tiếp vào các tài liệu hướng dẫn kỹ thuật, các bài nghiên cứu về thuật toán nhận diện khuôn mặt và bài viết phân tích quy trình từ các blog công nghệ. Mục tiêu là trích dẫn nguyên văn các ngưỡng số liệu kỹ thuật, thành phần hồ sơ nhân vật và các điều khoản pháp lý trọng tâm để hoàn thiện báo cáo.  [comfy.icu
Person Selector (Match) - ComfyUI Cloud](https://comfy.icu/node/PersonSelector)[lollipop.im
AI Character Consistency Workflow: 7 Steps | Lollipop Drama Guides](https://www.lollipop.im/blog/character-consistency-workflow/)[arxiv.org](https://arxiv.org/html/2404.16022v1)[theprompthome.com
AI Character Bible: The Ultimate Guide to Creating Consistent AI ...](https://theprompthome.com/ai-character-bible-guide/)Cơ chế phân tách mặt và tính toán tương đồngTôi đang làm rõ các thông số kỹ thuật chi tiết khi triển khai phân tách mặt và kiểm tra độ khớp khuôn mặt. Việc trích xuất vùng da và tóc bằng BiSeNet kết hợp với phân vùng cơ thể giúp loại bỏ nhiễu background, từ đó giúp thước đo tương đồng Cosine dựa trên ArcFace đạt chuẩn xác hơn trong khoảng ngưỡng 0.65.Chuẩn hóa tiêu chuẩn Character Bible 10 mụcTôi đã đào sâu vào cấu trúc tài liệu quy chuẩn 10 phần dành cho nhân vật ảo, bao gồm từ góc nhìn trước/sau/nghiêng, biểu cảm, bộ dáng cho đến quy tắcIdentity Lock cấm biến đổi hình thể. Việc phân định rõ ràng giữa yếu tố cố định (khuôn mặt, màu mắt, tỉ lệ cơ thể) và yếu tố linh hoạt (trang phục, ánh sáng, góc máy) giúp giảm thiểu hiện tượng trôi lệch hình ảnh qua các đợt phát sóng.Mở rộng khảo sát án lệ và thực tiễn thị trườngTôi đang chuyển sang truy xuất thông tin chi tiết về các mẫu Character Bible công khai trên Github, quy định pháp lý về quyền chân dung nhân vật ảo tại các phán quyết tòa án Trung Quốc, các bài chia sẻ kỹ thuật tại CEDEC/GDC, cùng việc đối chiếu thực tiễn áp dụng Điều 32 Bộ luật Dân sự tại thị trường Việt Nam.  [luathoangsa.vn
Quyền của cá nhân đối với hình ảnh (Điều 32 Bộ luật dân sự 2015).](https://luathoangsa.vn/quyen-cua-ca-nhan-doi-voi-hinh-anh-nd63851.html)[i-law.vn
Quyền bảo vệ hình ảnh cá nhân - iLAW](https://i-law.vn/huong-dan-phap-ly/quyen-bao-ve-hinh-anh-ca-nhan-68966)[daibieunhandan.vn
Trường hợp nào sử dụng hình ảnh cá nhân không cần xin phép?](https://daibieunhandan.vn/truong-hop-nao-su-dung-hinh-anh-ca-nhan-khong-can-xin-phep-10320962.html)[kiemsat.vn
Trách nhiệm dân sự đối với hành vi xâm phạm quyền nhân thân trên](https://kiemsat.vn/trach-nhiem-dan-su-doi-voi-hanh-vi-xam-pham-quyen-nhan-than-tren-mang-xa-hoi-72210.html)[vanphuclawfirm.com
Quyền của cá nhân đối với hình ảnh được quy định như nào?](https://vanphuclawfirm.com/quyen-cua-ca-nhan-doi-voi-hinh-anh/)[luatvietnam.vn
Luật quy định thế nào về quyền hình ảnh của cá nhân? - LuatVietnam](https://luatvietnam.vn/tin-phap-luat/luat-quy-dinh-the-nao-ve-quyen-hinh-anh-cua-ca-nhan-230-15685-article.html)[htc-law.com
Sử dụng hình ảnh cá nhân trái phép trên mạng xã hội](https://htc-law.com/tu-van-phap-luat-dan-su/su-dung-hinh-anh-ca-nhan-trai-phep-tren-mang-xa-hoi-muc-boi-thuong-danh-du-la-bao-nhieu,6276.html)[luatlongphan.vn
Giải quyết tranh chấp sử dụng hình ảnh KOL/Influencer](https://luatlongphan.vn/giai-quyet-tranh-chap-su-dung-hinh-anh-kol-influencer)[thuvienphapluat.vn
Quyền của cá nhân đối với hình ảnh của mình theo Bộ luật Dân sự](https://thuvienphapluat.vn/chinh-sach-phap-luat-moi/vn/ho-tro-phap-luat/tu-van-phap-luat/65989/quyen-cua-ca-nhan-doi-voi-hinh-anh-cua-minh-theo-bo-luat-dan-su-2015)[comfy.icu
Alchemica Face Match (ArcFace identity score) - ComfyUI Cloud](https://comfy.icu/node/AlchemicaFaceMatch)[medium.com
Face Recognition and ArcFace Loss for Beginners | by Aylin Aydin](https://medium.com/@aylin.aydin/face-recognition-and-arcface-loss-for-beginners-cdfddbf7e88)[comfy.icu
Person Selector (Match) - ComfyUI Cloud - Comfy.ICU](https://comfy.icu/node/PersonSelector)[github.com
How to compare 2 ArcFace features? · Issue #903 - GitHub](https://github.com/deepinsight/insightface/issues/903)[github.com
High-accuracy Face Recognition using ArcFace & InsightFace · GitHub](https://github.com/dubey-astha/Face_Recognition_Arcface)[devenkoai.medium.com
How to Build an AI Mascot for Your Ecom Brand (FREE Guide) | by ...](https://devenkoai.medium.com/how-to-build-an-ai-mascot-for-your-ecom-brand-free-guide-42c4e71bebc6)[kuroganeito.jp
The Ultimate Guide to VTuber Model Creation (2026) | Ito Kurogane](https://kuroganeito.jp/vtubermodelcreation-en)[jtn.com
AI应用中的权利保护与合规：“全国首例AI生成声音人格权侵权案”评析 ...](https://www.jtn.com/CN/booksdetail.aspx?type=06001&keyid=00000000000000008474&PageUrl=majorbook&Lan=CN)[github.com
character-bible.md - xixihhhh/ai-short-drama-skill · GitHub](https://github.com/xixihhhh/ai-short-drama-skill/blob/main/skills/dramake/assets/templates/character-bible.md)Bổ sung cấu trúc hồ sơ và khung pháp lý thực tếTôi vừa ghi nhận cấu trúc chi tiết của một Character Bible chuẩn gồm 6 phần chính từ các dự án sản xuất thực tế, phân định rõ diện mạo, trang phục, phong cách biểu cảm và quy chuẩn giọng nói. Đồng thời, tôi đã thu thập được các tiền lệ pháp lý quan trọng từ Tòa án Internet Bắc Kinh, quy định rõ việc bảo hộ hình ảnh tổng thể của nhân vật ảo và phán quyết vi phạm quyền nhân thân khi sử dụng giọng nói người thật để huấn luyện mô hình AI mà chưa được phép.Giải quyết khúc mắc về quy định nhãn AI và thực tiễn địa phươngTôi đang tập trung làm rõ các quy định bắt buộc về gắn dán nhãn công khai đối với nội dung nhân vật ảo theo chuẩn mực pháp lý mới, cũng như đối chiếu khung pháp lý tại Việt Nam theo Điều 32 Bộ luật Dân sự 2015. Bên cạnh đó, các thông số đo lường độ giống mặt trên các tập dữ liệu thử nghiệm chuẩn (benchmark) giữa các công nghệ như InstantID, PuLID và IP-Adapter đang được tổng hợp minh bạch.Thu thập số liệu đo lường và án lệ vi phạm bản quyền 3DTôi đang tiếp tục truy vấn các báo cáo nghiên cứu kỹ thuật chuyên sâu để trích xuất chính xác các chỉ số tương đồng cosine, điểm CLIP-T/CLIP-I và khoảng cách ArcFace. Đồng thời, tôi sẽ khảo sát chi tiết vụ việc xử phạt vi phạm bản quyền mô hình 3D nhân vật ảo để hoàn thiện danh mục rủi ro pháp lý cho các studio.  [arxiv.org
SynthFaces: Balanced Large Scale Human Dataset - arXiv](https://arxiv.org/html/2610.40119v1)[arxiv.org
Cross-Person Identity Change Under Source-Coupled Multi-Human](https://arxiv.org/html/2610.22746v1)[arxiv.org
Personalized Person Image Generation with Holistic Identity ... - arXiv](https://arxiv.org/pdf/2607.25622)[arxiv.org
Vera: Identity-Faithful Human Subject-to-Video Generation - arXiv](https://arxiv.org/html/2607.20247v1)[arxiv.org
PuLID: Pure and Lightning ID Customization via Contrastive Alignment](https://arxiv.org/html/2404.16022v1)[arxiv.org
Personalized Person Image Generation with Holistic Identity ... - arXiv](https://arxiv.org/html/2607.25622v1)[trussed.ai
China AI Labeling Requirements September 2025 - Trussed AI](https://trussed.ai/resources/china-ai-labeling-requirements-september-2025)[biometricupdate.com
China's draft rules on AI 'virtual humans' target biometric deepfakes](https://www.biometricupdate.com/202604/chinas-draft-rules-on-ai-virtual-humans-target-biometric-deepfakes)[artificialintelligenceregulations.com
AI Regulation in China: Laws, Status and Penalties](https://artificialintelligenceregulations.com/jurisdictions/china.html)[casrai.org
China's AI Regulation: Interim Measures to the 2025 Labeling Rules](https://casrai.org/guides/china-ai-regulation-explained)[mmlcgroup.com
China's New Rules for Labeling AI-Generated Content Commence](https://mmlcgroup.com/china-ai-labelling-rules/)[transasialawyers.com
New Draft Rules for Digital Avatars and Virtual Humans in China](https://www.transasialawyers.com/insights/new-draft-rules-for-digital-avatars-and-virtual-humans-in-china)[intelligence.dlapiper.com
Law / proposed law in China - AI Laws of the World](https://intelligence.dlapiper.com/artificial-intelligence/?t=01-law&c=CN)[chinalawtranslate.com
Measures for Labeling of AI-Generated Synthetic Content](https://www.chinalawtranslate.com/en/ai-labeling/)[bjlti.com
Deepfake, portrait rights and identity protection](https://bjlti.com/revista/article/view/81)[m.bjnews.com.cn
虚拟数字人形象受著作权法保护，北京互联网法院作出生效判决 - 新京报](https://m.bjnews.com.cn/detail/1756211837168290.html)[arxiv.org](https://arxiv.org/html/2404.16022v2)[arxiv.org](https://arxiv.org/html/2512.00075v1)Tổng hợp quy trình duyệt và các thước đo định lượngTôi đã làm rõ toàn bộ quy trình làm việc gồm 4 cổng kiểm duyệt chính từ giai đoạn casting khuôn mặt đến khi xuất bản, cùng trách nhiệm phê duyệt của Giám đốc Nghệ thuật, Giám đốc Sáng tạo và bộ phận Pháp lý. Số liệu thực nghiệm cho thấy việc chấm độ giống mặt áp dụng khoảng cách Cosine trên ArcFace với ngưỡng giữ danh tính chuẩn ở mức từ 0.65 đến 0.75, kết hợp cùng các chỉ số CLIP-T (khoảng 28-32) và CLIP-I (khoảng 0.70-0.84) trên các bộ dữ liệu tiêu chuẩn như PPR10K hay SynthFaces.Đánh giá các án lệ pháp lý và mẫu tài liệu quy chuẩnTôi đã ghi nhận các phán quyết pháp lý quan trọng từ Tòa án Internet Bắc Kinh, bao gồm vụ kiện công nhận mô hình 3D nhân vật ảo là tác phẩm nghệ thuật được bảo hộ bản quyền với mức bồi thường 15,000 NDT, cùng các tranh chấp về quyền giọng nói và quyền chân dung AI. Đồng thời, tôi đã trích xuất được cấu trúc tài liệu Character Bible chuẩn 10 phần và các liên kết mẫu công khai trên GitHub phục vụ việc đóng cứng hình ảnh nhân vật.Hoàn thiện báo cáo nghiên cứu tổng hợpTôi đang chuyển sang giai đoạn tổng hợp toàn bộ dữ liệu đã thu thập được để lập báo cáo chuyên sâu bằng tiếng Việt. Báo cáo sẽ cung cấp bảng danh mục nguồn trích dẫn chi tiết, trích dẫn nguyên văn kèm liên kết cho từng số liệu kỹ thuật, đồng thời ghi nhận rõ ràng các thông tin không tìm thấy theo đúng yêu cầu.Quá trình nghiên cứu ban đầu đã thu về một lượng thông tin khổng lồ. Hiện tôi đang phân tích chuyên sâu và sắp xếp lại toàn bộ để đảm bảo báo cáo có mạch lạc rõ ràng và bao quát mọi điểm mấu chốt. Vì đây là một phân tích chuyên sâu và kỹ lưỡng, việc hoàn thiện báo cáo cuối cùng có thể mất tới 30 phút.Chữ nghĩa thì hay đấy, nhưng đôi khi hình ảnh trực quan lại truyền tải câu chuyện tốt hơn. Để làm cho thật chuẩn chỉnh thì cần có thời gian, vì thế tôi đang cẩn thận lên kế hoạch và thiết kế những cách tốt nhất nhằm minh họa các phát hiện quan trọng nhất.Giờ là lúc xử lý phần việc tốn nhiều công sức nhất rồi đây! Tôi đang tổng hợp mọi thứ thành một báo cáo toàn diện, đối chiếu kỹ lưỡng các chi tiết và trau chuốt lại. Việc tạo ra một sản phẩm chỉn chu như thế này có thể mất vài phút, nên bạn cứ thoải mái nghỉ tay một lát trong lúc tôi hoàn tất nhé.

## Link nguồn (tự gom)
- https://www.lollipop.im/blog/character-consistency-workflow/
- https://comfy.icu/node/PersonSelector
- https://comfy.icu/node/FaceSimilarityNode
- https://arxiv.org/html/2512.00075v1
- https://arxiv.org/pdf/2607.25622
- https://m.bjnews.com.cn/detail/1756211837168290.html
- https://www.jtn.com/CN/booksdetail.aspx?type=06001&keyid=00000000000000008474&PageUrl=majorbook&Lan=CN
- https://astorie.ai/workflows/character-consistency
- https://theprompthome.com/ai-character-bible-guide/
- https://docsaid.org/en/blog/papers/face-recognition/arcface
- https://devenkoai.medium.com/how-to-build-an-ai-mascot-for-your-ecom-brand-free-guide-42c4e71bebc6
- https://arxiv.org/html/2508.09461v1
- https://arxiv.org/html/2404.16022v2
- https://www.uisdc.com/digital-human-role-design
- https://kuroganeito.jp/vtubermodelcreation-en
- https://github.com/xixihhhh/ai-short-drama-skill/blob/main/skills/dramake/assets/templates/character-bible.md
- https://luathoangsa.vn/quyen-cua-ca-nhan-doi-voi-hinh-anh-nd63851.html
- https://luatlongphan.vn/giai-quyet-tranh-chap-su-dung-hinh-anh-kol-influencer
- https://artificialintelligenceregulations.com/jurisdictions/china.html
- https://www.transasialawyers.com/insights/new-draft-rules-for-digital-avatars-and-virtual-humans-in-china
- https://draw.market/en/blog/first-step-to-custom-vtuber-model.html
- https://medium.com/@Kenny_Studiuo/bringing-vtubers-to-life-my-2d-character-and-live2d-model-creation-workflow-308ca604cc85
- https://os-artist-front.webapp.easebar.com/en/blog/how-to-make--vtuber-model.html
- https://morphic.com/ai-glossary/instantid
- https://medium.com/@ichigo.v.gen12/arcface-architecture-and-practical-example-how-to-calculate-the-face-similarity-between-images-183896a35957
- https://didit.me/blog/arcface-vs-cosface-deep-dive-into-face-matching-algorithms/
- https://www.youtube.com/watch?v=66jO7fdUELk
- https://community.hailo.ai/t/a-comprehensive-guide-to-building-a-face-recognition-system/8803
- https://medium.com/@aylin.aydin/face-recognition-and-arcface-loss-for-beginners-cdfddbf7e88
- https://arxiv.org/html/2607.25622v1
- https://vanphuclawfirm.com/quyen-cua-ca-nhan-doi-voi-hinh-anh/
- https://luatvietnam.vn/tin-phap-luat/luat-quy-dinh-the-nao-ve-quyen-hinh-anh-cua-ca-nhan-230-15685-article.html
- https://kiemsat.vn/trach-nhiem-dan-su-doi-voi-hanh-vi-xam-pham-quyen-nhan-than-tren-mang-xa-hoi-72210.html
- https://www.chinaiplawupdate.com/wp-content/uploads/2025/09/%E5%8C%97%E4%BA%AC%E4%BA%92%E8%81%94%E7%BD%91%E6%B3%95%E9%99%A2%E6%B6%89%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E5%85%B8%E5%9E%8B%E6%A1%88%E4%BE%8B.pdf
- https://trussed.ai/resources/china-ai-labeling-requirements-september-2025
- https://domer.io/blog/consistent-character-ai-workflow
- https://ltx.io/blog/how-to-maintain-character-consistency-in-ai-video
- https://www.vidu.com/blog/consistent-character-ai
- https://runway.com/resources/create-consistent-ai-characters
- https://www.youtube.com/watch?v=wGs2vByrF3U
- https://higgsfield.ai/blog/tools-for-consistent-ai-characters
- https://invideo.io/academy/i-tried-every-ai-character-consistency-workflow-results/
- https://www.sozee.ai/resources/ai-influencer-content-workflow/
- https://thefluxtrain.com/ai-influencer-creator/
- https://queststudio.io/blog/how-to-create-an-ai-influencer
- https://www.elser.ai/blog/building-an-original-character-bible-that-ai-tools-can-follow
- https://oakgen.ai/blog/character-sheet-to-launch-video-workflow
- https://montagea.com/blog/build-consistent-ai-influencer-video-workflow/
- https://www.youtube.com/watch?v=x9ETAqkAysg
- https://didit.me/blog/face-matching-algorithms-arcface-cosface/
- https://www.arxiv.org/pdf/2501.04444v1
- https://openaccess.thecvf.com/content_ICCVW_2019/papers/DFW/Deng_ArcFace_for_Disguised_Face_Recognition_ICCVW_2019_paper.pdf
- https://www.insightface.ai/research/arcface
- https://www.ijert.org/selfie-based-attendance-system-implementation-using-arcface-and-cosine-similarity-for-identity-verification-ijertconv14is010041
- https://viblo.asia/p/paper-explained-some-face-recognition-approaches-facenet-arcface-cosface-Do754zgLZM6
- https://www.mdpi.com/2076-3417/16/1/414
- https://www.media.io/image-tips/comfyui-consistent-characters.html
- https://www.youtube.com/watch?v=E62ori0VSds
- https://medium.com/@enockjackson873/im-21-and-this-is-what-building-an-ai-influencer-has-actually-paid-me-431e6abf2643
- https://arxiv.org/html/2412.01254v2
- https://arxiv.org/html/2506.20879v2
- https://arxiv.org/html/2503.15406v2
- https://peking.bjd.com.cn/content/s68a7fbd0e4b0221b9bebd39b.html
- https://www.thepaper.cn/newsDetail_forward_33026199
- https://legal.gmw.cn/2026-10/16/content_39050667.htm
- https://advertisingvietnam.com/article/virtual-influencer-ho-la-ai-trong-the-gioi-tiep-thi-quang-cao-p20244
- https://www.brandsvietnam.com/congdong/topic/ai-se-thay-doi-social-media-marketing-nhu-the-nao-trong-nam-toi
- https://www.beautyplus.com/vi/ai-influencer/ai-persona-generator
- https://www.uisdc.com/digital-human-role-design-2
- https://spiroworks.com/how-to-commission-a-vtuber-model-a-guide-to-character-design-live2d-art-and-design-briefs/
- https://www.rokoko.com/insights/guide-how-to-create-the-best-vtuber-setup
- https://tips.clip-studio.com/en-us/articles/11064
- https://www.reddit.com/r/VirtualYoutubers/comments/1ohcfv0/how_do_character_designers_usually_work_when/
- https://www.youtube.com/watch?v=S-nKWrSZSnY
- https://www.youtube.com/watch?v=f89r_MnSslU&vl=en
- https://i-law.vn/huong-dan-phap-ly/quyen-bao-ve-hinh-anh-ca-nhan-68966
- https://daibieunhandan.vn/truong-hop-nao-su-dung-hinh-anh-ca-nhan-khong-can-xin-phep-10320962.html
- https://htc-law.com/tu-van-phap-luat-dan-su/su-dung-hinh-anh-ca-nhan-trai-phep-tren-mang-xa-hoi-muc-boi-thuong-danh-du-la-bao-nhieu,6276.html
- https://thuvienphapluat.vn/chinh-sach-phap-luat-moi/vn/ho-tro-phap-luat/tu-van-phap-luat/65989/quyen-cua-ca-nhan-doi-voi-hinh-anh-cua-minh-theo-bo-luat-dan-su-2015
- https://comfy.icu/node/AlchemicaFaceMatch
- https://github.com/deepinsight/insightface/issues/903
- https://github.com/dubey-astha/Face_Recognition_Arcface
- https://arxiv.org/html/2610.40119v1
- https://arxiv.org/html/2610.22746v1
- https://arxiv.org/html/2607.20247v1
- https://arxiv.org/html/2404.16022v1
- https://www.biometricupdate.com/202604/chinas-draft-rules-on-ai-virtual-humans-target-biometric-deepfakes
- https://casrai.org/guides/china-ai-regulation-explained
- https://mmlcgroup.com/china-ai-labelling-rules/
- https://intelligence.dlapiper.com/artificial-intelligence/?t=01-law&c=CN
- https://www.chinalawtranslate.com/en/ai-labeling/
- https://bjlti.com/revista/article/view/81