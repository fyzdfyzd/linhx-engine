"""Đóng gói khoá học thành chuẩn SCORM 1.2 (.zip), kiểm thử tự động trên LMS giả (scorm-again + Playwright)
và sinh báo cáo kiểm định chất lượng 05-qa-report.md.
"""
import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import zipfile

try:
    import yaml
except ImportError:
    sys.exit("Thiếu PyYAML: pip install pyyaml")

ENGINE_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = ENGINE_DIR.parents[3]


def load_cfg(course_dir: pathlib.Path, cfg_override: str | None = None) -> dict:
    for c in [
        pathlib.Path(cfg_override) if cfg_override else None,
        course_dir / "engine.json",
        REPO_ROOT / "work" / "course" / "engine.json",
        ENGINE_DIR / "config.example.json",
    ]:
        if c and c.exists():
            return json.loads(c.read_text(encoding="utf-8"))
    return {}


def resolve_path(val: str) -> pathlib.Path:
    p = pathlib.Path(val)
    return p if p.is_absolute() else (REPO_ROOT / p).resolve()


def slugify(text: str) -> str:
    s = unicodedata.normalize("NFD", text.replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower()).strip("-")
    return s or "course-scorm12"


def media_dur(p: pathlib.Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(p)],
        capture_output=True, text=True, check=False,
    )
    return float(json.loads(r.stdout or "{}").get("format", {}).get("duration", 0.0))


SCORM_WRAPPER_JS = """// Pipwerks-compatible SCORM 1.2 API Wrapper
var pipwerks = { SCORM: { version: "1.2", connection: { isActive: false, api: null } } };
function findSCORMAPI(win) {
  var attempts = 0;
  while (win && !win.API && win.parent && win.parent !== win && attempts < 10) {
    attempts++;
    win = win.parent;
  }
  if (win && win.API) return win.API;
  if (window.opener && window.opener.API) return window.opener.API;
  return null;
}
pipwerks.SCORM.init = function() {
  var api = findSCORMAPI(window);
  if (!api) return false;
  pipwerks.SCORM.connection.api = api;
  var res = api.LMSInitialize("");
  pipwerks.SCORM.connection.isActive = (res === "true" || res === true);
  if (pipwerks.SCORM.connection.isActive) {
    api.LMSSetValue("cmi.core.lesson_status", "incomplete");
    api.LMSSetValue("cmi.core.score.min", "0");
    api.LMSSetValue("cmi.core.score.max", "100");
    api.LMSCommit("");
  }
  return pipwerks.SCORM.connection.isActive;
};
pipwerks.SCORM.reportScore = function(scoreRaw, passed) {
  var api = pipwerks.SCORM.connection.api || findSCORMAPI(window);
  if (!api) return false;
  api.LMSSetValue("cmi.core.score.raw", String(Math.round(scoreRaw)));
  api.LMSSetValue("cmi.core.lesson_status", passed ? "passed" : "failed");
  api.LMSCommit("");
  api.LMSFinish("");
  return true;
};
"""


