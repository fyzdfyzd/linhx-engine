app_name = "linhx_worker"
app_title = "LINHX Worker"
app_publisher = "LINHX"
app_description = "Hang viec agy cho LINHX ENGINE"
app_email = "dev@linhx.vn"
app_license = "mit"

after_install = "linhx_worker.setup.after_install"
after_migrate = "linhx_worker.setup.after_install"

scheduler_events = {
    "cron": {"* * * * *": ["linhx_worker.api.don_dep"]},
}
