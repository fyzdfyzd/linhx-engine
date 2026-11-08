"""Adapter `meta`: hộp thư và số liệu cho Facebook Page qua Graph API chính thức.
CHƯA KIỂM với tài khoản thật và chưa đối chiếu tài liệu Meta bản mới nhất; các endpoint dưới đây
là dạng phổ biến của Graph API (comments, replies, insights). Instagram dùng /replies thay /comments.
Quyền cần xin: pages_read_engagement, pages_manage_engagement, read_insights (và instagram_manage_comments)."""
import json
import os
import urllib.parse
import urllib.request

API = "https://graph.facebook.com/v21.0"


def _get(path, token, **q):
    q["access_token"] = token
    with urllib.request.urlopen(f"{API}/{path}?{urllib.parse.urlencode(q)}", timeout=30) as r:
        return json.loads(r.read())


def _post(path, token, **data):
    data["access_token"] = token
    req = urllib.request.Request(f"{API}/{path}", data=urllib.parse.urlencode(data).encode(), method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _token(cfg):
    return os.environ[cfg.get("meta_token_env", "META_PAGE_TOKEN")]


def dang(home, bai, cfg):
    raise NotImplementedError("đăng qua Postiz; adapter meta chỉ lo hộp thư và số liệu")


def keo_binh_luan(home, bai, cfg):
    kq = _get(f"{bai['ma_ngoai']}/comments", _token(cfg), fields="id,from,message,created_time", limit=100)
    return [{"ma_ngoai": c["id"], "loai": "binh_luan", "fan_ma": c.get("from", {}).get("id", "?"),
             "fan_ten": c.get("from", {}).get("name", "?"), "noi_dung": c.get("message", ""),
             "luc": c["created_time"][:19]} for c in kq.get("data", [])]


def gui_tra_loi(home, tin, noi_dung, cfg):
    canh = "replies" if cfg.get("la_instagram") else "comments"
    _post(f"{tin['ma_ngoai']}/{canh}", _token(cfg), message=noi_dung)
    return True


def keo_so_lieu(home, bai, cfg):
    kq = _get(f"{bai['ma_ngoai']}/insights", _token(cfg),
              metric="post_impressions,post_impressions_unique,post_engaged_users")
    v = {m["name"]: m["values"][0]["value"] for m in kq.get("data", [])}
    return {"view": v.get("post_impressions", 0), "reach": v.get("post_impressions_unique", 0),
            "like_": v.get("post_engaged_users", 0), "comment": 0, "share": 0, "save": 0}