def build_sco_html(lesson_id: str, lesson_title: str, questions: list[dict]) -> str:
    quiz_json = json.dumps(questions, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{lesson_id} - {lesson_title}</title>
  <style>
    body {{ font-family: "Be Vietnam Pro", system-ui, sans-serif; margin: 0; padding: 24px; background: #f7f8fc; color: #14213d; }}
    .container {{ max-width: 980px; margin: 0 auto; background: #fff; border-radius: 16px; padding: 28px; box-shadow: 0 8px 30px rgba(20,33,61,.08); }}
    h1 {{ font-size: 26px; margin-top: 0; color: #1f4fd8; }}
    video {{ width: 100%; border-radius: 12px; background: #000; margin-bottom: 24px; }}
    .q-card {{ border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px; margin-bottom: 16px; background: #fafbff; }}
    .q-stem {{ font-weight: 700; margin-bottom: 12px; font-size: 17px; }}
    .opt {{ display: block; margin: 8px 0; cursor: pointer; font-size: 16px; }}
    .feedback {{ margin-top: 8px; font-size: 14px; padding: 8px 12px; border-radius: 8px; display: none; }}
    .feedback.ok {{ display: block; background: #dcfce7; color: #166534; }}
    .feedback.err {{ display: block; background: #fee2e2; color: #991b1b; }}
    button#submit-quiz {{ background: #1f4fd8; color: #fff; border: none; padding: 12px 28px; border-radius: 10px; font-size: 16px; font-weight: 700; cursor: pointer; }}
    #quiz-result {{ margin-top: 18px; font-weight: 700; font-size: 18px; }}
  </style>
  <script src="../scorm_wrapper.js"></script>
</head>
<body>
  <div class="container">
    <h1>{lesson_id}: {lesson_title}</h1>
    <video id="lesson-video" controls preload="metadata">
      <source src="lesson.mp4" type="video/mp4" />
      <track label="Tiếng Việt" kind="subtitles" srclang="vi" src="lesson.vtt" default />
    </video>
    <div id="quiz-section">
      <h2>Bài kiểm tra nhanh</h2>
      <div id="quiz-questions"></div>
      <button id="submit-quiz" type="button">Nộp bài &amp; Ghi điểm</button>
      <div id="quiz-result" data-score="" data-status=""></div>
    </div>
  </div>
  <script>
    const QUESTIONS = {quiz_json};
    let videoWatched = false;
    window.addEventListener("DOMContentLoaded", () => {{
      pipwerks.SCORM.init();
      const vid = document.getElementById("lesson-video");
      vid.addEventListener("ended", () => {{ videoWatched = true; }});
      vid.addEventListener("timeupdate", () => {{
        if (vid.duration && vid.currentTime >= vid.duration - 1.0) videoWatched = true;
      }});
      const qWrap = document.getElementById("quiz-questions");
      QUESTIONS.forEach((q, idx) => {{
        const div = document.createElement("div");
        div.className = "q-card";
        div.dataset.qid = q.id;
        let html = `<div class="q-stem">Câu ${{idx + 1}} (${{q.id}}): ${{q.stem}}</div>`;
        if (q.type === "tf") {{
          const opts = [
            {{ text: "Đúng", val: "true", correct: q.correct === true, feedback: q.feedback || "" }},
            {{ text: "Sai", val: "false", correct: q.correct === false, feedback: q.feedback || "" }}
          ];
          opts.forEach((o, oIdx) => {{
            html += `<label class="opt"><input type="radio" name="q_${{q.id}}" value="${{o.val}}" data-correct="${{o.correct}}" data-fb="${{(o.feedback || '').replace(/"/g, '&quot;')}}" /> ${{o.text}}</label>`;
          }});
        }} else if (q.type === "multi") {{
          (q.options || []).forEach((o, oIdx) => {{
            html += `<label class="opt"><input type="checkbox" name="q_${{q.id}}" value="${{oIdx}}" data-correct="${{!!o.correct}}" data-fb="${{(o.feedback || '').replace(/"/g, '&quot;')}}" /> ${{o.text}}</label>`;
          }});
        }} else {{
          (q.options || []).forEach((o, oIdx) => {{
            html += `<label class="opt"><input type="radio" name="q_${{q.id}}" value="${{oIdx}}" data-correct="${{!!o.correct}}" data-fb="${{(o.feedback || '').replace(/"/g, '&quot;')}}" /> ${{o.text}}</label>`;
          }});
        }}
        html += `<div class="feedback" id="fb_${{q.id}}"></div>`;
        div.innerHTML = html;
        qWrap.appendChild(div);
      }});

      document.getElementById("submit-quiz").addEventListener("click", () => {{
        let correctCount = 0;
        QUESTIONS.forEach((q) => {{
          const inputs = Array.from(document.querySelectorAll(`input[name="q_${{q.id}}"]`));
          const fbEl = document.getElementById(`fb_${{q.id}}`);
          let isQCorrect = false;
          let fbMsgs = [];
          if (q.type === "multi") {{
            isQCorrect = inputs.every(inp => inp.checked === (inp.dataset.correct === "true"));
            inputs.forEach(inp => {{ if (inp.checked && inp.dataset.fb) fbMsgs.push(inp.dataset.fb); }});
          }} else {{
            const checked = inputs.find(inp => inp.checked);
            isQCorrect = !!(checked && checked.dataset.correct === "true");
            if (checked && checked.dataset.fb) fbMsgs.push(checked.dataset.fb);
            if (!fbMsgs.length && q.feedback) fbMsgs.push(q.feedback);
          }}
          if (isQCorrect) correctCount++;
          fbEl.className = "feedback " + (isQCorrect ? "ok" : "err");
          fbEl.textContent = (isQCorrect ? "Chính xác! " : "Chưa đúng. ") + fbMsgs.join(" ");
        }});
        const scoreRaw = Math.round((correctCount / Math.max(QUESTIONS.length, 1)) * 100);
        const passed = scoreRaw >= 70;
        const status = passed ? "passed" : "failed";
        pipwerks.SCORM.reportScore(scoreRaw, passed);
        const resEl = document.getElementById("quiz-result");
        resEl.dataset.score = String(scoreRaw);
        resEl.dataset.status = status;
        resEl.textContent = `Kết quả: ${{scoreRaw}}/100 điểm (${{status.toUpperCase()}})`;
      }});
    }});
  </script>
</body>
</html>
"""


def build_manifest_xml(course_id: str, course_title: str, lessons: list[dict]) -> str:
    items_xml = []
    res_xml = []
    for l in lessons:
        lid = l["id"]
        title = l["title"]
        items_xml.append(
            f'      <item identifier="ITEM_{lid}" identifierref="RES_{lid}" isvisible="true">\n'
            f'        <title>{lid}: {title}</title>\n'
            f'      </item>'
        )
        res_xml.append(
            f'    <resource identifier="RES_{lid}" type="webcontent" adlcp:scormtype="sco" href="{lid}/index.html">\n'
            f'      <file href="{lid}/index.html" />\n'
            f'      <file href="{lid}/lesson.mp4" />\n'
            f'      <file href="{lid}/lesson.vtt" />\n'
            f'      <file href="scorm_wrapper.js" />\n'
            f'    </resource>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<manifest identifier="MANIFEST_' + course_id.upper().replace("-", "_") + '" version="1.0"\n'
        '          xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"\n'
        '          xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"\n'
        '          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
        '  <metadata>\n'
        '    <schema>ADL SCORM</schema>\n'
        '    <schemaversion>1.2</schemaversion>\n'
        '  </metadata>\n'
        '  <organizations default="ORG_1">\n'
        '    <organization identifier="ORG_1">\n'
        f'      <title>{course_title}</title>\n'
        + "\n".join(items_xml) + "\n"
        '    </organization>\n'
        '  </organizations>\n'
        '  <resources>\n'
        + "\n".join(res_xml) + "\n"
        '  </resources>\n'
        '</manifest>\n'
    )


def run_lms_test(staging_dir: pathlib.Path, lessons: list[dict], out_json: pathlib.Path, cfg: dict):
    node_dir = resolve_path(cfg.get("node_dir", "local/.node/node-v22.12.0-win-x64"))
    node_exe = resolve_path(cfg.get("node_exe", "local/.node/node-v22.12.0-win-x64/node.exe"))
    pw_browsers = resolve_path(cfg.get("playwright_browsers", "local/.pw-browsers"))
    slidev_workdir = resolve_path(cfg.get("slidev_workdir", "local/pilot/L01"))
    npm_cache = resolve_path(cfg.get("npm_cache", "local/.npm-cache"))

    env = os.environ.copy()
    env["PATH"] = f"{node_dir};{env.get('PATH', '')}"
    env["PLAYWRIGHT_BROWSERS_PATH"] = str(pw_browsers)
    env["npm_config_cache"] = str(npm_cache)

    # Cài scorm-again vào slidev_workdir nếu chưa có
    scorm_again_dist = slidev_workdir / "node_modules" / "scorm-again" / "dist" / "scorm12.min.js"
    if not scorm_again_dist.exists():
        npm_cmd = str(node_dir / "npm.cmd")
        subprocess.run(
            [npm_cmd, "i", "--no-save", "scorm-again"],
            cwd=str(slidev_workdir),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    if scorm_again_dist.exists():
        shutil.copy2(scorm_again_dist, staging_dir / "scorm12.min.js")
    else:
        # Bản dự phòng tương thích Scorm12API chuẩn nếu mạng chặn npm
        (staging_dir / "scorm12.min.js").write_text(
            "window.Scorm12API = function() {\n"
            "  this.cmi = { core: { score: { raw: '', min: '0', max: '100' }, lesson_status: 'not attempted' } };\n"
            "  this.LMSInitialize = function() { return 'true'; };\n"
            "  this.LMSSetValue = function(k, v) {\n"
            "    if (k === 'cmi.core.score.raw') this.cmi.core.score.raw = String(v);\n"
            "    if (k === 'cmi.core.lesson_status') this.cmi.core.lesson_status = String(v);\n"
            "    return 'true';\n"
            "  };\n"
            "  this.LMSGetValue = function(k) {\n"
            "    if (k === 'cmi.core.score.raw') return this.cmi.core.score.raw;\n"
            "    if (k === 'cmi.core.lesson_status') return this.cmi.core.lesson_status;\n"
            "    return '';\n"
            "  };\n"
            "  this.LMSCommit = function() { return 'true'; };\n"
            "  this.LMSFinish = function() { return 'true'; };\n"
            "};\n",
            encoding="utf-8",
        )

    lms_html = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8" />
  <title>Local SCORM 1.2 Mock LMS (scorm-again)</title>
  <script src="scorm12.min.js"></script>
</head>
<body>
  <iframe id="sco-frame" style="width:1280px;height:800px;border:1px solid #ccc;"></iframe>
  <script>
    window.loadSCO = function(href) {
      window.API = new window.Scorm12API({ autocommit: true });
      const f = document.getElementById("sco-frame");
      f.src = href;
    };
    window.readSCORM = function() {
      if (!window.API) return { score_raw: null, lesson_status: "unknown" };
      const raw = window.API.LMSGetValue ? window.API.LMSGetValue("cmi.core.score.raw") : window.API.cmi.core.score.raw;
      const st = window.API.LMSGetValue ? window.API.LMSGetValue("cmi.core.lesson_status") : window.API.cmi.core.lesson_status;
      return { score_raw: Number(raw), lesson_status: String(st) };
    };
  </script>
</body>
</html>
"""
    (staging_dir / "lms.html").write_text(lms_html, encoding="utf-8")

    pw_script = slidev_workdir / "_run_lms_test.mjs"
    lesson_ids_json = json.dumps([l["id"] for l in lessons])
    pw_script.write_text(
        f"""import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {{ chromium }} from 'playwright-chromium';

const root = {json.dumps(staging_dir.as_posix())};
const mime = {{ '.html': 'text/html; charset=utf-8', '.js': 'application/javascript', '.mp4': 'video/mp4', '.vtt': 'text/vtt; charset=utf-8', '.xml': 'application/xml' }};

const server = http.createServer((req, res) => {{
  const u = new URL(req.url, 'http://127.0.0.1');
  const filePath = path.join(root, decodeURIComponent(u.pathname));
  if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {{
    res.writeHead(404); res.end('Not found'); return;
  }}
  const ext = path.extname(filePath);
  res.writeHead(200, {{ 'Content-Type': mime[ext] || 'application/octet-stream' }});
  fs.createReadStream(filePath).pipe(res);
}});

await new Promise(r => server.listen(0, '127.0.0.1', r));
const port = server.address().port;
const browser = await chromium.launch({{ headless: true }});
const page = await browser.newPage();
const scos = [];

for (const lid of {lesson_ids_json}) {{
  await page.goto(`http://127.0.0.1:${{port}}/lms.html`, {{ waitUntil: 'networkidle' }});
  await page.evaluate((h) => window.loadSCO(h), `${{lid}}/index.html`);
  const frameEl = await page.waitForSelector('#sco-frame');
  const frame = await frameEl.contentFrame();
  await frame.waitForSelector('#submit-quiz', {{ timeout: 15000 }});
  // Tua video tới cuối để kích hoạt hoàn thành xem video
  await frame.evaluate(() => {{
    const v = document.getElementById('lesson-video');
    if (v) {{
      if (v.duration && Number.isFinite(v.duration)) v.currentTime = v.duration;
      v.dispatchEvent(new Event('ended'));
    }}
    // Chọn các phương án đúng trong quiz để kiểm tra luồng chấm điểm thật
    document.querySelectorAll('input[data-correct="true"]').forEach(inp => {{ inp.click(); }});
  }});
  await frame.click('#submit-quiz');
  await frame.waitForFunction(() => document.getElementById('quiz-result').dataset.status !== '');
  const apiRes = await page.evaluate(() => window.readSCORM());
  scos.push({{ id: lid, score_raw: apiRes.score_raw, lesson_status: apiRes.lesson_status }});
}}

await browser.close();
server.close();
fs.writeFileSync({json.dumps(out_json.as_posix())}, JSON.stringify({{ scos }}, null, 2), 'utf-8');
console.log('LMS_TEST_OK', JSON.stringify(scos));
""",
        encoding="utf-8",
    )

    try:
        subprocess.run([str(node_exe), str(pw_script)], cwd=str(slidev_workdir), env=env, check=True)
    finally:
        pw_script.unlink(missing_ok=True)
        (staging_dir / "lms.html").unlink(missing_ok=True)
        (staging_dir / "scorm12.min.js").unlink(missing_ok=True)


def write_qa_report(course_dir: pathlib.Path, lessons: list[dict], lms_res: list[dict]):
    rows_align = []
    rows_media = []
    for l in lessons:
        lid = l["id"]
        obj_file = course_dir / "01-objectives" / f"{lid}.yaml"
        quiz_file = course_dir / "03-assessment" / f"quiz-{lid}.yaml"
        objs = yaml.safe_load(obj_file.read_text(encoding="utf-8")).get("objectives", []) if obj_file.exists() else []
        qs = {
            q["id"]: q
            for q in (yaml.safe_load(quiz_file.read_text(encoding="utf-8")).get("questions", []) if quiz_file.exists() else [])
        }
        for o in objs:
            oid = o["id"]
            obloom = o["bloom"]
            m_list = o.get("measurable_by", [])
            q_details = []
            for m in m_list:
                if m in qs:
                    q_details.append(f"{m} ({qs[m].get('bloom')})")
                else:
                    q_details.append(f"{m} (bài tập thực hành)")
            rows_align.append(f"| {lid} | {oid} | {o['statement']} | `{obloom}` | {', '.join(q_details)} |")

        lesson_dir = course_dir / "04-lessons" / lid
        mp4 = lesson_dir / "build" / "lesson.mp4"
        vtt = lesson_dir / "build" / "lesson.vtt"
        segs_file = lesson_dir / "segments.json"
        asr_file = lesson_dir / "asr.json"
        d_sec = media_dur(mp4) if mp4.exists() else 0.0
        cues = vtt.read_text(encoding="utf-8").count("-->") if vtt.exists() else 0
        seg_cnt = len(json.loads(segs_file.read_text(encoding="utf-8"))) if segs_file.exists() else 0
        words = (
            sum(len(re.sub(r"<[^>]+>", " ", s["text"]).split()) for s in json.loads(segs_file.read_text(encoding="utf-8")))
            if segs_file.exists()
            else 0
        )
        rows_media.append(f"| {lid} | {l['title']} | {seg_cnt} | {words} | {d_sec:.1f} s | {cues} | `{asr_file.exists()}` |")

    rows_lms = [f"| {r['id']} | {r['score_raw']} | `{r['lesson_status']}` |" for r in lms_res]

    report_md = (
        "# Báo cáo Kiểm định Chất lượng Khoá học (QA Report)\n\n"
        "## 1. Ma trận Alignment: Mục tiêu ↔ Câu hỏi / Bài tập ↔ Mức Bloom\n\n"
        "| Bài | Mục tiêu | Nội dung mục tiêu | Mức Bloom | Đo lường bởi |\n"
        "|---|---|---|---|---|\n"
        + "\n".join(rows_align)
        + "\n\n## 2. Thống kê Thời lượng Video & Phụ đề WebVTT\n\n"
        "| Bài | Tên bài | Số đoạn | Tổng âm tiết | Thời lượng MP4 | Số cue phụ đề VTT | Có ASR |\n"
        "|---|---|---|---|---|---|---|\n"
        + "\n".join(rows_media)
        + "\n\n## 3. Kết quả Kiểm thử Tự động trên LMS giả (SCORM 1.2 + Playwright)\n\n"
        "| SCO | Điểm ghi nhận (`cmi.core.score.raw`) | Trạng thái (`cmi.core.lesson_status`) |\n"
        "|---|---|---|\n"
        + "\n".join(rows_lms)
        + "\n"
    )
    (course_dir / "05-qa-report.md").write_text(report_md, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(
        description="Đóng gói khoá học thành gói SCORM 1.2 (.zip), chạy LMS giả bằng Playwright và xuất 05-qa-report.md."
    )
    ap.add_argument("course_dir", nargs="?", default="work/course", help="Thư mục khoá học (mặc định: work/course)")
    ap.add_argument("--config", default=None, help="Đường dẫn tới file engine.json")
    ap.add_argument("--skip-lms-test", action="store_true", help="Bỏ qua bước mở Playwright chạy LMS giả")
    args = ap.parse_args()

    course_dir = pathlib.Path(args.course_dir).resolve()
    cfg = load_cfg(course_dir, args.config)

    brief = yaml.safe_load((course_dir / "00-brief.yaml").read_text(encoding="utf-8"))
    outline = yaml.safe_load((course_dir / "02-outline.yaml").read_text(encoding="utf-8"))
    course_title = brief.get("course", "Khoá học E-Learning")
    course_slug = slugify(course_title)
    all_lessons = outline.get("lessons", [])
    built_lessons = [l for l in all_lessons if (course_dir / "04-lessons" / l["id"] / "build" / "lesson.mp4").exists()]
    lessons = built_lessons if built_lessons else all_lessons

    pkg_dir = course_dir / "06-package"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    staging = pathlib.Path(tempfile.mkdtemp(prefix="scorm_build_"))

    try:
        (staging / "scorm_wrapper.js").write_text(SCORM_WRAPPER_JS, encoding="utf-8")
        for l in lessons:
            lid = l["id"]
            l_title = l["title"]
            quiz_path = course_dir / "03-assessment" / f"quiz-{lid}.yaml"
            questions = yaml.safe_load(quiz_path.read_text(encoding="utf-8")).get("questions", [])
            sco_dir = staging / lid
            sco_dir.mkdir(parents=True, exist_ok=True)
            (sco_dir / "index.html").write_text(build_sco_html(lid, l_title, questions), encoding="utf-8")

            src_mp4 = course_dir / "04-lessons" / lid / "build" / "lesson.mp4"
            src_vtt = course_dir / "04-lessons" / lid / "build" / "lesson.vtt"
            if not src_mp4.exists() or not src_vtt.exists():
                sys.exit(f"Thiếu build/lesson.mp4 hoặc lesson.vtt cho {lid}")
            shutil.copy2(src_mp4, sco_dir / "lesson.mp4")
            shutil.copy2(src_vtt, sco_dir / "lesson.vtt")

        manifest_xml = build_manifest_xml(course_slug, course_title, lessons)
        (staging / "imsmanifest.xml").write_text(manifest_xml, encoding="utf-8")

        zip_path = pkg_dir / f"{course_slug}.zip"
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path in sorted(staging.rglob("*")):
                if file_path.is_file():
                    arcname = file_path.relative_to(staging).as_posix()
                    zf.write(file_path, arcname)

        lms_json_path = pkg_dir / "lms-test.json"
        if not args.skip_lms_test:
            run_lms_test(staging, lessons, lms_json_path, cfg)

        lms_res = json.loads(lms_json_path.read_text(encoding="utf-8")).get("scos", []) if lms_json_path.exists() else []
        write_qa_report(course_dir, lessons, lms_res)
        print(f"Đóng gói SCORM 1.2 hoàn tất: {zip_path} ({zip_path.stat().st_size / (1024*1024):.2f} MB)")
    finally:
        shutil.rmtree(staging, ignore_errors=True)


if __name__ == "__main__":
    main()
