app_name = "linhx_vn"
app_title = "LINHX VN"
app_publisher = "LINHX"
app_description = "Adapter Việt Nam (SePay, VietQR, sổ S1a) cho LINHX ENGINE"
app_email = "dev@linhx.vn"
app_license = "mit"

auth_hooks = [
    "linhx_vn.pay.api_sepay.xac_thuc_sepay_hook",
]

override_whitelisted_methods = {
    "linhx_core.pay.api_sepay.webhook": "linhx_vn.pay.api_sepay.webhook",
    "linhx_core.pay.api_thue.canh_bao_thue": "linhx_vn.pay.api_thue.canh_bao_thue",
}

doc_events = {
    "LX Don": {
        "on_update": "linhx_vn.pay.so_s1a.ghi_so_s1a_tu_don",
    },
}
