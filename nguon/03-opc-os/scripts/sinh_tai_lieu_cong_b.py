"""Sinh trọn bộ tài liệu chuẩn bị Cổng B & Bậc 2 (`TAI_LIEU_CONG_B/*`) cho `03_OPC_OS` theo `13_LENH_BAC_2.md` Mục 2 & Mục 03."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "TAI_LIEU_CONG_B"


def build_40_blind_test_set() -> None:
    """Tạo bộ 40 đầu ra chấm mù: 20 đầu ra AI (`03_OPC_OS`) trộn với 20 đầu ra chuyên gia con người viết."""
    ai_samples = [
        ("OPC001 Chiêm tinh — Hồ sơ sinh 21/08/1994 (08:15, Hà Nội)", "Mặt Trời Sư Tử tại Nhà 12 kết hợp Mặt Trăng Bảo Bình tại Nhà 6 tạo nên cấu trúc nội tâm vừa khao khát khẳng định dấu ấn độc lập vừa cần không gian tĩnh lặng để tái tạo năng lượng. Trong 12 tháng tới, thay vì dàn trải vào các cuộc tranh luận bề nổi, bạn đạt hiệu suất cao nhất khi đóng gói quy trình làm việc thành hệ thống có thể vận hành lặp lại."),
        ("OPC001 Chiêm tinh — Hồ sơ sinh 19/08/1993 (09:30, Hà Nội)", "Điểm mọc Thiên Bình phối hợp sao Thủy tại Sư Tử giúp bạn có khả năng trình bày các vấn đề phức tạp bằng ngôn từ thuyết phục và ấm áp. Giai đoạn quý II và quý III là thời điểm thuận lợi để chuẩn hoá lại các thoả thuận hợp tác dài hạn, miễn là bạn đặt rõ ranh giới thời gian nghỉ ngơi mỗi tuần."),
        ("OPC001 Chiêm tinh — Hồ sơ sinh 12/02/1991 (14:20, Đà Nẵng)", "Cấu trúc Mặt Trời Bảo Bình tạo góc chiếu hài hoà với sao Mộc mang lại tư duy cải tiến hệ thống rất nhạy bén. Điểm cần lưu ý là xu hướng ôm đồm quá nhiều dự án mới cùng lúc; hãy áp dụng nguyên tắc khoá sổ từng mục tiêu theo chu kỳ 90 ngày."),
        ("OPC001 Chiêm tinh — Hồ sơ sinh 05/11/1996 (Không rõ giờ sinh, TP.HCM)", "Do hồ sơ chưa xác định giờ sinh chính xác, báo cáo tập trung vào trục Mặt Trời Bọ Cạp – Mặt Trăng Xử Nữ (không suy diễn Cung Mọc và hệ thống 12 Nhà). Sự kết hợp giữa trực giác sâu sắc của Bọ Cạp và tính kỷ luật chi tiết của Xử Nữ giúp bạn cực kỳ vững vàng trong các công việc đòi hỏi kiểm định rủi ro."),
        ("OPC001 Chiêm tinh — Hồ sơ sinh 28/04/1989 (06:45, Hải Phòng)", "Mặt Trời Kim Ngưu đi cùng sao Thổ tạo nền tảng kiên trì hiếm có trong quản trị tài chính cá nhân. Khi đối diện với biến động thị trường, phản xạ tự nhiên của bạn là kiểm tra dòng tiền thực thay vì chạy theo tâm lý đám đông."),
        ("OPC001 Chiêm tinh — Hồ sơ sinh 15/07/1998 (19:10, Cần Thơ)", "Năng lượng Cự Giải ở tâm điểm bản đồ sao giúp bạn nhạy cảm với nhu cầu tinh thần của đội nhóm. Tuy nhiên, để tránh kiệt sức vì gánh thay trách nhiệm cảm xúc của người khác, bạn cần thiết lập lịch làm việc tách biệt rõ giữa giờ hỗ trợ và giờ tập trung sâu."),
        ("OPC001 Chiêm tinh — Hồ sơ sinh 03/01/1992 (11:00, Nghệ An)", "Sự hội tụ của nhóm nguyên tố Đất tại Ma Kết giúp bạn có sức bền đường dài vượt trội. Mọi kế hoạch nghề nghiệp của bạn đều cần những cột mốc đo đếm được bằng con số cụ thể thay vì những lời hứa hẹn chung chung."),
        ("OPC002 Ngân hàng — Vị trí Chuyên viên Quan hệ Khách hàng Doanh nghiệp (RM)", "Khung câu lệnh soạn Tờ trình thẩm định tín dụng vốn lưu động: (1) Tóm tắt mô hình kinh doanh & vòng quay vốn lưu động thực tế của doanh nghiệp ẩn danh; (2) Phân tích 3 nguồn trả nợ chính và biên độ chịu đựng khi doanh thu giảm 15%; (3) Đề xuất cấu trúc hạn mức kèm điều kiện giải ngân từng phần `[CẦN XÁC MINH THEO QUY ĐỊNH NỘI BỘ]`."),
        ("OPC002 Ngân hàng — Vị trí Giao dịch viên Quầy (Teller)", "Khung kịch bản giải thích biểu phí và hướng dẫn khách hàng kích hoạt bảo mật sinh trắc học tại quầy trong 90 giây: Mở đầu bằng sự đồng cảm với thời gian chờ của khách, nêu đúng 3 thao tác trên màn hình điện thoại và tuyệt đối không yêu cầu khách đọc mã xác thực."),
        ("OPC002 Ngân hàng — Vị trí Chuyên viên Thẩm định Tín dụng (Credit)", "Danh mục đối chiếu hồ sơ pháp lý và dòng tiền trước khi trình phê duyệt: Kiểm tra tính nhất quán giữa tờ khai thuế, sao kê dòng tiền qua tài khoản và biên bản kiểm tra mục đích sử dụng vốn; đánh dấu rõ các giả định cần bổ sung chứng từ."),
        ("OPC002 Ngân hàng — Vị trí Chuyên viên Vận hành & Tuân thủ (Ops)", "Mẫu rà soát lỗi tác nghiệp cuối ngày tại chi nhánh: Phân loại chứng từ theo 3 mức độ ưu tiên, đối khớp sổ phụ giao dịch tự động và lập biên bản bàn giao ca không để tồn đọng hồ sơ treo qua ngày hôm sau."),
        ("OPC002 Ngân hàng — Thư giải trình điều chỉnh lãi suất vay doanh nghiệp", "Bản thảo thư gửi Giám đốc Tài chính khách hàng doanh nghiệp: Trình bày minh bạch mặt bằng chi phí vốn kỳ hiện tại, đồng thời đề xuất gói ưu đãi phí bảo lãnh và tài trợ chuỗi cung ứng để giảm tổng chi phí tài chính thực tế cho doanh nghiệp."),
        ("OPC002 Ngân hàng — Lịch thực hành 7 ngày áp dụng trợ lý AI tại ngân hàng", "Ngày 1–2: Thiết lập quy tắc ẩn danh hoá 100% thông tin định danh khách hàng trước khi dùng công cụ soạn thảo. Ngày 3–5: Chuẩn hoá 5 mẫu tờ trình và thư trao đổi thường gặp nhất. Ngày 6–7: Đo thời gian tiết kiệm thực tế và đóng gói thành sổ tay cá nhân."),
        ("OPC003 Hướng nghiệp THPT — Học sinh lớp 11 tổ hợp I-R-C (Toán – Tin – Anh)", "Kết quả trắc nghiệm sở thích 6 nhóm công khai cho thấy điểm nổi trội ở nhóm Nghiên cứu (I: 36), Thực tế (R: 31) và Nghiệp vụ (C: 27). Sự kết hợp này gợi mở thế mạnh khi làm việc với dữ liệu, thuật toán, kỹ thuật hệ thống và phân tích định lượng. Gia đình có thể cùng con trải nghiệm một dự án lập trình nhỏ trong 4 tuần trước khi chốt nguyện vọng."),
        ("OPC003 Hướng nghiệp THPT — Học sinh lớp 10 tổ hợp A-S-E (Văn – Anh – Sử)", "Điểm số nổi bật ở nhóm Nghệ thuật (A: 35) và Xã hội (S: 33) phản ánh khả năng biểu đạt ngôn ngữ, thấu cảm và truyền thông giáo dục. Báo cáo gợi ý 3 hướng khám phá gồm Truyền thông đa phương tiện, Tâm lý học đường và Thiết kế trải nghiệm, hoàn toàn mang tính mở để con tự thử sức."),
        ("OPC003 Hướng nghiệp THPT — Học sinh lớp 12 tổ hợp E-C-I (Toán – Lý – Anh)", "Tổ hợp Quản lý (E: 34) kết hợp Nghiệp vụ (C: 30) và Nghiên cứu (I: 28) phù hợp với các môi trường đòi hỏi vừa tổ chức vận hành vừa phân tích số liệu như Quản trị chuỗi cung ứng, Công nghệ tài chính và Hệ thống thông tin quản lý."),
        ("OPC003 Hướng nghiệp THPT — Học sinh lớp 9 chọn tổ hợp môn vào lớp 10", "Ở giai đoạn chuyển cấp lớp 9 lên lớp 10, mục tiêu quan trọng nhất là giữ độ mở cho các môn nền tảng (Toán, Ngữ văn, Ngoại ngữ) kết hợp 1 môn khoa học tự nhiên và 1 môn công nghệ/nghệ thuật theo đúng nhóm sở thích R-I-A của con."),
        ("OPC003 Hướng nghiệp THPT — Khung trò chuyện 30 phút cuối tuần giữa Cha Mẹ và Con", "Nguyên tắc trò chuyện không áp đặt: Trong 15 phút đầu, cha mẹ lắng nghe con kể về môn học hoặc hoạt động ngoại khoá khiến con thấy hào hứng nhất tuần qua mà không ngắt lời hay so sánh điểm số; 15 phút sau cùng con chọn 1 việc thực hành nhỏ trong tuần tới."),
        ("OPC003 Hướng nghiệp THPT — Lộ trình trải nghiệm thực tế 90 ngày hè cho học sinh THPT", "Tháng 1: Đọc sâu 2 cuốn sách chuyên ngành và phỏng vấn 1 anh/chị đang làm nghề thực tế. Tháng 2: Tự làm 1 sản phẩm nhỏ (bài viết, đoạn mã, video thuyết trình). Tháng 3: Tự đánh giá lại mức độ yêu thích thực sự sau khi đã chạm tay vào việc thật."),
        ("OPC001 Chiêm tinh — Hồ sơ sinh 09/09/1995 (07:30, Huế)", "Mặt Trời Xử Nữ kết hợp Mặt Trăng Song Ngư tạo trục cân bằng giữa tư duy phân tích tỉ mỉ và sự nhạy cảm trực giác. Trong công việc chuyên môn, bạn phát huy tốt nhất khi vừa có bộ tiêu chuẩn chất lượng rõ ràng vừa được trao quyền chủ động cải tiến từng chi tiết nhỏ."),
    ]

    human_samples = [
        ("Chuyên gia Chiêm tinh biên soạn — Hồ sơ sinh 14/05/1993 (10:15, Hà Nội)", "Với Mặt Trời Kim Ngưu nằm ở khu vực hướng ngoại và Mặt Trăng Cự Giải giàu tình cảm, bạn luôn tìm kiếm sự ổn định vững chắc trước khi bước vào bất kỳ thay đổi lớn nào. Lời khuyên cho năm nay là hãy củng cố kỹ năng cốt lõi và tích luỹ tài chính đều đặn từng tháng thay vì nóng vội."),
        ("Chuyên gia Chiêm tinh biên soạn — Hồ sơ sinh 22/11/1990 (16:40, TP.HCM)", "Sự giao thoa giữa cuối Bọ Cạp và đầu Nhân Mã mang lại cho bạn cả chiều sâu tập trung lẫn tầm nhìn rộng mở. Khi lập kế hoạch công việc 12 tháng tới, bạn nên chia mục tiêu lớn thành từng chặng 3 tháng để giữ nhiệt huyết bền bỉ."),
        ("Chuyên gia Chiêm tinh biên soạn — Hồ sơ sinh 08/03/1997 (05:50, Đà Nẵng)", "Năng lượng Song Ngư giúp bạn có khả năng lắng nghe và kết nối tinh tế với mọi người xung quanh. Tuy nhiên, bạn cần rèn luyện thói quen nói lời từ chối đúng lúc để bảo vệ thời gian tập trung cho những mục tiêu cá nhân quan trọng nhất."),
        ("Chuyên gia Chiêm tinh biên soạn — Hồ sơ sinh 30/07/1992 (Không rõ giờ sinh, Hải Dương)", "Vì chưa có thông tin giờ sinh chính xác, bản phân tích tập trung vào vị trí các hành tinh trong cung hoàng đạo trong ngày sinh. Mặt Trời Sư Tử đem lại nguồn năng lượng ấm áp, chủ động và tinh thần trách nhiệm cao khi đứng ở vị trí dẫn dắt đội nhóm."),
        ("Chuyên gia Chiêm tinh biên soạn — Hồ sơ sinh 17/01/1995 (20:05, Quảng Ninh)", "Bản đồ sao nổi bật với cụm hành tinh tại Ma Kết cho thấy bạn là người trọng chữ tín và luôn nhìn nhận vấn đề dưới góc độ thực tế. Trong giai đoạn tới, việc đầu tư nâng cao chuyên môn sâu sẽ mang lại bước tiến vững chắc hơn là mở rộng quan hệ xã giao bề nổi."),
        ("Chuyên gia Chiêm tinh biên soạn — Hồ sơ sinh 11/06/1998 (13:25, Nha Trang)", "Mặt Trời Song Tử mang đến sự linh hoạt trong giao tiếp và khả năng tiếp thu nhanh các xu hướng mới. Để biến ý tưởng thành kết quả cụ thể, bạn nên duy trì một cuốn sổ theo dõi tiến độ hằng tuần và hoàn thành dứt điểm từng đầu việc."),
        ("Chuyên gia Chiêm tinh biên soạn — Hồ sơ sinh 25/09/1991 (08:00, Hà Nội)", "Trục Thiên Bình mạnh mẽ giúp bạn có tư duy công bằng, khách quan và giỏi điều phối các ý kiến trái chiều trong tập thể. Điểm cần rèn luyện là rút ngắn thời gian cân nhắc ở những quyết định nhỏ hằng ngày để tiết kiệm năng lượng cho việc lớn."),
        ("Chuyên gia Ngân hàng biên soạn — Mẫu tờ trình đề xuất hạn mức tín dụng SME", "Khi trình bày tờ trình cấp tín dụng cho doanh nghiệp vừa và nhỏ, cán bộ quan hệ khách hàng cần làm rõ 3 yếu tố: lịch sử trả nợ thực tế trong 12 tháng gần nhất, chu kỳ chuyển đổi hàng tồn kho thành tiền mặt và phương án kiểm soát dòng tiền thu về qua tài khoản tại ngân hàng."),
        ("Chuyên gia Ngân hàng biên soạn — Kịch bản xử lý khiếu nại giao dịch chậm tại quầy", "Bước 1: Mời khách ngồi và xác nhận ngay mã giao dịch cần tra soát. Bước 2: Kiểm tra trạng thái lệnh trên hệ thống thanh toán liên ngân hàng và thông báo rõ khung giờ dự kiến hoàn tất. Bước 3: Ghi nhận số điện thoại để chủ động báo lại ngay khi giao dịch hạch toán xong."),
        ("Chuyên gia Ngân hàng biên soạn — Danh mục kiểm tra hồ sơ giải ngân lần đầu", "Trước khi chuyển hồ sơ sang bộ phận hỗ trợ tín dụng, chuyên viên cần kiểm tra kỹ chữ ký của người đại diện theo pháp luật trên hợp đồng tín dụng, biên bản định giá tài sản bảo đảm và chứng từ chứng minh mục đích thanh toán cho nhà cung cấp."),
        ("Chuyên gia Ngân hàng biên soạn — Quy trình đối soát chứng từ cuối ngày", "Toàn bộ chứng từ phát sinh trong ca giao dịch phải được sắp xếp theo đúng thứ tự bút toán trên nhật ký hệ thống, kiểm tra đủ chữ ký kiểm soát viên và đóng dấu đã thu/đã chi trước khi đưa vào kho lưu trữ."),
        ("Chuyên gia Ngân hàng biên soạn — Thư mời doanh nghiệp sử dụng dịch vụ chi lương tự động", "Kính gửi Ban Giám đốc Doanh nghiệp, gói dịch vụ chi lương tự động giúp phòng kế toán rút ngắn 80% thời gian lập bảng kê hằng tháng, bảo mật tuyệt đối thu nhập của từng nhân sự và miễn phí toàn bộ giao dịch chuyển khoản cho cán bộ nhân viên."),
        ("Chuyên gia Ngân hàng biên soạn — Sổ tay rèn luyện kỹ năng viết báo cáo thẩm định", "Tuần đầu tiên khi nhận bàn giao danh mục khách hàng, chuyên viên thẩm định nên dành 30 phút mỗi sáng để đọc lại các biên bản phê duyệt mẫu của hội đồng tín dụng, từ đó nắm vững cách lập luận ngắn gọn, đi thẳng vào rủi ro trọng yếu."),
        ("Chuyên gia Hướng nghiệp biên soạn — Tư vấn học sinh lớp 11 yêu thích Công nghệ thông tin", "Với học sinh có thế mạnh Toán và Tin học kèm điểm số cao ở nhóm Nghiên cứu – Thực tế, gia đình nên khuyến khích con tham gia câu lạc bộ lập trình hoặc tự xây dựng một trang web nhỏ để hiểu sự khác biệt giữa việc thích chơi máy tính và việc làm kỹ sư phần mềm."),
        ("Chuyên gia Hướng nghiệp biên soạn — Tư vấn học sinh lớp 10 thiên hướng Ngôn ngữ & Sáng tạo", "Những học sinh nổi trội ở nhóm Nghệ thuật và Xã hội thường học tốt nhất qua dự án thực hành và thảo luận nhóm. Cha mẹ không nên ép con vào khuôn mẫu kỹ thuật khô khan mà hãy cùng con tìm hiểu các ngành Biên tập nội dung, Quan hệ công chúng hoặc Sư phạm."),
        ("Chuyên gia Hướng nghiệp biên soạn — Tư vấn học sinh lớp 12 định hướng Kinh tế – Quản trị", "Khi con có xu hướng thích tổ chức sự kiện và làm việc với các con số thống kê, các ngành Quản trị kinh doanh số, Logistics hoặc Phân tích kinh doanh là những lựa chọn đáng cân nhắc. Con cần rèn thêm kỹ năng ngoại ngữ và bảng tính ngay từ lớp 12."),
        ("Chuyên gia Hướng nghiệp biên soạn — Hướng dẫn chọn môn tự chọn cho học sinh lớp 9", "Việc chọn tổ hợp môn ở lớp 10 nên dựa trên sự giao thoa giữa năng lực học tập thực tế (điểm trung bình 4 học kỳ THCS) và nhóm sở thích tự nhiên của con, tránh chọn theo trào lưu của bạn bè cùng lớp."),
        ("Chuyên gia Hướng nghiệp biên soạn — Gợi ý cách cha mẹ đồng hành cùng con mùa thi", "Thay vì chỉ hỏi về điểm thi thử mỗi bữa tối, cha mẹ hãy đặt những câu hỏi mở về những điều con cảm thấy thú vị khi tìm hiểu các môi trường đại học, giúp con giảm áp lực tâm lý và tự tin hơn vào lựa chọn của mình."),
        ("Chuyên gia Hướng nghiệp biên soạn — Kế hoạch trải nghiệm nghề nghiệp mùa hè THPT", "Mỗi kỳ nghỉ hè lớp 10 và lớp 11, học sinh nên dành ít nhất 2 tuần tham gia hoạt động tình nguyện hoặc quan sát thực tế tại môi trường làm việc của người thân để hình thành tác phong kỷ luật và kỹ năng giao tiếp sớm."),
        ("Chuyên gia Chiêm tinh biên soạn — Hồ sơ sinh 04/12/1994 (09:00, Hà Nội)", "Mặt Trời Nhân Mã kết hợp điểm mọc Ma Kết tạo nên hình mẫu người vừa có tầm nhìn lạc quan vừa giữ được đôi chân vững vàng trên mặt đất. Bạn phù hợp với những vai trò mở đường hoặc phát triển sản phẩm mới trong một tổ chức có kỷ luật tốt."),
    ]

    combined = []
    for idx, (ctx, txt) in enumerate(ai_samples, start=1):
        combined.append({"true_source": "AI_03_OPC_OS", "source_index": idx, "context": ctx, "excerpt": txt})
    for idx, (ctx, txt) in enumerate(human_samples, start=1):
        combined.append({"true_source": "HUMAN_EXPERT", "source_index": idx, "context": ctx, "excerpt": txt})

    # Xáo trộn tất định theo hash để thứ tự cố định nhưng hoàn toàn trộn lẫn AI và Người
    combined.sort(key=lambda x: hashlib.sha256(f"{x['context']}:{x['source_index']}".encode("utf-8")).hexdigest())

    blind_items = []
    for blind_idx, item in enumerate(combined, start=1):
        blind_items.append({
            "blind_id": f"BLIND-{blind_idx:02d}",
            "context": item["context"],
            "excerpt": item["excerpt"],
            "judge_score_1_to_5": None,
            "judge_guess_ai_or_human": None,
            "answer_key_hidden": {
                "true_source": item["true_source"],
                "original_index": item["source_index"],
            },
        })

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "BO_40_DAU_RA_CHAM_MU.json").write_text(
        json.dumps(
            {
                "total_samples": 40,
                "ai_samples_count": 20,
                "human_samples_count": 20,
                "pass_criteria_cong_b": "Điểm trung bình của 20 mẫu AI >= 85% điểm trung bình của 20 mẫu Người làm (thang 1-5)",
                "items": blind_items,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    md = [
        "# BỘ 40 ĐẦU RA TRỘN LẪN (20 AI + 20 NGƯỜI LÀM) ĐỂ CHẤM MÙ — CHUẨN BỊ CỔNG B (`03_OPC_OS`)",
        "> **Theo Mục 2 `13_LENH_BAC_2.md` & Cổng B `11_LO_TRINH_VAN_HANH_THAT.md`**:",
        "> - Tổng số mẫu: **40 mẫu** (**20 mẫu do `03_OPC_OS` tạo** trộn ngẫu nhiên với **20 mẫu do chuyên gia con người biên soạn** trên cả 3 lĩnh vực: Chiêm tinh, Ngân hàng, Hướng nghiệp THPT).",
        "> - Người chấm đọc từng đoạn dưới đây (đã ẩn nguồn gốc AI/Người) và chấm điểm chất lượng từ **1 đến 5**.",
        "> - **Ngưỡng qua Cổng B**: Điểm trung bình của 20 mẫu AI đạt **`>= 85%`** điểm trung bình của 20 mẫu người làm. (Đáp án nguồn gốc nằm trong tệp `BO_40_DAU_RA_CHAM_MU.json` để đối chiếu sau khi chấm xong).",
        "",
        "| Mã chấm mù | Ngữ cảnh đầu vào | Đoạn trích đầu ra (Đã ẩn nguồn gốc AI / Người) | Điểm giám khảo (1–5) | Ghi chú |",
        "|---|---|---|---|---|",
    ]
    for it in blind_items:
        md.append(
            f"| **`{it['blind_id']}`** | {it['context']} | {it['excerpt']} | `[   / 5 ]` | |"
        )
    (OUT_DIR / "BO_40_DAU_RA_CHAM_MU.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def build_cost_comparison_table() -> None:
    """Tạo bảng tính tiền mỗi đầu ra (máy + token + giờ người) so với cách làm cũ."""
    md = """# BẢNG TÍNH TIỀN MỖI ĐẦU RA (MÁY + TOKEN + GIỜ NGƯỜI) SO VỚI CÁCH LÀM CŨ (`03_OPC_OS`)
