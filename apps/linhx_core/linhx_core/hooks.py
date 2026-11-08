from linhx_core.co_module import DOCTYPE_MODULE

app_name = "linhx_core"
app_title = "LINHX Core"
app_publisher = "LINHX"
app_description = "Khung app Frappe linhx_core cho LINHX ENGINE"
app_email = "dev@linhx.vn"
app_license = "mit"

NHAT_KY_HOOK = "linhx_core.linhx_core.doctype.lx_nhat_ky_truy_cap.lx_nhat_ky_truy_cap.ghi_nhat_ky_truy_cap"
DOCTYPE_KHACH = ("LX Nguoi", "LX To Chuc", "LX Don Vi")

before_request = ["linhx_core.co_module.frappe_before_request"]
after_request = ["linhx_core.linhx_core.doctype.lx_nhat_ky_truy_cap.lx_nhat_ky_truy_cap.ghi_nhat_ky_tu_request"]

has_permission = {
    dt: "linhx_core.co_module.frappe_has_permission"
    for dt in DOCTYPE_MODULE
}

permission_query_conditions = {
    dt: "linhx_core.co_module.frappe_permission_query_conditions"
    for dt in DOCTYPE_MODULE
}

doc_events = {
    **{
        dt: {
            "before_insert": "linhx_core.co_module.frappe_kiem_tra_doc_event",
            "validate": "linhx_core.co_module.frappe_kiem_tra_doc_event",
            "on_trash": (
                ["linhx_core.co_module.frappe_kiem_tra_doc_event", NHAT_KY_HOOK]
                if dt in DOCTYPE_KHACH
                else "linhx_core.co_module.frappe_kiem_tra_doc_event"
            ),
            **(
                {
                    "onload": NHAT_KY_HOOK,
                    "after_insert": NHAT_KY_HOOK,
                    "on_update": NHAT_KY_HOOK,
                }
                if dt in DOCTYPE_KHACH
                else {}
            ),
        }
        for dt in DOCTYPE_MODULE
    },
    "LX Cau Hinh": {
        "on_update": "linhx_core.co_module.xoa_cache_cau_hinh",
    },
}
