app_name = "linhx_goi_ops"
app_title = "LINHX Goi Ops"
app_publisher = "LINHX"
app_description = "Gói phiếu Agy nội bộ cho LINHX ENGINE"
app_email = "dev@linhx.vn"
app_license = "mit"

override_whitelisted_methods = {
    "linhx_core.ops.api_tho.keo": "linhx_goi_ops.ops.api_tho.keo",
    "linhx_core.ops.api_tho.nop": "linhx_goi_ops.ops.api_tho.nop",
    "linhx_core.ops.api_ban_phieu.phieu_cho": "linhx_goi_ops.ops.api_ban_phieu.phieu_cho",
    "linhx_core.ops.api_ban_phieu.duyet": "linhx_goi_ops.ops.api_ban_phieu.duyet",
    "linhx_core.ops.api_ban_phieu.tra_lai": "linhx_goi_ops.ops.api_ban_phieu.tra_lai",
}
