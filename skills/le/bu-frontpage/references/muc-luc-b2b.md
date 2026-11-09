# Mục lục yêu cầu của một BU B2B (đối chiếu IF Agent Event, 9/11)

Phạm vi WF01: frontend, giao diện, flow, own media, GEO. Phần lõi (CRM, chăm sóc tự động, thu tiền, ads) chỉ ghi để biết chỗ nối, không làm ở đây.

Ký hiệu trạng thái: ✓ có · ◐ nháp hoặc một phần · ✗ thiếu · ↗ thuộc lõi engine.
Ưu tiên: **P0** cần trước khi lên (sau CSMO 20/11) · **P1** trong 2 tuần sau khi lên · **P2** khi có số và nguồn lực.
Ai: **C** = Claude/agy dựng · **H** = chị Hằng/IF Agent đưa dữ liệu · **L** = Linh quyết.

## A. Đầu vào chiến lược
| # | Yêu cầu | Ưu tiên | Ai | IF Agent Event |
|---|---|---|---|---|
| A1 | Chân dung người mua: ai quyết định, ai tác động, ai dùng (bên tổ chức, agency, marketing brand) | P0 | C+H | ◐ có trong NGHIEN-CUU, chưa có bản chốt |
| A2 | Ba câu người mua hỏi đầu tiên và câu trả lời | P0 | H | ◐ biết câu hỏi (giá, thời gian dựng, case), chưa có số trả lời |
| A3 | Định vị một câu, điểm khác đối thủ | P0 | L | ✓ dữ liệu khách + nhân vật AI |
| A4 | Danh mục giải pháp theo đầu ra cho khách | P0 | C | ✓ 3 giải pháp |
| A5 | Gói dựng sẵn: gồm gì, giá hoặc khoảng giá, thời gian dựng, cọc | P0 | H | ◐ khung 3 gói có, **thiếu giá và thời gian thật** |
| A6 | Bằng chứng: case có số, ảnh/video thật, khách được nêu tên, lời xác nhận | P0 | H | **✗ chặn chất lượng** |
| A7 | Kho vấn đề khách (20–30 vấn đề từ câu hỏi thật) | P1 | C+H | ✗ |
| A8 | Đối thủ và bản đồ giá thị trường | P1 | C | ◐ chờ Deep Research DE-1 |
| A9 | Giọng thương hiệu, từ nên dùng và từ cấm | P0 | C | ✓ brand-ifagent + soát văn AI |

## B. Nhận diện và giao diện
| # | Yêu cầu | Ưu tiên | Ai | IF Agent Event |
|---|---|---|---|---|
| B1 | Logo, màu, chữ theo guideline | P0 | C | ✓ LAB043 |
| B2 | DESIGN.md + token + khoá băm + ảnh chuẩn | P0 | C | ✓ phương án A đã khoá |
| B3 | Bộ khối dùng lại (hero, gói, bảng, FAQ, CTA, form) | P0 | C | ✓ trong site.css + tao-trang.py |
| B4 | Ảnh thật sự kiện 10–20 tấm, video 15–30 giây | P0 | H | **✗** |
| B5 | Ảnh chia sẻ (OG), favicon | P0 | C | ✓ |
| B6 | Mẫu ấn phẩm MXH, bìa trang Facebook/LinkedIn/Zalo OA cùng bộ khoá | P1 | C | ✗ |