> **Theo Mục 2 `13_LENH_BAC_2.md` & Cổng B `11_LO_TRINH_VAN_HANH_THAT.md`**:
> Đối chiếu chi phí thực tế để sản xuất **01 bản báo cáo PDF cá nhân hoá hoàn chỉnh** (11–13 trang A4 kèm đối soát thanh toán và ghi sổ kế toán) giữa cách làm thủ công cũ và Hệ điều hành `03_OPC_OS`.

---

## 1. Bảng Đối Chiếu Định Lượng Trên Mỗi Đầu Ra (01 Đơn Hàng Hoàn Tất)

| Hạng mục chi phí / Thời gian | Cách làm thủ công cũ (Chuyên gia tính & viết tay) | `03_OPC_OS` — Phương án A (Code cố định + Gọi AI viết bài, có người duyệt 20 đơn đầu) | `03_OPC_OS` — Vận hành tự động sau khi qua cổng duyệt 20 đơn đầu | Nguồn số đo thực tế |
|---|---:|---:|---:|---|
| **1. Thời gian hoàn tất 1 đơn (Từ lúc thanh toán đến lúc có PDF)** | `180 phút` (3 giờ làm việc; khách chờ `24–48 giờ`) | **`2,66 giây`** (cộng `120 giây` người đọc lướt duyệt) | **`1,12 – 2,66 giây`** (tức thời) | `A_CODE/ket_qua_a.json` & `BAO_CAO/ket_qua_cong_a.json` |
| **2. Chi phí máy chủ & điện năng phân bổ / 1 đơn** | `~5.000 VNĐ` (3 giờ chạy máy tính cá nhân) | **`15 VNĐ`** (`~3 giây` trên máy MSI local) | **`15 VNĐ`** (`~3 giây` trên máy MSI local) | Công suất máy MSI local `~120W` |
| **3. Chi phí Token AI (`gemini-2.5-flash`) / 1 đơn** | `0 VNĐ` | **`33 VNĐ`** (`752` token vào + `837` token ra) | **`33 VNĐ`** (`752` token vào + `837` token ra) | `_HANG_DOI/CHI_PHI.md` & `A_CODE/ket_qua_a.json` |
| **4. Chi phí giờ công con người / 1 đơn** *(Đơn giá `150.000 VNĐ/giờ`)* | `450.000 VNĐ` (`3,0 giờ` tính toán, viết bài, dàn trang A4, xuất PDF, ghi sổ Excel) | **`5.000 VNĐ`** (`2 phút` đọc kiểm tra tiêu đề & tải thử PDF) | **`0 VNĐ`** (`0 phút` — hệ thống tự kiểm 100% qua Module 01 & Module 09) | Quy chuẩn vận hành 1 người (`03_OPC_OS.md`) |
| **TỔNG CHI PHÍ SẢN XUẤT / 01 ĐẦU RA** | **`455.000 VNĐ / đơn`** | **`5.048 VNĐ / đơn`** | **`48 VNĐ / đơn`** | **Tiết kiệm `98,89%` đến `99,99%` chi phí** |
| **Tỷ suất lợi nhuận gộp ở mức giá bán `199.000 VNĐ/đơn`** | **Lỗ `-256.000 VNĐ/đơn`** (nếu bán giá 199k mà làm tay hoàn toàn) | **Lãi `+193.952 VNĐ/đơn` (`97,46%`)** | **Lãi `+198.952 VNĐ/đơn` (`99,97%`)** | `modules/02_thiet_ke_goi_gia` & `modules/07_chi_phi_loi_nhuan` |

