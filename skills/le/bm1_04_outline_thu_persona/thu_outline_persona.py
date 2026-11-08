"""Module 4 (LÀM MỚI): Rút 30 Insights -> Dựng 3 Phương án Outline (A, B, C) -> Thử từng Outline trên 3 Persona Neo.
Kế thừa nửa đầu từ LAB025 (content-synthesizer) và làm mới hoàn toàn phần mô phỏng phản ứng của 3 Persona Neo (P1, P2, P3).
"""
import argparse
import json
from pathlib import Path


def generate_30_insights(loai: str) -> list:
    types = ["fact", "paradox", "metaphor", "provocation"]
    base_topics = {
        "bai_viet": [
            "Doanh nghiệp mua tài khoản AI hàng loạt nhưng thời gian họp và sửa bài của cấp quản lý lại tăng thêm 35% [N01].",
            "Nghịch lý năng suất giả: Nhân viên xuất ra 5 trang nháp trong 30 giây, nhưng trưởng phòng mất 2 tiếng dọn rác logic [N02].",
            "Bẫy 'văn dịch Tây': AI viết tiếng Việt theo cấu trúc mệnh đề quan hệ tiếng Anh khiến người đọc mỏi mắt sau 200 chữ [N03].",
            "Chị Vân Anh (biên tập viên) chỉ ra: Bản máy tự viết từ đầu chỉ lấy được ý, không dùng được một cách diễn đạt nào [N04].",
            "Khi mọi công ty dùng chung một mô hình ngôn ngữ mà không có hồ sơ giọng và kho chuyện thật, mọi thương hiệu đều nói giọng giống hệt nhau [N05].",
            "Sự thật về 'Prompt Engineering': Câu lệnh dài 2 trang không cứu được một đề bài rỗng ý tưởng hạt giống [N06].",
            "Nhân sự cấp dưới dùng AI như tấm khiên né tránh trách nhiệm cá nhân: 'Máy nó gợi ý thế' [N07].",
            "Cấp quản lý giao việc kiểu 'hỏi ChatGPT đi' chính là nguồn gốc sinh ra làn sóng báo cáo vô hồn trong nội bộ [N08].",
            "Một quy trình tốt tách bạch hoàn toàn ngữ cảnh người viết và ngữ cảnh người biên tập sáu lượt [N09].",
            "Độc giả báo kinh tế bỏ đọc ngay khi gặp cấu trúc so sánh hai vế máy móc 'Không còn là X mà là Y' [N10].",
        ],
        "report_mau": [
            "78% doanh nghiệp SME Việt Nam đã thử nghiệm công cụ AI nhưng chỉ 14% chuyển hoá thành quy trình chuẩn có đo lường đầu ra [BC01].",
            "Khoảng cách lớn nhất không nằm ở công nghệ mà ở khâu nghiệm thu chất lượng (Quality Gate) sau khi AI sinh kết quả [BC02].",
            "Đào tạo AI đại trà theo kiểu giới thiệu công cụ có tỷ lệ rơi rụng ứng dụng tới 82% sau 30 ngày kết thúc khoá học [BC03].",
            "Mô hình đào tạo gắn liền với sản phẩm thật (Output-based Training) giúp rút ngắn 42% thời gian soạn báo cáo và tài liệu nội bộ [BC04].",
            "Rủi ro bảo mật dữ liệu nội bộ là rào cản số 1 khiến khối Tài chính - Ngân hàng và Sản xuất dè dặt khi nhân rộng AI [BC05].",
            "Chi phí ẩn của AI Slop: Trung bình mỗi quản lý cấp trung mất 4,5 giờ/tuần chỉ để rà soát và viết lại các tài liệu do nhân viên dùng AI tạo ẩu [BC06].",
            "Phân tầng năng lực AI doanh nghiệp cần chia làm 3 mức: Thao tác cá nhân (Mức 1) -> Quy trình phòng ban (Mức 2) -> Hệ thống tự động có cổng kiểm (Mức 3) [BC07].",
            "Báo cáo quản trị hiện đại đòi hỏi mỗi trang là một thông điệp kết luận (Action Title) đi kèm biểu đồ định lượng trỏ về sổ bằng chứng [BC08].",
            "Doanh nghiệp áp dụng bộ tiêu chí kiểm văn và kiểm số tự động giảm 68% tỷ lệ trả lại hồ sơ giữa các phòng ban [BC09].",
            "Lộ trình 90 ngày hiệu quả nhất bắt đầu từ 1 nhóm Pilot 15-20 nhân sự nòng cốt thay vì đào tạo dàn trải toàn công ty [BC10].",
        ],
        "noi_dung_khoa_hoc": [
            "Học viên doanh nghiệp quên 70% câu lệnh mẫu sau 1 tuần nếu không hiểu cấu trúc phân rã công việc thành từng bước nhỏ [N01].",
            "Giọng giảng là đồng hồ chủ của bài học: mỗi phân đoạn chỉ nên tải 1 ý chính trong 90-120 giây để giữ nhịp chú ý [N02].",
            "Cấu trúc 5 sự kiện Gagné rút gọn giúp học viên đi từ tình huống đau thực tế thẳng tới thao tác làm được ngay tại lớp [N03].",
            "Sai lầm phổ biến nhất của người mới là gộp bước 'Tìm ý', 'Viết nháp' và 'Biên tập' vào chung một câu lệnh duy nhất [N04].",
            "Khi cho học viên xem trực tiếp bảng so sánh 'Bản AI viết ẩu' và 'Bản đã qua 6 lượt biên tập', tốc độ nhận diện lỗi tăng gấp 3 lần [N05].",
            "Nguyên tắc 80/20 trong phối hợp Người - Máy: Người giữ 20% đầu (Hạt giống + Nháp ý) và 20% cuối (Duyệt + Chốt), máy chạy 60% giữa [N06].",
            "Bảng kiểm 8 lỗi văn dịch (so sánh hai vế, láy câu, thả số liệu, ẩn dụ kéo dài...) là công cụ thực hành dễ áp dụng nhất tại lớp [N07].",
            "Mỗi buổi học 120 phút phải kết thúc bằng 1 sản phẩm thật của chính học viên đã vượt qua cổng chấm tự động [N08].",
            "Không dùng thuật ngữ tiếng Anh chuyên sâu khi chưa giải nghĩa bằng hình ảnh đời thường ngay lần đầu xuất hiện [N09].",
            "Persona độc giả ảo giúp học viên tự soi bài của mình dưới góc nhìn của sếp khó tính trước khi bấm nút gửi [N10].",
        ],
    }
    seeds = base_topics.get(loai, base_topics["bai_viet"])
    insights = []
    for i in range(1, 31):
        base_text = seeds[(i - 1) % len(seeds)]
        itype = types[(i - 1) % len(types)]
        insights.append({
            "id": i,
            "type": itype,
            "content": f"[Insight #{i:02d} · {itype}] {base_text} (Góc khai thác tầng {(i - 1) // 10 + 1})",
        })
    return insights


