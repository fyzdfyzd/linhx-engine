"""Sinh PA A, PA C (màn đầu khác) từ index.html để chụp so sánh. Chạy: python3 _phuong-an-bo/dung-pa.py"""
import re, pathlib
G = pathlib.Path(__file__).parent
idx = (G.parent / "public/index.html").read_text(encoding="utf-8")
PA = {
"a": ("""<style>
.hero-a{background:var(--kem);padding:72px 0 80px;position:relative;overflow:hidden}
.hero-a .hero-grid{grid-template-columns:1.1fr .9fr;align-items:center}
.hero-a h1{color:var(--nau);max-width:15ch}
.hero-a .sub{color:var(--nau-xam)}
.hero-a .btn-sang{color:var(--nau);border-color:var(--nau)}
.hero-a .facts{border-top-color:var(--xam-be)}.hero-a .facts dt{color:var(--ho-phach)}.hero-a .facts dd{color:var(--nau)}
.a-hinh{position:relative;width:440px;height:440px;justify-self:end}
.a-hinh .xoan{position:absolute;inset:-70px;width:580px;height:580px;max-width:none}
.a-hinh .tron{position:absolute;inset:30px;border-radius:50%;border:10px solid var(--cam);background:url(/_pa/anh-tap-huan-vuong.jpg) center/cover}
.a-hinh p{position:absolute;left:0;right:0;bottom:-44px;text-align:center;font-size:14px;color:var(--nau-xam)}
@media (max-width:980px){.hero-a .hero-grid{grid-template-columns:1fr}.hero-a{padding:40px 0 90px}.a-hinh{justify-self:center;width:300px;height:300px}.a-hinh .xoan{inset:-50px;width:400px;height:400px}.a-hinh .tron{inset:20px}}
</style>
<section class="hero-a"><div class="wrap hero-grid"><div class="hero-copy">
<h1>Truyền thông và AI cho dự án phát triển</h1>
<p class="sub">TUVA đồng hành cùng NGO, cơ quan UN và nhà tài trợ: dùng AI an toàn trong tổ chức, kể chuyện dự án tới đúng người, viết sẵn hạng mục cho đề xuất tài trợ.</p>
<div class="cta-row"><a class="btn btn-main" href="#brief">Trao đổi một dự án</a><a class="btn btn-sang" href="#bo-quy-tac">Tải bộ quy tắc AI</a></div>
<dl class="facts"><div><dt>An toàn dữ liệu</dt><dd>Bộ quy tắc AI cho tổ chức</dd></div><div><dt>Đề xuất tài trợ</dt><dd>Concept note, ngân sách, logframe</dd></div><div><dt>Lĩnh vực</dt><dd>Bình đẳng giới, di sản, y tế</dd></div></dl>
</div><div class="a-hinh"><img class="xoan" src="/img/xoan-cam.svg" alt=""><div class="tron" role="img" aria-label="Một buổi tập huấn truyền thông do TUVA tổ chức"></div><p>Ảnh tập huấn của TUVA</p></div></div></section>"""),
"c": ("""<style>
.hero-c{background:var(--be) url(/img/song-xoan-cam.svg) left bottom/110px repeat-x;padding:64px 0 150px}
.hero-c .hero-grid{grid-template-columns:1fr 1fr;align-items:start}
.hero-c h1{color:var(--nau);max-width:17ch}
.hero-c .sub{color:var(--nau-xam)}
.hero-c .btn-sang{color:var(--nau);border-color:var(--nau)}
.ho-so{background:var(--trang);padding:0 0 18px;border-top:8px solid var(--nau)}
.ho-so .tab{display:flex;border-bottom:2px solid var(--be)}
.ho-so .tab span{flex:1;padding:14px 10px;text-align:center;font:700 14px "MS";text-transform:uppercase;letter-spacing:.05em;color:var(--nau-xam)}
.ho-so .tab span.on{color:var(--nau);box-shadow:inset 0 -4px 0 var(--cam)}
.ho-so table{width:100%;border-collapse:collapse;font-size:15px}
.ho-so th,.ho-so td{text-align:left;padding:10px 18px;border-bottom:1px solid var(--be);vertical-align:top}
.ho-so th{font:700 13px "MS";text-transform:uppercase;color:var(--nau-xam)}
.ho-so tr.tv td{background:var(--kem);font-weight:700}.ho-so tr.tv td:first-child{box-shadow:inset 6px 0 0 var(--cam)}
.ho-so .mh{font-size:14px;color:var(--nau-xam);padding:12px 18px 0}
@media (max-width:980px){.hero-c .hero-grid{grid-template-columns:1fr}.hero-c{padding:40px 0 130px}.ho-so th,.ho-so td{padding:8px 10px}.ho-so .tab span{font-size:12px;padding:12px 4px}}
</style>
<section class="hero-c"><div class="wrap hero-grid"><div class="hero-copy">
<h1>Đưa truyền thông và AI vào đề xuất tài trợ của bạn</h1>
<p class="sub">TUVA viết hợp phần truyền thông và năng lực AI cùng NGO và cán bộ chương trình, từ concept note tới ngân sách và logframe, rồi làm tới khi dự án kết thúc.</p>
<div class="cta-row"><a class="btn btn-main" href="#brief">Gửi hạn nộp của bạn</a><a class="btn btn-sang" href="#bo-quy-tac">Tải bộ quy tắc AI</a></div>
</div><div><div class="ho-so" aria-label="Minh hoạ một logframe có hợp phần TUVA"><div class="tab"><span>Concept note</span><span>Ngân sách</span><span class="on">Logframe</span></div>
<table><tr><th>Đầu ra</th><th>Chỉ số</th></tr><tr><td>1. Năng lực chuyên môn của đối tác</td><td>Số khoá tập huấn</td></tr><tr class="tv"><td>2. Đội ngũ dùng AI an toàn theo bộ quy tắc</td><td>Tỉ lệ nhân viên làm theo quy tắc</td></tr><tr class="tv"><td>3. Thông điệp dự án tới đúng nhóm công chúng</td><td>Lượt tiếp cận, thảo luận đo được</td></tr><tr><td>4. Quản lý dự án</td><td>Báo cáo đúng hạn</td></tr></table>
<p class="mh">Minh hoạ. Dòng tô cam là phần TUVA viết cùng bạn.</p></div></div></div></section>"""),
}
for k, h in PA.items():
    s = re.sub(r'<section class="hero">.*?</section>', lambda m: h, idx, count=1, flags=re.S)
    (G / f"pa-{k}.html").write_text(s, encoding="utf-8")
print("ok")