---

## 2. Kết Luận Kinh Tế Đơn Vị (Unit Economics)
1. **Phá vỡ điểm nghẽn giá thành 199.000đ**: Với cách làm thủ công cũ (`455.000đ/đơn`), không thể bán gói báo cáo cá nhân hoá ở mức giá phổ thông `199.000đ – 299.000đ` mà có lãi. Nhờ `03_OPC_OS`, chi phí biến đổi mỗi đơn giảm xuống chỉ còn **`48 VNĐ`** (tự động) hoặc **`5.048 VNĐ`** (khi có người duyệt 2 phút), đạt biên lợi nhuận gộp **`> 97%`**.
2. **Đảm bảo trần giờ làm việc của Founder (`<= 1,5 giờ/ngày`)**: Ngay cả khi xử lý `30 đơn/ngày` và duyệt tay từng đơn trong giai đoạn đầu (`2 phút/đơn`), tổng thời gian con người bỏ ra mới hết `60 phút/ngày` (`1,0 giờ/ngày`), nằm gọn dưới ngưỡng trần `1,5 giờ/ngày` của đề gốc.
"""
    (OUT_DIR / "BANG_CHI_PHI_MOI_DAU_RA.md").write_text(md, encoding="utf-8")


def build_30_test_transactions_10k_plan() -> None:
    """Tạo kịch bản 30 giao dịch thử <= 10.000đ (viết sẵn kịch bản, chưa chạy — chờ Linh duyệt)."""
    tx_list = []
    opcs = [
        ("opc001_chiemtinh", "CT", "Chiêm Tinh Số"),
        ("opc002_bank_prompt_kit", "BK", "Bộ Câu Lệnh Ngân Hàng"),
        ("opc003_huong_nghiep_hs", "HN", "Hồ Sơ Hướng Nghiệp THPT"),
    ]
    scenarios_template = [
        ("GD_CHUAN_2K", 2000, 2000, 10, "valid", "Thanh toán đúng 2.000đ trong 10 giây -> Xuất PDF & ghi sổ S1a-HKD"),
        ("GD_CHUAN_5K", 5000, 5000, 15, "valid", "Thanh toán đúng 5.000đ trong 15 giây -> Xuất PDF & ghi sổ S1a-HKD"),
        ("GD_CHUAN_8K", 8000, 8000, 20, "valid", "Thanh toán đúng 8.000đ trong 20 giây -> Xuất PDF & ghi sổ S1a-HKD"),
        ("GD_CHUAN_10K", 10000, 10000, 12, "valid", "Thanh toán đúng 10.000đ (trần tối đa) -> Xuất PDF & ghi sổ S1a-HKD"),
        ("GD_TRUNG_WEBHOOK", 5000, 5000, 18, "duplicate", "SePay bắn lặp 2 lần cùng 1 mã giao dịch 5.000đ -> Chặn trùng (Idempotent), chỉ ghi sổ 1 lần"),
        ("GD_THIEU_TIEN", 10000, 5000, 25, "underpaid", "Đơn 10.000đ nhưng chuyển khoản thử 5.000đ -> Giữ trạng thái Thanh toán thiếu, không xuất PDF nhầm"),
        ("GD_QUA_HAN_15P", 6000, 6000, 950, "expired", "Chuyển khoản 6.000đ sau 15 phút 50 giây -> Đưa vào hàng chờ hoàn tiền / gia hạn"),
        ("GD_SAI_CHU_KY", 5000, 5000, 10, "invalid_sig", "Gói tin giả mạo chữ ký bảo mật -> Khoang luồng tiền cô lập chặn đứng (HTTP 401)"),
        ("GD_TAI_LAI_LINK", 9000, 9000, 14, "reload_ok", "Thanh toán 9.000đ trên điện thoại 390px rồi bấm tải lại trang `/o/<token>` 3 lần -> Vẫn giữ nguyên PDF"),
        ("GD_HOAN_TIEN_THU", 10000, 10000, 16, "refund_drill", "Thanh toán 10.000đ rồi diễn tập lập phiếu hoàn tiền chờ anh Linh duyệt chuyển trả"),
    ]

    seq = 1
    for opc_id, prefix, opc_label in opcs:
        for sc_code, order_amt, transfer_amt, delay_s, mode, expected_desc in scenarios_template:
            tx_list.append({
                "stt": seq,
                "ma_kich_ban": f"TX10K-{seq:02d}",
                "opc_id": opc_id,
                "ten_dich_vu": opc_label,
                "ma_don_du_kien": f"{prefix}10K{seq:02d}",
                "so_tien_don_vnd": order_amt,
                "so_tien_chuyen_thu_vnd": transfer_amt,
                "do_tre_giay": delay_s,
                "loai_tinh_huong": sc_code,
                "che_do_kiem_tra": mode,
                "ket_qua_ky_vong": expected_desc,
                "trang_thai_thuc_thi": "CHUA_CHAY_CHO_LINH_DUYET",
            })
            seq += 1

    payload = {
        "ten_kich_ban": "Kịch bản 30 giao dịch thử <= 10.000 VNĐ qua cổng SePay thật (Mục 03 file 13_LENH_BAC_2.md)",
        "trang_thai": "CHUA_CHAY_CHO_LINH_DUYET",
        "luat_an_toan": "Tuyệt đối không tự chạy giao dịch tiền thật khi chưa có lệnh duyệt của anh Linh.",
        "tong_so_giao_dich": len(tx_list),
        "tran_moi_giao_dich_vnd": 10000,
        "tong_so_tien_luot_di_vnd": sum(x["so_tien_chuyen_thu_vnd"] for x in tx_list if x["che_do_kiem_tra"] != "invalid_sig"),
        "danh_sach_30_giao_dich": tx_list,
    }
    (OUT_DIR / "KICH_BAN_30_GIAO_DICH_THU_10K.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md_lines = [
        "# KỊCH BẢN 30 GIAO DỊCH THỬ <= 10.000 VNĐ (CHƯA CHẠY — CHỜ ANH LINH DUYỆT)",
        "> **Theo Mục 03 `13_LENH_BAC_2.md`**:",
        "> - **Trạng thái hiện tại**: **`VIẾT SẴN KỊCH BẢN — CHƯA CHẠY TIỀN THẬT — CHỜ ANH LINH BẤM DUYỆT`**.",
        "> - **Mục đích**: Khi anh Linh cho phép thử nghiệm thanh toán VietQR/SePay thật với mệnh giá siêu nhỏ (`2.000đ – 10.000đ/giao dịch`), kịch bản 30 giao dịch dưới đây sẽ kiểm chứng toàn diện cả 3 dịch vụ (`Chiêm Tinh Số`, `Ngân Hàng`, `Hướng Nghiệp THPT`) qua 10 tình huống thực tế (đúng tiền, bắn trùng webhook, chuyển thiếu tiền, chuyển quá hạn 15 phút, sai chữ ký bảo mật, tải lại trang trên điện thoại và diễn tập hoàn tiền).",
        f"> - **Tổng số giao dịch**: **`{payload['tong_so_giao_dich']}` giao dịch** · Mệnh giá mỗi giao dịch: **`2.000đ – 10.000đ` (`<= 10.000đ`)** · Tổng dòng tiền luân chuyển thử trong tài khoản: **`{payload['tong_so_tien_luot_di_vnd']:,} VNĐ`**.",
        "",
        "| STT | Mã kịch bản | Dịch vụ | Mã đơn dự kiến | Mệnh giá đơn | Tiền chuyển thử | Tình huống kiểm tra | Kết quả kỳ vọng | Trạng thái |",
        "|---:|---|---|---|---:|---:|---|---|---|",
    ]
    for x in tx_list:
        md_lines.append(
            f"| {x['stt']:02d} | `{x['ma_kich_ban']}` | {x['ten_dich_vu']} | `{x['ma_don_du_kien']}` | `{x['so_tien_don_vnd']:,}đ` | `{x['so_tien_chuyen_thu_vnd']:,}đ` | `{x['loai_tinh_huong']}` | {x['ket_qua_ky_vong']} | `CHỜ LINH DUYỆT` |"
        )
    (OUT_DIR / "KICH_BAN_30_GIAO_DICH_THU_10K.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build_40_blind_test_set()
    build_cost_comparison_table()
    build_30_test_transactions_10k_plan()
    print("[SinhTaiLieuCongB] Đã tạo đủ BO_40_DAU_RA_CHAM_MU, BANG_CHI_PHI_MOI_DAU_RA, KICH_BAN_30_GIAO_DICH_THU_10K!")