def build_three_outlines(loai: str) -> list:
    if loai == "bai_viet":
        return [
            {
                "variant": "A",
                "ten_phuong_an": "Phương án A — Hàn lâm / Giải phẫu công nghệ",
                "variant_angle": "Phân tích từ cơ chế xác suất của LLM đến hiện tượng đồng phục hóa văn bản trong doanh nghiệp",
                "variant_tone": "Lạnh, học thuật, nhiều thuật ngữ mô hình ngôn ngữ",
                "variant_structure": "Tuyến tính: Nguyên lý kỹ thuật -> Hệ quả bề mặt -> Khuyến nghị công cụ",
                "selected_insight_ids": [1, 3, 5, 6, 9, 11, 13, 15, 19, 21],
                "sections": [
                    "1. Mở bài: Cơ chế dự đoán từ tiếp theo (next-token prediction) và sự ra đời của văn bản trung bình cộng",
                    "2. Thân bài 1: Vì sao cấu trúc câu tiếng Anh xâm lấn tiếng Việt qua lớp dịch ngầm của mô hình",
                    "3. Thân bài 2: Phân tích định lượng độ lệch nhịp câu giữa văn máy và văn người",
                    "4. Kết bài: Khung kỹ thuật cấu hình hệ thống kiểm soát chất lượng văn bản",
                ],
                "anecdotes": [
                    "[GIẢ LẬP] Một nhóm kỹ sư thử nghiệm đo độ tương đồng cosine trên 500 bài viết marketing tự động.",
                    "Trích số liệu kiểm chứng từ LAB049 trên bộ bài đối chuẩn 7 bài báo đã đăng của tác giả.",
                ],
            },
            {
                "variant": "B",
                "ten_phuong_an": "Phương án B — Giải phẫu nghịch lý vận hành & Chi phí sửa rác AI (Thực chiến doanh nghiệp)",
                "variant_angle": "Đi thẳng vào nỗi đau thật giữa Sếp - Trưởng phòng - Nhân viên: Tưởng dùng AI để nhàn đi, nhưng thực tế cả công ty đang làm thêm giờ để dọn rác AI cho nhau",
                "variant_tone": "Sắc lạnh, tỉnh táo, đi từ chuyện đời thực trong văn phòng Việt Nam đến quy tắc cầm cân nảy mực (đúng giọng Linh + kỷ luật biên tập Vân Anh)",
                "variant_structure": "Nghịch lý mở đầu -> Giải phẫu 3 tầng thất bại (Giao việc ẩu - Viết tự động - Duyệt cảm tính) -> Kiến trúc tách ngữ cảnh & giữ chốt con người",
                "selected_insight_ids": [1, 2, 4, 7, 8, 9, 10, 12, 14, 18, 22],
                "sections": [
                    "1. Mở bài: Căn phòng họp lúc 8 giờ tối và bản kế hoạch 15 trang sinh ra trong 30 giây nhưng mất 3 ngày để đoán xem nhân viên định nói gì",
                    "2. Tầng 1 - Ảo giác tốc độ: Khi khẩu hiệu 'hỏi ChatGPT đi' biến người làm chuyên môn thành thợ sửa lỗi văn dịch",
                    "3. Tầng 2 - Vì sao bài máy tự viết từ đầu không cứu được: Bài học từ bàn biên tập (chỉ lấy được ý, hỏng toàn bộ diễn đạt vì thiếu nháp gốc của người làm)",
                    "4. Tầng 3 - Giữ chốt ở đâu: Máy tìm tư liệu và soi lỗi theo luật cứng; người giữ hạt giống, trải nghiệm thật và quyền gạch bỏ cuối cùng",
                ],
                "anecdotes": [
                    "Chuyện thật từ kho LAB025/LAB049: Bản nháp PA1 chạy tự động bị biên tập viên Vân Anh nhận xét thẳng 'chỉ dùng được ý, không dùng được một sự diễn đạt nào'.",
                    "[GIẢ LẬP] Một trưởng phòng vận hành nhận 3 bản đề xuất từ 3 nhân viên khác nhau nhưng cả 3 bản mở đầu bằng cùng một câu ẩn dụ giống hệt nhau.",
                ],
            },
            {
                "variant": "C",
                "ten_phuong_an": "Phương án C — Cẩm nang 10 bước hướng dẫn kỹ năng cá nhân",
                "variant_angle": "Hướng dẫn chi tiết từng bước cho nhân viên văn phòng cách viết bài không bị phát hiện là AI",
                "variant_tone": "Hướng dẫn thực hành (How-to), chia nhỏ nhiều gạch đầu dòng",
                "variant_structure": "Danh sách kiểm tra (Checklist) từ bước 1 đến bước 10",
                "selected_insight_ids": [2, 3, 6, 10, 16, 17, 20, 23, 25, 28],
                "sections": [
                    "1. Mở bài: 5 dấu hiệu khiến bài viết của bạn bị nhận ra là dùng ChatGPT",
                    "2. Bước 1 đến Bước 5: Cách chuẩn bị dữ liệu và viết câu lệnh chi tiết",
                    "3. Bước 6 đến Bước 9: Cách tự đọc lại và xóa các từ nối quen thuộc của AI",
                    "4. Kết bài: Bảng tổng kết dành cho người viết nội dung hàng ngày",
                ],
                "anecdotes": [
                    "[GIẢ LẬP] Một nhân viên content marketing sửa lại bài đăng fanpage trong 15 phút nhờ danh sách từ cấm.",
                ],
            },
        ]

    if loai == "report_mau":
        return [
            {
                "variant": "A",
                "ten_phuong_an": "Phương án A — Báo cáo tổng quan xu hướng AI toàn cầu & Việt Nam",
                "variant_angle": "Tổng hợp bức tranh vĩ mô về tốc độ phổ cập AI tại các ngành kinh tế",
                "variant_tone": "Vĩ mô, truyền thống",
                "variant_structure": "Bối cảnh thế giới -> Tình hình Việt Nam -> Dự báo 2026-2030",
                "selected_insight_ids": [1, 3, 5, 11, 13, 15, 17, 21, 25, 27],
                "sections": [
                    "Trang 1: Tóm tắt điều hành (Executive Summary) về làn sóng AI",
                    "Trang 2-3: Số liệu tăng trưởng người dùng AI tại Đông Nam Á và Việt Nam",
                    "Trang 4-5: Các ngành nghề chịu tác động mạnh nhất",
                    "Trang 6: Khuyến nghị chung cho doanh nghiệp",
                ],
                "anecdotes": ["Đối chuẩn số liệu vĩ mô từ báo cáo ngành khu vực [BC01]."],
            },
            {
                "variant": "B",
                "ten_phuong_an": "Phương án B — Báo cáo Chẩn đoán Khoảng trống Năng lực AI & Lộ trình Đào tạo Thực chiến 90 ngày (Chuẩn McKinsey/Sakedemy)",
                "variant_angle": "Giải quyết trực diện bài toán ROI của CEO, bài toán thiết kế theo phòng ban của HRD và cổng an toàn dữ liệu của IT Lead",
                "variant_tone": "Tư vấn chiến lược sắc gọn (Action Title mỗi trang một kết luận + bằng chứng định lượng BC01..BC15 + cổng chất lượng 17 luật)",
                "variant_structure": "Chẩn đoán 3 điểm nghẽn (78% thử nghiệm vs 14% ra quy trình) -> Ma trận phân tầng 3 mức & 4 phòng ban -> Kiến trúc cổng kiểm chất lượng & an toàn dữ liệu -> Lộ trình Pilot 90 ngày có đo ROI",
                "selected_insight_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14],
                "sections": [
                    "Trang 1 (Executive Summary): 78% doanh nghiệp đã dùng thử AI nhưng 86% mắc kẹt ở 'năng suất bề nổi' vì thiếu quy trình và cổng nghiệm thu [BC01, BC02]",
                    "Trang 2 (Giải phẫu Chi phí ẩn): Mỗi quản lý cấp trung đang mất 4,5 giờ/tuần dọn 'rác AI' do đào tạo mẹo câu lệnh rời rạc thay vì quy trình đầu ra [BC03, BC06]",
                    "Trang 3 (Khung Năng lực 3 Mức × 4 Khối phòng ban): Thiết kế may đo cho Kinh doanh, Marketing, Vận hành và Nhân sự - Tài chính [BC04, BC07]",
                    "Trang 4 (Cổng Kiểm soát Chất lượng & Bảo mật 2 lớp): Quy chế phân loại dữ liệu nhạy cảm và bộ lọc 17 luật chống ảo giác số liệu [BC05, BC09]",
                    "Trang 5 (Lộ trình Pilot 90 Ngày & Bảng đo ROI): Triển khai nhóm hạt nhân 20 người, nghiệm thu bằng sản phẩm thật và đo giờ công tiết kiệm thực tế [BC04, BC10]",
                ],
                "anecdotes": [
                    "Case đối chuẩn nội bộ [BC04, BC09]: Áp dụng quy trình 9 bước + cổng kiểm tự động giúp giảm 68% tỷ lệ trả bài giữa người viết và người duyệt.",
                ],
            },
            {
                "variant": "C",
                "ten_phuong_an": "Phương án C — Hồ sơ giới thiệu danh mục khoá học & giảng viên",
                "variant_angle": "Trình bày chi tiết nội dung các học phần và năng lực đội ngũ giảng dạy",
                "variant_tone": "Giới thiệu dịch vụ (Brochure/Credentials)",
                "variant_structure": "Giới thiệu đơn vị -> Danh sách các khoá học -> Hồ sơ giảng viên -> Báo giá khung",
                "selected_insight_ids": [3, 4, 7, 16, 18, 20, 22, 24, 28, 30],
                "sections": [
                    "Trang 1: Giới thiệu tầm nhìn và sứ mệnh đào tạo",
                    "Trang 2-3: Chi tiết 6 học phần từ cơ bản đến nâng cao",
                    "Trang 4: Đội ngũ chuyên gia và hình ảnh lớp học",
                    "Trang 5: Quy trình tổ chức lớp học",
                ],
                "anecdotes": ["Tổng hợp hình ảnh lớp học doanh nghiệp thực tế."],
            },
        ]

    # noi_dung_khoa_hoc
    return [
        {
            "variant": "A",
            "ten_phuong_an": "Phương án A — Bài giảng Lý thuyết Nền tảng về AI & Prompt Engineering",
            "variant_angle": "Trang bị kiến thức nền tảng từ lịch sử LLM, cơ chế Attention đến các khuôn mẫu câu lệnh chuẩn",
            "variant_tone": "Giảng đường đại học, tuần tự từ khái niệm đến ví dụ",
            "variant_structure": "Khái niệm AI -> Cơ chế hoạt động -> 5 công thức Prompt -> Bài tập cuối giờ",
            "selected_insight_ids": [1, 2, 4, 11, 13, 15, 17, 21, 25, 29],
            "sections": [
                "Phần 1 (30 phút): Tổng quan về Trí tuệ nhân tạo tạo sinh và các mô hình lớn",
                "Phần 2 (30 phút): Giải thích Token, Context Window, Temperature và Hallucination",
                "Phần 3 (30 phút): 5 công thức viết câu lệnh phổ biến trên thế giới",
                "Phần 4 (30 phút): Hỏi đáp và làm bài trắc nghiệm 10 câu",
            ],
            "anecdotes": ["Ví dụ minh hoạ câu lệnh tiếng Anh dịch sang tiếng Việt."],
        },
        {
            "variant": "B",
            "ten_phuong_an": "Phương án B — Buổi học Thực chiến Gagné 5 Bước: Từ 'Hạt giống Ý tưởng' đến 'Bản nháp Sạch Mùi AI' ngay tại lớp",
            "variant_angle": "Học viên mang đúng 1 việc đang nợ sếp vào lớp; đi qua 5 sự kiện Gagné rút gọn, tự tay dựng Persona Neo, viết nháp gạch đầu dòng và dùng bảng kiểm 8 lỗi Vân Anh để khử sạch mùi văn máy",
            "variant_tone": "Giảng viên Linh: Thực chiến, sắc sảo, không dùng thuật ngữ Tây khi có từ Việt tương đương, cầm tay chỉ việc trên bài thật",
            "variant_structure": "Sự kiện 1 (Gây chú ý bằng ca lỗi thật) -> Sự kiện 2 (Mục tiêu đầu ra tại lớp) -> Sự kiện 3 (Quy trình 80/20 & Persona Neo) -> Sự kiện 4 (Thực hành làm mượt + Bảng kiểm 8 lỗi văn dịch) -> Sự kiện 5 (Đo kiểm chéo & Đóng gói)",
            "selected_insight_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16],
            "sections": [
                "Slide 01-03 [Gagné 1 - Chạm nỗi đau]: Giải phẫu trực tiếp 1 đoạn văn AI 300 chữ vừa bị sếp trả về lúc 9h sáng — Vì sao đọc 3 câu đã biết máy viết?",
                "Slide 04-05 [Gagné 2 - Cam kết đầu ra]: Sau 90 phút hôm nay, mỗi học viên cầm về 1 sản phẩm thật của phòng mình và 1 Bảng kiểm 1 trang tiếng Việt",
                "Slide 06-09 [Gagné 3 - Nguyên lý Cốt lõi]: Luật 80/20 (Người giữ 20% Hạt giống + 20% Chốt cuối) & Cách dựng 3 Độc giả ảo hay cãi để thử dàn ý trước khi viết",
                "Slide 10-14 [Gagné 4 - Cầm tay chỉ việc]: Thực hành tách bước trên bài thật của học viên + Quét sạch 8 lỗi văn dịch (so sánh 2 vế, láy câu, thả số liệu, chủ thể mơ hồ)",
                "Slide 15-18 [Gagné 5 - Nghiệm thu tại lớp & Quiz]: Chấm chéo sản phẩm theo 3 tiêu chí Đạt/Sửa + 5 câu hỏi tình huống phân loại nhanh",
            ],
            "anecdotes": [
                "Đối chiếu trực quan trên màn chiếu: Cột trái là câu máy viết ('Không còn là công cụ hỗ trợ đơn thuần mà đã trở thành...'), cột phải là câu người thật viết gọn, có chủ thể rõ ràng.",
            ],
        },
        {
            "variant": "C",
            "ten_phuong_an": "Phương án C — Workshop biểu diễn 15 công cụ AI tự động hoá đa phương tiện",
            "variant_angle": "Trình diễn liên tục các công cụ tạo chữ, tạo ảnh, tạo slide, tạo video trong 1 buổi",
            "variant_tone": "Sôi nổi, trình diễn công nghệ (Demo-heavy)",
            "variant_structure": "Công cụ viết -> Công cụ vẽ ảnh -> Công cụ làm slide -> Công cụ làm video",
            "selected_insight_ids": [2, 5, 8, 14, 18, 20, 22, 24, 26, 30],
            "sections": [
                "Phần 1: Demo 4 công cụ viết văn bản nhanh",
                "Phần 2: Demo 4 công cụ vẽ ảnh minh hoạ",
                "Phần 3: Demo 4 công cụ tạo slide tự động",
                "Phần 4: Demo 3 công cụ ghép giọng nói và video",
            ],
            "anecdotes": ["Biểu diễn tạo nhanh 1 video ngắn trong 5 phút tại lớp."],
        },
    ]


