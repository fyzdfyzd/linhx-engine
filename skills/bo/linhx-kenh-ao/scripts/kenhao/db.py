"""CSDL SQLite của một kênh người ảo. Mọi thay đổi đi qua CLI để cổng chặn và nhật ký luôn chạy."""
import json
import os
import sqlite3
from datetime import datetime

SCHEMA = """
CREATE TABLE IF NOT EXISTS nguon (
  id INTEGER PRIMARY KEY, loai TEXT, tieu_de TEXT, url TEXT UNIQUE, tom_tat TEXT,
  tru_cot TEXT, diem REAL DEFAULT 0, da_dung INTEGER DEFAULT 0, nhap_luc TEXT);
CREATE TABLE IF NOT EXISTS khe (
  id INTEGER PRIMARY KEY, ngay TEXT, gio TEXT, nen_tang TEXT, uu_tien TEXT,
  tru_cot TEXT, dinh_dang TEXT, bai_id INTEGER, UNIQUE(ngay, gio, nen_tang));
CREATE TABLE IF NOT EXISTS bai (
  id INTEGER PRIMARY KEY, khe_id INTEGER, nen_tang TEXT, tru_cot TEXT, dinh_dang TEXT,
  hook TEXT, noi_dung TEXT, media TEXT, nguon_id INTEGER, trang_thai TEXT DEFAULT 'nhap',
  diem_critic REAL, ghi_chu_critic TEXT, thi_nghiem_id INTEGER, nhanh TEXT,
  luat_viet_pb INTEGER, hen_luc TEXT, dang_luc TEXT, ma_ngoai TEXT, tao_luc TEXT,
  muc_dich TEXT, cho_ai TEXT, tieu_hoa_ids TEXT, persona TEXT, cam_xuc TEXT, phan_ung TEXT);
CREATE TABLE IF NOT EXISTS duyet (
  id INTEGER PRIMARY KEY, bai_id INTEGER, quyet_dinh TEXT, gop_y TEXT,
  ban_cu TEXT, ban_moi TEXT, da_hoc INTEGER DEFAULT 0, luc TEXT);
CREATE TABLE IF NOT EXISTS fan (
  id INTEGER PRIMARY KEY, nen_tang TEXT, ma_ngoai TEXT, ten TEXT, diem REAL DEFAULT 0,
  bac TEXT DEFAULT 'nguoi_la', lan_dau TEXT, lan_cuoi TEXT, khong_nhan INTEGER DEFAULT 0,
  ghi_chu TEXT, UNIQUE(nen_tang, ma_ngoai));
CREATE TABLE IF NOT EXISTS tin (
  id INTEGER PRIMARY KEY, nen_tang TEXT, loai TEXT, ma_ngoai TEXT UNIQUE, bai_id INTEGER,
  fan_id INTEGER, noi_dung TEXT, luc TEXT, hang TEXT, nhan TEXT, ly_do TEXT,
  trang_thai TEXT DEFAULT 'moi', tra_loi TEXT, duyet_boi TEXT, tra_luc TEXT);
CREATE TABLE IF NOT EXISTS su_kien_fan (
  id INTEGER PRIMARY KEY, fan_id INTEGER, loai TEXT, diem REAL, luc TEXT, tham_chieu TEXT);
CREATE TABLE IF NOT EXISTS so_lieu (
  id INTEGER PRIMARY KEY, bai_id INTEGER, luc TEXT, view INTEGER, reach INTEGER,
  like_ INTEGER, comment INTEGER, share INTEGER, save INTEGER);
CREATE TABLE IF NOT EXISTS hanh_dong (
  id INTEGER PRIMARY KEY, ngay TEXT, loai TEXT, tham_chieu TEXT, luc TEXT);
CREATE TABLE IF NOT EXISTS luat_viet (
  id INTEGER PRIMARY KEY, phien_ban INTEGER, luat TEXT, tu_duyet INTEGER, con_hieu_luc INTEGER DEFAULT 1, luc TEXT);
CREATE TABLE IF NOT EXISTS thi_nghiem (
  id INTEGER PRIMARY KEY, ten TEXT, gia_thuyet TEXT, bien TEXT, nhanh_a TEXT, nhanh_b TEXT,
  chi_so TEXT DEFAULT 'ty_le_tuong_tac', can_n INTEGER, trang_thai TEXT DEFAULT 'dang_chay',
  ket_qua TEXT, mo_luc TEXT, dong_luc TEXT);
CREATE TABLE IF NOT EXISTS brand_lead (
  id INTEGER PRIMARY KEY, fan_id INTEGER, tin_id INTEGER, ten TEXT,
  giai_doan TEXT DEFAULT 'hoi', ghi_chu TEXT, luc TEXT);
CREATE TABLE IF NOT EXISTS vong (
  id INTEGER PRIMARY KEY, nen_tang TEXT, ma_ngoai TEXT, ten TEXT, nhom TEXT, ly_do TEXT,
  la_minh INTEGER DEFAULT 0, la_nha INTEGER DEFAULT 0, bac_thang INTEGER DEFAULT 0, diem_tin REAL DEFAULT 0,
  so_bai_da_doc INTEGER DEFAULT 0, cham_khong_dap INTEGER DEFAULT 0, them_luc TEXT,
  UNIQUE(nen_tang, ma_ngoai));
CREATE TABLE IF NOT EXISTS luot_doc (
  id INTEGER PRIMARY KEY, vong_id INTEGER, nen_tang TEXT, url TEXT UNIQUE, tac_gia TEXT,
  noi_dung TEXT, chu_de TEXT, tuong_tac INTEGER, dang_luc TEXT, doc_luc TEXT);
CREATE TABLE IF NOT EXISTS tieu_hoa (
  id INTEGER PRIMARY KEY, luot_doc_ids TEXT, loai TEXT, ghi_chu TEXT, luc TEXT);
CREATE TABLE IF NOT EXISTS hanh_dong_ra (
  id INTEGER PRIMARY KEY, vong_id INTEGER, luot_doc_id INTEGER, loai TEXT, muc_dich TEXT,
  vi_sao TEXT, noi_dung TEXT, chi_tiet TEXT, trang_thai TEXT, ly_do_chan TEXT,
  tao_luc TEXT, lam_luc TEXT);
CREATE TABLE IF NOT EXISTS su_kien_vong (
  id INTEGER PRIMARY KEY, vong_id INTEGER, loai TEXT, diem REAL, luc TEXT, ghi_chu TEXT);
CREATE TABLE IF NOT EXISTS quan_sat_persona (
  id INTEGER PRIMARY KEY, luot_doc_id INTEGER UNIQUE, kieu TEXT, cam_xuc TEXT, phan_ung TEXT,
  flaw TEXT, giong TEXT, ghi_chu TEXT, luc TEXT);
CREATE TABLE IF NOT EXISTS phan_hoi (
  id INTEGER PRIMARY KEY, loai_muc TEXT, muc_id INTEGER, hanh_dong TEXT, ly_do TEXT,
  khoang_sua REAL, cho_giay INTEGER, luc TEXT);
CREATE TABLE IF NOT EXISTS tham_so (
  khoa TEXT PRIMARY KEY, gia_tri REAL, alpha REAL, beta REAL, n REAL, cap_nhat TEXT);
CREATE TABLE IF NOT EXISTS thay_doi (
  id INTEGER PRIMARY KEY, khoa TEXT, cu REAL, moi REAL, ly_do TEXT, bang_chung TEXT,
  luc TEXT, xet_lai_ngay TEXT, ket_qua TEXT);
CREATE TABLE IF NOT EXISTS bai_hoc (
  id INTEGER PRIMARY KEY, nguon TEXT, khoa TEXT UNIQUE, noi_dung TEXT, bang_chung TEXT,
  tang INTEGER, trang_thai TEXT DEFAULT 'de_xuat', luc TEXT, quyet_luc TEXT);
CREATE TABLE IF NOT EXISTS nhat_ky (
  id INTEGER PRIMARY KEY, luc TEXT, viec TEXT, chi_tiet TEXT);
"""


