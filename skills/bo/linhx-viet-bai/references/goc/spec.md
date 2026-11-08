ANTIGRAVITY CO-WRITING ENGINE: "FLOW v FM"Technical Specification & Agent Orchestration GuideProject Name: Antigravity Narrative EngineTarget Persona: Đinh Trần Tuấn Linh (Narrative Nonfiction / Byung-Chul Han Style)Version: 4.0 (Fully Automated & Modular Research)Status: Implementation ReadyI. NGUYÊN TẮC CỐT LÕI & CẤU TRÚC DỮ LIỆU1. Nguyên Tắc Vận Hành (Core Principles)Automation First: Toàn bộ quy trình từ lúc nhập Idea đến khi ra bài viết cuối cùng là tự động. Các bước chọn lọc, lập kế hoạch đều do AI giả lập quyết định.State Preservation: Lưu file vật lý sau mỗi bước để đảm bảo có thể debug hoặc resume.Simulated Persona: AI phải tự đóng vai tác giả để đưa ra các lựa chọn mang tính chủ quan (bias) tại các bước chọn lọc thông tin, thay vì chờ người dùng.Iterative Refinement: Vẫn giữ nguyên vòng lặp "Critic Loop" để đảm bảo chất lượng.2. Cấu Trúc Thư Mục (Directory Structure)Cấu trúc giữ nguyên để đảm bảo tính tổ chức dữ liệu./Antigravity_Workspace
  ├── /Idea_{Timestamp}_{Slug_Name}  <-- Root Project Folder
  │   ├── 01_Seed_Input.json             (User Input)
  │   ├── 02_Context_Expansion.json      (AI tự hỏi tự trả lời)
  │   ├── 03_Research_Plan.md            (AI tự lập kế hoạch)
  │   ├── 04_Raw_Research_Data.json      (Kết quả tìm kiếm từ LLM + Web Search)
  │   ├── 05_Synthesis_Insights.md       (30 "Tứ" thô)
  │   ├── 06_AI_Curated_List.json        (AI đóng vai User để chọn lọc & thêm thắt)
  │   ├── /07_The_Critic_Loop
  │   │   ├── /Loop_01...
  │   │   ├── /Loop_02...
  │   │   └── ...
  │   └── 08_Final_Output.md             (Kết quả cuối cùng)
  └── /System_Prompts
