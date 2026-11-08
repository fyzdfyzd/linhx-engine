// Chuẩn hoá sự kiện hook của Claude Code và Antigravity CLI (agy) về một dạng chung.
// Kết quả: { agent, parent, source, project, cwd, kind, state, tool, detail, title, failed, ts }
//   kind: 'start' | 'update' | 'end'  (end = agent rời văn phòng)
//   state: idle | thinking | reading | research | writing | running | delegating | waiting | done | error

const path = require('path');

const READ_TOOLS = new Set(['Read', 'Grep', 'Glob', 'LS', 'NotebookRead']);
const WEB_TOOLS = new Set(['WebFetch', 'WebSearch']);
const WRITE_TOOLS = new Set(['Edit', 'Write', 'MultiEdit', 'NotebookEdit']);
const DELEGATE_TOOLS = new Set(['Agent', 'Task']);

function short(s, n = 80) {
  if (s == null) return '';
  s = String(s).replace(/\s+/g, ' ').trim();
  return s.length > n ? s.slice(0, n - 1) + '…' : s;
}

function projectOf(cwd) {
  if (!cwd) return 'khác';
  return path.basename(String(cwd).replace(/[\\/]+$/, '')) || 'khác';
}

function fileName(p) {
  return p ? path.basename(String(p)) : '';
}

// Mô tả ngắn cho một lần gọi tool của Claude
function claudeToolDetail(tool, input = {}) {
  if (tool === 'Grep' || tool === 'Glob') return `Tìm "${short(input.pattern, 40)}"`;
  if (READ_TOOLS.has(tool)) return `Đọc ${fileName(input.file_path || input.notebook_path || input.path)}`.trim();
  if (WRITE_TOOLS.has(tool)) return `Sửa ${fileName(input.file_path || input.notebook_path)}`;
  if (tool === 'Bash') return `Chạy: ${short(input.description || input.command, 60)}`;
  if (tool === 'WebSearch') return `Tìm web: ${short(input.query, 60)}`;
  if (tool === 'WebFetch') return `Đọc web: ${short(input.url, 60)}`;
  if (DELEGATE_TOOLS.has(tool)) return `Giao việc: ${short(input.description || input.prompt, 60)}`;
  if (tool && tool.startsWith('mcp__')) return `Dùng ${tool.split('__').slice(1).join(' · ')}`;
  return tool || '';
}

function claudeToolState(tool) {
  if (READ_TOOLS.has(tool)) return 'reading';
  if (WEB_TOOLS.has(tool)) return 'research';
  if (WRITE_TOOLS.has(tool)) return 'writing';
  if (DELEGATE_TOOLS.has(tool)) return 'delegating';
  if (tool === 'AskUserQuestion' || tool === 'ExitPlanMode') return 'waiting';
  if (tool === 'TodoWrite' || tool === 'EnterPlanMode') return 'thinking';
  return 'running';
}

function fromClaude(p) {
  const ev = p.hook_event_name || '';
  const session = p.session_id || 'claude';
  // Sự kiện bắn từ bên trong subagent mang agent_id riêng
  const sub = p.agent_id ? `${session}:${p.agent_id}` : null;
  const base = {
    source: 'claude',
    agent: sub || session,
    parent: sub ? session : null,
    cwd: p.cwd || '',
    project: projectOf(p.cwd),
    role: sub ? (p.agent_type || 'subagent') : 'Claude',
    ts: Date.now(),
  };
  switch (ev) {
    case 'SessionStart':
      return { ...base, kind: 'start', state: 'idle', detail: 'Vào văn phòng' };
    case 'UserPromptSubmit':
      return { ...base, kind: 'update', state: 'thinking', detail: 'Đang nghĩ', title: short(p.prompt, 60) };
    case 'PreToolUse':
      return { ...base, kind: 'update', state: claudeToolState(p.tool_name), tool: p.tool_name,
        detail: claudeToolDetail(p.tool_name, p.tool_input || {}), file: (p.tool_input || {}).file_path };
    case 'PostToolUse':
      return { ...base, kind: 'update', state: 'thinking', tool: p.tool_name, detail: 'Xem kết quả', ok: true,
        key: `${p.tool_name} ${short((p.tool_input || {}).command || (p.tool_input || {}).file_path || '', 60)}` };
    case 'PostToolUseFailure':
      return { ...base, kind: 'update', state: 'error', tool: p.tool_name, failed: true,
        detail: `Lỗi: ${claudeToolDetail(p.tool_name, p.tool_input || {})}`,
        key: `${p.tool_name} ${short((p.tool_input || {}).command || (p.tool_input || {}).file_path || '', 60)}` };
    case 'PermissionRequest':
      return { ...base, kind: 'update', state: 'waiting', tool: p.tool_name,
        detail: `Xin phép: ${claudeToolDetail(p.tool_name, p.tool_input || {})}` };
    case 'Notification':
      if (/permission|waiting|idle/i.test(`${p.notification_type || ''} ${p.message || ''}`))
        return { ...base, kind: 'update', state: 'waiting', detail: short(p.message || 'Cần bạn', 60) };
      return null;
    case 'SubagentStart':
      return { ...base, agent: `${session}:${p.agent_id || 'sub'}`, parent: session, kind: 'start',
        role: p.agent_type || 'subagent', state: 'thinking', detail: `Nhận việc (${p.agent_type || 'subagent'})` };
    case 'SubagentStop':
      return { ...base, agent: `${session}:${p.agent_id || 'sub'}`, parent: session, kind: 'end',
        role: p.agent_type || 'subagent', state: 'done', detail: 'Xong việc' };
    case 'PreCompact':
      return { ...base, kind: 'update', state: 'thinking', detail: 'Dọn trí nhớ (compact)' };
    case 'Stop':
      return { ...base, kind: 'update', state: 'done', detail: 'Xong lượt, chờ việc mới' };
    case 'SessionEnd':
      return { ...base, kind: 'end', state: 'done', detail: 'Rời văn phòng' };
    default:
      return null;
  }
}

