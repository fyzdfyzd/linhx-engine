// Bộ tool của thư ký (học từ adjutant bridge-rpc-tools và happy realtimeClientTools):
// nhiều tool đọc, hai tool giao việc, gọi bằng TÊN dự án, kết quả trả về là một chuỗi văn xuôi
// (mảng lồng nhau từng làm model Live audio lỗi 1011 trong dự án Live Character).

const projects = require('./projects');

const EMOTIONS = ['idle', 'greeting', 'talking', 'excited', 'thinking', 'listening', 'action'];

function declarations(extraPoses = []) {
  const emotions = [...EMOTIONS, ...extraPoses.filter((p) => !EMOTIONS.includes(p))];
  const S = (description) => ({ type: 'STRING', description });
  return [{
    functionDeclarations: [
      { name: 'set_emotion', description: 'Change the character body pose/animation to match what you are saying.',
        parameters: { type: 'OBJECT', properties: { emotion: { type: 'STRING', enum: emotions } }, required: ['emotion'] } },
      { name: 'danh_sach_du_an', description: 'List all of Linh\'s projects (lab folders) by name.',
        parameters: { type: 'OBJECT', properties: {} } },
      { name: 'tinh_hinh_du_an', description: 'Get the status of one project: its overview, the end of its log, and the last Claude Code session there (last question and answer).',
        parameters: { type: 'OBJECT', properties: { du_an: S('Project name as Linh said it, e.g. LAB025') }, required: ['du_an'] } },
      { name: 'agent_dang_chay', description: 'What Claude/Antigravity agents are working right now, and the jobs you have delegated with their numbers and states.',
        parameters: { type: 'OBJECT', properties: {} } },
      { name: 'hoi_claude', description: 'Ask Claude Code inside a project folder a question (read-only, it will not change files). Runs in the background; the answer comes back later as a [BÁO_CÁO] message.',
        parameters: { type: 'OBJECT', properties: { du_an: S('Project name'), cau_hoi: S('The question, in Vietnamese, complete and self-contained') }, required: ['du_an', 'cau_hoi'] } },
      { name: 'giao_viec', description: 'Delegate a task to Claude Code inside a project folder (it may edit files there). Only after Linh clearly asked for it. Runs in the background; the result comes back as a [BÁO_CÁO] message.',
        parameters: { type: 'OBJECT', properties: { du_an: S('Project name'), noi_dung: S('The full instruction, in Vietnamese, self-contained'), tiep_tuc: { type: 'BOOLEAN', description: 'true = continue the last Claude session of that project instead of a new one' } }, required: ['du_an', 'noi_dung'] } },
      { name: 'ket_qua_viec', description: 'Get the state and result text of a delegated job by its number.',
        parameters: { type: 'OBJECT', properties: { so: { type: 'NUMBER', description: 'Job number' } }, required: ['so'] } },
      { name: 'dung_viec', description: 'Stop a running delegated job by its number. Only when Linh asks.',
        parameters: { type: 'OBJECT', properties: { so: { type: 'NUMBER', description: 'Job number' } }, required: ['so'] } },
    ],
  }];
}

function systemText(cfg, name) {
  const when = new Intl.DateTimeFormat('vi-VN', { dateStyle: 'full', timeStyle: 'short', timeZone: 'Asia/Ho_Chi_Minh' }).format(new Date());
  return [
    `Tên: ${name}. Vai trò: thư ký ảo của Linh (chủ LINHX LAB), điều phối các trợ lý Claude Code đang làm ở từng dự án.`,
    'Xưng "em", gọi "anh Linh". Nói tiếng Việt tự nhiên, 1 đến 3 câu mỗi lượt, như thư ký báo cáo sếp.',
    `--- BỐI CẢNH ---\nThời điểm hiện tại: ${when}.`,
    '--- QUY TẮC ---',
    '- Hỏi về dự án nào thì gọi tinh_hinh_du_an trước rồi mới trả lời; không bịa tiến độ.',
    '- Hỏi "ai đang làm gì", "việc nào đang chạy" thì gọi agent_dang_chay.',
    '- Câu hỏi cần đọc code hoặc tài liệu trong dự án thì gọi hoi_claude. Linh bảo làm, sửa, viết, chạy thì gọi giao_viec; nếu chưa rõ dự án hay việc gì thì hỏi lại một câu ngắn.',
    '- Sau khi giao, nói ngắn: đã giao cho Claude ở dự án nào, việc số mấy. Không chờ kết quả.',
    '- Tin bắt đầu bằng "[BÁO_CÁO]" là kết quả việc đã giao: tóm tắt cho anh Linh trong 1 đến 2 câu, nói số việc và dự án, luôn báo kể cả khi lỗi.',
    '- Không đọc mã phiên, đường dẫn dài hay ký hiệu kỹ thuật; gọi dự án bằng tên ngắn (ví dụ "LAB hai mươi lăm").',
    '- Không tự giao việc xoá, đăng, gửi ra ngoài; những việc đó nhắc anh Linh tự làm trong phiên Claude.',
  ].join('\n');
}

