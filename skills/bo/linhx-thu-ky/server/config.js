// Cấu hình thư ký: ~/.linhx-thu-ky/config.json (tạo bằng `/thu-ky setup`), ghi đè bằng biến môi trường.
// Khoá Gemini không bao giờ gửi xuống trình duyệt.

const fs = require('fs');
const os = require('os');
const path = require('path');

const HOME_DIR = path.join(os.homedir(), '.linhx-thu-ky');
const CONFIG_FILE = process.env.LINHX_THU_KY_CONFIG || path.join(HOME_DIR, 'config.json');

const DEFAULTS = {
  port: 4850,
  // Thư mục chứa các dự án; mỗi thư mục con là một dự án
  roots: [],
  // Dự án thêm tay: [{ "ten": "LAB025", "thu_muc": "D:/LINHX/LAB/LAB025-QUY-TRINH-VIET-BAI" }]
  projects: [],
  // Nhân vật: file cấu hình Live Character (videoMatrix) và thư mục chứa clip
  character: { config: '', videoDir: '' },
  envFile: '',
  liveModel: 'gemini-2.5-flash-native-audio-preview-12-2025',
  voice: 'Aoede',
  name: 'Emily',
  claudeCommand: 'claude',
  permissionMode: 'acceptEdits',
  maxJobs: 3,
  jobTimeoutMin: 30,
  officeUrl: 'http://127.0.0.1:4848',
  geminiWsUrl: 'wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent',
};

function readEnvFile(file) {
  const out = {};
  if (!file) return out;
  try {
    for (const line of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
      const m = /^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/.exec(line);
      if (m) out[m[1]] = m[2].replace(/^["']|["']$/g, '');
    }
  } catch {}
  return out;
}

function load() {
  let file = {};
  try { file = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8')); } catch {}
  const cfg = { ...DEFAULTS, ...file, character: { ...DEFAULTS.character, ...(file.character || {}) } };
  if (process.env.LINHX_THU_KY_PORT) cfg.port = Number(process.env.LINHX_THU_KY_PORT);
  if (process.env.LINHX_THU_KY_ROOTS) cfg.roots = process.env.LINHX_THU_KY_ROOTS.split(path.delimiter).filter(Boolean);
  if (process.env.LINHX_CLAUDE_BIN) cfg.claudeCommand = process.env.LINHX_CLAUDE_BIN;
  if (process.env.GEMINI_WS_URL) cfg.geminiWsUrl = process.env.GEMINI_WS_URL;
  if (process.env.LINHX_CHAR_CONFIG) cfg.character.config = process.env.LINHX_CHAR_CONFIG;
  if (process.env.LINHX_CHAR_VIDEOS) cfg.character.videoDir = process.env.LINHX_CHAR_VIDEOS;
  const env = readEnvFile(cfg.envFile);
  cfg.geminiApiKey = process.env.GEMINI_API_KEY || env.GEMINI_API_KEY || env.GEMINI_KEY_01 || '';
  if (!file.liveModel && env.GEMINI_LIVE_MODEL) cfg.liveModel = env.GEMINI_LIVE_MODEL;
  return cfg;
}

// Đọc cấu hình nhân vật Live Character; suy ra thư mục clip nếu chưa khai báo.
function loadCharacter(cfg) {
  const c = cfg.character || {};
  if (!c.config) return null;
  let ch;
  try { ch = JSON.parse(fs.readFileSync(c.config, 'utf8')); } catch { return null; }
  const vm = ch.videoMatrix;
  if (!vm || !vm.clips) return null;
  let dir = c.videoDir;
  if (!dir && /^\/assets\//.test(vm.basePath || '')) {
    dir = path.join(path.dirname(c.config), '..', 'public', vm.basePath);
  }
  return {
    id: ch.id, name: ch.name, voice: (ch.ai && ch.ai.voice) || cfg.voice,
    assetType: 'video_matrix', videoDir: dir,
    videoMatrix: { ...vm, basePath: '/clips/' },
  };
}

module.exports = { load, loadCharacter, HOME_DIR, CONFIG_FILE, DEFAULTS };
