# Bảng mã lỗi chung

Mọi lượt soát trong plugin ghi lỗi bằng đúng các mã này, để gộp, đếm và học được. Cột "Gốc" cho biết mã lấy từ đâu: CQS và APS là hai prompt biên tập gốc của Linh (`goc/editor-qa.txt`, `goc/ai-detector.txt`), LAMP là 7 nhóm lỗi văn máy của Chakrabarty et al. 2025, CK là checklist biên tập của Linh (`goc/EDITORIAL_CHECKLIST.md`, phần C).

## Tầng sự thật
| Mã | Lỗi | Ví dụ | Gốc |
|---|---|---|---|
| NG | Khẳng định không có nguồn, hoặc nói nhiều hơn nguồn | gắn [N1] vào điều N1 không nói | LAB049 |
| SO | Số sai nguồn, sai đơn vị, bỏ chữ "tự khai", "đăng ký" | "BCG thấy" thay vì "người trả lời tự đánh giá" | LAB049 |
| BI | Bịa chi tiết (cảnh, người, lời nói) mà không gắn [GIẢ LẬP] | slide "mười hai robot" | LAB049 |
| PL | Sai thuật ngữ pháp lý, tên văn bản, tên cơ quan | "giấy phép" thay vì "giấy chứng nhận đăng ký doanh nghiệp" | LAB049 |

## Tầng cấu trúc
| Mã | Lỗi | Gốc |
|---|---|---|
| MD | Mạch đứt: nhắc điều bài chưa giới thiệu, nhảy ý không cầu nối | CQS 1 |
| LA | Lặp ý: cùng một ý hai lần, khác chữ | APS 3, ai_detector "lặp ý" |
| TH | Thừa đoạn: đoạn không phục vụ luận điểm hay hộp "bài này nói gì" | CQS 1 |
| NH | Nhịp: đoạn đều nhau, cảm xúc leo đều, bài "tròn trịa" | APS 1, ai_detector R4 R6 Y2 |
| MO | Mở bằng bối cảnh, lý thuyết hoặc câu hỏi tu từ | CK 8 |
| KE | Kết khuyên nhủ, tóm tắt, tích cực gượng | CK 9, ai_detector R3 R5 |
| DO | Lệch độ dài so với đơn đặt hàng | LAB049 |
| BU | Gạch đầu dòng, tiêu đề mục rời trong văn xuôi | CK 10 |

## Tầng câu và chữ
| Mã | Lỗi | Gốc |
|---|---|---|
| VD | Văn dịch: "đóng vai trò", "trong bối cảnh", bị động "được… bởi", "sự/việc/của" dày | CQS 5, LAMP |
| KH | Khuôn máy: bộ ba cân bằng, "không phải X mà là Y", câu chốt đúc sẵn, câu hỏi tu từ cuối đoạn | APS 1 và 3, ai_detector R1 R2, LAMP |
| SA | Sáo ngữ, cụm thời thượng | ai_detector "cliché", LAMP |
| TT | Trừu tượng, thiếu cảnh, danh từ chung thay danh từ cụ thể | APS 2, LAMP |
| GT | Giải thích lại điều câu trước đã cho thấy | APS 3, LAMP |
| TU | Từ thừa (cắt mà nghĩa không đổi), trạng từ, tính từ thừa | CQS 2 |
| CU | Câu cụt, ba câu ngắn liền nhau, nên nối | CK 1 |
| SS | Song hành lệch, định ngữ đặt sai chỗ gây tối nghĩa | CQS 3 và 4 |
| GI | Lệch giọng: lên giọng, rao giảng, trị liệu, cảm xúc nói thẳng, "chúng ta" dày | CQS 6, LAMP |
| SC | Số viết bằng chữ số trong văn xuôi | CK 7 |

## Tầng độc giả
| Mã | Lỗi | Gốc |
|---|---|---|
| KH-DG | Độc giả không hiểu, phải đọc lại | LAB049 |
| BO | Độc giả suýt bỏ đọc | LAB049 |
| TAY | Độc giả thấy "như Tây dịch", "như sách giáo khoa" | LAB049 |
| CAI | Độc giả muốn cãi mà bài chưa trả lời | LAB049 |

## Mức nặng
- **Chặn**: NG, SO, BI, PL, và mọi lỗi trúng sổ hồi quy. Không giao bài khi còn.
- **Nặng**: MD, LA, TH, KE, BU, KH, GI, CAI.
- **Nhẹ**: các mã còn lại.

Hồ sơ biên tập viên (`ho-so-bien-tap/<ten>/LUAT.md`) có thể thêm mã riêng, đặt tên dạng `VA-01`, `VA-02`, và ghi rõ luật đó thuộc tầng nào, mức nặng nào.

## Mã từ hồ sơ Vân Anh (19/10/2026, xem `ho-so-bien-tap/van-anh/LUAT.md`)
`HV` so sánh hai vế (VA-01, VA-02) · `AD` ẩn dụ xuyên đoạn, chồng danh từ (VA-05) · `FT` thả số liệu không gánh luận điểm (VA-04) · `CT` chủ thể mơ hồ (VA-06) · `CK` chuyện kể nghe không thật (VA-07, mức chặn) · `DN` thuật ngữ chưa giải nghĩa. Mức nặng, trừ `CK`.
