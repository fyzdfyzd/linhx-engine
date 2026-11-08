from linhx_core.co_module import DOCTYPE_MODULE

app_name = "linhx_core"
app_title = "LINHX Core"
app_publisher = "LINHX"
app_description = "Khung app Frappe linhx_core cho LINHX ENGINE"
app_email = "dev@linhx.vn"
app_license = "mit"

fixtures = [
    {
        "dt": "Role",
        "filters": [["name", "in", ["LX Nhan Vien"]]],
    }
]

before_install = "linhx_core.crm.quyen_don_vi.dam_bao_vai_tro"
after_install = "linhx_core.crm.quyen_don_vi.dam_bao_vai_tro"
before_migrate = ["linhx_core.crm.quyen_don_vi.dam_bao_vai_tro"]
after_migrate = ["linhx_core.crm.quyen_don_vi.dam_bao_vai_tro"]

NHAT_KY_HOOK = "linhx_core.linhx_core.doctype.lx_nhat_ky_truy_cap.lx_nhat_ky_truy_cap.ghi_nhat_ky_truy_cap"
QUYEN_DON_VI_DOC_HOOK = "linhx_core.crm.quyen_don_vi.kiem_tra_quyen_doc"
DOCTYPE_KHACH = ("LX Nguoi", "LX To Chuc", "LX Don Vi")
DOCTYPE_QUYEN_DON_VI = ("LX Nguoi", "LX Co Hoi")

before_request = ["linhx_core.co_module.frappe_before_request"]
after_request = ["linhx_core.linhx_core.doctype.lx_nhat_ky_truy_cap.lx_nhat_ky_truy_cap.ghi_nhat_ky_tu_request"]

has_permission = {
    **{
        dt: "linhx_core.co_module.frappe_has_permission"
        for dt in DOCTYPE_MODULE
    },
    "LX Nguoi": "linhx_core.crm.quyen_don_vi.frappe_has_permission",
    "LX Co Hoi": "linhx_core.crm.quyen_don_vi.frappe_has_permission",
}

permission_query_conditions = {
    **{
        dt: "linhx_core.co_module.frappe_permission_query_conditions"
        for dt in DOCTYPE_MODULE
    },
    "LX Nguoi": "linhx_core.crm.quyen_don_vi.frappe_permission_query_conditions",
    "LX Co Hoi": "linhx_core.crm.quyen_don_vi.frappe_permission_query_conditions",
}

doc_events = {
    **{
        dt: {
            "before_insert": (
                ["linhx_core.co_module.frappe_kiem_tra_doc_event", QUYEN_DON_VI_DOC_HOOK]
                if dt in DOCTYPE_QUYEN_DON_VI
                else "linhx_core.co_module.frappe_kiem_tra_doc_event"
            ),
            "validate": (
                ["linhx_core.co_module.frappe_kiem_tra_doc_event", QUYEN_DON_VI_DOC_HOOK]
                if dt in DOCTYPE_QUYEN_DON_VI
                else "linhx_core.co_module.frappe_kiem_tra_doc_event"
            ),
            **(
                {"before_save": QUYEN_DON_VI_DOC_HOOK}
                if dt in DOCTYPE_QUYEN_DON_VI
                else {}
            ),
            "on_trash": [
                "linhx_core.co_module.frappe_kiem_tra_doc_event",
                *([QUYEN_DON_VI_DOC_HOOK] if dt in DOCTYPE_QUYEN_DON_VI else []),
                *([NHAT_KY_HOOK] if dt in DOCTYPE_KHACH else []),
            ],
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