## C. Trang web
| # | Trang | Việc của trang | Ưu tiên | IF Agent Event |
|---|---|---|---|---|
| C1 | Trang chủ | Trả lời 3 câu trong 10 giây, dẫn tới form | P0 | ✓ |
| C2 | Giải pháp (trang tổng) | Chọn giải pháp theo việc | P0 | ✓ |
| C3 | Từng giải pháp (3 trang) | Giải thích, FAQ riêng, CTA | P0 | ✓ |
| C4 | Gói và giá | So sánh gói, giá phụ thuộc vào đâu, may đo | P0 | ✓ trang có, chờ giá |
| C5 | Dự án / case | Mỗi case: việc, giải pháp, số, người xác nhận | P0 | ◐ khung, **chờ số** |
| C6 | Theo loại sự kiện (hội chợ, ra mắt, hội nghị) | Bắt từ khoá theo ngữ cảnh, dẫn về gói | P1 | ✓ |
| C7 | Cho agency | Đối tác bán lại, hỗ trợ pitch | P1 | ✓ |
| C8 | Giới thiệu | Ai đứng sau, tin vào gì, liên hệ | P0 | ◐ **thiếu đội ngũ, pháp nhân** |
| C9 | Liên hệ | Form + Zalo + email + địa chỉ | P0 | ✓ thiếu địa chỉ |
| C10 | Hỏi đáp | 10 câu, schema FAQ | P0 | ✓ |
| C11 | Cẩm nang + trang trụ "công nghệ sự kiện" | GEO, kéo khách tìm kiếm | P0 | ✓ chờ chị Hằng duyệt |
| C12 | 10–20 bài theo kho vấn đề | Cụm bài quanh trang trụ | P1 | ✗ |
| C13 | Cảm ơn | Sau gửi brief, đo chuyển đổi, bước tiếp | P0 | ✓ |
| C14 | Tải hồ sơ năng lực (đổi email) | Mồi cho người chưa sẵn sàng gửi brief | P1 | ✗ cần PDF |
| C15 | Công cụ tính gói | Mồi tương tác, điền sẵn form | P0 | ✓ trên trang chủ |
| C16 | Chính sách dữ liệu | Nghị định 13/2023 | P0 | ◐ nháp, **chờ pháp chế** |
| C17 | Điều khoản sử dụng | | P1 | ✗ |
| C18 | 404 | | P0 | ✓ |
| C19 | Bản tiếng Anh (khách FDI, agency nước ngoài) | | P2 | ✗ |
| C20 | Tuyển dụng / đối tác thiết bị | | P2 | ✗ |

## D. Flow chuyển đổi
| # | Yêu cầu | Ưu tiên | Ai | IF Agent Event |
|---|---|---|---|---|
| D1 | Form brief: bắt buộc tối thiểu, đồng ý không tick sẵn, bẫy bot | P0 | C | ✓ |
| D2 | Giữ nguồn `?kenh=` + utm theo phiên, ghi vào lead | P0 | C | ✓ |
| D3 | Mã lead trả về, chuyển trang cảm ơn | P0 | C | ✓ |
| D4 | Báo người phụ trách ngay (Telegram/Zalo/Sheet) | P0 | C+L | ◐ code có, **chưa có token** |
| D5 | Thư xác nhận tự động cho khách | P0 | C | ◐ mẫu xong; gửi thật cần dịch vụ mail ↗ |
| D6 | Follow-up 24 giờ và 5 ngày | P0 | H | ✓ mẫu, chờ duyệt |
| D7 | Nút Zalo nổi trên điện thoại | P0 | C | ✓ |
| D7b | Form gọi lại nhanh (tên + số + đồng ý) | P0 | C | ✓ |
| D8 | Đặt lịch gọi 15 phút | P1 | C+H | ✗ |
| D9 | Đường lùi khi form lỗi (Zalo) | P0 | C | ✓ |
| D10 | Chấm lead (gói, ngân sách, ngày sự kiện gần) | P1 | ↗ | ✗ |
| D11 | Chuỗi chăm sóc theo trạng thái (ONBOARD) | P2 | ↗ | ✗ |

## E. Tài liệu bán hàng
| # | Yêu cầu | Ưu tiên | Ai | IF Agent Event |
|---|---|---|---|---|
| E1 | Hồ sơ năng lực PDF 8–12 trang | P1 | C+H | ✗ (WF03/WF05) |
| E2 | Mẫu báo giá theo gói | P0 | H | ✗ |
| E3 | Case một trang | P1 | C+H | ✗ chờ số |
| E4 | Mẫu báo cáo số đo 24 giờ (để khách thấy trước) | P0 | C | ✓ trang /mau-bao-cao/ |
| E5 | Checklist kỹ thuật gửi bên tổ chức | P1 | C | ◐ rải trong trang loại sự kiện |
| E6 | Mẫu brief tải về | P2 | C | ✗ |

