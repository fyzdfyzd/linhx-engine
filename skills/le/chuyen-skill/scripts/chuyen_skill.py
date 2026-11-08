#!/usr/bin/env python3
"""Chuyển skill/plugin Claude Code sang Copilot, Gemini CLI, Antigravity. 0 token, chỉ stdlib.

  python chuyen_skill.py <nguon> <dich> [--kieu chung|copilot|gemini-ext|tat-ca]

<nguon>: thư mục một skill (có SKILL.md) hoặc một plugin Claude (có skills/, commands/, agents/).
<dich>: gốc repo/thư mục ra.
  chung      -> .agents/skills/<ten>/   (Copilot, Gemini CLI, Antigravity đều đọc)
  copilot    -> .github/skills, .github/prompts/*.prompt.md, .github/agents/*.agent.md
  gemini-ext -> gemini-ext/<plugin>/ gồm gemini-extension.json, GEMINI.md, skills/, commands/*.toml, agents/
In ra bảng cảnh báo những chỗ chỉ Claude hiểu.
"""
import argparse, json, re, shutil, sys
from pathlib import Path

# Chỗ chỉ Claude Code hiểu, nền khác bỏ qua hoặc hiểu sai
CANH_BAO = [
    (r"\$\{CLAUDE_PLUGIN_ROOT\}", "biến CLAUDE_PLUGIN_ROOT, đã đổi thành đường dẫn tương đối"),
    (r"\$\{CLAUDE_SKILL_DIR\}", "biến CLAUDE_SKILL_DIR, đã đổi thành '.'"),
    (r"!`[^`]+`", "chèn lệnh động !`...` chỉ Claude chạy"),
    (r"\b(AskUserQuestion|TodoWrite|TaskCreate|NotebookEdit)\b", "tên tool riêng của Claude"),
    (r"\b(Task|Agent) tool\b|subagent_type", "gọi subagent kiểu Claude, nền khác gọi bằng @ten-agent"),
    (r"\bclaude -p\b|claude plugin", "lệnh CLI claude"),
]
FM_SKILL = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}  # chuẩn agentskills.io


def doc_fm(text):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    fm, key = {}, None
    for dong in m.group(1).splitlines():
        k = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", dong)
        if k:
            key = k.group(1); fm[key] = k.group(2).strip()
        elif key:
            fm[key] += "\n" + dong
    return fm, m.group(2)


def viet_fm(fm, body):
    return "---\n" + "".join(f"{k}: {v}\n" for k, v in fm.items()) + "---\n" + body


def bo_ngoac(v):
    v = v.strip()
    return v[1:-1] if len(v) > 1 and v[0] == v[-1] and v[0] in "\"'" else v


def soat(text, noi, log):
    for mau, y in CANH_BAO:
        if re.search(mau, text):
            log.append((noi, y))
    text = re.sub(r"\$\{CLAUDE_PLUGIN_ROOT\}/skills/[^/\s]+/?", "", text)
    text = re.sub(r"\$\{CLAUDE_PLUGIN_ROOT\}/?", "../../", text)
    return re.sub(r"\$\{CLAUDE_SKILL_DIR\}", ".", text)


def tim(nguon):
    """Trả về (ten_plugin, mo_ta, [skill_dir], [command.md], [agent.md])."""
    if (nguon / "SKILL.md").exists():
        return nguon.name, "", [nguon], [], []
    pj = nguon / ".claude-plugin" / "plugin.json"
    meta = json.loads(pj.read_text(encoding="utf-8")) if pj.exists() else {}
    return (meta.get("name", nguon.name), meta.get("description", ""),
            sorted(p.parent for p in nguon.glob("skills/*/SKILL.md")),
            sorted(nguon.glob("commands/*.md")), sorted(nguon.glob("agents/*.md")))


