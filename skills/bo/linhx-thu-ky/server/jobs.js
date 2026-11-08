// Giao việc cho Claude Code: chạy `claude -p` trong thư mục dự án, lời nhắn đi qua stdin
// (không ghép vào dòng lệnh, nên lời nói không thể chèn lệnh shell). Mỗi việc là một job có trạng thái.

const { spawn } = require('child_process');
const { EventEmitter } = require('events');

const MODES = new Set(['plan', 'acceptEdits', 'default']);
const SID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
// Server thường được bật từ trong một phiên Claude (/thu-ky open), nên kế thừa biến định danh phiên đó.
// Phải bỏ đi, nếu không claude -p con sẽ ghi vào transcript của phiên cha (đã gặp khi thử 13/10).
const INHERITED = ['CLAUDECODE', 'CLAUDE_CODE_SESSION_ID', 'CLAUDE_CODE_ENTRYPOINT', 'CLAUDE_CODE_SSE_PORT', 'CLAUDE_PID', 'CLAUDE_CODE_CHILD_SESSION', 'CLAUDE_CODE_REMOTE_SESSION_ID'];
function childEnv(id) {
  const env = { ...process.env, LINHX_THU_KY_JOB: String(id) };
  for (const k of INHERITED) delete env[k];
  return env;
}

// Trên Windows claude chạy qua cmd (shell), phải diệt cả cây tiến trình.
function kill(proc) {
  if (process.platform === 'win32' && proc.pid) spawn('taskkill', ['/pid', String(proc.pid), '/T', '/F'], { windowsHide: true });
  else proc.kill();
}

const PREFIX = '[Lệnh từ thư ký ảo LINHX: Linh nói bằng giọng, thư ký chuyển lại] ';

class Jobs extends EventEmitter {
  constructor(cfg) {
    super();
    this.cfg = cfg;
    this.jobs = new Map();
    this.seq = 0;
  }

  running() { return [...this.jobs.values()].filter((j) => j.trang_thai === 'dang_lam'); }

  publicJob(j) {
    const { proc, out, err, timer, ...rest } = j;
    return rest;
  }

  list() { return [...this.jobs.values()].map((j) => this.publicJob(j)); }

  get(id) { return this.jobs.get(Number(String(id).replace(/\D/g, ''))) || null; }

  // project: {ten, thu_muc}; opts: {che_do: 'plan'|'acceptEdits', resume: session_id}
  start(project, text, opts = {}) {
    if (this.running().length >= this.cfg.maxJobs) return { ok: false, error: `Đang có ${this.cfg.maxJobs} việc chạy, chờ xong bớt rồi giao tiếp.` };
    const mode = MODES.has(opts.che_do) ? opts.che_do : this.cfg.permissionMode;
    const args = ['-p', '--output-format', 'json', '--permission-mode', mode];
    if (opts.resume && SID.test(opts.resume)) args.push('--resume', opts.resume);
    const id = ++this.seq;
    const job = {
      id, du_an: project.ten, thu_muc: project.thu_muc, noi_dung: String(text).slice(0, 2000), che_do: mode,
      trang_thai: 'dang_lam', bat_dau: new Date().toISOString(), xong_luc: null, ket_qua: '', session_id: opts.resume || null,
      out: '', err: '',
    };
    let proc;
    try {
      proc = spawn(this.cfg.claudeCommand, args, { cwd: project.thu_muc, shell: process.platform === 'win32', windowsHide: true, env: childEnv(id) });
    } catch (e) {
      return { ok: false, error: `Không chạy được claude: ${e.message}` };
    }
    job.proc = proc;
    this.jobs.set(id, job);
    proc.stdout.on('data', (d) => { if (job.out.length < 2e6) job.out += d; });
    proc.stderr.on('data', (d) => { if (job.err.length < 1e5) job.err += d; });
    proc.on('error', (e) => this.finish(job, 1, e.message));
    proc.on('close', (code) => this.finish(job, code));
    proc.stdin.end(PREFIX + job.noi_dung);
    const ms = (this.cfg.jobTimeoutMin || 30) * 60000;
    job.timer = setTimeout(() => { if (job.trang_thai === 'dang_lam') { job.ly_do_dung = 'Hết thời gian, đã dừng.'; kill(proc); } }, ms);
    this.emit('update', this.publicJob(job));
    return { ok: true, job: this.publicJob(job) };
  }

  finish(job, code, errMsg) {
    if (job.trang_thai !== 'dang_lam') return;
    clearTimeout(job.timer);
    delete job.timer;
    let r = null;
    try { r = JSON.parse(job.out.trim().split('\n').pop()); } catch {}
    job.xong_luc = new Date().toISOString();
    if (r && typeof r.result === 'string') {
      job.ket_qua = r.result;
      job.session_id = r.session_id || job.session_id;
      job.chi_phi_usd = r.total_cost_usd;
      job.trang_thai = r.is_error ? 'loi' : 'xong';
    } else {
      job.trang_thai = 'loi';
      job.ket_qua = job.ly_do_dung || (errMsg || job.err || job.out || `claude thoát mã ${code}`).slice(0, 1500);
    }
    this.emit('update', this.publicJob(job));
    this.emit('done', this.publicJob(job));
  }

  stop(id) {
    const j = this.get(id);
    if (!j || j.trang_thai !== 'dang_lam') return { ok: false, error: 'Không có việc đang chạy với số này' };
    j.ly_do_dung = 'Linh cho dừng.';
    kill(j.proc);
    return { ok: true };
  }
}

module.exports = { Jobs, PREFIX };
