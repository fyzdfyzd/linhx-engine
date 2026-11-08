"""Event Bus cắm rút chuẩn cho OPC OS (`03_OPC_OS.md`).

Nguyên tắc:
- Các module nói chuyện với nhau qua sự kiện (`don.tao_moi`, `don.da_tra`, `don.loi_thanh_toan`,
  `don.het_han`, `report.xong`, `report.cho_duyet_tay`, `khach.hoi`, `so_cai.da_ghi`,
  `canh_bao.doanh_thu_400tr`, `kpi.cap_nhat`).
- Không module nào gọi thẳng code của module khác.
- Mọi sự kiện đều được ghi vết thời gian thực (append-only JSONL) để đối soát và kiểm toán.
"""
from __future__ import annotations

import json
import time
import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable


@dataclass
class Event:
    event_id: str
    topic: str
    opc_id: str
    source_module: str
    payload: dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="milliseconds"))
    epoch_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def to_dict(self) -> dict:
        return asdict(self)


class EventBus:
    def __init__(self, log_file: Path | None = None):
        self._subscribers: dict[str, list[tuple[str, Callable[[Event], dict | None]]]] = defaultdict(list)
        self._history: list[Event] = []
        self.log_file = log_file
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def subscribe(self, topic: str, subscriber_module: str, handler: Callable[[Event], dict | None]) -> None:
        self._subscribers[topic].append((subscriber_module, handler))

    def publish(self, topic: str, opc_id: str, source_module: str, payload: dict) -> list[dict]:
        ev = Event(
            event_id=f"ev-{uuid.uuid4().hex[:10]}",
            topic=topic,
            opc_id=opc_id,
            source_module=source_module,
            payload=payload,
        )
        self._history.append(ev)
        if self.log_file:
            with self.log_file.open("a", encoding="utf-8") as fp:
                fp.write(json.dumps(ev.to_dict(), ensure_ascii=False) + "\n")

        results = []
        for sub_mod, handler in self._subscribers.get(topic, []):
            res = handler(ev)
            results.append({"subscriber": sub_mod, "result": res})
        return results

    @property
    def history(self) -> list[Event]:
        return list(self._history)
