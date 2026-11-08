from linhx_core.co_module import DOCTYPE_MODULE

app_name = "linhx_core"
app_title = "LINHX Core"
app_publisher = "LINHX"
app_description = "Khung app Frappe linhx_core cho LINHX ENGINE"
app_email = "dev@linhx.vn"
app_license = "mit"

before_request = ["linhx_core.co_module.frappe_before_request"]

has_permission = {
    dt: "linhx_core.co_module.frappe_has_permission"
    for dt in DOCTYPE_MODULE
}

permission_query_conditions = {
    dt: "linhx_core.co_module.frappe_permission_query_conditions"
    for dt in DOCTYPE_MODULE
}

doc_events = {
    dt: {
        "before_insert": "linhx_core.co_module.frappe_kiem_tra_doc_event",
        "validate": "linhx_core.co_module.frappe_kiem_tra_doc_event",
        "on_trash": "linhx_core.co_module.frappe_kiem_tra_doc_event",
    }
    for dt in DOCTYPE_MODULE
}
