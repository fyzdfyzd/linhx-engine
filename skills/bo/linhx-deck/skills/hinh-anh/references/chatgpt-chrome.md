# ChatGPT Plus qua Claude in Chrome: các bước đã chạy được (13/10/2026, 4 deck thử)

Dùng `javascript_tool` trên tab ChatGPT của deck. Mỗi deck **một chat riêng**; ghi link chat vào `11-goi-anh/nhat-ky.json` (`chat_url`).

## 1. Nạp hàm trợ giúp (một lần mỗi tab, chạy lại sau khi tải lại trang)

```js
window.__busy = () => [...document.querySelectorAll('button')].some(b => /stop/i.test(b.getAttribute('aria-label') || ''));
window.__soAnh = () => [...document.querySelectorAll('main img')].filter(i => i.alt.startsWith('Generated image') && i.naturalWidth > 500).length;
window.__gui = async (t) => {               // chèn chữ vào ô chat rồi bấm gửi (gõ phím ở tab nền hay rơi chữ)
  const el = document.querySelector('.ProseMirror[contenteditable="true"]');
  el.focus(); document.execCommand('insertText', false, t);
  await new Promise(r => setTimeout(r, 1000));
  const b = document.querySelector('[data-testid="send-button"]') || [...document.querySelectorAll('button')].find(x => /send/i.test(x.getAttribute('aria-label') || ''));
  if (!b) return 'không thấy nút gửi'; b.click(); return 'đã gửi';
};
window.__dl = async (ten) => {              // tải ảnh vừa tạo về Downloads
  const imgs = [...document.querySelectorAll('main img')].filter(i => i.alt.startsWith('Generated image') && i.naturalWidth > 500);
  const im = imgs[imgs.length - 1]; const b = await (await fetch(im.src)).blob();
  const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = ten; document.body.appendChild(a); a.click(); a.remove();
  return [imgs.length, b.size, im.naturalWidth, im.naturalHeight];
};
```

## 2. Mỗi ảnh

1. `find` "input type=file Attach photos" → `file_upload` đúng thứ tự: (ảnh cần sửa nếu là vòng sửa), ảnh neo, 1–2 moodboard.
2. Chờ 5 giây cho ảnh tải lên (`await new Promise(r => setTimeout(r, 5000))`), rồi `await __gui("<prompt một dòng>")`.
3. Chờ: gọi lặp `const t0=Date.now(); while (Date.now()-t0 < 30000 && __busy()) await new Promise(r=>setTimeout(r,3000)); __busy()` (mỗi lần gọi ≤ 40 giây, công cụ cắt ở 45 giây). Một ảnh thường 60–120 giây. **Đừng tải khi `__busy()` còn true**: ảnh đang hiện là bản xem trước.
4. Hết bận: chờ thêm 2 giây, `await __dl('<deck>-<tep>.png')`, kiểm cỡ (2:3 → 1024×1536, 16:9 → 1672×941).
5. Ngay sau đó (trước khi tải ảnh khác): `deck.py nhan-anh <dir> --vao anh --ten <tep> --ref <đúng các tệp đã đính kèm> --phut 3`. `nhan-anh` lấy tệp mới nhất trong Downloads, nên **tải và nhận từng ảnh một** dù chạy nhiều chat song song.

## 3. Lỗi đã gặp

| Hiện tượng | Cách xử lý |
|---|---|
| Gõ bằng `computer type` không vào ô chat (tab nền) | dùng `__gui` (execCommand insertText) |
| Ref của `find` hết hạn sau khi trang đổi | gọi `find` lại ngay trước `file_upload` |
| Gõ ngay sau khi đính kèm, chữ mất | chờ 3–5 giây cho ảnh tải lên |
| "Edit the previous image" sửa nhầm ảnh khác trong chat dài | đính kèm ảnh cần sửa đầu tiên, prompt nói "Edit the FIRST attached image" (`sua-anh` đã làm sẵn) |
| Vật thể đâm xuyên nhau (cổng xuyên bậc) | khối cấm có câu "nothing pierces or intersects"; vẫn soi kỹ H8 |
| Vật chính giống logo có thật (khối bát diện giống logo tiền mã hoá) | chấm H7 trượt, sửa: đổi hình khối |
| `javascript_tool` báo timeout 45 giây khi trang đang tạo ảnh | gọi lại; không tải lúc đó |