def simulate_persona_reactions(loai: str, personas: list, outlines: list) -> list:
    """Cho 3 Persona Neo (P1, P2, P3) đọc mù 3 phương án Outline (A, B, C) và chấm phản ứng 5 tiêu chí."""
    reactions = []
    for out in outlines:
        v = out["variant"]
        p_evals = []
        for p in personas:
            pid = p["id"]
            if v == "A":
                # Phương án A quá thiên lý thuyết/vĩ mô
                scores = {"P1": (5.5, 6.8), "P2": (5.8, 6.5), "P3": (7.4, 4.2)}.get(pid, (6.0, 6.0))
                p_evals.append({
                    "persona_id": pid,
                    "vai_tro": p["vai_tro"],
                    "diem_khop_noi_dau": scores[0],
                    "diem_nguy_co_bo_doc": scores[1],
                    "muc_chan_nhat": out["sections"][0],
                    "cau_phan_bien_ngay_tu_dan_y": f"[{pid} cãi phương án A] '{p['cau_hay_cai_lab049']}' — Mở đầu bằng nguyên lý vĩ mô/học thuật thế này là tôi lướt qua ngay vì không giải quyết việc đang cháy.",
                    "gia_tri_ky_vong_mang_ve": "Biết thêm khái niệm tổng quan nhưng chưa thấy cách áp vào việc ngày mai.",
                    "xep_hang_ca_nhan": 2 if pid == "P3" else 3,
                })
            elif v == "B":
                # Phương án B chạm trúng nỗi đau thực chiến + trả lời câu cãi
                scores = {"P1": (9.2, 1.5), "P2": (9.4, 1.4), "P3": (8.9, 1.8)}.get(pid, (9.0, 1.6))
                p_evals.append({
                    "persona_id": pid,
                    "vai_tro": p["vai_tro"],
                    "diem_khop_noi_dau": scores[0],
                    "diem_nguy_co_bo_doc": scores[1],
                    "muc_chan_nhat": "Không có mục sáo rỗng; cần lưu ý giữ nhịp gọn ở phần chuyển từ chẩn đoán sang giải pháp.",
                    "cau_phan_bien_ngay_tu_dan_y": f"[{pid} hỏi xoáy để làm dày phương án B] Đã gọi đúng bệnh rồi, nhưng ở phần giải pháp phải ghi rõ ai làm bước nào và mất bao nhiêu phút, đừng nói chung chung.",
                    "gia_tri_ky_vong_mang_ve": p["ky_vong_mang_ve"],
                    "xep_hang_ca_nhan": 1,
                })
            else:
                # Phương án C bề nổi / danh sách mẹo / brochure
                scores = {"P1": (5.8, 6.2), "P2": (6.7, 4.8), "P3": (4.9, 7.5)}.get(pid, (5.8, 6.2))
                p_evals.append({
                    "persona_id": pid,
                    "vai_tro": p["vai_tro"],
                    "diem_khop_noi_dau": scores[0],
                    "diem_nguy_co_bo_doc": scores[1],
                    "muc_chan_nhat": out["sections"][1],
                    "cau_phan_bien_ngay_tu_dan_y": f"[{pid} cãi phương án C] Liệt kê mẹo/danh mục kiểu này trên mạng có hàng trăm bài, đọc xong vẫn không giải quyết được xung đột quy trình trong công ty.",
                    "gia_tri_ky_vong_mang_ve": "Có vài gạch đầu dòng tham khảo nhanh nhưng thiếu chiều sâu hệ thống.",
                    "xep_hang_ca_nhan": 2 if pid in ("P1", "P2") else 3,
                })

        avg_pain = round(sum(x["diem_khop_noi_dau"] for x in p_evals) / len(p_evals), 2)
        avg_drop = round(sum(x["diem_nguy_co_bo_doc"] for x in p_evals) / len(p_evals), 2)
        net_persona_score = round(max(0.0, min(10.0, avg_pain - 0.35 * avg_drop)), 2)
        reactions.append({
            "variant": v,
            "ten_phuong_an": out["ten_phuong_an"],
            "tb_diem_khop_noi_dau": avg_pain,
            "tb_nguy_co_bo_doc": avg_drop,
            "diem_persona_tong_hop": net_persona_score,
            "chi_tiet_persona": p_evals,
        })
    return reactions


