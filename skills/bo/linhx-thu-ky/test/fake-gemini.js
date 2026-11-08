#!/usr/bin/env node
// Gemini Live giả để thử luồng không cần khoá thật: nhận setup, gọi tool theo câu chữ, trả lời bằng phụ đề + 0,3 s âm thanh.
// Chạy: node test/fake-gemini.js 4999  rồi đặt GEMINI_WS_URL=ws://127.0.0.1:4999 và GEMINI_API_KEY=gia

const http = require('http');
const ws = require('../server/ws');

const port = Number(process.argv[2] || 4999);
const silence = Buffer.alloc(24000 * 2 * 0.3).toString('base64'); // 0,3 s PCM16 24 kHz
const log = [];

function say(c, text) {
  c.send(JSON.stringify({ serverContent: { outputTranscription: { text } } }));
  c.send(JSON.stringify({ serverContent: { modelTurn: { parts: [{ inlineData: { mimeType: 'audio/pcm;rate=24000', data: silence } }] } } }));
  c.send(JSON.stringify({ serverContent: { turnComplete: true } }));
}

let n = 0;
const server = http.createServer((req, res) => { res.end(JSON.stringify(log)); });
server.on('upgrade', (req, socket) => {
  const c = ws.accept(req, socket);
  c.on('message', (raw) => {
    const m = JSON.parse(raw);
    log.push(m.setup ? { setup: { tools: m.setup.tools[0].functionDeclarations.map((f) => f.name), voice: m.setup.generationConfig.speechConfig.voiceConfig.prebuiltVoiceConfig.voiceName } } : m);
    if (m.setup) return c.send(JSON.stringify({ setupComplete: {} }));
    if (m.toolResponse) {
      const r = m.toolResponse.functionResponses[0];
      return say(c, `Dạ, ${(r.response.result.text || r.response.result.error || '').slice(0, 140)}`);
    }
    const text = m.clientContent && m.clientContent.turns[0].parts[0].text;
    if (!text) return;
    if (text.startsWith('[BÁO_CÁO]')) return say(c, `Báo cáo anh Linh: ${text.slice(10, 120)}`);
    const call = (name, args) => c.send(JSON.stringify({ toolCall: { functionCalls: [{ id: `c${++n}`, name, args }] } }));
    if (/tình hình/i.test(text)) return call('tinh_hinh_du_an', { du_an: text.replace(/.*tình hình\s*/i, '') });
    if (/^giao/i.test(text)) return call('giao_viec', { du_an: 'lab 25', noi_dung: text.replace(/^giao[^:]*:\s*/i, '') });
    if (/ai đang/i.test(text)) return call('agent_dang_chay', {});
    if (/vẫy/i.test(text)) return call('set_emotion', { emotion: 'wave' });
    say(c, 'Chào anh Linh, em nghe đây ạ.');
  });
});
server.listen(port, '127.0.0.1', () => console.log(`fake gemini ${port}`));
