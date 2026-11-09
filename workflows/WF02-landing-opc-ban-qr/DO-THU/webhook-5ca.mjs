// Máy đo A (webhook 5 ca) — bản thử tự viết, theo định dạng chữ ký trong tài liệu SePay.
// Chạy: node webhook-5ca.mjs . Không mạng, không gói ngoài.
import crypto from 'node:crypto';
const SECRET = 'test-secret';
const orders = { 'DH100': { amount: 199000, delivered: 0 } };
const seen = new Set();
const sign = (ts, body) => 'sha256=' + crypto.createHmac('sha256', SECRET).update(`${ts}.${body}`).digest('hex');
function handle({ sig, ts, body }, now) {
  if (Math.abs(now / 1000 - ts) > 300) return 401;
  const want = Buffer.from(sign(ts, body)), got = Buffer.from(sig || '');
  if (want.length !== got.length || !crypto.timingSafeEqual(want, got)) return 401;
  const e = JSON.parse(body);
  if (seen.has(e.id)) return 200;
  seen.add(e.id);
  const o = orders[e.code];
  if (o && e.transferAmount >= o.amount) o.delivered++;
  return 200;
}
const now = Date.now(), ts = Math.floor(now / 1000);
const mk = (id, amt, t = ts, bad = false) => { const body = JSON.stringify({ id, code: 'DH100', transferAmount: amt });
  return { sig: bad ? 'sha256=00' : sign(t, body), ts: t, body }; };
const kq = [];
const t = (ten, ok) => kq.push([ten, ok]);
t('chữ ký sai bị từ chối (401)', handle(mk(1, 199000, ts, true), now) === 401 && orders.DH100.delivered === 0);
t('lệch giờ > 5 phút bị từ chối (401)', handle(mk(2, 199000, ts - 400), now) === 401 && orders.DH100.delivered === 0);
t('trả thiếu: trả 200, không giao', handle(mk(3, 100000), now) === 200 && orders.DH100.delivered === 0);
t('trả thừa: giao', handle(mk(4, 250000), now) === 200 && orders.DH100.delivered === 1);
const r5 = handle(mk(4, 250000), now);
t('gửi lại cùng id: trả 200, chỉ giao 1 lần', r5 === 200 && orders.DH100.delivered === 1);
kq.forEach(([a, b]) => console.log(b ? 'QUA ' : 'TRƯỢT', a));
console.log(`${kq.filter(x => x[1]).length}/${kq.length}`);
