"""Adapter `postiz`: đăng qua Public API của Postiz tự host (gitroomhq/postiz-app, AGPL; gọi qua API
nên không phải mở mã). Đường dẫn và schema đọc từ code Postiz ngày 16/10/2026:
  apps/backend/src/public-api/routes/v1/public.integrations.controller.ts  (POST /public/v1/posts)
  libraries/nestjs-libraries/src/dtos/posts/create.post.dto.ts               (CreatePostDto)
  apps/sdk/src/index.ts                                                      (header Authorization: <api key>)
Chưa chạy với Postiz thật. Postiz không đọc bình luận/DM: phần đó dùng adapter `meta`."""
import json
import os
import urllib.request

from ..db import bay_gio


def dang(home, bai, cfg):
    base = cfg["postiz_url"].rstrip("/")
    khoa = os.environ[cfg.get("postiz_api_key_env", "POSTIZ_API_KEY")]
    than = {
        "type": cfg.get("postiz_type", "schedule"),  # "draft" nếu muốn duyệt thêm lần nữa trong Postiz
        "shortLink": False,
        "date": bai["hen_luc"] or bay_gio().isoformat(timespec="seconds"),
        "tags": [],
        "posts": [{
            "integration": {"id": cfg["postiz_integration_id"]},
            "value": [{"content": bai["noi_dung"], "image": json.loads(bai["media"] or "[]")}],
            "settings": {"__type": cfg["postiz_provider"]},
        }],
    }
    req = urllib.request.Request(f"{base}/public/v1/posts", data=json.dumps(than).encode(),
                                 headers={"Authorization": khoa, "Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        kq = json.loads(r.read() or b"{}")
    if isinstance(kq, list) and kq:
        kq = kq[0]
    return str(kq.get("postId") or kq.get("id") or kq.get("group") or "postiz-?")


def keo_binh_luan(home, bai, cfg):
    return []


def gui_tra_loi(home, tin, noi_dung, cfg):
    raise NotImplementedError("Postiz không trả lời bình luận; khai `hop_thu_adapter: meta` cho nền tảng này")


def keo_so_lieu(home, bai, cfg):
    return None