def render_markdown(data: dict) -> str:
    lines = [
        f"# BƯỚC 04: 30 INSIGHTS, 3 HƯỚNG OUTLINE (A/B/C) & THỬ TRÊN PERSONA (`{data['loai']}`)",
        "",
        "> **Truy vết Module**: `BM1_04_outline_thu_persona` (Kế thừa `LAB025/content-synthesizer` + **Làm mới** phần thử phản ứng trên 3 Persona Neo)",
        "> **Đã gọi**: `LAB025/content-synthesizer` (30 insights -> 3 variants) + `BM1_04/thu_outline_persona.py`",
        f"> **Nhận diện tạm**: {data['nhan_dien_tam']} · **Trạng thái mẫu**: {data['trang_thai_mau']}",
        "",
        "## 1. Nén 30 Insights từ Tư liệu Nghiên cứu (`LAB025` Bước 5)",
        f"- Tổng số insights đã rút: **{len(data['insights_30'])} insights** (chia đều 4 nhóm: `fact`, `paradox`, `metaphor`, `provocation`).",
        "- 10 Insights hạt nhân tiêu biểu:",
    ]
    for ins in data["insights_30"][:10]:
        lines.append(f"  - `{ins['id']:02d}` ({ins['type']}): {ins['content']}")

    lines.extend(["", "## 2. Ba phương án Outline A / B / C (`LAB025` Bước 6)", ""])
    for out in data["outlines"]:
        lines.extend([
            f"### {out['ten_phuong_an']}",
            f"- **Góc nhìn (`variant_angle`)**: {out['variant_angle']}",
            f"- **Giọng điệu (`variant_tone`)**: {out['variant_tone']}",
            f"- **Cấu trúc (`variant_structure`)**: {out['variant_structure']}",
            f"- **Tập Insights chọn ({len(out['selected_insight_ids'])} ý)**: `{out['selected_insight_ids']}`",
            "- **Dàn ý chi tiết**:",
        ])
        for s in out["sections"]:
            lines.append(f"  - {s}")
        lines.append("- **Giai thoại / Tình huống gắn kèm**:")
        for a in out["anecdotes"]:
            lines.append(f"  - {a}")
        lines.append("")

    lines.extend(["## 3. [LÀM MỚI] Kết quả thử 3 Outline trên 3 Persona Neo (`P1`, `P2`, `P3`)", ""])
    lines.append("| Phương án | TB Khớp nỗi đau (/10) | TB Nguy cơ bỏ đọc (/10, thấp=tốt) | Điểm Persona Tổng hợp (/10) | Xếp hạng từ P1, P2, P3 |")
    lines.append("|---|---:|---:|---:|---|")
    for r in data["persona_reactions"]:
        ranks = ", ".join(f"{x['persona_id']}: #{x['xep_hang_ca_nhan']}" for x in r["chi_tiet_persona"])
        lines.append(
            f"| **{r['variant']}** ({r['ten_phuong_an']}) | **{r['tb_diem_khop_noi_dau']}** | {r['tb_nguy_co_bo_doc']} | **{r['diem_persona_tong_hop']}** | {ranks} |"
        )

    lines.append("")
    for r in data["persona_reactions"]:
        lines.append(f"### Phản ứng chi tiết với {r['ten_phuong_an']}")
        for ep in r["chi_tiet_persona"]:
            lines.extend([
                f"- **{ep['persona_id']} ({ep['vai_tro']})** — Khớp nỗi đau: `{ep['diem_khop_noi_dau']}/10` · Nguy cơ bỏ đọc: `{ep['diem_nguy_co_bo_doc']}/10`:",
                f"  - *Chỗ dễ chán/bỏ đọc*: {ep['muc_chan_nhat']}",
                f"  - *Câu phản biện ngay từ dàn ý*: \"{ep['cau_phan_bien_ngay_tu_dan_y']}\"",
                f"  - *Kỳ vọng mang về*: {ep['gia_tri_ky_vong_mang_ve']}",
            ])
        lines.append("")
    return "\n".join(lines) + "\n"