// Antigravity CLI: tên tool khác Claude (view_file, write_to_file, run_command…)
function agyToolState(tool = '') {
  const t = tool.toLowerCase();
  if (/url|web|browser|search_web/.test(t)) return 'research';
  if (/write|replace|edit|create|delete|move/.test(t)) return 'writing';
  if (/run|command|terminal|shell|exec/.test(t)) return 'running';
  if (/view|read|grep|find|list|search|codebase/.test(t)) return 'reading';
  return 'running';
}

function fromAgy(p, eventArg, env = {}) {
  const ev = p.hookEventName || p.hook_event_name || eventArg || '';
  const conv = p.conversationId || (p.transcriptPath ? path.basename(path.dirname(p.transcriptPath)) : 'default');
  const cwd = (p.toolCall && p.toolCall.args && p.toolCall.args.Cwd) ||
    (Array.isArray(p.workspacePaths) && p.workspacePaths[0]) || env.cwd || '';
  // agy được Claude gọi (agy -p trong Bash) thì nhận Claude là người giao việc
  const parent = env.LINHX_OFFICE_PARENT || env.CLAUDE_CODE_SESSION_ID || null;
  const tool = (p.toolCall && (p.toolCall.name || p.toolCall.toolName)) || p.toolName || p.tool_name || '';
  const args = (p.toolCall && p.toolCall.args) || {};
  const base = {
    source: 'agy', agent: `agy:${conv}`, parent, cwd, project: projectOf(cwd), role: 'Antigravity', ts: Date.now(),
  };
  switch (ev) {
    case 'PreInvocation':
      return { ...base, kind: 'start', state: 'thinking', detail: 'Nhận việc', title: short(p.prompt || p.userPrompt || '', 60) || undefined };
    case 'PreToolUse':
    case 'PostToolUse': {
      const err = p.error || (p.toolResult && p.toolResult.error);
      const target = args.AbsolutePath || args.TargetFile || args.CommandLine || args.Query || args.Url || '';
      return { ...base, kind: 'update', state: err ? 'error' : agyToolState(tool), tool, failed: !!err,
        detail: `${tool} ${short(fileName(target) || target, 50)}`.trim(), file: args.TargetFile || args.AbsolutePath,
        key: `${tool} ${short(target, 60)}`, ok: !err };
    }
    case 'PostInvocation':
      return { ...base, kind: 'update', state: 'done', detail: 'Xong lượt' };
    case 'Stop': {
      if (p.fullyIdle === false) return { ...base, kind: 'update', state: 'thinking', detail: 'Làm tiếp' };
      const bad = /error|fail/i.test(p.terminationReason || '');
      return { ...base, kind: 'update', state: bad ? 'error' : 'done', detail: bad ? 'Dừng vì lỗi' : 'Xong việc' };
    }
    default:
      return null;
  }
}

module.exports = { fromClaude, fromAgy, agyToolState, claudeToolState };
