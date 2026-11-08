#!/usr/bin/env python3
"""Rào cứng của người canh LINHX ENGINE (chạy NGOÀI tay thợ, bản ở nhánh tích hợp).

  py -3.12 canh/rao.py <worktree> <goc_sha> <features.json tương đối> <ID> [--log <phieu>.jsonl]

K1 cổng vùng: mọi file đổi trong goc..HEAD phải khớp "vung" của feature (glob, ** = nhiều cấp),
   cộng phần luôn được: bang-chung/<ID>/** và file features của chính nó (chỉ passes/bang_chung của <ID>).
   Luôn cấm: tests/nghiem-thu/**, *.khoa, pytest.ini, canh/**, .canh/**, file bí mật.
K3 nhật ký agy: đọc stdout stream-json của agy, gom file agy đã ghi (kể cả file ghi rồi xoá trước commit),
   so với vùng. Ghi trong repo ngoài vùng là lỗi; ghi vào nhánh tích hợp / thư mục canh là lỗi;
   ghi ra ngoài repo chỉ là lưu ý.
In ra JSON {"loi": [...], "luu_y": [...], "file_doi": [...], "file_ghi": [...], "token_vao", "token_ra"}.
Mã thoát 0 (kể cả có lỗi: người gọi đọc "loi"); 2 khi gọi sai.
"""
import json
import os
import pathlib
import re
import subprocess
import sys

LUON_CAM = ["tests/nghiem-thu/**", "**/*.khoa", "*.khoa", "pytest.ini", "canh/**", ".canh/**"]
TU_GHI = {"write", "edit", "multiedit", "multi_edit", "create", "replace", "str_replace", "notebookedit",
          "write_file", "edit_file", "create_file", "replace_file_content", "write_to_file",
          "multi_replace_file_content", "apply_patch", "patch", "sed_file", "notebook_edit"}
KHOA_DUONG = ("file_path", "path", "filePath", "TargetFile", "target_file", "absolute_path",
              "notebook_path", "AbsolutePath", "Path", "File", "FilePath", "TargetPath", "file")
BI_MAT = re.compile(r"(^|/)(\.env|tho\.env)$|(^|/)\.env\.(?!example$|mau$|sample$)|\.(pem|key|p12|pfx)$")


def glob_re(g):
    """glob kiểu git: ** khớp nhiều cấp, * khớp trong một cấp."""
    g = g.strip().replace("\\", "/")
    if g.endswith("/"):
        g += "**"
    out, i = "", 0
    while i < len(g):
        if g.startswith("**/", i):
            out += r"(?:.*/)?"
            i += 3
        elif g.startswith("**", i):
            out += r".*"
            i += 2
        elif g[i] == "*":
            out += r"[^/]*"
            i += 1
        elif g[i] == "?":
            out += r"[^/]"
            i += 1
        else:
            out += re.escape(g[i])
            i += 1
    return re.compile("^" + out + "$")


def khop(duong, cac_glob):
    duong = duong.replace("\\", "/")
    return any(glob_re(g).match(duong) for g in cac_glob)


