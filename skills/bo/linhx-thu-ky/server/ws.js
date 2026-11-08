// WebSocket phía server tối giản (RFC 6455), không thư viện ngoài.
// Chỉ cần cho trình duyệt cục bộ: khung text, ping/pong, close. Khung từ client luôn có mask.

const crypto = require('crypto');
const { EventEmitter } = require('events');

const GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11';
const MAX_MSG = 2 * 1024 * 1024;

class Conn extends EventEmitter {
  constructor(socket) {
    super();
    this.socket = socket;
    this.buf = Buffer.alloc(0);
    this.parts = [];
    this.open = true;
    socket.on('data', (d) => this.onData(d));
    socket.on('close', () => this.finish());
    socket.on('error', () => this.finish());
  }

  finish() {
    if (!this.open) return;
    this.open = false;
    this.emit('close');
  }

  onData(d) {
    this.buf = Buffer.concat([this.buf, d]);
    while (this.open) {
      const f = this.readFrame();
      if (!f) return;
      this.onFrame(f);
    }
  }

  readFrame() {
    const b = this.buf;
    if (b.length < 2) return null;
    const fin = (b[0] & 0x80) !== 0;
    const op = b[0] & 0x0f;
    const masked = (b[1] & 0x80) !== 0;
    let len = b[1] & 0x7f;
    let off = 2;
    if (len === 126) { if (b.length < 4) return null; len = b.readUInt16BE(2); off = 4; }
    else if (len === 127) { if (b.length < 10) return null; len = Number(b.readBigUInt64BE(2)); off = 10; }
    if (len > MAX_MSG) { this.close(1009); return null; }
    const maskLen = masked ? 4 : 0;
    if (b.length < off + maskLen + len) return null;
    let data = b.subarray(off + maskLen, off + maskLen + len);
    if (masked) {
      const m = b.subarray(off, off + 4);
      data = Buffer.from(data);
      for (let i = 0; i < data.length; i++) data[i] ^= m[i & 3];
    }
    this.buf = b.subarray(off + maskLen + len);
    return { fin, op, data };
  }

  onFrame({ fin, op, data }) {
    if (op === 0x8) { this.close(1000); return; }
    if (op === 0x9) { this.writeFrame(0xA, data); return; }
    if (op === 0xA) return;
    if (op === 0x1 || op === 0x2 || op === 0x0) {
      this.parts.push(data);
      if (!fin) return;
      const msg = Buffer.concat(this.parts);
      this.parts = [];
      this.emit('message', msg.toString('utf8'));
    }
  }

  writeFrame(op, payload) {
    if (!this.open) return;
    const len = payload.length;
    let head;
    if (len < 126) head = Buffer.from([0x80 | op, len]);
    else if (len < 65536) { head = Buffer.alloc(4); head[0] = 0x80 | op; head[1] = 126; head.writeUInt16BE(len, 2); }
    else { head = Buffer.alloc(10); head[0] = 0x80 | op; head[1] = 127; head.writeBigUInt64BE(BigInt(len), 2); }
    this.socket.write(Buffer.concat([head, payload]));
  }

  send(text) { this.writeFrame(0x1, Buffer.from(String(text), 'utf8')); }

  close(code = 1000) {
    if (!this.open) return;
    const p = Buffer.alloc(2); p.writeUInt16BE(code, 0);
    try { this.writeFrame(0x8, p); this.socket.end(); } catch {}
    this.finish();
  }
}

// Hoàn tất bắt tay nâng cấp; trả về Conn hoặc null nếu yêu cầu không hợp lệ.
function accept(req, socket) {
  const key = req.headers['sec-websocket-key'];
  if (!key || String(req.headers.upgrade || '').toLowerCase() !== 'websocket') {
    socket.end('HTTP/1.1 400 Bad Request\r\n\r\n');
    return null;
  }
  const acceptKey = crypto.createHash('sha1').update(key + GUID).digest('base64');
  socket.write('HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n' +
    `Sec-WebSocket-Accept: ${acceptKey}\r\n\r\n`);
  socket.setNoDelay(true);
  return new Conn(socket);
}

module.exports = { accept };
