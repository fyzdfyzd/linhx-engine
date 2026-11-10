app_name = "linhx_goi_agentforce"
app_title = "LINHX Goi AgentForce"
app_publisher = "LINHX"
app_description = "Gói Agent Force (pilot và kho case có số) cho LINHX ENGINE"
app_email = "dev@linhx.vn"
app_license = "mit"

override_whitelisted_methods = {
    "linhx_core.cred.api_cred.danh_sach_case": "linhx_goi_agentforce.cred.api_cred.danh_sach_case",
    "linhx_core.cred.api_cred.noi_dung_ifagent": "linhx_goi_agentforce.cred.api_cred.noi_dung_ifagent",
}