function fmtJob(j) {
  const st = { dang_lam: 'đang làm', xong: 'xong', loi: 'lỗi' }[j.trang_thai] || j.trang_thai;
  return `Việc số ${j.id} ở ${j.du_an} (${j.che_do === 'plan' ? 'hỏi' : 'làm'}): ${st}. Nội dung: ${j.noi_dung.slice(0, 160)}`;
}

async function officeAgents(cfg) {
  try {
    const r = await fetch(`${cfg.officeUrl}/api/state`, { signal: AbortSignal.timeout(1500) });
    const s = await r.json();
    return (s.agents || []).map((a) => `${a.name} (${a.source}) ở ${a.project}: ${a.detail || a.state}`);
  } catch { return null; }
}

// Thực thi các tool chạy ở server. set_emotion do trình duyệt xử lý nên không có ở đây.
async function run(name, args, ctx) {
  const { cfg, jobs } = ctx;
  const need = () => {
    const p = projects.find(cfg, args.du_an);
    if (!p) throw new Error(`Không thấy dự án "${args.du_an}". Có: ${projects.list(cfg).map((x) => x.ten).slice(0, 40).join(', ')}`);
    return p;
  };
  switch (name) {
    case 'danh_sach_du_an': {
      const all = projects.list(cfg);
      return all.length ? `Có ${all.length} dự án: ${all.map((p) => p.ten).join(', ')}.` : 'Chưa khai báo thư mục dự án nào (roots trong cấu hình).';
    }
    case 'tinh_hinh_du_an': {
      const s = projects.summary(need());
      const ses = s.phien_claude;
      return [`Dự án ${s.ten}.`, s.tom_tat && `Tổng quan: ${s.tom_tat}`, s.nhat_ky_cuoi && `Nhật ký gần nhất: ${s.nhat_ky_cuoi}`,
        ses ? `Phiên Claude gần nhất lúc ${ses.luc}: Linh hỏi "${ses.cau_hoi_cuoi}"; Claude trả lời "${ses.tra_loi_cuoi}"` : 'Chưa thấy phiên Claude Code nào ở thư mục này trên máy.'].filter(Boolean).join('\n');
    }
    case 'agent_dang_chay': {
      const office = await officeAgents(cfg);
      const js = jobs.list();
      return [office === null ? 'Văn phòng linhx-office chưa bật nên không thấy các phiên Claude mở tay.' : office.length ? `Trong văn phòng: ${office.join('; ')}.` : 'Văn phòng đang trống.',
        js.length ? `Việc em đã giao: ${js.map(fmtJob).join(' | ')}` : 'Em chưa giao việc nào.'].join('\n');
    }
    case 'hoi_claude':
    case 'giao_viec': {
      const p = need();
      const text = name === 'hoi_claude' ? args.cau_hoi : args.noi_dung;
      if (!text || !String(text).trim()) throw new Error('Thiếu nội dung');
      const resume = args.tiep_tuc ? (projects.lastSession(p.thu_muc) || {}).session_id : undefined;
      const r = jobs.start(p, text, { che_do: name === 'hoi_claude' ? 'plan' : undefined, resume });
      if (!r.ok) throw new Error(r.error);
      return `Đã giao: việc số ${r.job.id} cho Claude ở ${p.ten}${resume ? ' (tiếp phiên cũ)' : ''}. Kết quả sẽ báo lại sau.`;
    }
    case 'ket_qua_viec': {
      const j = jobs.get(args.so);
      if (!j) return `Không có việc số ${args.so}.`;
      return `${fmtJob(j)}${j.ket_qua ? `\nKết quả: ${j.ket_qua.slice(0, 1500)}` : ''}`;
    }
    case 'dung_viec': {
      const r = jobs.stop(args.so);
      return r.ok ? `Đã dừng việc số ${args.so}.` : r.error;
    }
    default:
      throw new Error('unknown tool');
  }
}

module.exports = { declarations, systemText, run, fmtJob, EMOTIONS };
