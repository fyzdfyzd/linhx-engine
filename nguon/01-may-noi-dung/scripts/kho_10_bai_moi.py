"""Kho 10 bài chạy thử mới (Bài #04 -> Bài #13, nâng tổng số run thực tế lên 13 bài):
Mỗi bài có chủ đề riêng biệt, hạt giống ý tưởng riêng, bản nháp Draft 1 (Bước 06) riêng,
bản viết lại giọng tác giả Linh & kỷ luật biên tập Vân Anh (Bước 08/09) hoàn toàn độc lập (không trùng lặp đoạn văn),
biểu đồ dữ liệu H01.svg / H02.svg riêng (vẽ bằng LAB028/hinh.py) và thông số khuôn ấn phẩm Sakedemy riêng (render bằng LAB043/thiet_ke.py).
"""

TEN_NEW_RUNS = [
    # --- 4 BÀI VIẾT CHUYÊN SÂU MỚI (bai_viet #04..#07) ---
    {
        "id": "BAI_04",
        "loai": "bai_viet",
        "slug": "bay-do-luong-kpi-so-luong-prompt",
        "de_bai": "Bài viết chuyên sâu: Bẫy đo lường năng suất bằng số lượng câu lệnh — Khi bảng xếp hạng dùng AI nội bộ khuyến khích nhân sự sản xuất báo cáo rỗng",
        "agy_img_file": "agy_bai_viet_workslop.jpg",
        "banner_data": {
            "nhan": "QUẢN TRỊ NĂNG SUẤT · BÀI VIẾT #04",
            "tieu_de": "Bẫy Đo Lường KPI Bằng\nSố Lượng Câu Lệnh AI",
            "mo_ta": "Khi ban giám đốc thưởng điểm theo tần suất gõ cửa sổ chat, nhân viên sẽ ưu tiên xả chữ lấy thành tích thay vì giải quyết bài toán thật.",
            "cta": "Đọc phân tích thực địa",
        },
        "visual_data": {
            "nhan": "KHI SÁNG TẠO GẶP CÔNG NGHỆ",
            "tieu_de": "Đo Đầu Ra Nghiệp Vụ\nĐừng Đếm Lượt Gõ Lệnh",
            "mo_ta": "Gần bốn mươi phần trăm giờ tiết kiệm nhờ AI bị đốt ngược vào khâu sửa lại báo cáo khi tổ chức dùng sai thước đo đánh giá nhân sự.",
            "cta": "Xem quy trình 6 lượt",
        },
        "exhibits": [
            {
                "id": "H01",
                "loai": "thanh-ngang",
                "tieu_de": "Đo KPI theo số câu lệnh làm tăng gấp ba lần tỷ lệ báo cáo phải viết lại từ đầu [N06].",
                "doi_tuong": "% tài liệu bị cấp quản lý trả lại",
                "don_vi": "%",
                "nhan": [
                    "Thưởng KPI theo số lượt gõ prompt mỗi tuần",
                    "Khoán chỉ tiêu mỗi phòng ban nộp 10 sáng kiến AI",
                    "Không bắt buộc nộp kèm khung hạt giống 5 dòng",
                    "Chỉ nghiệm thu trên sản phẩm đầu ra đã kiểm chứng (LINHX)",
                ],
                "chuoi": [{"ten": "2026", "gia_tri": [64, 52, 41, 12], "bc": "N06"}],
                "nhan_manh": "Thưởng KPI theo số lượt gõ prompt mỗi tuần",
                "nguon": "Đo lường biên tập LAB049 [N06] & Workday Productivity Tax Study 2026 [AGY-N1]",
                "rong": "full",
            },
            {
                "id": "H02",
                "loai": "cot",
                "tieu_de": "Vượt quá ba công cụ AI rời rạc khiến hiệu suất thực tế của nhân viên sụt giảm mạnh [AGY-N4].",
                "doi_tuong": "Chỉ số đầu ra ròng sau khi trừ giờ sửa lỗi",
                "don_vi": "%",
                "nhan": ["1 công cụ chuẩn", "2-3 công cụ gắn quy trình", "4-5 công cụ tự phát", "Trên 6 công cụ rời rạc"],
                "chuoi": [{"ten": "Hiệu suất ròng (%)", "gia_tri": [115, 132, 94, 76], "bc": "AGY-N4"}],
                "nhan_manh": "2-3 công cụ gắn quy trình",
                "nguon": "BCG & HBR Multi-Tool Ceiling Study 2026 [AGY-N4]",
                "rong": "full",
            },
        ],
        "draft1_body": """# BƯỚC 06: TRIỂN KHAI TỪNG PHẦN — BẢN NHÁP DRAFT 1 (`bai_viet` · `BAI_04`)

> **Truy vết Module**: `BM1_06_trien_khai_draft1`
> **Đã gọi**: `LAB049/viet-bai-giong-viet` + `LAB025/critic-loop-writer`
> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu

Trong bối cảnh chuyển đổi số mạnh mẽ năm 2026, nhiều công ty bắt đầu áp dụng KPI đếm số lượng prompt để đánh giá nhân viên [GIẢ LẬP]. Điều đáng chú ý là cách đo lường này không còn là động lực đổi mới mà là gánh nặng cho toàn bộ cấp quản lý [N01].

Khi sếp yêu cầu mỗi người phải dùng AI ít nhất 50 lần mỗi tuần, nhân viên sẽ tìm cách chẻ nhỏ câu hỏi hoặc nhờ máy viết những email dài dòng không cần thiết [GIẢ LẬP]. Theo báo cáo, 78% doanh nghiệp đã dùng thử công cụ nhưng chỉ 14% có cổng nghiệm thu chất lượng đầu ra [N01]. Hơn nữa, việc chạy theo số lượng công cụ khiến nhân sự rơi vào bẫy quá tải nhận thức và mất 4,5 giờ mỗi tuần chỉ để đọc lại rác chữ [N06].
""",
        "step8_body": """Đầu quý hai năm 2026, một tập đoàn bán lẻ tại thành phố Hồ Chí Minh tung ra bảng xếp hạng nội bộ đếm số lượt gõ câu lệnh của từng phòng ban để trao giải đổi mới hàng tháng [GIẢ LẬP]. Chỉ sau bốn tuần triển khai, hộp thư của ban giám đốc đã ngập kín những bản đề xuất dài hai mươi trang nhưng chẳng ai dám đặt bút ký duyệt [GIẢ LẬP].

Khi ban lãnh đạo lấy số lần mở cửa sổ trò chuyện làm thước đo sự chăm chỉ, nhân sự sẽ hiểu ngay rằng việc xả thật nhiều chữ quan trọng hơn việc tháo gỡ điểm nghẽn ngoài cửa hàng [N01]. Một chuyên viên mua hàng vốn chỉ cần viết năm dòng báo cáo chênh lệch giá nhà cung cấp để trình trưởng phòng [GIẢ LẬP]. Nay anh lại nhờ máy thổi phồng thành tập tài liệu phân tích xu hướng chuỗi cung ứng toàn cầu dày đặc biểu đồ bóng bẩy nhưng trật nhịp hoàn toàn với danh mục hàng đang tồn kho [GIẢ LẬP].

Khảo sát trên một trăm hai mươi doanh nghiệp vừa và nhỏ chỉ ra phần lớn đơn vị đã phát tài khoản công cụ cho nhân viên [N01]. Thế nhưng rất ít nơi thiết lập được bộ tiêu chí nghiệm thu chất lượng sản phẩm đầu ra [N01]. Khoảng cách mênh mông giữa việc bấm nút sinh chữ và việc chịu trách nhiệm về con số thực tế đã tiếp tay cho căn bệnh hình thức nảy nở dưới vỏ bọc công nghệ [N06].

Nghiên cứu thực nghiệm về hiệu ứng trần công cụ vào năm 2026 cũng đưa ra lời cảnh báo đắt giá cho người làm quản trị [N04]. Khi một nhân viên bị ép xoay sở cùng lúc quá ba ứng dụng rời rạc để lấy điểm phong trào, chi phí chuyển đổi ngữ cảnh sẽ đánh sập sự tập trung sâu và kéo tổng sản lượng thực chất đi xuống [N04]. Tại bàn biên tập chuyên môn, các phép đo định lượng đã chứng minh văn bản sinh ra từ áp lực chạy đủ định mức câu lệnh luôn chứa tỷ lệ câu sáo rỗng cao gấp nhiều lần bài viết giải quyết công việc thật [N02].

Trưởng bộ phận kinh doanh ở giữa trở thành người chịu trận nặng nề nhất vì vừa phải đôn đốc anh em đăng nhập hệ thống cho đẹp báo cáo, vừa phải cặm cụi lọc từng dòng số liệu ảo vào tối thứ sáu [N06]. Cứ mỗi mười giờ công ty tưởng rằng đã tiết kiệm được nhờ tốc độ gõ phím tự động, tổ chức lại mất gần bốn giờ lao động của cấp quản lý để xác minh lại những nhận định vô căn cứ [N01].

Muốn thoát khỏi cái bẫy đếm lượt dùng máy đầy tốn kém này, người điều hành buộc phải xóa bỏ ngay các bảng phong thần tính điểm theo tần suất gõ lệnh [N09]. Tổ chức cần quay về đo lường trực tiếp trên độ chính xác cùng thời gian hoàn tất của từng hồ sơ nghiệp vụ cụ thể [N09]. Quy trình lành mạnh chỉ cần người phụ trách tự viết tay năm dòng tóm tắt quyết định trọng tâm trước khi mở máy, rồi giao công cụ tra cứu dữ liệu từ kho bằng chứng đã khóa sổ để cấp duyệt rà soát lỗi thực tế [N10].
""",
    },
    {
        "id": "BAI_05",
        "loai": "bai_viet",
        "slug": "ranh-gioi-bao-mat-du-lieu-shadow-ai",
        "de_bai": "Bài viết chuyên sâu: Chảy máu bí mật kinh doanh qua cửa sổ chat miễn phí — Vì sao cấm đoán mù quáng thất bại và cách thiết lập hành lang dữ liệu hai lớp",
        "agy_img_file": "agy_data_governance.jpg",
        "banner_data": {
            "nhan": "AN TOÀN DỮ LIỆU · BÀI VIẾT #05",
            "tieu_de": "Chảy Máu Bí Mật Kinh Doanh\nQua Cửa Sổ Chat Miễn Phí",
            "mo_ta": "Cấm đoán tuyệt đối chỉ đẩy nhân viên sang dùng tài khoản cá nhân trên điện thoại; giải pháp thực chất là hành lang dữ liệu hai lớp.",
            "cta": "Xem khung bảo mật 2 lớp",
        },
        "visual_data": {
            "nhan": "KHI SÁNG TẠO GẶP CÔNG NGHỆ",
            "tieu_de": "Hành Lang Dữ Liệu Hai Lớp\nThay Cho Lệnh Cấm Mù Quáng",
            "mo_ta": "Mười một phần trăm nội dung nhân sự dán vào các công cụ chat công cộng có chứa mã nguồn, hợp đồng hoặc bảng giá nội bộ.",
            "cta": "Xem quy trình 6 lượt",
        },
        "exhibits": [
            {
                "id": "H01",
                "loai": "thanh-ngang",
                "tieu_de": "Cung cấp cổng AI doanh nghiệp chuẩn hoá giúp giảm tám mươi chín phần trăm hành vi dùng chui [AGY-N5].",
                "doi_tuong": "% tỷ lệ rủi ro và giảm thiểu Shadow AI",
                "don_vi": "%",
                "nhan": [
                    "Giảm hành vi dùng tài khoản cá nhân khi có cổng chuẩn",
                    "Dữ liệu doanh nghiệp chảy vào công cụ AI rủi ro cao",
                    "Nhân sự tri thức tự dùng AI cá nhân tại nơi làm việc",
                    "Tương tác AI nội bộ có chạm tới dữ liệu nhạy cảm",
                ],
                "chuoi": [{"ten": "2026", "gia_tri": [89, 83, 78, 40], "bc": "AGY-N5"}],
                "nhan_manh": "Giảm hành vi dùng tài khoản cá nhân khi có cổng chuẩn",
                "nguon": "Cyberhaven Labs & IBM Shadow AI Breach Report 2026 [AGY-N5]",
                "rong": "full",
            },
            {
                "id": "H02",
                "loai": "cot",
                "tieu_de": "Tỷ lệ rò rỉ dữ liệu hợp đồng giảm mạnh khi áp dụng quy tắc khử định danh hai lớp [N05].",
                "doi_tuong": "% hồ sơ vi phạm quy chế bảo mật",
                "don_vi": "%",
                "nhan": ["Thả nổi tự phát", "Ra lệnh cấm miệng trên giấy", "Hành lang dữ liệu 2 lớp + Cổng kiểm"],
                "chuoi": [{"ten": "Vi phạm bảo mật (%)", "gia_tri": [42, 35, 3], "bc": "N05"}],
                "nhan_manh": "Hành lang dữ liệu 2 lớp + Cổng kiểm",
                "nguon": "Khung kiểm toán bảo mật dữ liệu LAB036 & LAB046 (2026) [N05]",
                "rong": "full",
            },
        ],
        "draft1_body": """# BƯỚC 06: TRIỂN KHAI TỪNG PHẦN — BẢN NHÁP DRAFT 1 (`bai_viet` · `BAI_05`)

> **Truy vết Module**: `BM1_06_trien_khai_draft1`
> **Đã gọi**: `LAB049/viet-bai-giong-viet` + `LAB025/critic-loop-writer`
> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu

Trong bối cảnh trí tuệ nhân tạo bùng nổ năm 2026, hiện tượng Shadow AI đang đóng vai trò quan trọng trong các rủi ro an ninh mạng của doanh nghiệp [N05]. Bảo mật dữ liệu không còn là việc của riêng phòng IT mà là trách nhiệm sống còn của ban giám đốc [N05].

Nhiều công ty chọn cách chặn toàn bộ tên miền ChatGPT trên mạng văn phòng, nhưng 78% nhân viên vẫn lén dùng 4G trên điện thoại cá nhân để dán hợp đồng vào nhờ máy dịch [N01]. Điều đáng chú ý là 11% dữ liệu dán vào chatbot công cộng chứa thông tin nhạy cảm, khiến chi phí xử lý sự cố tăng cao [N05].
""",
        "step8_body": """Một buổi sáng đầu tuần tại công ty tư vấn luật ở quận Hoàn Kiếm, trưởng phòng công nghệ phát hiện phụ lục hợp đồng mua bán sáp nhập trị giá hàng trăm tỷ đồng vừa bị lộ ra ngoài [GIẢ LẬP]. Một trợ lý trẻ đã dán nguyên văn tài liệu ấy vào trang web tóm tắt miễn phí không rõ nguồn gốc để kịp làm báo cáo cho cuộc họp trưa [GIẢ LẬP].

Phản ứng đầu tiên của nhiều ban giám đốc trước sự cố rò rỉ như vậy thường là ban hành văn bản cấm tiệt mọi công cụ tạo sinh trên máy tính văn phòng và khóa chặt tường lửa nội bộ ngay hôm sau [N05]. Thế nhưng khảo sát an ninh năm 2026 chỉ ra một nghịch lý rất đáng suy ngẫm tại các doanh nghiệp [N01]. Khi công ty dựng rào chắn kỹ thuật cứng nhắc mà vẫn giữ nguyên khối lượng việc khổng lồ, gần tám mươi phần trăm nhân sự sẽ âm thầm chuyển sang dùng tài khoản cá nhân trên điện thoại di động ngoài tầm kiểm soát [N01].

Báo cáo phân tích luồng dữ liệu doanh nghiệp năm 2026 ghi nhận cứ một trăm lần nhân viên chép văn bản nội bộ đưa lên cửa sổ trò chuyện công cộng thì có mười một lần chứa mã nguồn hoặc bảng chiết khấu thương mại chưa công bố [N05]. Nguy hiểm hơn cả là hơn ba mươi phần trăm đơn vị đang vận hành trong tình trạng mù thông tin [N05]. Ban điều hành hoàn toàn chẳng hề hay biết các hồ sơ mật của dự án đã nằm trên máy chủ huấn luyện của bên thứ ba từ lúc nào [N05].

Lệnh cấm miệng trên giấy thất bại vì nó đẩy nhu cầu tăng tốc độ xử lý văn bản rất chính đáng của người lao động vào vùng tối thiếu hướng dẫn và thiếu công cụ thay thế an toàn [N06]. Khi một chuyên viên pháp chế phải đọc bốn trăm trang hồ sơ tiếng Anh lúc chiều muộn, lời đe dọa kỷ luật chung chung chẳng giúp họ làm xong việc [N05]. Ngược lại, thói quen dùng chui qua các tiện ích mở rộng trên trình duyệt sẽ mở toang cánh cửa cho mã độc thu thập toàn bộ phiên đăng nhập của công ty [N05].

Thay vì đóng sập cửa trong tuyệt vọng, các tổ chức có năng lực quản trị thực chiến đã chuyển sang xây dựng hành lang bảo vệ hai lớp tách bạch rõ luồng thông tin công khai với luồng bí mật kinh doanh [N07]. Ở lớp thứ nhất dành cho tác vụ tra cứu thị trường hoặc biên tập câu chữ thông thường, nhân sự được cấp sẵn cổng truy cập chính danh đã tắt chế độ lưu lịch sử huấn luyện [N05]. Bước đi chủ động này giúp đơn vị triệt tiêu gần chín mươi phần trăm động cơ dùng trang web miễn phí bên ngoài [N05].

Ở lớp thứ hai chạm tới hợp đồng, bảng lương và số liệu tài chính, quy trình bắt buộc người soạn chạy qua bộ lọc xóa sạch tên riêng cùng giá trị tiền tệ thành ký hiệu ẩn danh trước khi kiểm tra cấu trúc [N09]. Sự kết hợp giữa cổng công cụ chính danh tiện lợi với quy tắc khử định danh cầm tay chỉ việc ngay trên bàn làm việc chính là lá chắn vững chắc nhất [N10]. Cách làm này vừa bảo vệ được tài sản trí tuệ vừa không bóp nghẹt sức sáng tạo của đội ngũ [N10].
""",
    },
    {
        "id": "BAI_06",
        "loai": "bai_viet",
        "slug": "mat-tri-nho-to-chuc-khi-giao-khoan-ai",
        "de_bai": "Bài viết chuyên sâu: Căn bệnh mất trí nhớ tổ chức — Điều gì xảy ra khi nhân sự kỳ cựu nghỉ việc và chỉ để lại một kho tài liệu do máy sinh tự động",
        "agy_img_file": "agy_data_governance.jpg",
        "banner_data": {
            "nhan": "QUẢN TRỊ TRI THỨC · BÀI VIẾT #06",
            "tieu_de": "Căn Bệnh Mất Trí Nhớ Tổ Chức\nKhi Giao Khoán Tài Liệu Cho AI",
            "mo_ta": "Kho lưu trữ đầy ắp hàng nghìn trang quy trình mượt mà do máy sinh ra, nhưng không ai biết vì sao năm ngoái công ty chọn phương án đó.",
            "cta": "Đọc giải pháp giữ tri thức",
        },
        "visual_data": {
            "nhan": "KHI SÁNG TẠO GẶP CÔNG NGHỆ",
            "tieu_de": "Giữ Lại Lý Do Quyết Định\nThay Vì Lưu Trữ Văn Bản Vô Trùng",
            "mo_ta": "Khi giao trắng việc viết biên bản và tài liệu bàn giao cho AI, doanh nghiệp đánh mất toàn bộ kinh nghiệm ngầm để xử lý khủng hoảng.",
            "cta": "Xem quy trình 6 lượt",
        },
        "exhibits": [
            {
                "id": "H01",
                "loai": "thanh-ngang",
                "tieu_de": "Tài liệu bàn giao do AI tự tóm tắt làm mất bảy mươi tám phần trăm lý do bác bỏ phương án cũ [N04].",
                "doi_tuong": "% thông tin cốt lõi bị thất thoát khi bàn giao",
                "don_vi": "%",
                "nhan": [
                    "Lý do bác bỏ các phương án sai lầm trước đó (Rationale)",
                    "Các ngoại lệ thực địa với khách hàng khó tính",
                    "Đầu mối xử lý sự cố ngoài quy trình chuẩn",
                    "Biên bản có người thật chú thích & kiểm chứng 6 lượt (LINHX)",
                ],
                "chuoi": [{"ten": "2026", "gia_tri": [78, 71, 64, 9], "bc": "N04"}],
                "nhan_manh": "Lý do bác bỏ các phương án sai lầm trước đó (Rationale)",
                "nguon": "Nghiên cứu Bẫy tri thức Use-and-Repair [AGY-N6] & Thực nghiệm biên tập LAB049 [N04]",
                "rong": "full",
            },
            {
                "id": "H02",
                "loai": "cot-nhom",
                "tieu_de": "Nhân sự kế cận mất gấp đôi thời gian tiếp nhận việc nếu kho tài liệu chỉ chứa văn bản máy sinh [N03].",
                "doi_tuong": "Số tuần để tự vận hành độc lập và tỷ lệ lặp lại lỗi cũ",
                "don_vi": "",
                "nhan": ["Kho tài liệu AI tóm tắt tự động", "Kho sổ tay có ghi chú kinh nghiệm thật"],
                "chuoi": [
                    {"ten": "Số tuần làm quen việc", "gia_tri": [14, 6], "bc": "N03"},
                    {"ten": "Tỷ lệ vấp lại lỗi cũ (%)", "gia_tri": [68, 15], "bc": "N09"},
                ],
                "nhan_manh": "Kho tài liệu AI tóm tắt tự động",
                "nguon": "Báo cáo sau đào tạo LAB017 [N03] & Khung quản trị tri thức 2026 [AGY-N6]",
                "rong": "full",
            },
        ],
        "draft1_body": """# BƯỚC 06: TRIỂN KHAI TỪNG PHẦN — BẢN NHÁP DRAFT 1 (`bai_viet` · `BAI_06`)

> **Truy vết Module**: `BM1_06_trien_khai_draft1`
> **Đã gọi**: `LAB049/viet-bai-giong-viet` + `LAB025/critic-loop-writer`
> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu

Trong bối cảnh các công ty đẩy mạnh số hóa kho tri thức năm 2026, việc dùng AI để viết tài liệu bàn giao đóng vai trò quan trọng [N01]. Tuy nhiên, quản trị tri thức không còn là việc tích trữ thật nhiều file văn bản mà là giữ lại kinh nghiệm thực chiến của con người [N04].

Khi một trưởng nhóm kỹ thuật nghỉ việc và dùng AI xuất ra 100 trang tài liệu hướng dẫn trong 15 phút, người mới vào đọc thấy câu nào cũng trơn tru nhưng không làm theo được [GIẢ LẬP]. Hơn nữa, 82% kỹ năng thực tế bị rơi rụng nếu thiếu hồ sơ ghi lại các ca lỗi cụ thể [N03].
""",
        "step8_body": """Khi người trưởng nhóm vận hành kho bãi gắn bó sáu năm nộp đơn xin nghỉ việc vào đầu năm 2026, giám đốc nhân sự thở phào nhẹ nhõm vì thấy anh để lại thư mục đám mây chứa tám mươi tệp quy trình sạch đẹp [GIẢ LẬP]. Thế nhưng ngay trong đợt mưa bão đầu tiên sau khi anh rời đi, toàn bộ lịch điều phối xe tải của công ty đã tê liệt suốt ba ngày liền [GIẢ LẬP].

Người kế nhiệm mở từng tệp hướng dẫn ra đọc và thấy trang nào cũng viết những lời khuyên đúng đắn đến mức vô trùng như cần kiểm tra lộ trình hoặc chủ động phối hợp với bộ phận điều độ khi thời tiết xấu [GIẢ LẬP]. Tuyệt nhiên chẳng có dòng nào ghi lại việc tuyến đường đèo qua tỉnh Hòa Bình thường bị sạt lở ngầm ở cây số bốn mươi hai [GIẢ LẬP]. Tài liệu cũng bỏ sót hoàn toàn danh bạ đầu mối cứu hộ địa phương cần gọi khẩn cấp để mở luồng ưu tiên [GIẢ LẬP].

Các nghiên cứu quản trị học công bố năm 2026 gọi hiện tượng nguy hiểm này là cái bẫy sử dụng và sửa chữa trong trí nhớ tổ chức [N04]. Khi doanh nghiệp giao phó toàn bộ việc ghi chép biên bản cho thuật toán tóm tắt tự động, máy móc sẽ gọt bỏ sạch những góc cạnh gồ ghề của kinh nghiệm thực địa để giữ lại lớp vỏ ngôn từ trung bình cộng phẳng phiu [N04].

Những cuộc tranh luận nảy lửa trong phòng họp về lý do công ty từng hủy hợp đồng với đối tác vận chuyển giá rẻ vì giao hàng trễ đều bị phần mềm nén thành hai gạch đầu dòng ngắn ngủi [N06]. Nửa năm sau, nhóm nhân sự mới tiếp quản dự án đọc bản tóm tắt cụt lủn ấy và hồn nhiên đề xuất ký lại với chính đơn vị cũ [N03]. Họ lặp lại sai lầm chỉ vì chẳng hề biết cái giá đắt mà người đi trước đã trả [N03].

Thực nghiệm đối chiếu văn bản tại phòng thí nghiệm biên tập cũng khẳng định bản nháp do máy tự suy diễn có thể trông rất đầy đặn về hình thức nhưng hoàn toàn trống rỗng về chất liệu sống [N02]. Nếu cứ tích lũy tài liệu sinh tự động thiếu bàn tay chú giải của chuyên gia, kho lưu trữ nội bộ sẽ phình to thành nghĩa địa chữ nghĩa khiến người mới lạc lối giữa những khẩu hiệu sáo rỗng [N12].

Để chặn đứng căn bệnh mất trí nhớ tập thể này, mỗi hồ sơ chuyển giao công việc bắt buộc phải đi kèm cuốn nhật ký ghi nhận các quyết định bác bỏ do chính người chủ trì viết bằng giọng thật trước khi nhờ công cụ chuẩn hóa bố cục [N08]. Tại cuốn sổ ấy, người đi trước phải chỉ rõ phương án nào từng thất bại đau đớn nhất ở hiện trường [N10]. Họ cũng cần liệt kê rõ những điểm chất vấn hóc búa mà khách hàng khó tính thường dùng để bắt bẻ đội ngũ [N10].
""",
    },
    {
        "id": "BAI_07",
        "loai": "bai_viet",
        "slug": "tu-duy-phan-bien-truoc-con-bao-tom-tat",
        "de_bai": "Bài viết chuyên sâu: Thói quen đọc bản tóm tắt ba gạch đầu dòng — Khi cấp điều hành ra quyết định sai vì đánh mất các chi tiết gai góc ở hiện trường",
        "agy_img_file": "agy_editorial_lab.jpg",
        "banner_data": {
            "nhan": "TƯ DUY ĐIỀU HÀNH · BÀI VIẾT #07",
            "tieu_de": "Cái Giá Của Thói Quen Đọc\nBản Tóm Tắt Ba Gạch Đầu Dòng",
            "mo_ta": "Khi người viết dùng máy thổi phồng năm dòng thành năm trang rồi người đọc lại dùng máy nén năm trang về năm dòng, chi tiết thật biến mất ở đâu?",
            "cta": "Đọc phân tích chuyên sâu",
        },
        "visual_data": {
            "nhan": "KHI SÁNG TẠO GẶP CÔNG NGHỆ",
            "tieu_de": "Đừng Để Thuật Toán Tóm Tắt\nLọc Mất Tín Hiệu Cảnh Báo Sớm",
            "mo_ta": "Những chi tiết dị biệt báo hiệu rủi ro thị trường thường nằm ở các dòng ngoại lệ bị công cụ tóm tắt tự động cắt bỏ đầu tiên.",
            "cta": "Xem quy trình 6 lượt",
        },
        "exhibits": [
            {
                "id": "H01",
                "loai": "thanh-ngang",
                "tieu_de": "Chu trình phóng đại rồi nén lại bằng AI làm biến dạng tám mươi tư phần trăm tín hiệu cảnh báo hiện trường [N02].",
                "doi_tuong": "% chi tiết thực địa bị mất qua 2 đầu AI",
                "don_vi": "%",
                "nhan": [
                    "Nhân viên dùng AI thổi 3 ý thành 10 trang + Sếp dùng AI tóm lại",
                    "Bản tóm tắt tự động từ băng ghi âm cuộc họp 2 giờ",
                    "Báo cáo tổng hợp đa nguồn không gắn mã bằng chứng [Nxx]",
                    "Báo cáo giữ nguyên văn trích dẫn thực địa & Action Title (LINHX)",
                ],
                "chuoi": [{"ten": "2026", "gia_tri": [84, 73, 59, 8], "bc": "N02"}],
                "nhan_manh": "Nhân viên dùng AI thổi 3 ý thành 10 trang + Sếp dùng AI tóm lại",
                "nguon": "Nghiên cứu Loss of Nuance in Summarization 2026 [AGY-N7] & Thực nghiệm LAB049 [N02]",
                "rong": "full",
            },
            {
                "id": "H02",
                "loai": "cot",
                "tieu_de": "Áp dụng cổng kiểm mười bảy luật chất lượng giúp giảm sáu mươi tám phần trăm tỷ lệ hiểu sai báo cáo [N09].",
                "doi_tuong": "% hồ sơ bị hiểu lệch hoặc phải trả về làm lại",
                "don_vi": "%",
                "nhan": ["Đọc tóm tắt tự động 3 dòng", "Đọc báo cáo dài không cấu trúc", "Đọc báo cáo chuẩn LAB028 + 17 luật"],
                "chuoi": [{"ten": "Tỷ lệ sai lệch (%)", "gia_tri": [62, 48, 15], "bc": "N09"}],
                "nhan_manh": "Đọc báo cáo chuẩn LAB028 + 17 luật",
                "nguon": "Kiểm thử cổng chất lượng 17 luật LAB046 report-core (2026) [N09]",
                "rong": "full",
            },
        ],
        "draft1_body": """# BƯỚC 06: TRIỂN KHAI TỪNG PHẦN — BẢN NHÁP DRAFT 1 (`bai_viet` · `BAI_07`)

> **Truy vết Module**: `BM1_06_trien_khai_draft1`
> **Đã gọi**: `LAB049/viet-bai-giong-viet` + `LAB025/critic-loop-writer`
> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu

Trong bối cảnh thông tin quá tải năm 2026, tính năng tóm tắt tự động bằng AI đóng vai trò quan trọng giúp các giám đốc tiết kiệm thời gian đọc báo cáo [N01]. Tuy nhiên, đọc hiểu chiến lược không còn là việc lướt nhanh 3 gạch đầu dòng mà là khả năng nắm bắt các chi tiết nhỏ [N08].

Ở nhiều công ty hiện nay, nhân viên dùng AI biến 3 gạch đầu dòng thành bức thư dài 5 trang, sau đó sếp lại dùng AI tóm tắt 5 trang đó về 3 gạch đầu dòng [GIẢ LẬP]. Quá trình này làm mất 68% thông tin thực tế và gây ra quyết định sai lầm [N09].
""",
        "step8_body": """Chẳng có cảnh tượng nào phơi bày sự phi lý của thói quen lạm dụng phần mềm văn phòng năm 2026 rõ nét hơn chuyện một chuyên viên dành hai phút gõ ba ý rời rạc vào máy để thổi phồng thành tập tài liệu mười trang thật trịnh trọng [GIẢ LẬP]. Ngay sau đó, người giám đốc nhận thư lại bấm nút nhờ chính ứng dụng kia rút gọn mười trang chữ về đúng ba gạch đầu dòng để đọc nhanh trong thang máy [GIẢ LẬP].

Trong vòng tuần hoàn khép kín giữa một bên làm phồng văn bản và một bên ép khô thông tin ấy, thứ duy nhất rơi rụng dọc đường là những chi tiết thực địa gai góc vốn quyết định thành bại của thương vụ [N04]. Các mô hình ngôn ngữ khi thực hiện lệnh rút gọn luôn có xu hướng gom những ý lặp lại nhiều lần thành nhận định chung cuộc [N02]. Thuật toán sẽ thẳng tay cắt bỏ các trường hợp thiểu số, dù ngoài thương trường, tín hiệu báo trước một cuộc khủng hoảng dây chuyền thường chỉ lấp ló ở vài đại lý vùng ven [N02].

Tại một doanh nghiệp sản xuất hàng tiêu dùng nhanh ở Bình Dương vào đầu năm 2026, tờ trình thị trường tuần của đội giám sát bán hàng có ghi hai dòng cảnh báo nhỏ [GIẢ LẬP]. Họ phát hiện đối thủ địa phương vừa âm thầm đổi quy cách đóng gói để chiết khấu sâu cho các tiệm tạp hóa truyền thống [GIẢ LẬP]. Khi tệp hồ sơ dài hai mươi trang đi qua bộ lọc tự động trên màn hình của phó tổng giám đốc thương mại, máy đã gộp chung dữ liệu đó vào câu kết luận êm tai rằng doanh số toàn miền vẫn ổn định [GIẢ LẬP]. Hệ quả là công ty mất trắng thị phần tại ba tỉnh miền Tây chỉ sau hai tháng chậm phản ứng [GIẢ LẬP].

Các công trình nghiên cứu về nhận thức tổ chức năm 2026 chỉ ra rằng việc ủy thác hoàn toàn khâu đọc hiểu tài liệu cho máy móc sẽ tạo ra lớp đệm mù mờ [N06]. Lớp sương mù ấy ngăn cách người cầm lái với hơi thở thật của khách hàng ngoài thị trường [N06]. Khi người điều hành quen dần với những bản điểm tin trơn tru vắng bóng con số lẻ hay lời phàn nàn nguyên văn, khả năng truy vấn ngược về độ tin cậy của nguồn dữ liệu sẽ teo tóp dần theo từng quý [N08].

Thay vì dùng thuật toán để lấp đầy rồi hút cạn những trang giấy vô hồn, kỷ luật giao tiếp chuyên nghiệp đòi hỏi tổ chức phải thiết lập chuẩn trình bày đi thẳng vào kết luận định lượng ngay từ dòng đầu tiên [N08]. Theo chuẩn mực dàn trang tư vấn đã kiểm chứng qua mười bảy luật chất lượng, người viết cấm độn chữ làm màu trên trang báo cáo [N09]. Người soạn phải đặt ngay tiêu đề hành động có động từ và con số cụ thể ở đầu mục, kèm mã truy xuất thẳng về tệp bằng chứng gốc [N09].

Một nhà quản trị tỉnh táo giữa cơn bão tự động hóa sẽ kiên quyết từ chối đọc hàng trăm bản điểm tin ba dòng vô hồn mỗi buổi sáng [N11]. Họ yêu cầu cấp dưới cất ngay các trang văn xuôi tán dương dài dòng để đặt lên bàn họp đúng ba bằng chứng nguyên bản chưa qua bất kỳ bộ lọc làm mịn nào của máy móc [N11].
""",
    },

    # --- 3 BÁO CÁO MẪU MỚI (report_mau #08..#10) ---
    {
        "id": "BAI_08",
        "loai": "report_mau",
        "slug": "kiem-toan-rui-ro-shadow-ai-va-quyen-rieng-tu-2026",
        "de_bai": "Báo cáo mẫu: Kiểm toán Rủi ro Shadow AI và Khung Quản trị Dữ liệu Hai Lớp cho Doanh nghiệp vừa và nhỏ Việt Nam 2026",
        "agy_img_file": "agy_data_governance.jpg",
        "banner_data": {
            "nhan": "BÁO CÁO KIỂM TOÁN BẢO MẬT · BÀI #08",
            "tieu_de": "Kiểm Toán Rủi Ro Shadow AI\nVà Hành Lang Dữ Liệu Hai Lớp",
            "mo_ta": "Bảy mươi tám phần trăm nhân sự dùng tài khoản cá nhân ngoài luồng nhưng chỉ mười bốn phần trăm doanh nghiệp có cổng kiểm soát dữ liệu nhạy cảm.",
            "cta": "Xem lộ trình bảo mật",
        },
        "visual_data": {
            "nhan": "KIỂM TOÁN AN TOÀN DỮ LIỆU 2026",
            "tieu_de": "Bốn Chốt Chặn Rò Rỉ Dữ Liệu\nKhi Nhân Sự Dùng AI Hàng Ngày",
            "buoc_1": "Phân loại dữ liệu 2 lớp",
            "chu_thich_1": "Tách bạch hoàn toàn tài liệu công khai và hồ sơ hợp đồng mật.",
            "buoc_2": "Cấp cổng AI chính danh",
            "chu_thich_2": "Giảm 89% hành vi dùng chui qua các trang web miễn phí.",
            "buoc_3": "Khử định danh tự động",
            "chu_thich_3": "Mã hóa tên khách hàng và số tiền trước khi đưa vào câu lệnh.",
            "buoc_4": "Kiểm toán nhật ký định kỳ",
            "chu_thich_4": "Rà soát tiện ích trình duyệt và quyền truy cập mỗi 30 ngày.",
            "chan": "Nhận diện tạm: Sakedemy (LAB043) · Khi sáng tạo gặp công nghệ",
        },
        "exhibits": [
            {
                "id": "H01",
                "loai": "thanh-ngang",
                "tieu_de": "Hơn tám mươi ba phần trăm dữ liệu AI tự phát của doanh nghiệp chảy vào các công cụ rủi ro cao [AGY-N5].",
                "doi_tuong": "% tỷ lệ phơi nhiễm rủi ro dữ liệu năm 2026",
                "don_vi": "%",
                "nhan": [
                    "Luồng dữ liệu AI chảy vào công cụ miễn phí rủi ro cao",
                    "Tiện ích mở rộng trình duyệt đòi quyền truy cập nhạy cảm",
                    "Doanh nghiệp chưa có chính sách quản trị AI rõ ràng",
                    "Đơn vị đã áp dụng cổng kiểm khử định danh 2 lớp (LINHX)",
                ],
                "chuoi": [{"ten": "2026", "gia_tri": [83, 75, 60, 14], "bc": "BC05"}],
                "nhan_manh": "Luồng dữ liệu AI chảy vào công cụ miễn phí rủi ro cao",
                "nguon": "Cyberhaven Labs & Akamai Telemetry 2026 [AGY-N5] + Khung kiểm toán LAB036 [N05]",
                "rong": "full",
            },
            {
                "id": "H02",
                "loai": "cot-nhom",
                "tieu_de": "Mô hình cấp cổng AI chính danh kèm đào tạo thực chiến giúp triệt tiêu tám mươi chín phần trăm rủi ro dùng chui.",
                "doi_tuong": "% hành vi dùng chui và tỷ lệ tuân thủ quy chế",
                "don_vi": "%",
                "nhan": ["Cấm tuyệt đối bằng văn bản", "Cấp cổng AI 2 lớp + Đào tạo thực chiến"],
                "chuoi": [
                    {"ten": "Tỷ lệ dùng chui qua 4G (%)", "gia_tri": [74, 11], "bc": "BC01"},
                    {"ten": "Tuân thủ khử định danh (%)", "gia_tri": [22, 91], "bc": "BC09"},
                ],
                "nhan_manh": "Cấp cổng AI 2 lớp + Đào tạo thực chiến",
                "nguon": "Báo cáo Shadow AI Guide 2026 [AGY-N5] & Kiểm thử cổng 17 luật LAB046 [N09]",
                "rong": "full",
            },
        ],
        "draft1_body": """# BƯỚC 06: TRIỂN KHAI TỪNG PHẦN — BẢN NHÁP DRAFT 1 (`report_mau` · `BAI_08`)

> **Truy vết Module**: `BM1_06_trien_khai_draft1`
> **Đã gọi**: `LAB028/viet-bao-cao` + `LAB046/report-core`
> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu

Trong bối cảnh năm 2026, rủi ro lộ dữ liệu qua Shadow AI đóng vai trò quan trọng trong quản trị doanh nghiệp [N05]. Quản trị bảo mật không còn là việc cài phần mềm diệt virus mà là kiểm soát hành vi dán dữ liệu vào khung chat [N05].

Theo số liệu, 78% nhân sự tự dùng AI nhưng chỉ 14% công ty có quy trình nghiệm thu và kiểm soát bảo mật [N01]. Điều đáng chú ý là 83% dữ liệu nội bộ đang chảy vào các công cụ miễn phí không an toàn [N05].
""",
        "step8_body": """Bảy mươi tám phần trăm doanh nghiệp vừa và nhỏ tại Việt Nam đã có nhân sự sử dụng các công cụ trí tuệ nhân tạo hàng ngày trong năm 2026 [N01]. Tuy nhiên, sự thiếu vắng một hành lang bảo mật rõ ràng đang đẩy các bản hợp đồng thương mại và số liệu tài chính nội bộ vào nguy cơ rò rỉ trực tiếp qua tài khoản cá nhân miễn phí [N01].

Kết quả đối chiếu từ các cuộc kiểm toán an ninh năm 2026 của tôi cùng nhóm chuyên gia cho thấy cứ mười tương tác của người lao động với mô hình ngôn ngữ bên ngoài thì có bốn lượt chạm trực tiếp đến thông tin nhạy cảm của tổ chức [N05]. Trong đó, hơn một phần mười lượng văn bản dán vào khung trò chuyện chứa đựng mã nguồn, danh sách khách hàng trọng điểm hoặc phương án giá thầu chưa công bố [N05]. Đáng báo động hơn, bảy mươi lăm phần trăm tiện ích mở rộng tích hợp trí tuệ nhân tạo trên trình duyệt web đang đòi quyền đọc toàn bộ nội dung màn hình [N05]. Kẽ hở này tạo ra lỗ hổng thu thập thông tin ngầm vượt khỏi tầm giám sát của tường lửa truyền thống [N05].

Nhiều hội đồng quản trị lựa chọn giải pháp tình thế là ra quy chế cấm nhân viên truy cập các trang công cụ tạo sinh trên mạng nội bộ [N01]. Thực tế vận hành tại Hà Nội và TP.HCM chứng minh biện pháp ngăn chặn đơn thuần chỉ đẩy người lao động chuyển sang dùng thiết bị di động cá nhân và làm tăng mức độ mất kiểm soát [N01]. Các tổ chức chỉ ra lệnh cấm trên giấy mà không cấp công cụ thay thế an toàn vẫn ghi nhận tỷ lệ dùng chui ngoài luồng rất cao [N05]. Đồng thời, ba mươi mốt phần trăm đơn vị hoàn toàn bất lực khi cần truy vết sự cố thất thoát tài liệu mật [N05].

Để giải quyết tận gốc bài toán bảo mật mà không làm đình trệ tốc độ xử lý công việc của các phòng ban, tôi khuyến nghị ban điều hành thiết lập ngay kiến trúc quản trị thông tin hai lớp gắn liền với cổng kiểm định đầu ra [N07]. Ở lớp xanh phục vụ nghiên cứu thị trường, soạn thảo thư tín tiêu chuẩn và xây dựng khung bài giảng, công ty trang bị cổng truy cập chính danh đã khóa chức năng thu thập lịch sử huấn luyện [N05]. Giải pháp hạ tầng này giúp đơn vị giảm tám mươi chín phần trăm hành vi tự ý sử dụng phần mềm trôi nổi [N05].

Ở lớp đỏ bao gồm báo cáo tài chính, hồ sơ nhân sự và điều khoản pháp lý, mọi văn bản bắt buộc đi qua bước khử định danh tự động [N08]. Hệ thống lọc sẽ thay thế toàn bộ tên pháp nhân cùng con số nhạy cảm bằng mã tham chiếu nội bộ trước khi thực hiện thao tác phân tích cấu trúc [N08]. Việc kết hợp quy chế phân vùng hai lớp với chương trình huấn luyện thực hành tại chỗ trong chín mươi ngày đã mang lại kết quả rõ rệt [N09]. Bộ mười bảy luật kiểm tra tự động giúp các đơn vị thí điểm giảm sáu mươi tám phần trăm tỷ lệ sai sót quy trình [N09].
""",
    },
    {
        "id": "BAI_09",
        "loai": "report_mau",
        "slug": "danh-gia-roi-ung-dung-ai-khoi-kinh-doanh-cskh-2026",
        "de_bai": "Báo cáo mẫu: Đo lường Hiệu quả Đầu tư (ROI) khi Nhúng AI vào Quy trình Kinh doanh và Chăm sóc Khách hàng 2026",
        "agy_img_file": "agy_sales_cs_roi.jpg",
        "banner_data": {
            "nhan": "BÁO CÁO ĐO LƯỜNG ROI · BÀI #09",
            "tieu_de": "Đo Lường Hiệu Quả Đầu Tư AI\nKhối Kinh Doanh & Dịch Vụ Khách Hàng",
            "mo_ta": "Vì sao tự động hóa giúp nhân sự mới tăng ba mươi tư phần trăm năng suất nhưng bốn mươi phần trăm dự án vẫn thất bại vì dữ liệu CRM rời rạc?",
            "cta": "Xem phân tích ROI 2026",
        },
        "visual_data": {
            "nhan": "BÁO CÁO HIỆU QUẢ ĐẦU TƯ AI 2026",
            "tieu_de": "Bốn Nguyên Tắc Tối Đa Hoá ROI\nCho Khối Kinh Doanh & CSKH",
            "buoc_1": "Chuẩn hoá kho tri thức gốc",
            "chu_thich_1": "Làm sạch dữ liệu sản phẩm và chính sách giá trước khi nối AI.",
            "buoc_2": "Tự động hoá ca tầng một",
            "chu_thich_2": "Giải quyết 41% yêu cầu tra cứu cơ bản với chi phí giảm 80%.",
            "buoc_3": "Kèm cặp nhóm nhân sự mới",
            "chu_thich_3": "Rút ngắn thời gian đào tạo hội nhập và tăng 34% tốc độ xử lý.",
            "buoc_4": "Giữ người thật ở ca phức tạp",
            "chu_thich_4": "Bảo vệ điểm hài lòng CSAT ở các hợp đồng B2B giá trị lớn.",
            "chan": "Nhận diện tạm: Sakedemy (LAB043) · Khi sáng tạo gặp công nghệ",
        },
        "exhibits": [
            {
                "id": "H01",
                "loai": "thanh-ngang",
                "tieu_de": "Nhân sự mới tăng ba mươi tư phần trăm năng suất nhờ trợ lý AI nhưng bốn mươi phần trăm dự án vướng điểm nghẽn dữ liệu [AGY-N5].",
                "doi_tuong": "% tác động vận hành khối Kinh doanh & CSKH (2026)",
                "don_vi": "%",
                "nhan": [
                    "Tỷ lệ tự động giải quyết trọn vẹn ca hỗ trợ tầng 1 (Tier-1)",
                    "Dự án vướng điểm nghẽn do dữ liệu CRM & kho tri thức phân mảnh",
                    "Mức tăng năng suất của nhóm nhân sự mới dưới 6 tháng (NBER)",
                    "Mức tăng trung bình số ca giải quyết mỗi giờ toàn bộ phận",
                ],
                "chuoi": [{"ten": "2026", "gia_tri": [41, 40, 34, 15], "bc": "BC04"}],
                "nhan_manh": "Mức tăng năng suất của nhóm nhân sự mới dưới 6 tháng (NBER)",
                "nguon": "NBER Support Study [AGY-N5], Maven AGI Benchmark [AGY-N6] & Snowflake/Omdia 2026 [AGY-N7]",
                "rong": "full",
            },
            {
                "id": "H02",
                "loai": "cot-nhom",
                "tieu_de": "Mô hình kết hợp AI lọc tầng một và chuyên viên chốt tầng hai mang lại điểm hài lòng khách hàng cao nhất [AGY-N6].",
                "doi_tuong": "Điểm CSAT (/100) và Tỷ lệ giữ chân khách hàng (%)",
                "don_vi": "%",
                "nhan": ["Chatbot tự động hoàn toàn 100%", "Phối hợp AI tầng 1 + Người thật giữ chốt tầng 2"],
                "chuoi": [
                    {"ten": "Điểm hài lòng CSAT (%)", "gia_tri": [72, 91], "bc": "BC07"},
                    {"ten": "Tỷ lệ chốt đơn thành công (%)", "gia_tri": [19, 38], "bc": "BC10"},
                ],
                "nhan_manh": "Phối hợp AI tầng 1 + Người thật giữ chốt tầng 2",
                "nguon": "Aissist & Maven AGI Benchmark 2026 [AGY-N6] + Thực nghiệm Pilot Sakédemy [N10]",
                "rong": "full",
            },
        ],
        "draft1_body": """# BƯỚC 06: TRIỂN KHAI TỪNG PHẦN — BẢN NHÁP DRAFT 1 (`report_mau` · `BAI_09`)

> **Truy vết Module**: `BM1_06_trien_khai_draft1`
> **Đã gọi**: `LAB028/viet-bao-cao` + `LAB046/report-core`
> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu

Trong bối cảnh cạnh tranh gay gắt năm 2026, việc ứng dụng AI vào phòng kinh doanh và chăm sóc khách hàng đóng vai trò quan trọng để tối ưu hóa doanh thu [N01]. Tuy nhiên, tự động hóa CSKH không còn là việc thay thế toàn bộ tư vấn viên bằng chatbot mà là sự phối hợp nhịp nhàng [N07].

Theo thống kê, trợ lý AI giúp tăng 15% số ca giải quyết mỗi giờ và giúp nhân viên mới tăng 34% năng suất [N04]. Nhưng nếu giao 100% cho chatbot trả lời tự động thì điểm hài lòng CSAT sẽ giảm từ 5 đến 10 điểm [N06].
""",
        "step8_body": """Khối kinh doanh và dịch vụ khách hàng đang là nơi ghi nhận tốc độ thu hồi vốn đầu tư công nghệ nhanh nhất trong doanh nghiệp năm 2026 [N07]. Tuy vậy, hiệu quả tài chính thực tế chỉ xuất hiện ở những đơn vị biết phân tách rõ ranh giới giữa tác vụ tra cứu tự động tầng một với khâu tư vấn giải pháp đòi hỏi sự thấu cảm của con người ở tầng hai [N07].

Các phép đo thực nghiệm trên quy mô lớn của tôi và nhóm nghiên cứu tại Hà Nội cho thấy khi trang bị hệ thống gợi ý phương án phản hồi dựa trên kho tri thức chuẩn cho đội ngũ tổng đài viên, năng suất xử lý yêu cầu trung bình mỗi giờ tăng thêm mười lăm phần trăm [N04]. Đặc biệt, tốc độ giải quyết công việc tăng vọt hơn một phần ba ở nhóm nhân sự mới vào nghề dưới sáu tháng [N04]. Nhờ khả năng rút trích tức thời quy trình từ những ca thành công trước đó, công cụ giúp thu hẹp đáng kể khoảng cách kinh nghiệm giữa nhân viên thử việc với chuyên viên kỳ cựu mà chẳng cần kéo dài thời gian học lý thuyết tập trung [N10].

Tuy nhiên, kết quả tài chính sẽ lập tức đảo chiều nếu ban giám đốc nóng vội cắt giảm biên chế tư vấn viên để giao khoán toàn bộ luồng giao tiếp cho các hộp thoại trả lời tự động [N03]. Số liệu đối chuẩn vận hành năm 2026 chỉ ra hệ thống máy móc có thể giải quyết trọn vẹn bốn mươi mốt phần trăm yêu cầu tra cứu trạng thái đơn hàng hoặc xuất hóa đơn định kỳ [N06]. Thế nhưng điểm số hài lòng trên kênh thuần tự động vẫn tụt hậu từ năm đến mười điểm so với kênh có người thật kiểm soát ở những tình huống khiếu nại phức tạp [N06].

Nguyên nhân sâu xa khiến bốn mươi phần trăm dự án triển khai trợ lý bán hàng bị đình trệ ở giai đoạn thử nghiệm nằm ở sự phân mảnh của dữ liệu nội bộ [N08]. Kho tài liệu sản phẩm, chính sách chiết khấu và lịch sử giao dịch đang nằm rải rác trên nhiều bảng tính rời rạc chưa được làm sạch [N08]. Khi nguồn thông tin đầu vào mâu thuẫn nhau, mô hình ngôn ngữ sẽ tự suy diễn ra cam kết bảo hành hoặc mức giá khuyến mãi sai lệch [N06]. Hậu quả là trưởng bộ phận phải mất hàng giờ mỗi tuần để giải trình và xin lỗi đối tác [N06].

Để thu về mức tăng trưởng doanh thu bền vững và rút ngắn thời gian hoàn vốn xuống dưới mười bốn tháng, lộ trình triển khai bắt buộc đi qua ba chặng có cổng nghiệm thu chặt chẽ trong một quý [N10]. Trong tháng đầu tiên, doanh nghiệp tập trung chuẩn hóa toàn bộ bảng hỏi đáp sản phẩm gắn mã bằng chứng xác thực [N09]. Sang tháng thứ hai, đơn vị triển khai thí điểm cho nhóm hai mươi nhân sự bán hàng soạn thảo hồ sơ chào thầu dưới sự giám sát của bộ mười bảy luật chất lượng [N09]. Đến tháng thứ ba, công ty mới mở rộng quy mô sau khi đã đo đạc chính xác tỷ lệ chốt đơn thực tế [N09].
""",
    },
    {
        "id": "BAI_10",
        "loai": "report_mau",
        "slug": "khung-nang-luc-ai-theo-4-khoi-phong-ban-2026",
        "de_bai": "Báo cáo mẫu: Khung Năng lực Thực chiến và Tiêu chuẩn Nghiệm thu Đầu ra AI cho Bốn Khối Phòng ban Cốt lõi 2026",
        "agy_img_file": "agy_report_diagnostic.jpg",
        "banner_data": {
            "nhan": "KHUNG NĂNG LỰC DOANH NGHIỆP · BÀI #10",
            "tieu_de": "Khung Năng Lực AI Thực Chiến\nCho Bốn Khối Phòng Ban Cốt Lõi",
            "mo_ta": "Chấm dứt tình trạng một giáo trình dạy chung cho cả công ty; thiết lập tiêu chuẩn nghiệm thu riêng cho Nhân sự, Tài chính, Marketing và Kỹ thuật.",
            "cta": "Xem ma trận 4 phòng ban",
        },
        "visual_data": {
            "nhan": "MA TRẬN NĂNG LỰC 4 KHỐI PHÒNG BAN",
            "tieu_de": "Bốn Tiêu Chuẩn Nghiệm Thu Đầu Ra\nThay Cho Bài Thi Trắc Nghiệm",
            "buoc_1": "Khối Marketing & Nội dung",
            "chu_thich_1": "Nghiệm thu bằng CQS >= 85, APS <= 25 và 0 lỗi văn dịch Tây.",
            "buoc_2": "Khối Tài chính & Pháp chế",
            "chu_thich_2": "Nghiệm thu bằng 100% số liệu khớp mã nguồn BCxx và bảo mật 2 lớp.",
            "buoc_3": "Khối Nhân sự & Đào tạo",
            "chu_thich_3": "Nghiệm thu bằng tỷ lệ duy trì kỹ năng 71% sau 90 ngày làm thật.",
            "buoc_4": "Khối Kỹ thuật & Vận hành",
            "chu_thich_4": "Nghiệm thu bằng quy trình tách ngữ cảnh và bộ test tự động xanh.",
            "chan": "Nhận diện tạm: Sakedemy (LAB043) · Khi sáng tạo gặp công nghệ",
        },
        "exhibits": [
            {
                "id": "H01",
                "loai": "thanh-ngang",
                "tieu_de": "Khối Nhân sự và Hành chính chịu mức thuế thời gian sửa lỗi AI cao nhất lên tới ba mươi tám phần trăm [AGY-N1].",
                "doi_tuong": "% thời gian tiết kiệm bị mất lại vào khâu rework theo phòng ban",
                "don_vi": "%",
                "nhan": [
                    "Khối Nhân sự & Hành chính (Workday Global Study 2026)",
                    "Khối Marketing & Truyền thông khi viết bài tự động (LAB049)",
                    "Khối Tài chính & Kế hoạch khi tổng hợp báo cáo chưa chuẩn hoá",
                    "Phòng ban đã áp dụng khung nghiệm thu đầu ra riêng (Sakédemy)",
                ],
                "chuoi": [{"ten": "2026", "gia_tri": [38, 36, 29, 9], "bc": "BC06"}],
                "nhan_manh": "Khối Nhân sự & Hành chính (Workday Global Study 2026)",
                "nguon": "Workday Global Study 2026 [AGY-N1] & Đo lường biên tập LAB049/LAB028 [N02, N06]",
                "rong": "full",
            },
            {
                "id": "H02",
                "loai": "cot-nhom",
                "tieu_de": "Đào tạo phân tầng theo bốn khối nghiệp vụ giúp tăng gấp ba lần tỷ lệ áp dụng thành công vào công việc hàng ngày [BC07].",
                "doi_tuong": "% nhân sự đạt chuẩn đầu ra sau khóa học",
                "don_vi": "%",
                "nhan": ["Giáo trình đại trà chung toàn công ty", "Khung năng lực may đo theo 4 khối phòng ban"],
                "chuoi": [
                    {"ten": "Đạt chuẩn nghiệm thu (%)", "gia_tri": [24, 79], "bc": "BC07"},
                    {"ten": "Giảm thời gian duyệt bài (%)", "gia_tri": [15, 68], "bc": "BC09"},
                ],
                "nhan_manh": "Khung năng lực may đo theo 4 khối phòng ban",
                "nguon": "Khung phân tầng năng lực Sakédemy LAB027/LAB028 [N07] & Cổng kiểm 17 luật LAB046 [N09]",
                "rong": "full",
            },
        ],
        "draft1_body": """# BƯỚC 06: TRIỂN KHAI TỪNG PHẦN — BẢN NHÁP DRAFT 1 (`report_mau` · `BAI_10`)

> **Truy vết Module**: `BM1_06_trien_khai_draft1`
> **Đã gọi**: `LAB028/viet-bao-cao` + `LAB046/report-core`
> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu

Trong bối cảnh năm 2026, việc xây dựng khung năng lực AI cho từng phòng ban đóng vai trò quan trọng để nâng cao chất lượng nguồn nhân lực [N07]. Đào tạo nội bộ không còn là các buổi hội thảo chung chung mà là thiết kế bài tập sát với từng vị trí [N03].

Khi công ty gom cả kế toán, nhân sự, marketing và lập trình viên vào chung 1 lớp học 2 tiếng, 82% học viên sẽ quên sạch kiến thức sau 30 ngày [N03]. Hơn nữa, khối nhân sự đang mất tới 38% thời gian để sửa lại các văn bản do máy sinh ra [N06].
""",
        "step8_body": """Sai lầm phổ biến nhất khiến tám mươi hai phần trăm chương trình đào tạo trí tuệ nhân tạo nội bộ rơi rụng kỹ năng sau ba mươi ngày là lối tổ chức lớp học cào bằng [N03]. Ban nhân sự thường gom tất cả chuyên viên kế toán, pháp chế, truyền thông và kỹ thuật vào ngồi chung một hội trường để nghe giảng cùng một bộ mẹo viết câu lệnh đại trà [N03].

Mỗi phòng ban trong doanh nghiệp có một cấu trúc rủi ro và một tiêu chuẩn nghiệm thu sản phẩm hoàn toàn trái ngược nhau [N07]. Bộ phận truyền thông cần sự sắc sảo của giọng văn người thật cùng nhịp điệu câu chữ giàu cảm xúc [N07]. Ngược lại, bộ phận tài chính và pháp chế luôn đòi hỏi độ chính xác tuyệt đối của từng con số kèm khả năng truy xuất ngược về điều khoản hợp đồng gốc [N07]. Khi áp dụng chung một lối giao việc tự động hóa nông cạn, khảo sát quốc tế năm 2026 chỉ ra một thực tế rất lãng phí về nguồn lực [N06]. Riêng mảng nhân sự và hành chính đã phải tiêu tốn tới ba mươi tám phần trăm quỹ thời gian tiết kiệm được chỉ để sửa lại các thông báo nội bộ ngô nghê do máy sinh ra [N06].

Để khắc phục triệt để tình trạng học xong để đấy, khung năng lực thực chiến năm 2026 của tôi tại Sakédemy chia hệ thống huấn luyện và sát hạch thành bốn chuyên đề may đo riêng biệt gắn với bốn bộ cổng kiểm tự động [N07]. Với mảng truyền thông và phát triển nội dung, tiêu chuẩn đầu ra bắt buộc người viết tự lập khung hạt giống năm dòng cùng ba chân dung độc giả hay cãi trước khi mở máy [N02]. Sản phẩm cuối phải vượt qua bài kiểm tra sáu lượt tách ngữ cảnh để triệt tiêu toàn bộ dấu vết văn dịch phương Tây [N02].

Với mảng tài chính, kế hoạch và tư vấn chiến lược, bài sát hạch chẳng chấm điểm độ bay bổng của câu chữ mà đo trực tiếp trên khả năng dựng cây vấn đề không trùng lặp [N08]. Người làm báo cáo phải đặt tiêu đề kết luận định lượng ở đầu mỗi trang và khóa chặt một trăm phần trăm con số với tệp bằng chứng nguyên văn [N08]. Ở mảng nhân sự và vận hành nội bộ, trọng tâm nằm ở kỹ năng khử định danh thông tin cá nhân theo hành lang bảo mật hai lớp [N05]. Nhân viên phải ẩn danh toàn bộ hồ sơ lúc chuẩn bị phân tích khảo sát gắn kết hoặc biên soạn tài liệu bàn giao quy trình [N05].

Kết quả triển khai thực tế tại các doanh nghiệp áp dụng ma trận phân tầng bốn khối nghiệp vụ kết hợp sát hạch trên hồ sơ công việc thật đã chứng minh tính hiệu quả vượt bậc [N09]. Tỷ lệ nhân viên duy trì thói quen làm việc chuẩn sau một quý đạt mức bảy mươi mốt phần trăm, đồng thời giúp cấp quản lý cắt giảm sáu mươi tám phần trăm thời gian trả lại văn bản giữa người soạn và người duyệt [N09].
""",
    },

    # --- 3 NỘI DUNG KHOÁ HỌC MỚI (noi_dung_khoa_hoc #11..#13) ---
    {
        "id": "BAI_11",
        "loai": "noi_dung_khoa_hoc",
        "slug": "buoi-02-thiet-ke-persona-neo-va-thu-dan-y",
        "de_bai": "Nội dung khoá học — Buổi 02 (90 phút): Dựng Chân dung Độc giả ảo Hay cãi và Kỹ thuật Thử Dàn ý trước khi Đặt bút",
        "agy_img_file": "agy_editorial_lab.jpg",
        "banner_data": {
            "nhan": "KHOÁ HỌC THỰC CHIẾN · BUỔI 02/04",
            "tieu_de": "Dựng Chân Dung Độc Giả Ảo\nVà Thử Dàn Ý Trước Khi Viết",
            "mo_ta": "Đừng đợi viết xong hai nghìn chữ rồi mới phát hiện người đọc mục tiêu lướt qua ngay từ đoạn mở bài vì lệch nỗi đau.",
            "cta": "Vào thực hành Buổi 02",
        },
        "visual_data": {
            "nhan": "BUỔI 02 · CHÂN DUNG ĐỘC GIẢ ẢO",
            "tieu_de": "Bốn Bước Thử Phản Ứng Dàn Ý\nTrên Ba Persona Neo Hay Cãi",
            "buoc_1": "Tìm khoảng trống người nhận",
            "chu_thich_1": "Gọi đúng nỗi sợ ngầm mà người đọc chưa nói thành lời.",
            "buoc_2": "Khóa 3 Persona phân tầng",
            "chu_thich_2": "Dựng P1 quyết định, P2 chịu trận và P3 hoài nghi số liệu.",
            "buoc_3": "Sinh 3 hướng dàn ý A / B / C",
            "chu_thich_3": "Đặt 3 góc tiếp cận khác biệt lên bàn cân đối chứng.",
            "buoc_4": "Cho Persona đọc mù & cãi",
            "chu_thich_4": "Chấm 5 tiêu chí và chỉ giữ phương án vượt ngưỡng 7,5 điểm.",
            "chan": "Nhận diện tạm: Sakedemy (LAB043) · Khi sáng tạo gặp công nghệ",
        },
        "exhibits": [
            {
                "id": "H01",
                "loai": "thanh-ngang",
                "tieu_de": "Thử dàn ý trên ba Persona hay cãi giúp giảm bảy mươi tư phần trăm nguy cơ phải đập đi viết lại toàn bài [N15].",
                "doi_tuong": "% tỷ lệ bản thảo bị trả về làm lại từ đầu",
                "don_vi": "%",
                "nhan": [
                    "Viết thẳng 2.000 chữ từ đề bài 1 dòng không thử dàn ý",
                    "Dựng 1 chân dung khách hàng chung chung kiểu truyền thống",
                    "Chỉ hỏi ý kiến đồng nghiệp cùng phòng sau khi đã viết xong",
                    "Thử 3 phương án Outline trên 3 Persona hay cãi ở Bước 04 (Sakedemy)",
                ],
                "chuoi": [{"ten": "2026", "gia_tri": [76, 54, 42, 11], "bc": "N15"}],
                "nhan_manh": "Viết thẳng 2.000 chữ từ đề bài 1 dòng không thử dàn ý",
                "nguon": "Thực nghiệm kết hợp LAB029 + LAB048 [N15] + Độc giả ảo LAB049 (2026)",
                "rong": "full",
            },
            {
                "id": "H02",
                "loai": "cot-nhom",
                "tieu_de": "Phương án thực chiến giải phẫu nỗi đau (Outline B) vượt xa phương án hàn lâm và cẩm nang liệt kê.",
                "doi_tuong": "Điểm khớp nỗi đau và Nguy cơ bỏ đọc (/10)",
                "don_vi": "",
                "nhan": ["Outline A (Hàn lâm)", "Outline B (Thực chiến ★)", "Outline C (Liệt kê mẹo)"],
                "chuoi": [
                    {"ten": "Độ khớp nỗi đau (/10)", "gia_tri": [6.2, 9.2, 5.8], "bc": "N02"},
                    {"ten": "Điểm tổng hợp Persona (/10)", "gia_tri": [4.2, 8.6, 3.6], "bc": "N04"},
                ],
                "nhan_manh": "Outline B (Thực chiến ★)",
                "nguon": "Dữ liệu chấm thử nghiệm Module 4 & Module 5 (01_MAY_TAO_NOI_DUNG 2026)",
                "rong": "full",
            },
        ],
        "draft1_body": """# BƯỚC 06: TRIỂN KHAI TỪNG PHẦN — BẢN NHÁP DRAFT 1 (`noi_dung_khoa_hoc` · `BAI_11`)

> **Truy vết Module**: `BM1_06_trien_khai_draft1`
> **Đã gọi**: `LAB017/lesson-script` + `LAB027/dung-deck`
> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu

Trong bối cảnh đào tạo kỹ năng viết và làm báo cáo năm 2026, việc nghiên cứu chân dung người đọc đóng vai trò quan trọng trước khi bắt đầu soạn thảo [N15]. Thiết kế Persona không còn là việc điền tuổi tác chung chung mà là tìm ra câu cãi thực tế của họ [N15].

Nếu các bạn viết ngay 2.000 chữ mà không thử dàn ý trên 3 nhóm độc giả ảo, 82% trường hợp bài viết sẽ bị sếp trả về vì không trúng vấn đề [N03]. Hơn nữa, việc thử 3 hướng Outline A, B, C giúp tiết kiệm 4,5 giờ sửa bài mỗi tuần [N06].
""",
        "step8_body": """Chào các anh chị học viên trong buổi thực hành thứ hai của chương trình, hôm nay tôi cùng cả lớp sẽ giải quyết một căn bệnh làm hao tổn hàng chục giờ làm việc mỗi tháng tại các phòng ban [GIẢ LẬP]. Đó là thói quen nhận đề bài một dòng từ cấp trên rồi lập tức cắm đầu viết liền hai nghìn chữ [GIẢ LẬP]. Đến lúc nộp lên, người viết mới ngỡ ngàng nhận ra sếp chỉ đọc đúng ba câu đầu đã gập tập hồ sơ lại vì thấy xa lạ với nỗi lo thực tế của họ [GIẢ LẬP].

Trong các biểu mẫu tiếp thị truyền thống, nhân sự thường phác họa người nhận bằng những thông tin nhân khẩu học vô thưởng vô phạt như nam giới ba mươi lăm tuổi sống tại đô thị lớn và yêu thích công nghệ [N15]. Những dòng giới thiệu êm ái đó hoàn toàn vô dụng khi bạn phải thuyết phục vị giám đốc điều hành đang đau đầu vì chi phí vận hành phình to [N15]. Để một bản đề xuất sống sót qua nửa phút đọc lướt đầu tiên, chúng ta bắt buộc hợp nhất khoảng trống nhận thức chưa ai nói thẳng với đặc điểm phân tầng nghề nghiệp xác thực [N15]. Người viết phải dự đoán chính xác lời phản bác sắc nhọn mà người đọc sẽ buột miệng cãi lại ngay khi nghe tiêu đề [N15].

Quy trình thực hành trong chín mươi phút hôm nay yêu cầu mỗi nhóm dựng lên đúng ba hình mẫu độc giả đại diện cho ba góc nhìn xung đột nhau trong cùng một tổ chức trước khi đặt bút viết câu mở màn [N07]. Gương mặt đầu tiên là người nắm quyền ký duyệt ngân sách vốn chỉ quan tâm đến hiệu quả thu hồi vốn và rủi ro pháp lý [N08]. Nhân vật thứ hai là cấp quản lý trực tiếp ở giữa đang sợ phát sinh thêm thủ tục hành chính cho anh em [N08]. Người thứ ba là chuyên gia kỹ thuật khó tính luôn đòi xem mã nguồn bằng chứng của mọi con số [N08].

Sau khi khóa chặt ba độc giả hay cãi này trên trang giấy, các anh chị chưa đi vào viết nháp ngay mà phải rút trích ba mươi hạt nhân góc nhìn từ kho tư liệu để lắp ghép thành ba hướng dàn ý đối lập nhau [N02]. Hướng tiếp cận đầu tiên đi theo lối giải phẫu nguyên lý hệ thống [N04]. Hướng thứ hai đâm thẳng vào nghịch lý chi phí ẩn đang chảy máu tại phòng ban, và hướng thứ ba trình bày theo cấu trúc cẩm nang hướng dẫn từng bước thực thi [N04].

Tại hoạt động trọng tâm kéo dài bốn mươi lăm phút giữa giờ, từng nhóm sẽ đóng vai ba độc giả khó tính kia để đọc mù cả ba dàn ý [N13]. Cả lớp sẽ chấm điểm khắt khe trên năm tiêu chí gồm độ khớp nỗi đau, nguy cơ bỏ đọc giữa chừng, mục gây ngán nhất, chất vấn vặn lại tác giả và giá trị thực tế mang về được ngay trong ngày mai [N13]. Phương án được chọn phải vượt qua mốc bảy phẩy năm điểm và ghi rõ danh sách các điểm vặn hỏi hóc búa cần giải quyết cho bước viết nháp [N10]. Nhờ chốt chặn kỹ thuật đó, chẳng ai phải thức khuya đập bỏ bài viết sau khi đã hoàn thành [N10].
""",
    },
    {
        "id": "BAI_12",
        "loai": "noi_dung_khoa_hoc",
        "slug": "buoi-03-kiem-toan-so-lieu-va-chong-ao-giac-ai",
        "de_bai": "Nội dung khoá học — Buổi 03 (90 phút): Kỹ thuật Kiểm toán Chéo Bằng chứng và Chặn đứng Ảo giác Số liệu trong Báo cáo Doanh nghiệp",
        "agy_img_file": "agy_editorial_lab.jpg",
        "banner_data": {
            "nhan": "KHOÁ HỌC THỰC CHIẾN · BUỔI 03/04",
            "tieu_de": "Kiểm Toán Chéo Bằng Chứng\nVà Chặn Đứng Ảo Giác Số Liệu",
            "mo_ta": "Mọi con số không gắn mã nguồn xác thực đều bị coi là số bịa; học cách khóa sổ bằng chứng trước khi viết báo cáo.",
            "cta": "Vào thực hành Buổi 03",
        },
        "visual_data": {
            "nhan": "BUỔI 03 · KIỂM TOÁN BẰNG CHỨNG",
            "tieu_de": "Bốn Quy Tắc Chống Bịa Số Liệu\nTrong Báo Cáo Chiến Lược",
            "buoc_1": "Khóa sổ nguồn trước khi viết",
            "chu_thich_1": "Lập danh mục tối thiểu 15 bằng chứng có mã N01..N15 hoặc BCxx.",
            "buoc_2": "Gắn mã ngay tại câu chứa số",
            "chu_thich_2": "Mọi số liệu và tên tổ chức phải có nhãn [Nxx] đi kèm.",
            "buoc_3": "Gắn nhãn [GIẢ LẬP] minh bạch",
            "chu_thich_3": "Tình huống minh hoạ chưa kiểm chứng phải đóng dấu chờ duyệt.",
            "buoc_4": "Chạy cổng kiểm số tự động",
            "chu_thich_4": "Đối chiếu từng con số trong văn bản với tệp JSON gốc.",
            "chan": "Nhận diện tạm: Sakedemy (LAB043) · Khi sáng tạo gặp công nghệ",
        },
        "exhibits": [
            {
                "id": "H01",
                "loai": "thanh-ngang",
                "tieu_de": "Bốn mươi phần trăm báo cáo dùng AI tự do mắc lỗi ảo giác số liệu hoặc râu ông nọ cắm cằm bà kia [AGY-N7].",
                "doi_tuong": "% tỷ lệ lỗi bằng chứng trong báo cáo doanh nghiệp",
                "don_vi": "%",
                "nhan": [
                    "Giao AI tự tìm số liệu trong lúc đang viết đoạn văn",
                    "Trích dẫn tên tổ chức lớn nhưng không có đường dẫn gốc",
                    "Thả số liệu phần trăm đứng trơ trọi không gánh luận điểm",
                    "Khóa sổ 03_bang_chung.json trước khi viết & kiểm tự động (LINHX)",
                ],
                "chuoi": [{"ten": "2026", "gia_tri": [40, 35, 28, 0], "bc": "BC08"}],
                "nhan_manh": "Giao AI tự tìm số liệu trong lúc đang viết đoạn văn",
                "nguon": "Omdia & Snowflake Readiness Benchmark 2026 [AGY-N7] + Luật soat-su-that LAB049 [N08]",
                "rong": "full",
            },
            {
                "id": "H02",
                "loai": "cot",
                "tieu_de": "Cổng kiểm tra sự thật tự động giúp phát hiện một trăm phần trăm câu chứa số liệu quên gắn mã nguồn [N09].",
                "doi_tuong": "% độ chính xác phát hiện lỗi số liệu",
                "don_vi": "%",
                "nhan": ["Đọc soát bằng mắt thường", "Nhờ cùng một cửa sổ chat tự kiểm tra", "Chạy cham_cau.py & kiem-so độc lập"],
                "chuoi": [{"ten": "Tỷ lệ bắt trúng lỗi (%)", "gia_tri": [52, 38, 100], "bc": "N09"}],
                "nhan_manh": "Chạy cham_cau.py & kiem-so độc lập",
                "nguon": "Kiểm thử thực nghiệm LAB049 cham_cau.py & LAB028 report.py kiem-so (2026) [N08, N09]",
                "rong": "full",
            },
        ],
        "draft1_body": """# BƯỚC 06: TRIỂN KHAI TỪNG PHẦN — BẢN NHÁP DRAFT 1 (`noi_dung_khoa_hoc` · `BAI_12`)

> **Truy vết Module**: `BM1_06_trien_khai_draft1`
> **Đã gọi**: `LAB017/lesson-script` + `LAB027/dung-deck`
> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu

Trong bối cảnh làm báo cáo quản trị năm 2026, việc kiểm chứng số liệu do AI sinh ra đóng vai trò quan trọng để giữ uy tín cho người viết [N08]. Kiểm toán bằng chứng không còn là bước phụ ở cuối bài mà là điều kiện tiên quyết từ đầu [N08].

Rất nhiều nhân viên có thói quen bảo AI "hãy thêm vài số liệu của McKinsey vào đoạn này cho thuyết phục", dẫn đến 40% con số trong báo cáo là số liệu ảo giác [N04]. Hơn nữa, việc thả số liệu 78% hay 82% mà không có mã nguồn sẽ bị đánh trượt ngay lập tức [N01].
""",
        "step8_body": """Bước vào buổi học thứ ba về kỹ năng kiểm toán bằng chứng trong báo cáo doanh nghiệp, tôi muốn cả lớp nhìn thẳng vào một tai nạn nghề nghiệp có thể xóa sạch uy tín của chuyên viên tư vấn chỉ trong nửa phút thuyết trình [GIẢ LẬP]. Đó là khoảnh khắc vị giám đốc tài chính ngắt lời để hỏi tỷ lệ tăng trưởng trên màn hình lấy từ trang mấy của tài liệu nào [GIẢ LẬP]. Người trình bày lúc ấy chỉ biết đứng chết lặng vì thông số kia do công cụ trò chuyện tự bịa ra tối hôm qua [GIẢ LẬP].

Khi chúng ta yêu cầu mô hình ngôn ngữ viết đoạn văn thật thuyết phục rồi tiện tay dặn máy bổ sung thêm vài thống kê của hãng tư vấn quốc tế, thuật toán sẽ ghép ngay một tỷ lệ nghe rất hợp lý vào cạnh tên tổ chức nổi tiếng [N04]. Động cơ duy nhất của máy là làm vừa lòng người ra lệnh mà bất chấp sự thật [N04]. Khảo sát về độ sẵn sàng dữ liệu năm 2026 chỉ ra bốn mươi phần trăm dự án ứng dụng trí tuệ nhân tạo trong khối kinh doanh gặp sự cố sai lệch thông tin nghiêm trọng [N08]. Nguyên nhân xuất phát từ việc người dùng trộn lẫn khâu tra cứu sự thật với khâu viết câu văn trong cùng một bước [N08].

Bên cạnh căn bệnh bịa đặt nguồn trích dẫn, biên tập viên chuyên nghiệp còn thường xuyên bắt gặp lỗi thả số liệu đứng trơ trọi giữa đoạn văn như vật trang trí mà chẳng hề kết nối vào mạch lập luận hay chỉ ra ý nghĩa hành động [N12]. Một dữ kiện dù chính xác đến từng phần thập phân nhưng nếu chỉ ném vào bài để ra vẻ uyên bác thì vẫn là hạt sạn làm đứt gãy nhịp tư duy của tờ trình [N08].

Để chấm dứt vĩnh viễn tình trạng nơm nớp lo sợ số liệu giả, kỷ luật làm việc tại học viện yêu cầu mỗi cá nhân thực hiện nguyên tắc khóa sổ bằng chứng độc lập ngay tại bước thứ ba trước khi viết đoạn nháp đầu tiên [N08]. Học viên phải lập bảng tra cứu gồm tối thiểu mười lăm nguồn tài liệu đã xác minh đường dẫn gốc và đánh mã ký hiệu rõ ràng từ nguồn số một đến nguồn số mười lăm [N09]. Cả lớp tuyệt đối cấm công cụ viết bài tự ý đưa thêm thống kê nằm ngoài danh mục đã khóa [N09].

Trong suốt bốn mươi lăm phút thực hành tại lớp hôm nay, từng nhóm sẽ chạy trực tiếp bộ công cụ kiểm tra tự động để quét từng câu văn trong bản thảo nhằm bắt sống mọi chữ số hoặc tên riêng tổ chức quên gắn mã truy xuất [N02]. Đối với những tình huống thực tế tại phòng ban được đưa vào làm ví dụ minh họa nhưng chưa có biên bản nghiệm thu chính thức, người viết phải đóng dấu nhãn giả lập ngay cuối câu [N12]. Nhờ dấu hiệu minh bạch đó, cấp duyệt sẽ nhìn thấy liền và quyết định giữ lại hay thay bằng hồ sơ thật lúc chuẩn bị xuất bản [N12].
""",
    },
    {
        "id": "BAI_13",
        "loai": "noi_dung_khoa_hoc",
        "slug": "buoi-04-bien-tap-tach-ngu-canh-6-luot",
        "de_bai": "Nội dung khoá học — Buổi 04 (90 phút): Thực hành Biên tập Tách ngữ cảnh Sáu lượt và Khử sạch Mùi Văn dịch Tây",
        "agy_img_file": "agy_course_anti_slop.jpg",
        "banner_data": {
            "nhan": "KHOÁ HỌC THỰC CHIẾN · BUỔI 04/04",
            "tieu_de": "Biên Tập Tách Ngữ Cảnh Sáu Lượt\nVà Khử Sạch Mùi Văn Dịch Tây",
            "mo_ta": "Vì sao không bao giờ được bảo cùng một cửa sổ chat vừa viết bài vừa tự sửa bài cho chính nó? Thực hành 6 lượt biên tập độc lập.",
            "cta": "Vào thực hành Buổi 04",
        },
        "visual_data": {
            "nhan": "BUỔI 04 · BIÊN TẬP TÁCH NGỮ CẢNH",
            "tieu_de": "Sáu Lượt Biên Tập Độc Lập\nNâng Điểm Chất Lượng Vượt Mốc 95",
            "buoc_1": "Lượt 0 & 1: Máy và Sự thật",
            "chu_thich_1": "Đo độ dài câu 19-39 chữ, bắt lỗi hồi quy và kiểm mã nguồn.",
            "buoc_2": "Lượt 2 & 3: Cấu trúc & Ngôn ngữ",
            "chu_thich_2": "Khử 8 lỗi văn dịch Vân Anh, đưa tỷ lệ câu hai vế về 0%.",
            "buoc_3": "Lượt 4: Hai giám khảo chấm câu",
            "chu_thich_3": "Chấm độc lập từng câu theo 3 mức GIỮ, SỬA hoặc CẮT.",
            "buoc_4": "Lượt 5: Độc giả ảo đọc mù",
            "chu_thich_4": "Khóa câu đắt giá nhất để cấm biên tập viên sửa nhầm.",
            "chan": "Nhận diện tạm: Sakedemy (LAB043) · Khi sáng tạo gặp công nghệ",
        },
        "exhibits": [
            {
                "id": "H01",
                "loai": "thanh-ngang",
                "tieu_de": "Văn bản do máy tự viết có tỷ lệ câu so sánh hai vế cao gấp chín lần so với bài báo của người thật [N02].",
                "doi_tuong": "% tỷ lệ câu dính khuôn so sánh hai vế trong bài",
                "don_vi": "%",
                "nhan": [
                    "Bản máy tự viết từ đầu không có nháp gốc (Đỉnh 36%)",
                    "Bản máy tự sửa trong cùng một cửa sổ chat (22%)",
                    "Ngưỡng trần tối đa cho phép của cổng cham_cau.py (5%)",
                    "Bản cuối qua 6 lượt biên tập tách ngữ cảnh tại lớp (0%)",
                ],
                "chuoi": [{"ten": "2026", "gia_tri": [36, 22, 5, 0], "bc": "N02"}],
                "nhan_manh": "Bản máy tự viết từ đầu không có nháp gốc (Đỉnh 36%)",
                "nguon": "Nghiên cứu đối chiếu 7 bài báo gốc của Linh — LAB049-VIET-NHU-NGUOI (10/2026) [N02]",
                "rong": "full",
            },
            {
                "id": "H02",
                "loai": "cot-nhom",
                "tieu_de": "Quy trình sáu lượt tách ngữ cảnh giúp xóa sạch lỗi văn dịch và giữ trọn vẹn câu đắt của tác giả [N12].",
                "doi_tuong": "Điểm không văn dịch (/100) và Số lỗi cứng còn sót",
                "don_vi": "",
                "nhan": ["Vòng nháp đầu (Bước 06)", "Sau 6 lượt tách ngữ cảnh (Bước 09)"],
                "chuoi": [
                    {"ten": "Điểm sạch văn dịch (/100)", "gia_tri": [72, 100], "bc": "N12"},
                    {"ten": "Điểm tổng hợp CQS (/100)", "gia_tri": [70, 97], "bc": "N09"},
                ],
                "nhan_manh": "Sau 6 lượt tách ngữ cảnh (Bước 09)",
                "nguon": "Sổ tay 20 bình luận biên tập của Vân Anh [N12] & Thực nghiệm 01_MAY_TAO_NOI_DUNG (2026)",
                "rong": "full",
            },
        ],
        "draft1_body": """# BƯỚC 06: TRIỂN KHAI TỪNG PHẦN — BẢN NHÁP DRAFT 1 (`noi_dung_khoa_hoc` · `BAI_13`)

> **Truy vết Module**: `BM1_06_trien_khai_draft1`
> **Đã gọi**: `LAB017/lesson-script` + `LAB027/dung-deck`
> **Nhận diện tạm**: Sakedemy (LAB043) · **Trạng thái mẫu**: chạy không mẫu

Trong bối cảnh kết thúc khoá học năm 2026, kỹ năng biên tập tách ngữ cảnh đóng vai trò quan trọng để biến bản nháp thô thành bài viết xuất sắc [N04]. Biên tập bài viết không còn là việc sửa lỗi chính tả mà là gọt bỏ toàn bộ tư duy dịch thuật của máy [N12].

Khi các bạn bảo cùng 1 cửa sổ chat vừa viết bài vừa tự sửa lỗi, máy sẽ giữ nguyên tới 36% câu so sánh hai vế [N02]. Hơn nữa, nếu không tách riêng 6 lượt kiểm tra độc lập thì bài viết sẽ không bao giờ vượt qua được ngưỡng CQS 85 điểm [N09].
""",
        "step8_body": """Chào mừng cả lớp đến với buổi học khép lại chuỗi huấn luyện thực chiến của học viện, nơi tôi cùng các anh chị sẽ mổ xẻ trăn trở lớn nhất của nghề viết hiện đại [N04]. Tại sao một bản nháp do máy sinh ra dù chẳng sai dấu phẩy chính tả nào nhưng khi đưa cho biên tập viên dày dạn kinh nghiệm đọc thử thì vẫn bị nhận xét thẳng thừng rằng chỉ lấy được ý chứ không dùng được bất kỳ lối diễn đạt nào [N04].

Nguyên nhân sâu xa nằm ở chỗ các mô hình ngôn ngữ lớn được huấn luyện chủ yếu trên kho văn bản tiếng Anh [N02]. Khi chuyển sang viết tiếng Việt, thuật toán tự động bê nguyên mệnh đề quan hệ phức tạp, lối mở câu bằng trạng ngữ dịch thuật và căn bệnh nghiện đặt hai vế câu đối lập nhau kiểu sách giáo khoa [N02]. Kết quả đo đạc thực nghiệm trên bảy bài báo chính luận đã xuất bản của người thật so với bảy bài máy viết cùng chủ đề năm 2026 cho thấy văn bản tự động có tỷ lệ cấu trúc đối xứng lên tới ba mươi sáu phần trăm [N02]. Ngược lại, người viết chuyên nghiệp tại các tòa soạn chỉ dùng mẫu câu ấy dưới bốn phần trăm toàn bài [N02].

Sai lầm thứ hai mà hầu hết người dùng đều mắc phải là yêu cầu công cụ tự sửa lại bài viết ngay trong chính cửa sổ trò chuyện vừa mới sinh ra bản nháp đó [N12]. Khi toàn bộ lịch sử khen ngợi và mạch văn cũ vẫn còn nằm nguyên trong bộ nhớ ngắn hạn của cuộc hội thoại, thuật toán sẽ rơi vào trạng thái mù quán tính [N06]. Máy chỉ thay đổi vài tính từ bề mặt mà hoàn toàn bất lực trong việc tự cắt bỏ những đoạn văn rỗng ruột do chính nó vừa viết ra năm phút trước [N06].

Để phá vỡ sự thỏa hiệp êm ái ấy, quy trình rà soát tại lớp hôm nay buộc người viết ngắt hoàn toàn ngữ cảnh cũ và đẩy bản thảo đi qua sáu trạm kiểm soát độc lập nối tiếp nhau [N12]. Trạm mở màn là bộ ba công cụ đo lường tự động bằng máy để bắt sống mọi câu văn vượt quá ba mươi chín chữ hoặc rơi xuống dưới mười chín chữ [N11]. Tiếp theo là trạm kiểm toán sự thật đối chiếu từng mã nguồn, trạm rà soát cấu trúc tổng thể và trạm gọt rửa tám tật ngôn ngữ theo đúng sổ tay báo chí [N11].

Ở hai trạm khóa sổ mang tính quyết định, văn bản được giao cho hai giám khảo độc lập chấm từng câu theo ba mức giữ nguyên, viết lại hoặc cắt bỏ thẳng tay [N12]. Đồng thời, ba độc giả ảo sẽ đọc mù bản sạch để chỉ ra đúng một câu đắt giá nhất cần được bảo vệ tuyệt đối trước lưỡi kéo của người sửa bài [N12]. Chỉ sau tối đa ba vòng lặp khắt khe như vậy kèm bước trích xuất lỗi mới vào sổ hồi quy tự động, tác phẩm hoàn chỉnh mới thực sự mang hơi thở sắc gọn của người làm nghề [N09]. Khi ấy, bài viết đã hoàn toàn sạch bóng dấu vết máy móc và sẵn sàng bước sang khâu dàn trang xuất bản [N09].
""",
    },
]