def chep_skill(sd, dich, log):
    ra = dich / sd.name
    if ra.exists():
        shutil.rmtree(ra)
    shutil.copytree(sd, ra, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    fm, body = doc_fm((sd / "SKILL.md").read_text(encoding="utf-8"))
    if not fm.get("description"):
        log.append((sd.name, "THIẾU description, nền nào cũng không tự gọi được"))
    if fm.get("name") and fm["name"] != sd.name:
        log.append((sd.name, f"name '{fm['name']}' khác tên thư mục, Copilot/Gemini đòi trùng"))
    thua = [k for k in fm if k not in FM_SKILL]
    if thua:
        log.append((sd.name, "bỏ trường chỉ Claude dùng: " + ", ".join(thua)))
    fm = {k: v for k, v in fm.items() if k in FM_SKILL}
    fm.setdefault("name", sd.name)
    (ra / "SKILL.md").write_text(viet_fm(fm, soat(body, sd.name, log)), encoding="utf-8")
    for f in ra.rglob("*.md"):
        if f.name != "SKILL.md":
            f.write_text(soat(f.read_text(encoding="utf-8"), f"{sd.name}/{f.name}", log), encoding="utf-8")


def agent_fm(fm, ten, log, nen):
    if fm.get("tools"):
        log.append((ten, f"tools '{fm['tools'].strip()}' là tên tool Claude; {nen} dùng tên khác, đã bỏ (agent nhận đủ tool), tự giới hạn lại nếu cần"))
    if fm.get("model") and fm["model"] not in ("inherit",):
        log.append((ten, f"model '{fm['model']}' đã bỏ, dùng model mặc định của {nen}"))
    return {"name": fm.get("name", ten), "description": fm.get("description", "")}


def ra_copilot(skills, cmds, agents, dich, log):
    for sd in skills:
        chep_skill(sd, dich / ".github/skills", log)
    for c in cmds:
        fm, body = doc_fm(c.read_text(encoding="utf-8"))
        body = soat(body, c.name, log).replace("$ARGUMENTS", "${input:args}")
        out = {"description": fm.get("description", c.stem), "agent": "agent"}
        p = dich / ".github/prompts" / f"{c.stem}.prompt.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(viet_fm(out, body), encoding="utf-8")
    for a in agents:
        fm, body = doc_fm(a.read_text(encoding="utf-8"))
        p = dich / ".github/agents" / f"{a.stem}.agent.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(viet_fm(agent_fm(fm, a.stem, log, "Copilot"), soat(body, a.name, log)), encoding="utf-8")


def ra_gemini_ext(ten, mo_ta, skills, cmds, agents, dich, log):
    goc = dich / "gemini-ext" / ten
    for sd in skills:
        chep_skill(sd, goc / "skills", log)
    for c in cmds:
        fm, body = doc_fm(c.read_text(encoding="utf-8"))
        body = soat(body, c.name, log).replace("$ARGUMENTS", "{{args}}").strip()
        p = goc / "commands" / f"{c.stem}.toml"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"description = {json.dumps(bo_ngoac(fm.get('description', c.stem)), ensure_ascii=False)}\n"
                     f'prompt = """\n{body}\n"""\n', encoding="utf-8")
    for a in agents:
        fm, body = doc_fm(a.read_text(encoding="utf-8"))
        p = goc / "agents" / a.name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(viet_fm(agent_fm(fm, a.stem, log, "Gemini CLI"), soat(body, a.name, log)), encoding="utf-8")
    goc.mkdir(parents=True, exist_ok=True)
    (goc / "gemini-extension.json").write_text(json.dumps(
        {"name": ten, "version": "0.1.0", "description": mo_ta, "contextFileName": "GEMINI.md"},
        ensure_ascii=False, indent=2), encoding="utf-8")
    ds = "\n".join(f"- {sd.name}" for sd in skills)
    (goc / "GEMINI.md").write_text(f"# {ten}\n\n{mo_ta}\n\nSkill trong extension này (tự gọi theo description):\n{ds}\n", encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("nguon"); ap.add_argument("dich")
    ap.add_argument("--kieu", default="tat-ca", choices=["chung", "copilot", "gemini-ext", "tat-ca"])
    a = ap.parse_args(argv)
    nguon, dich = Path(a.nguon).resolve(), Path(a.dich).resolve()
    ten, mo_ta, skills, cmds, agents = tim(nguon)
    if not (skills or cmds or agents):
        sys.exit(f"Không thấy SKILL.md, commands/ hay agents/ trong {nguon}")
    log = []
    if a.kieu in ("chung", "tat-ca"):
        for sd in skills:
            chep_skill(sd, dich / ".agents/skills", log)
        if cmds or agents:
            log.append((ten, "kiểu chung chỉ mang skill; command/agent cần --kieu copilot hoặc gemini-ext"))
    if a.kieu in ("copilot", "tat-ca"):
        ra_copilot(skills, cmds, agents, dich, log)
    if a.kieu in ("gemini-ext", "tat-ca"):
        ra_gemini_ext(ten, mo_ta, skills, cmds, agents, dich, log)
    log = list(dict.fromkeys(log))
    print(f"{ten}: {len(skills)} skill, {len(cmds)} command, {len(agents)} agent -> {dich}")
    for noi, y in log:
        print(f"  ! {noi}: {y}")
    return log


if __name__ == "__main__":
    main()
