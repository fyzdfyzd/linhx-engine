# Chọn máy dựng

Cả ba đều: viết trang → trình duyệt headless chụp từng khung → ffmpeg ghép MP4. Đều đã chạy thử 21/10/2026 trên Linux (bản 4 giây, chữ Việt có dấu đúng): xem `LAB059-DUNG-PHIM-CODE/demo/`.

| | Lemo-Opuscar | HyperFrames | Remotion |
|---|---|---|---|
| Viết bằng | canvas 2D / WebGL (three.js), hàm `window.render(t)` | HTML + CSS + GSAP, thời gian bằng `data-*` | React (TSX), `useCurrentFrame()` |
| Mạnh nhất | chất liệu tranh, giấy, mực, 3D, hiệu ứng từng pixel; 51 style có luật sẵn | chữ chuyển động, bố cục, bài giảng, slide thành video, phụ đề, chụp website | một khuôn ra nhiều bản từ dữ liệu (props, CSV), thành phần tái dùng, Studio xem trực tiếp |
| Yếu | chữ và bố cục phải tự vẽ trên canvas | chất liệu tranh khó, 3D phải qua adapter | nặng cài đặt; tranh vẽ cũng phải tự viết |
| Giấy phép | MIT (demo CC BY 4.0) | Apache-2.0 | miễn phí cho cá nhân và công ty ≤ 3 người; công ty lớn hơn phải mua license |
| Kiểm có sẵn | `readcheck.mjs` (thời gian đọc), `sheet.py`, `mux.sh` −14 LUFS | `lint`, `check` (layout, contrast), `snapshot` | `still`, Studio |
| Thử 4 giây 960×540 | 96 khung trong 3 giây | 5,9 giây (beginframe, GPU mềm) | khoảng 20 giây gồm bundle |

Quy tắc chọn:
1. Style trong nhóm vẽ tay, Đông Á, in ấn, hoạt hình, game, 3D → **Lemo**.
2. Style đồ hoạ/chữ (swiss-motion, dark-keynote, dataviz, whiteboard đơn giản) hoặc phim e-learning, giải thích có nhiều chữ → **HyperFrames**, mượn luật hình từ `STYLE.md` của Lemo.
3. Cần 10+ bản cùng khuôn khác số liệu/tên (báo cáo tuần, thẻ khoá học, video cá nhân hoá) → **Remotion** (`--props` mỗi lần render), hoặc HyperFrames variables nếu khuôn đơn giản.
4. Có thể trộn: nền tranh render bằng Lemo ra MP4, đặt vào HyperFrames làm `<video>` rồi chồng chữ.

## Lemo-Opuscar

Cài một lần:
```bash
git clone --depth 1 https://github.com/lemomo-ai/lemo-opuscar ~/lemo-opuscar
cd ~/lemo-opuscar && npm i            # playwright-core, three
# tiếng/nhạc khi cần: sh plugin/skills/lemo-opuscar/scripts/setup.sh deps voice | deps music
```
Linux không tải trình duyệt được thì trỏ `PLAYWRIGHT_CHROME` tới headless_shell có sẵn. Windows: Playwright tự tải.

Trang tối thiểu (thư mục phim, chạy lệnh từ `$LIB`, thư viện dùng URL tuyệt đối `/core/lib.js`):
```html
<canvas id="c"></canvas>
<script type="module">
import {seg, ss, eo, mulberry} from '/core/lib.js';
const W=innerWidth,H=innerHeight,c=document.getElementById('c');c.width=W;c.height=H;const g=c.getContext('2d');
window.DUR = 4;                       // giây
window.render = (t) => { /* vẽ khung ở giây t, tất định, không Math.random */ };
window.TEXTS = (t) => [/* {id,text,x0,y0,x1,y1} mọi chữ đang hiện */];
await document.fonts.load('10px Sans'); window.READY = true;
</script>
```
Lệnh:
```bash
cd "$LIB"
node core/render/still.mjs <phim> 1 2.5 4 --size 960x540        # khung tĩnh
node core/render/video.mjs <phim> --fps 12 --size 960x540 --out <phim>/out/nhap.mp4
node core/render/readcheck.mjs <phim>                            # chữ đủ lâu để đọc
node core/render/video.mjs <phim> --fps 24 --workers 4 --out <phim>/out/hinh.mp4
sh core/render/mux.sh <phim>/out/hinh.mp4 <phim>/am-thanh/giong.wav <phim>/<ten>.mp4 24 2
```
Bẫy: `ctx.textAlign` đặt ở chỗ khác lọt sang chữ sau (đã gặp khi thử: phụ đề bị lệch ra ngoài khung). Đặt lại `textAlign` trước mỗi lần vẽ chữ.

## HyperFrames

Cài vào thư mục phim (không phải thư mục chung): `npm i hyperframes gsap`. Nên cài thêm skill chính hãng: `npx hyperframes skills update` (router `/hyperframes`, `hyperframes-core`, `hyperframes-animation`...).

Khung tối thiểu (`index.html`):
```html
<script src="gsap.min.js"></script>   <!-- chép từ node_modules/gsap/dist, đừng dùng CDN: cloud chặn -->
<div id="root" data-composition-id="main" data-start="0" data-width="1920" data-height="1080" data-duration="4">
  <section id="s1" class="clip" data-start="0" data-duration="2"><h1 id="t1">…</h1></section>
</div>
<script>
const tl = gsap.timeline({paused:true});
tl.fromTo("#t1",{opacity:0,y:40},{opacity:1,y:0,duration:.6},.2);
window.__timelines["main"] = tl;
</script>
```
Lệnh: `npx hyperframes lint`, `npx hyperframes check`, `npx hyperframes snapshot --at 1,3`, `npx hyperframes render -o out/<ten>.mp4`. Giọng: `<audio id="vo" src="am-thanh/giong.wav" data-start="0">` (bắt buộc có `id`).
Bẫy: font tên riêng phải có `@font-face` trỏ file local; không đặt `transform` CSS rồi tween cùng thuộc tính; không tween `visibility` của `.clip`. Phim nhiều cảnh thì tách sub-composition (lint sẽ nhắc).

## Remotion

Cài vào thư mục phim: `npx create-video@latest` (chọn Blank) hoặc `npm i remotion @remotion/cli react react-dom`. Nên cài skill chính hãng: `npx skills add remotion-dev/skills`.

Khung tối thiểu (`src/Root.tsx`, `src/index.ts` gọi `registerRoot(Root)`):
```tsx
const Phim: React.FC<{tieuDe:string}> = ({tieuDe}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const s = spring({frame: f-6, fps});
  return <AbsoluteFill style={{fontFamily:'BVP'}}><div style={{transform:`scale(${s})`}}>{tieuDe}</div></AbsoluteFill>;
};
export const Root = () => <Composition id="Phim" component={Phim} durationInFrames={120} fps={30} width={1920} height={1080} defaultProps={{tieuDe:'…'}}/>;
```
Font local: `staticFile('fonts/BeVietnamPro-600.ttf')` qua `FontFace`, bọc `delayRender/continueRender` để khung đầu không thiếu font.
Lệnh: `npx remotion studio` (xem), `npx remotion still src/index.ts Phim out/f.png --frame=45`, `npx remotion render src/index.ts Phim out/<ten>.mp4 --props='{"tieuDe":"…"}'`. Linux thiếu trình duyệt: `--browser-executable=<headless_shell>`.
Làm loạt: một vòng lặp shell đọc CSV, mỗi dòng một lần `render --props`.
