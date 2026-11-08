"""Module 04: Quản lý User, Đồng ý dữ liệu NĐ 13/2023, Hồ sơ Phụ huynh-Con & Quyền xoá dữ liệu."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.event_bus import Event, EventBus  # noqa: E402


class UserManagementModule:
    module_id = "04_quan_ly_user"

    def __init__(self, bus: EventBus, data_dir: Path):
        self.bus = bus
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.users_file = self.data_dir / "users.json"
        self.bus.subscribe("don.tao_moi", self.module_id, self.on_order_created)
        self.bus.subscribe("user.yeu_cau_xoa", self.module_id, self.on_erase_requested)

    def _load(self) -> dict[str, dict]:
        return json.loads(self.users_file.read_text(encoding="utf-8")) if self.users_file.exists() else {}

    def _save(self, users: dict[str, dict]) -> None:
        self.users_file.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")

    def upsert_from_order(self, opc_id: str, order_code: str, customer_input: dict) -> dict:
        contact = str(
            customer_input.get("contact")
            or customer_input.get("sdt_phu_huynh")
            or customer_input.get("ten")
            or order_code
        ).strip()
        uid = "usr_" + hashlib.sha256(f"{opc_id}:{contact}".encode("utf-8")).hexdigest()[:10]
        users = self._load()
        existing = users.get(uid, {
            "user_id": uid,
            "opc_id": opc_id,
            "orders": [],
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        })

        is_minor_career = bool(customer_input.get("ten_phu_huynh") or customer_input.get("ten_hoc_sinh"))
        if is_minor_career:
            profile_mode = "two_profiles_parent_and_student"
            retention_policy = "auto_delete_raw_quiz_after_30_days"
        else:
            profile_mode = "single_adult_buyer"
            retention_policy = "erase_on_request"

        orders_list = list(existing.get("orders", []))
        if order_code not in orders_list:
            orders_list.append(order_code)

        segment = "khach_mua_lai" if len(orders_list) >= 2 else (
            "phu_huynh_chon_nganh" if is_minor_career else "khach_moi"
        )

        record = {
            **existing,
            "profile_mode": profile_mode,
            "consent_nd13_verified": bool(customer_input.get("consent") or customer_input.get("dong_y_phu_huynh")),
            "consent_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "retention_policy": retention_policy,
            "pii_data": {
                "ten": customer_input.get("ten") or customer_input.get("ten_phu_huynh"),
                "ten_hoc_sinh": customer_input.get("ten_hoc_sinh"),
                "ngay_sinh": customer_input.get("ngay_sinh"),
                "gio_sinh": customer_input.get("gio_sinh"),
                "noi_sinh": customer_input.get("noi_sinh"),
                "contact": contact,
            },
            "orders": orders_list,
            "segment": segment,
            "erased": False,
        }
        users[uid] = record
        self._save(users)
        self.bus.publish("user.da_luu_ho_so", opc_id=opc_id, source_module=self.module_id, payload=record)
        return record

    def erase_user(self, user_id: str, reason: str = "Khách yêu cầu xoá dữ liệu theo NĐ 13/2023") -> dict:
        users = self._load()
        if user_id not in users:
            raise KeyError(f"Không tìm thấy user_id={user_id}")
        rec = users[user_id]
        rec["pii_data"] = {
            "ten": "[ĐÃ XOÁ THEO YÊU CẦU]",
            "ten_hoc_sinh": None,
            "ngay_sinh": None,
            "gio_sinh": None,
            "noi_sinh": None,
            "contact": "[ĐÃ XOÁ]",
        }
        rec["erased"] = True
        rec["erased_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        rec["erase_reason"] = reason
        self._save(users)
        self.bus.publish("user.da_xoa_du_lieu", opc_id=rec["opc_id"], source_module=self.module_id, payload=rec)
        return rec

    def on_order_created(self, event: Event) -> dict:
        p = event.payload
        return self.upsert_from_order(p["opc_id"], p["code"], p["customer_input"])

    def on_erase_requested(self, event: Event) -> dict:
        return self.erase_user(event.payload["user_id"], event.payload.get("reason", ""))


def main() -> int:
    ap = argparse.ArgumentParser(description="Module 04: Quản lý User")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    in_path = HERE / "demo" / "input" / "demo_in.json"
    out_path = HERE / "demo" / "output" / "demo_out.json"
    data = json.loads(in_path.read_text(encoding="utf-8"))

    bus = EventBus()
    mod = UserManagementModule(bus, HERE / "demo" / "output" / "data")
    created = mod.upsert_from_order(data["opc_id"], data["order_code"], data["customer_input"])
    erased = mod.erase_user(created["user_id"]) if data.get("test_erase_after_upsert") else None

    out = {"upserted_profile": created, "erased_profile_proof": erased}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Module 04] Xong user_id={created['user_id']} | Consent={created['consent_nd13_verified']} | Erased={bool(erased)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