## F. GEO / SEO
| # | Yêu cầu | Ưu tiên | Ai | IF Agent Event |
|---|---|---|---|---|
| F1 | Cụm từ muốn sở hữu + bản đồ từ khoá → trang | P0 | C | ◐ có cụm, chưa có bản đồ |
| F2 | title/description/h1/canonical từng trang | P0 | C | ✓ cổng K10 kiểm |
| F3 | JSON-LD: Organization, Service, FAQPage, Breadcrumb, Article | P0 | C | ✓ |
| F4 | sitemap.xml, robots.txt, llms.txt | P0 | C | ✓ |
| F5 | Google Search Console + Bing Webmaster, gửi sitemap | P0 | L | ✗ cần quyền domain |
| F6 | Google Business Profile | P1 | H | ✗ |
| F7 | Đo AI nhắc tên khi hỏi "photobooth AI", "công nghệ sự kiện Việt Nam" (LAB036) | P1 | C | ✗ |
| F8 | Nhắc tên trên trang ngoài: danh bạ event, báo, đối tác CSMO | P1 | H | ✗ |
| F9 | 301 từ đường dẫn cũ của event.ifagent.net | P0 | C | ✗ **cần đọc site cũ trên máy cty** |

## G. Own media
| # | Yêu cầu | Ưu tiên | Ai | IF Agent Event |
|---|---|---|---|---|
| G1 | Danh sách kênh + người giữ tài khoản | P0 | H | **✗ chưa biết** |
| G2 | Trụ nội dung và tỉ lệ | P0 | C | ◐ |
| G3 | Lịch 3 pha CSMO (trước/trong/sau), link đo | P0 | C | ✓ 25 bài |
| G4 | Toàn văn bài từng kênh, soát văn AI | P0 | C | ✓ chờ duyệt |
| G5 | Quy trình duyệt (ai duyệt, hạn) | P0 | L | ◐ mặc định chị Hằng |
| G6 | Kho ảnh/video từ sự kiện, quyền dùng | P0 | H | ✗ |
| G7 | Lớp đăng (Postiz) | P1 | ↗ | ✗ |
| G8 | Bản tin email tháng | P2 | C | ✗ |
| G9 | Trang cá nhân LinkedIn chị Hằng | P1 | H | ✗ |

## H. Đo lường
| # | Yêu cầu | Ưu tiên | Ai | IF Agent Event |
|---|---|---|---|---|
| H1 | Quy ước utm + `kenh` | P0 | C | ✓ |
| H2 | Công cụ đo truy cập (GA4 hoặc Plausible) + sự kiện chuyển đổi gửi brief | P0 | L | ✗ chọn công cụ |
| H3 | Pixel Meta / LinkedIn (chỉ khi chạy ads, kèm thông báo cookie) | P2 | L | ✗ |
| H4 | Bảng lead theo kênh, tuần | P1 | ↗ | ✗ |
| H5 | Cảnh báo form im 48 giờ hoặc hỏng (LEAD-WATCH) | P1 | C | ◐ có `/api/song` để canh |

## I. Pháp lý và tin cậy
| # | Yêu cầu | Ưu tiên | Ai | IF Agent Event |
|---|---|---|---|---|
| I1 | Tên pháp nhân, mã số thuế, địa chỉ ở chân trang | P0 | H | **✗** |
| I2 | Chính sách dữ liệu, lưu bằng chứng đồng ý | P0 | H | ◐ nháp + server lưu đồng ý |
| I3 | Đồng ý ảnh chân dung tại sự kiện | P0 | H | ◐ nêu trong trang, cần mẫu thật |
| I4 | Quyền dùng ảnh, logo khách | P0 | H | ✗ |
| I5 | Thông báo cookie (khi có pixel) | P2 | C | — |

## J. Kỹ thuật và vận hành
| # | Yêu cầu | Ưu tiên | Ai | IF Agent Event |
|---|---|---|---|---|
| J1 | Máy chủ, HTTPS, domain | P0 | L | ✗ chờ VM |
| J2 | Cổng máy K1–K10 chạy mỗi lần sửa | P0 | C | ✓ |
| J3 | Sao lưu `leads.jsonl` hằng ngày | P0 | C | ✗ |
| J4 | Canh sống (uptime) | P1 | C | ✗ |
| J5 | Gửi mail có SPF/DKIM | P1 | L | ✗ |

## Chặn lớn nhất
A5 giá và thời gian dựng, A6 case có số, B4 ảnh thật, I1 pháp nhân, G1 người giữ kênh. Cả năm thứ đều cần IF Agent đưa. Không có thì trang vẫn chạy được nhưng thiếu bằng chứng, chấm mù dễ trượt.

## Claude làm được ngay mà không chờ ai (P0)
C2, C4, C6–C11, C13 sinh trang; D3 chuyển trang cảm ơn; D7 nút Zalo nổi; E4 mẫu báo cáo 24 giờ; F1 bản đồ từ khoá; G3–G4 lịch và bài; J3 sao lưu lead.