def bay_gio():
    gia_lap = os.environ.get("KENHAO_GIO")  # dùng khi chạy thử để giả lập ngày giờ
    if gia_lap:
        return datetime.fromisoformat(gia_lap)
    return datetime.now()


def mo(home):
    con = sqlite3.connect(os.path.join(home, "kenh.db"))
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    for bang, cot in (("bai", "du_doan REAL"), ("bai", "hien_luc TEXT"), ("hanh_dong_ra", "hien_luc TEXT")):
        try:
            con.execute(f"ALTER TABLE {bang} ADD COLUMN {cot}")
        except sqlite3.OperationalError:
            pass  # cột đã có
    return con


def ghi_nhat_ky(con, viec, chi_tiet):
    con.execute("INSERT INTO nhat_ky(luc, viec, chi_tiet) VALUES (?,?,?)",
                (bay_gio().isoformat(timespec="seconds"), viec,
                 json.dumps(chi_tiet, ensure_ascii=False)))


def dem_hanh_dong(con, loai, ngay):
    return con.execute("SELECT COUNT(*) FROM hanh_dong WHERE loai=? AND ngay=?",
                       (loai, ngay)).fetchone()[0]


def ghi_hanh_dong(con, loai, tham_chieu):
    t = bay_gio()
    con.execute("INSERT INTO hanh_dong(ngay, loai, tham_chieu, luc) VALUES (?,?,?,?)",
                (t.date().isoformat(), loai, str(tham_chieu), t.isoformat(timespec="seconds")))
