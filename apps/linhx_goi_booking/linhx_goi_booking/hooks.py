app_name = "linhx_goi_booking"
app_title = "LINHX Goi Booking"
app_publisher = "LINHX"
app_description = "Gói đặt lịch gọi tư vấn cho LINHX ENGINE"
app_email = "dev@linhx.vn"
app_license = "mit"

override_whitelisted_methods = {
    "linhx_core.booking.api_booking.dat_lich_goi": "linhx_goi_booking.api_booking.dat_lich_goi",
    "linhx_core.booking.api_booking.viec_cho_lich_goi": "linhx_goi_booking.api_booking.viec_cho_lich_goi",
}