def git(wt, *a):
    r = subprocess.run(["git", "-C", str(wt), *a], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout


def doc_json_git(wt, rev, duong):
    chu = git(wt, "show", f"{rev}:{duong}")
    try:
        return json.loads(chu)
    except Exception:
        return None


def kiem_file_features(wt, goc, ff, fid):
    """Trong file features chỉ được đổi passes/bang_chung của chính fid."""
    loi = []
    cu, moi = doc_json_git(wt, goc, ff), doc_json_git(wt, "HEAD", ff)
    if cu is None or moi is None:
        return [f"không đọc được {ff} ở mốc hoặc HEAD"]
    if {k: v for k, v in cu.items() if k != "features"} != {k: v for k, v in moi.items() if k != "features"}:
        loi.append(f"{ff}: sửa phần đầu file")
    a = {f["id"]: f for f in cu.get("features", [])}
    b = {f["id"]: f for f in moi.get("features", [])}
    if set(a) != set(b):
        loi.append(f"{ff}: thêm/xoá feature")
    for k in set(a) & set(b):
        if a[k] == b[k]:
            continue
        if k != fid:
            loi.append(f"{ff}: sửa feature {k} (phiếu chỉ được đổi {fid})")
            continue
        khac = {x for x in set(a[k]) | set(b[k]) if a[k].get(x) != b[k].get(x)}
        if khac - {"passes", "bang_chung"}:
            loi.append(f"{ff}: sửa {', '.join(sorted(khac - {'passes', 'bang_chung'}))} của {fid}")
    return loi


def duyet(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from duyet(v)
    elif isinstance(o, list):
        for v in o:
            yield from duyet(v)


def doc_log(p):
    """Trả (file_ghi, token_vao, token_ra, so_dong_json)."""
    ghi, tv, tr, n = [], None, None, 0
    try:
        dong = pathlib.Path(p).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ghi, tv, tr, 0
    cac = []
    for d in dong:
        d = d.strip()
        if not d:
            continue
        try:
            cac.append(json.loads(d))
            n += 1
        except Exception:
            continue
    if not cac:  # --output-format json: cả file là một JSON
        try:
            cac = [json.loads("\n".join(dong))]
            n = 1
        except Exception:
            pass
    for o in cac:
        for x in duyet(o):
            ten = x.get("name") or x.get("tool") or x.get("tool_name") or x.get("toolName")
            if isinstance(ten, str):
                vao = x.get("input", x.get("arguments", x.get("parameters", x.get("args"))))
                if isinstance(vao, str):
                    try:
                        vao = json.loads(vao)
                    except Exception:
                        vao = None
                if re.sub(r"[^a-z_]", "", ten.lower().split("__")[-1]) in TU_GHI and isinstance(vao, dict):
                    for k in KHOA_DUONG:
                        if isinstance(vao.get(k), str) and vao[k].strip():
                            ghi.append(vao[k].strip())
                            break
            u = x.get("usage")
            if isinstance(u, dict) and ("input_tokens" in u or "output_tokens" in u):
                tv = int(u.get("input_tokens") or 0) + int(u.get("cache_read_input_tokens") or 0)
                tr = int(u.get("output_tokens") or 0)
    return list(dict.fromkeys(ghi)), tv, tr, n


def main(argv):
    if len(argv) < 4:
        sys.exit(__doc__)
    wt, goc, ff, fid = pathlib.Path(argv[0]).resolve(), argv[1], argv[2].replace("\\", "/"), argv[3]
    log = argv[argv.index("--log") + 1] if "--log" in argv else None
    cam_them = argv[argv.index("--cam") + 1].split(";") if "--cam" in argv else []
    data = json.loads((wt / ff).read_text(encoding="utf-8"))
    f = next((x for x in data["features"] if x["id"] == fid), None)
    kq = {"loi": [], "luu_y": [], "file_doi": [], "file_ghi": [], "token_vao": None, "token_ra": None}
    if f is None:
        kq["loi"].append(f"không thấy {fid} trong {ff}")
        print(json.dumps(kq, ensure_ascii=False))
        return 0
    vung = list(f.get("vung") or [])
    if not vung:
        kq["loi"].append(f"{fid} chưa có vung trong {ff}: không chấm được cổng vùng")
    duoc = vung + [f"bang-chung/{fid}/**", ".canh-tho/**"]
    # So với chỗ rẽ khỏi main, không chỉ mốc phiếu: phần dở các phiếu trước (vd đổi passes feature khác) cũng sẽ vào main khi gộp (lỗi 8/11 A2 hạ C1)
    mb = git(wt, "merge-base", "HEAD", "main").strip()
    if mb:
        goc = mb
    doi = [x for x in git(wt, "diff", "--name-only", f"{goc}..HEAD").splitlines() if x.strip()]
    kq["file_doi"] = doi
    for x in doi:
        if khop(x, LUON_CAM):
            kq["loi"].append(f"Sửa file cấm: {x}")
        elif x == ff:
            kq["loi"] += kiem_file_features(wt, goc, ff, fid)
        elif not khop(x, duoc):
            kq["loi"].append(f"Sửa ngoài vùng {fid} ({', '.join(vung)}): {x}")
        if BI_MAT.search(x):
            kq["loi"].append(f"Commit file bí mật: {x}")
    if log:
        ghi, tv, tr, n = doc_log(log)
        kq["token_vao"], kq["token_ra"] = tv, tr
        if n == 0:
            kq["luu_y"].append(f"K3: không đọc được nhật ký agy {log}")
        elif not ghi:
            kq["luu_y"].append("K3: nhật ký agy không có lệnh ghi file nào nhận ra được")
        cam_ngoai = [pathlib.Path(c).resolve() for c in cam_them if c.strip()]
        for g in ghi:
            p = pathlib.Path(g)
            p = (wt / p) if not p.is_absolute() else p
            try:
                p = p.resolve()
            except OSError:
                pass
            try:
                rel = p.relative_to(wt).as_posix()
            except ValueError:
                rel = None
            if rel is None:
                if any(p == c or c in p.parents for c in cam_ngoai):
                    kq["loi"].append(f"K3: agy ghi vào chỗ của người canh: {p}")
                else:
                    kq["luu_y"].append(f"K3: agy ghi ngoài repo: {p}")
                continue
            kq["file_ghi"].append(rel)
            if khop(rel, LUON_CAM):
                kq["loi"].append(f"K3: agy đã ghi file cấm (kể cả nếu trả lại trước commit): {rel}")
            elif rel != ff and not khop(rel, duoc):
                kq["loi"].append(f"K3: agy đã ghi ngoài vùng {fid}: {rel}")
    kq["loi"] = list(dict.fromkeys(kq["loi"]))
    print(json.dumps(kq, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
