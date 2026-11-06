import frappe

WORKFLOWS = [
    {"ma": "kiem-duong-ong", "ten": "Kiểm đường ống", "che_do": "kiem", "tran_phut": 2,
     "mo_ta": "Thợ tự trả lời, không gọi agy. Dùng để thử thợ mới đã nối đúng chưa.",
     "de_mau": "{dau_vao}", "vi_du": "xin chào"},
    {"ma": "viet-nhap", "ten": "Viết nháp", "che_do": "agy", "tran_phut": 15,
     "mo_ta": "agy viết một bản nháp ngắn bằng tiếng Việt theo chủ đề.",
     "de_mau": "Viết bằng tiếng Việt, thuần Việt, câu đủ ý, không giọng AI, không chêm tiếng Anh, tối đa 300 chữ. Chỉ trả về bài viết, không giải thích.\n\nChủ đề: {dau_vao}",
     "vi_du": "Vì sao một người làm sản phẩm cần ghi lại mọi tình huống của khách"},
    {"ma": "nghien-cuu-nhanh", "ten": "Nghiên cứu nhanh", "che_do": "agy", "tran_phut": 20,
     "mo_ta": "agy tìm hiểu nhanh một câu hỏi, trả 5 ý chính có nguồn.",
     "de_mau": "Tìm hiểu nhanh câu hỏi dưới đây. Trả lời tiếng Việt: 5 ý chính, mỗi ý 1 câu, kèm đường dẫn nguồn nếu có. Không tạo hay sửa file nào.\n\nCâu hỏi: {dau_vao}",
     "vi_du": "Frappe Framework v15 khác v16 điểm nào đáng kể"},
    {"ma": "lam-phieu-code", "ten": "Làm phiếu code", "che_do": "agy", "tran_phut": 40, "nhan_can": "repo",
     "mo_ta": "agy làm một phiếu ≤40 phút trong thư mục repo của thợ, theo AGENTS.md của repo. Chỉ thợ có nhãn repo nhận.",
     "de_mau": "Làm phiếu sau trong repo hiện tại, theo AGENTS.md. Không đụng tests/nghiem-thu, không đưa bí mật. Xong thì tóm tắt đã sửa file nào và kết quả test.\n\nPhiếu: {dau_vao}",
     "vi_du": "Thêm mục README hướng dẫn chạy test"},
    {"ma": "ai-noi-gi-ve-brand", "ten": "AI nói gì về thương hiệu của bạn", "che_do": "gop", "tran_phut": 60,
     "mo_ta": "Quy trình gộp: mỗi AI (ChatGPT, Gemini, Claude) một việc 'hoi-mot-ai' trên máy có trình duyệt, rồi một việc 'viet-bao-cao' gán nhãn và viết nhận định. Server tính 4 chỉ số.",
     "de_mau": "", "vi_du": "brand: (tên thương hiệu)\nnganh: (ngành)\nthi_truong: Việt Nam\ndoi_thu: (một đối thủ)\nsu_that: (3 sự thật)"},
    {"ma": "hoi-mot-ai", "ten": "Hỏi một AI qua trình duyệt", "che_do": "agy", "tran_phut": 12, "nhan_can": "trinh-duyet",
     "mo_ta": "Bước 1 của báo cáo thương hiệu: agy mở một trang AI, hỏi 2–3 câu, chép nguyên văn.", "de_file": "hoi_mot_ai.md"},
    {"ma": "cham-mot-ai", "ten": "Gán nhãn câu trả lời của một AI", "che_do": "agy", "tran_phut": 10,
     "mo_ta": "Bước 2: gán nhãn đúng/sai/đề xuất và dữ kiện cho 8 câu của một AI. Thợ nào cũng nhận.", "de_file": "cham_mot_ai.md"},
    {"ma": "viet-bao-cao", "ten": "Viết nhận định báo cáo thương hiệu", "che_do": "agy", "tran_phut": 10,
     "mo_ta": "Bước 3: từ nhãn và chỉ số đã tính, viết điểm sai, bước rơi, lớp yếu, kế hoạch 30 ngày. Thợ nào cũng nhận.", "de_file": "viet_bao_cao.md"},
]


def after_install():
    if frappe.db.get_single_value("System Settings", "time_zone") != "Asia/Ho_Chi_Minh":
        frappe.db.set_single_value("System Settings", "time_zone", "Asia/Ho_Chi_Minh")
    for role in ("LX Operator", "LX Worker"):
        if not frappe.db.exists("Role", role):
            frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1 if role == "LX Operator" else 0}).insert(ignore_permissions=True)
    for wf in WORKFLOWS:
        wf = dict(wf)
        f = wf.pop("de_file", None)
        if f:
            with open(frappe.get_app_path("linhx_worker", "de", f), encoding="utf-8") as fh:
                wf["de_mau"] = fh.read()
        if not frappe.db.exists("LX Workflow", wf["ma"]):
            frappe.get_doc({"doctype": "LX Workflow", "bat": 1, **wf}).insert(ignore_permissions=True)
        else:
            # cau hinh workflow chuan lay tu code (ban moi nhat cua app); chi giu nguyen co 'bat'
            frappe.db.set_value("LX Workflow", wf["ma"], {k: v for k, v in wf.items() if k != "ma"})
    frappe.db.commit()


def tao_tho(ma, loai="may", may="", nhan=""):
    """bench --site X execute linhx_worker.setup.tao_tho --kwargs "{'ma':'may-cty','nhan':'repo,windows'}"
    In ra khoa API dang key:secret (chi hien mot lan)."""
    email = f"tho-{ma}@linhx.local"
    if not frappe.db.exists("User", email):
        u = frappe.get_doc({"doctype": "User", "email": email, "first_name": f"Thợ {ma}", "user_type": "System User", "send_welcome_email": 0})
        u.insert(ignore_permissions=True)
    u = frappe.get_doc("User", email)
    if "LX Worker" not in [r.role for r in u.roles]:
        u.add_roles("LX Worker")
    key = u.api_key or frappe.generate_hash(length=15)
    secret = frappe.generate_hash(length=15)
    u.api_key = key
    u.api_secret = secret
    u.save(ignore_permissions=True)
    if not frappe.db.exists("LX Worker", ma):
        frappe.get_doc({"doctype": "LX Worker", "ma": ma, "loai": loai, "may": may, "nhan": nhan, "user": email}).insert(ignore_permissions=True)
    else:
        frappe.db.set_value("LX Worker", ma, {"user": email, "loai": loai, "nhan": nhan})
    frappe.db.commit()
    print(f"LINHX_TOKEN={key}:{secret}")
    return f"{key}:{secret}"


def tao_dieu_hanh(email, mat_khau, ten="Linh"):
    if not frappe.db.exists("User", email):
        frappe.get_doc({"doctype": "User", "email": email, "first_name": ten, "send_welcome_email": 0, "new_password": mat_khau}).insert(ignore_permissions=True)
    from frappe.utils.password import update_password
    update_password(email, mat_khau)
    u = frappe.get_doc("User", email)
    u.add_roles("LX Operator", "System Manager")
    frappe.db.commit()
    print("ok", email)