II. QUY TRÌNH CHI TIẾT (FULLY AUTOMATED FLOW)BƯỚC 1: GIEO MẦM (SEEDING) - Bước duy nhất cần UserHành động: User nhập ý tưởng.Lưu trữ: 01_Seed_Input.jsonInput mẫu: "Sự chung thủy trong thời đại Tinder chỉ là do thiếu cơ hội."BƯỚC 2: MỞ RỘNG GÓC NHÌN (CONTEXT AGENT)Input: 01_Seed_Input.jsonCơ chế tự động: Agent tự chạy, tự trả lời toàn bộ 11 câu hỏi. Không chờ User tick chọn. Nó sẽ tự đánh dấu (flag) 3 câu trả lời "đắt" nhất để ưu tiên cho bước sau.➤ PROMPT (CONTEXT AGENT)ROLE: Bạn là nhà quan sát xã hội sắc sảo (Cynical Observer).
TASK: Phân tích ý tưởng: "{INPUT_IDEA}".
ACTION:
1. Trả lời 11 câu hỏi Deep Inquiry (như phiên bản cũ).
2. QUAN TRỌNG: Tự đánh giá và thêm trường "priority": true cho 3 câu hỏi/câu trả lời mang lại góc nhìn đột phá nhất.
OUTPUT: JSON format đầy đủ.
Lưu trữ: 02_Context_Expansion.jsonBƯỚC 3: THIẾT KẾ NGHIÊN CỨU (ARCHITECT AGENT)Input: 02_Context_Expansion.json (Ưu tiên các mục có priority: true).Cơ chế tự động: Tự động convert các góc nhìn thành danh sách từ khóa tìm kiếm.➤ PROMPT (ARCHITECT AGENT)ROLE: Research Lead.
TASK: Lập kế hoạch tìm kiếm dữ liệu.
NOTE: Chỉ tập trung vào các Keywords và Questions để nạp cho công cụ Search.
OUTPUT: Markdown List.
Lưu trữ: 03_Research_Plan.mdBƯỚC 4: THỰC THI NGHIÊN CỨU (SCOUT AGENT - MODULAR)Input: 03_Research_Plan.mdCơ chế hiện tại (Phase 1): Sử dụng LLM kết hợp công cụ Search cơ bản (Google Search/Bing Search Tool) để tổng hợp thông tin.Cơ chế tương lai (Phase 2): Đây là điểm chờ (Interface) để gọi DeepResearch API.Yêu cầu đầu ra: Dù dùng công cụ nào, output phải luôn là JSON chứa danh sách các snippets/quotes/stats tìm được.➤ PROMPT (SCOUT AGENT - BASIC SEARCH)ROLE: Research Assistant.
TASK: Dựa trên Research Plan, hãy sử dụng công cụ tìm kiếm để thu thập thông tin.
REQUIREMENT:
- Tìm số liệu cụ thể.
- Tìm các quan điểm triết học liên quan (Byung-Chul Han, Zygmunt Bauman...).
- Tìm các case study thực tế.
OUTPUT: JSON Raw Data (Source URL + Content Snippet).
Lưu trữ: 04_Raw_Research_Data.jsonBƯỚC 5: TỔNG HỢP (ANALYST AGENT)Input: 04_Raw_Research_Data.jsonNhiệm vụ: Nén dữ liệu thành 30 Insights.Lưu trữ: 05_Synthesis_Insights.md (Format Markdown Bullet points).BƯỚC 6: AI CURATION (SIMULATED USER) - Thay thế HumanĐây là bước quan trọng nhất để hệ thống tự động hóa nhưng vẫn có "hồn". Một Agent sẽ đóng vai chính tác giả (Đinh Trần Tuấn Linh) để chọn lọc.Input: 05_Synthesis_Insights.mdAgent: The Author Simulator.➤ PROMPT (CURATOR AGENT)ROLE: Bạn chính là tác giả Đinh Trần Tuấn Linh.
CONTEXT: Bạn đang đọc danh sách 30 dữ liệu thô mà trợ lý gửi lên.
TASK:
1. SÀNG LỌC: Hãy chọn ra 10-12 ý (facts/insights) mà bạn thấy tâm đắc nhất, phù hợp với giọng văn "lạnh", "mỉa mai" và "triết luận" của bạn. Loại bỏ những ý sáo rỗng.
2. SÁNG TẠO (QUAN TRỌNG): Hãy tự viết thêm 2-3 "Ghi chú cá nhân" (Personal Anecdotes). Đây là những câu chuyện ngắn hoặc quan sát đời thường mà bạn "nhớ ra" khi đọc dữ liệu.
   - Ví dụ: "Nhớ lại hồi ngồi cafe ở Paris...", hoặc "Hôm qua thấy một đôi tình nhân cãi nhau ở Circle K...".
   - Mục đích: Làm cho bài viết có cảm giác được viết bởi con người có trải nghiệm.

OUTPUT: File JSON `06_Curated_List.json` chứa danh sách final để đưa sang viết bài.
Lưu trữ: 06_AI_Curated_List.jsonBƯỚC 7 & 8: THE CRITIC LOOP (GIỮ NGUYÊN)Quy trình tự động viết và tự sửa bài.Writer Agent: Nhận input từ 06_AI_Curated_List.json. Viết Draft v1.Critic Agent: Chấm điểm v1. Nếu < 9 điểm -> Generate Feedback (JSON).Writer Agent: Nhận Feedback -> Viết lại Draft v2.Lặp: Tối đa 3 lần.Lưu trữ: Thư mục /07_The_Critic_LoopBƯỚC 9: FINAL OUTPUTHành động: Copy bản Draft tốt nhất từ Loop ra ngoài.Lưu trữ: 08_Final_Output.mdKết quả: User nhận được bài viết hoàn chỉnh cuối cùng mà không cần động tay vào bất kỳ bước nào ở giữa.III. GHI CHÚ KỸ THUẬT VỀ RESEARCH APIHiện tại Step 4 đang chạy bằng LLM + Search Tool Prompting. Để chuẩn bị cho việc nâng cấp lên DeepResearch API sau này, Dev cần lưu ý:Interface Isolation: Code xử lý Step 4 nên tách thành một function riêng execute_research(plan_object).Data Contract: Đầu ra của function này phải luôn đảm bảo format JSON chuẩn:[
  {
    "source": "url",
    "type": "stat/quote/theory",
    "content": "text content..."
  },
  ...
]
Future Upgrade: Khi có DeepResearch API, chỉ cần thay ruột function execute_research, input (Plan) và output (JSON) giữ nguyên, không ảnh hưởng đến Step 3 và Step 5.