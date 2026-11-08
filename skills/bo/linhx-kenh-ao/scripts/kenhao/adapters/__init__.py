"""Giao diện tay chân chung: dang, keo_binh_luan, gui_tra_loi, keo_so_lieu."""
import importlib


def lay(ten):
    return importlib.import_module(f"{__name__}.{ten}")