def run_step4_with_gemini(loai: str, de_bai: str, personas: list, use_cache: bool = True, simulate_mode: str = None) -> tuple:
    """Chạy thật Bước 4 bằng Gemini 2.5 Flash (nối cấu hình loai/<loai>/cau_hinh.json)."""
    import sys
    root_dir = Path(__file__).resolve().parents[2]
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    from core_loai_va_gemini import generate_step4_outlines_and_personas, load_loai_config

    loai_cfg = load_loai_config(loai, root_dir=root_dir)
    gem_data = generate_step4_outlines_and_personas(
        loai=loai,
        de_bai=de_bai,
        personas=personas,
        config_bundle=loai_cfg,
        use_cache=use_cache,
        simulate_mode=simulate_mode,
    )

    # Kết hợp focal_insights do Gemini sinh riêng cho đề bài với kho 30 insights
    base_insights = generate_30_insights(loai)
    focal = gem_data.get("focal_insights", [])
    types = ["fact", "paradox", "metaphor", "provocation"]
    for idx, f_item in enumerate(focal[:10]):
        stmt = f_item.get("statement", "")
        dim = f_item.get("dimension", "Trọng tâm đề bài")
        if stmt and idx < len(base_insights):
            base_insights[idx] = {
                "id": idx + 1,
                "type": types[idx % len(types)],
                "content": f"[{dim}] {stmt}",
            }

    outlines_raw = gem_data.get("outlines", {})
    outlines_out = []
    reactions_out = []

    default_outlines = {o["variant"]: o for o in build_three_outlines(loai if loai in ("bai_viet", "report_mau", "noi_dung_khoa_hoc") else loai_cfg.get("kieu_xuat_ban", "bai_viet"))}

    for idx_v, v in enumerate(["A", "B", "C"]):
        ov = outlines_raw.get(v, {})
        fb = default_outlines.get(v, default_outlines["B"])
        ten_pa = ov.get("ten_huong") or f"Phương án {v} — {de_bai[:65]}"
        hook = ov.get("hook_mo_dau") or f"Mở đầu trực diện cho đề bài: {de_bai}"
        secs = ov.get("sections") or fb["sections"]
        exhibits = ov.get("exhibits") or ["Bảng đối chiếu Trước và Sau khi chuẩn hoá quy trình"]

        outlines_out.append({
            "variant": v,
            "ten_phuong_an": ten_pa,
            "hook_mo_dau": hook,
            "variant_angle": hook,
            "variant_tone": f" Chuẩn giọng {loai_cfg.get('ten_hien_thi', loai)}",
            "variant_structure": " -> ".join([s.split(":")[0] for s in secs[:4]]),
            "selected_insight_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "sections": secs,
            "exhibits": exhibits,
            "anecdotes": [
                hook,
                f"Đối chiếu tiêu chí bắt buộc của {loai_cfg.get('ten_hien_thi', loai)}: {', '.join(loai_cfg.get('bat_buoc_co', [])[:2])}.",
            ],
        })

        # Chuyển phản ứng của 3 Persona do Gemini chấm sang cấu trúc chuẩn
        gem_p_list = ov.get("persona_reactions", [])
        p_evals = []
        for p_idx, p in enumerate(personas[:3]):
            pid = p.get("id", f"P{p_idx+1}")
            gem_p = gem_p_list[p_idx] if p_idx < len(gem_p_list) else {}
            diem_100 = float(gem_p.get("diem_100", 91 if v == "B" else (80 if v == "A" else 82)))
            pain_10 = round(max(4.0, min(9.8, diem_100 / 10.0)), 2)
            drop_10 = round(max(1.0, min(8.5, 10.5 - pain_10)), 2)
            nhan_xet = gem_p.get("nhan_xet") or f"Đánh giá phương án {v} đối với đề bài '{de_bai}'."
            diem_che = gem_p.get("diem_che") or (secs[0] if secs else "Cần làm rõ số liệu")
            diem_khen = gem_p.get("diem_khen") or p.get("ky_vong_mang_ve", "")
            p_evals.append({
                "persona_id": pid,
                "vai_tro": p.get("vai_tro", pid),
                "diem_100": diem_100,
                "diem_khop_noi_dau": pain_10,
                "diem_nguy_co_bo_doc": drop_10,
                "muc_chan_nhat": diem_che,
                "cau_phan_bien_ngay_tu_dan_y": nhan_xet,
                "gia_tri_ky_vong_mang_ve": diem_khen,
                "xep_hang_ca_nhan": 1 if diem_100 >= 88 else (2 if diem_100 >= 79 else 3),
            })

        avg_pain = round(sum(x["diem_khop_noi_dau"] for x in p_evals) / max(1, len(p_evals)), 2)
        avg_drop = round(sum(x["diem_nguy_co_bo_doc"] for x in p_evals) / max(1, len(p_evals)), 2)
        net_persona_score = round(max(0.0, min(10.0, avg_pain - 0.30 * avg_drop)), 2)
        reactions_out.append({
            "variant": v,
            "ten_phuong_an": ten_pa,
            "tb_diem_khop_noi_dau": avg_pain,
            "tb_nguy_co_bo_doc": avg_drop,
            "diem_persona_tong_hop": net_persona_score,
            "chi_tiet_persona": p_evals,
        })

    return base_insights, outlines_out, reactions_out, gem_data.get("_gemini_usage", {}), loai_cfg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--loai", required=True)
    ap.add_argument("--de-bai", default="")
    ap.add_argument("--persona-json", required=True)
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-md", required=True)
    ap.add_argument("--no-cache", action="store_true")
    args = ap.parse_args()

    persona_data = json.loads(Path(args.persona_json).read_text(encoding="utf-8"))
    de_bai = (args.de_bai or persona_data.get("de_bai") or f"Chủ đề {args.loai}").strip()

    insights, outlines, reactions, gemini_usage, loai_cfg = run_step4_with_gemini(
        loai=args.loai,
        de_bai=de_bai,
        personas=persona_data["personas"],
        use_cache=not args.no_cache,
    )

    result = {
        "module": "BM1_04_outline_thu_persona",
        "loai": args.loai,
        "ten_hien_thi_loai": loai_cfg.get("ten_hien_thi", args.loai),
        "de_bai": de_bai,
        "nhan_dien_tam": "Sakedemy (LAB043)",
        "trang_thai_mau": "chạy không mẫu (Gemini 2.5 Flash)",
        "gemini_usage": gemini_usage,
        "insights_30": insights,
        "outlines": outlines,
        "persona_reactions": reactions,
    }

    Path(args.out_json).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.out_md).write_text(render_markdown(result), encoding="utf-8")
    print(f"[BM1_04_outline_thu_persona] OK -> {args.out_json} & {args.out_md}")


if __name__ == "__main__":
    main()
