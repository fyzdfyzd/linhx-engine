"""python -I test_chuyen_skill.py  (stdlib, không mạng)"""
import sys, tempfile, tomllib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import chuyen_skill as cs

def plugin_mau(g):
    (g / ".claude-plugin").mkdir(parents=True)
    (g / ".claude-plugin/plugin.json").write_text('{"name":"mau","description":"plugin mẫu"}', encoding="utf-8")
    s = g / "skills/viet-tom-tat"; (s / "scripts").mkdir(parents=True)
    (s / "SKILL.md").write_text("---\nname: viet-tom-tat\ndescription: Tóm tắt file khi Linh nói 'tóm tắt'\nallowed-tools: Read\nwhen_to_use: x\n---\nChạy `python ${CLAUDE_PLUGIN_ROOT}/skills/viet-tom-tat/scripts/t.py`.\nHỏi bằng AskUserQuestion.\n", encoding="utf-8")
    (s / "scripts/t.py").write_text("print(1)\n")
    (g / "commands").mkdir(); (g / "commands/tom.md").write_text('---\ndescription: "Tóm tắt nhanh"\n---\nDùng skill viet-tom-tat cho: $ARGUMENTS\n', encoding="utf-8")
    (g / "agents").mkdir(); (g / "agents/phan-bien.md").write_text("---\nname: phan-bien\ndescription: Phản biện bản nháp\ntools: Read, Grep\nmodel: sonnet\n---\nBạn là người phản biện.\n", encoding="utf-8")

def test():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t); plugin_mau(t / "p"); log = cs.main([str(t / "p"), str(t / "ra")])
        r = t / "ra"; y = " ".join(v for _, v in log)
        sk = (r / ".agents/skills/viet-tom-tat/SKILL.md").read_text(encoding="utf-8")
        ok = [
            ("1 chung có skill + script", (r / ".agents/skills/viet-tom-tat/scripts/t.py").exists()),
            ("2 bỏ CLAUDE_PLUGIN_ROOT", "CLAUDE_PLUGIN_ROOT" not in sk and "`python scripts/t.py`" in sk),
            ("3 bỏ trường lạ, giữ allowed-tools", "when_to_use" not in sk and "allowed-tools" in sk),
            ("4 cảnh báo AskUserQuestion", "tên tool riêng" in y),
            ("5 copilot prompt ${input:args}", "${input:args}" in (r / ".github/prompts/tom.prompt.md").read_text(encoding="utf-8")),
            ("6 copilot agent không tools", "tools" not in (r / ".github/agents/phan-bien.agent.md").read_text(encoding="utf-8")),
            ("7 gemini toml hợp lệ + {{args}}", "{{args}}" in tomllib.loads((r / "gemini-ext/mau/commands/tom.toml").read_text(encoding="utf-8"))["prompt"]),
            ("8 gemini-extension.json + GEMINI.md", (r / "gemini-ext/mau/gemini-extension.json").exists() and "viet-tom-tat" in (r / "gemini-ext/mau/GEMINI.md").read_text(encoding="utf-8")),
            ("9 cảnh báo tools/model agent", "đã bỏ (agent" in y and "model 'sonnet'" in y),
        ]
    for n, v in ok: print(("ĐẠT " if v else "TRƯỢT ") + n)
    print(f"{sum(v for _, v in ok)}/{len(ok)}"); return all(v for _, v in ok)

if __name__ == "__main__":
    sys.exit(0 if test() else 1)
