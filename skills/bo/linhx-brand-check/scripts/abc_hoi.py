"""Hỏi AI như khách thật và lưu câu trả lời thành file (định dạng của ai-visibility-skill).

Mỗi câu trả lời: <lan>/tra-loi/<mo_hinh>/<id>__l<luot>.md. Header ID/PROMPT/MODEL/DATE, dòng ====, rồi câu trả lời;
nguồn AI dẫn được ghi cuối file dạng "[nguon] <tên miền> | <url>".

Mô hình (tên dùng trong --mo-hinh):
  dan-tay:<ten>     tạo file trống để người dán câu trả lời thật từ ứng dụng chat (đáng tin nhất)
  claude-tim        claude -p, cho phép WebSearch/WebFetch
  claude-nho        claude -p, cấm công cụ web
  agy               agy -p (Antigravity, Gemini)
  codex             codex exec
  gemini-tim / gemini-nho     Gemini API (GEMINI_API_KEY), tim = có Google Search
  openrouter:<model>[:online] OpenRouter (OPENROUTER_API_KEY), :online = có tra web
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nen.aeolib import parse_response_file, write_response_stub  # noqa: E402

PERSONA = ("Bạn là trợ lý AI của một người dùng tại {market}. Trả lời bằng tiếng Việt, ngắn gọn (tối đa 200 từ), "
           "nêu tên thương hiệu cụ thể khi được hỏi, dẫn link nguồn nếu có.")
NHO = " Không tra web, không dùng công cụ; chỉ trả lời từ hiểu biết sẵn có, không biết thì nói không biết."
TIMEOUT = 180


def _cli(cmd: list[str]) -> str:
    exe = shutil.which(cmd[0])
    if not exe:
        raise RuntimeError(f"không tìm thấy lệnh {cmd[0]} trong PATH")
    r = subprocess.run([exe] + cmd[1:], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=TIMEOUT)
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError((r.stderr or "lệnh không trả nội dung")[-300:])
    return r.stdout.strip()


def _post(url: str, headers: dict, body: dict) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"content-type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))


def ask(model: str, question: str, market: str) -> tuple[str, list[tuple[str, str]]]:
    sys_p = PERSONA.format(market=market)
    if model == "claude-tim":
        return _cli(["claude", "-p", f"{sys_p}\n\nCâu hỏi: {question}", "--allowedTools", "WebSearch,WebFetch"]), []
    if model == "claude-nho":
        return _cli(["claude", "-p", f"{sys_p}{NHO}\n\nCâu hỏi: {question}", "--disallowedTools", "WebSearch,WebFetch,Bash"]), []
    if model == "agy":
        return _cli(["agy", "-p", f"{sys_p}\n\nCâu hỏi: {question}"]), []
    if model == "codex":
        return _cli(["codex", "exec", f"{sys_p}\n\nCâu hỏi: {question}"]), []
    if model.startswith("gemini-"):
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("thiếu GEMINI_API_KEY")
        tim = model == "gemini-tim"
        body = {"systemInstruction": {"parts": [{"text": sys_p + ("" if tim else NHO)}]},
                "contents": [{"role": "user", "parts": [{"text": question}]}],
                "generationConfig": {"temperature": 0.7}}
        if tim:
            body["tools"] = [{"google_search": {}}]
        m = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        d = _post(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent", {"x-goog-api-key": key}, body)
        cand = (d.get("candidates") or [{}])[0]
        text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []))
        src = [((c.get("web") or {}).get("title", ""), (c.get("web") or {}).get("uri", ""))
               for c in (cand.get("groundingMetadata") or {}).get("groundingChunks", [])]
        return text.strip(), src
    if model.startswith("openrouter:"):
        key = os.environ.get("OPENROUTER_API_KEY")
        if not key:
            raise RuntimeError("thiếu OPENROUTER_API_KEY")
        name = model.split(":", 1)[1]
        online = name.endswith(":online")
        body = {"model": name, "messages": [{"role": "system", "content": sys_p + ("" if online else NHO)},
                                            {"role": "user", "content": question}]}
        d = _post("https://openrouter.ai/api/v1/chat/completions", {"authorization": f"Bearer {key}"}, body)
        msg = (d.get("choices") or [{}])[0].get("message", {})
        src = [(a.get("url_citation", {}).get("title", ""), a.get("url_citation", {}).get("url", ""))
               for a in msg.get("annotations", []) or [] if a.get("type") == "url_citation"]
        return str(msg.get("content", "")).strip(), src
    raise RuntimeError(f"không biết mô hình {model}")


def answer_path(run_dir: Path, model: str, qid: str, luot: int) -> Path:
    safe = model.replace(":", "_").replace("/", "_")
    return run_dir / "tra-loi" / safe / f"{qid}__l{luot}.md"


def collect(run_dir: Path, questions: list[dict], models: list[str], luot: int, market: str,
            date: str, only_missing: bool = True) -> dict:
    done = failed = stub = 0
    for model in models:
        paste = model.startswith("dan-tay:")
        label = model.split(":", 1)[1] if paste else model
        for q in questions:
            for n in range(1, luot + 1):
                p = answer_path(run_dir, label, q["id"], n)
                if only_missing and p.exists() and parse_response_file(p)["body"]:
                    continue
                if paste:
                    write_response_stub(p, q["id"], q["text"], label, date)
                    stub += 1
                    continue
                try:
                    text, src = ask(model, q["text"], market)
                except Exception as e:  # noqa: BLE001 - ghi lỗi, chạy tiếp câu khác
                    print(f"  ! {model} {q['id']} l{n}: {e}", file=sys.stderr)
                    failed += 1
                    continue
                write_response_stub(p, q["id"], q["text"], label, date)
                tail = "".join(f"\n[nguon] {t or ''} | {u}" for t, u in src if u)
                p.write_text(p.read_text(encoding="utf-8").replace("(no response)\n", text + "\n" + tail + "\n"), encoding="utf-8")
                done += 1
                print(f"  ✓ {label} {q['id']} l{n}")
    return {"da_hoi": done, "loi": failed, "file_cho_dan": stub}


def load_answers(run_dir: Path) -> list[dict]:
    out = []
    for p in sorted((run_dir / "tra-loi").glob("*/*.md")):
        r = parse_response_file(p)
        if not r["body"]:
            continue
        qid, _, l = p.stem.rpartition("__l")
        body, src = [], []
        for line in r["body"].splitlines():
            if line.startswith("[nguon]"):
                t, _, u = line[7:].partition("|")
                src.append({"title": t.strip(), "url": u.strip()})
            else:
                body.append(line)
        out.append({"model": p.parent.name, "qid": qid, "luot": int(l or 1), "question": r["prompt"],
                    "answer": "\n".join(body).strip(), "sources": src, "file": str(p)})
    return out
