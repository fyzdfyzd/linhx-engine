"""Nén thư mục nhiệm vụ thành <MA>-<nhan>.zip đặt cạnh thư mục. Dùng: python3 dong_goi.py <thu-muc> <nhan>"""
import sys
import zipfile
from pathlib import Path

goc, nhan = Path(sys.argv[1]).resolve(), sys.argv[2]
z = goc.parent / f"{goc.name}-{nhan}.zip"
files = [p for p in goc.rglob("*") if p.is_file() and p.suffix != ".zip"]
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
    for p in files:
        zf.write(p, f"{goc.name}/{p.relative_to(goc).as_posix()}")
print(f"{z}: {len(files)} file, {z.stat().st_size / 1024:.0f} KB")
