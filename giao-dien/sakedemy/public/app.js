// Sakédemy: ba form (tư vấn lớp doanh nghiệp, gọi lại, học thử), giữ nguồn ?kenh= + utm theo phiên, cấu hình từ cau-hinh.json.
var CFG = {};
var NGUON = (function () {
  var q = new URLSearchParams(location.search), n = {};
  ["kenh", "ref", "utm_source", "utm_medium", "utm_campaign", "utm_content"].forEach(function (k) { if (q.get(k)) n[k] = q.get(k).slice(0, 80); });
  try {
    if (Object.keys(n).length) sessionStorage.setItem("sk_nguon", JSON.stringify(n));
    else n = JSON.parse(sessionStorage.getItem("sk_nguon") || "{}");
  } catch (e) {}
  return n;
})();
function duongLui() {
  // Khi chưa có liên hệ thật thì chỉ đường lùi bằng form gọi lại.
  if (CFG.zalo) return " Bạn thử lại, hoặc nhắn Zalo " + CFG.zalo + ".";
  if (CFG.email) return " Bạn thử lại, hoặc gửi email tới " + CFG.email + ".";
  return " Bạn thử lại sau ít phút.";
}
function gui(data) {
  data.nguon = NGUON; data.trang = location.pathname;
  return fetch("/api/brief", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
    .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, j: j }; }); })
    .then(function (k) { if (!k.ok) throw new Error(k.j.loi || "Gửi chưa được"); return k.j; });
}
function bao(msg, t, loai) { msg.textContent = t; msg.className = "form-msg " + (loai || ""); }

// Form chính: đăng ký tư vấn lớp doanh nghiệp.
(function () {
  var form = document.getElementById("form-brief");
  if (!form) return;
  var msg = form.querySelector(".form-msg"), hint = document.getElementById("hint-lienhe"), nut = form.querySelector('button[type="submit"]');
  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var f = form.elements, loi = [];
    [f.ho_ten, f.cong_ty].forEach(function (el) { var sai = !el.value.trim(); el.setAttribute("aria-invalid", sai ? "true" : "false"); if (sai) loi.push(el); });
    var dt = f.dien_thoai.value.trim(), em = f.email.value.trim();
    var dtSai = dt && !/^[0-9+().\s-]{8,20}$/.test(dt), emSai = em && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em), thieu = !dt && !em;
    f.dien_thoai.setAttribute("aria-invalid", dtSai || thieu ? "true" : "false");
    f.email.setAttribute("aria-invalid", emSai || thieu ? "true" : "false");
    hint.classList.toggle("loi", thieu || dtSai || emSai);
    hint.textContent = thieu ? "Cần ít nhất một trong hai: điện thoại hoặc email." : dtSai ? "Số điện thoại chưa đúng." : emSai ? "Email chưa đúng." : "Cần ít nhất một trong hai: điện thoại hoặc email.";
    if (thieu || dtSai || emSai) loi.push(dtSai || thieu ? f.dien_thoai : f.email);
    if (!f.dong_y.checked) loi.push(f.dong_y);
    if (loi.length) { bao(msg, !f.dong_y.checked && loi.length === 1 ? "Bạn cần tick ô đồng ý để chúng tôi liên hệ." : "Bạn kiểm lại các ô được đánh dấu nhé.", "loi"); loi[0].focus(); return; }
    var chon = function (n) { return Array.prototype.filter.call(form.querySelectorAll('input[name="' + n + '"]'), function (x) { return x.checked; }).map(function (x) { return x.value; }); };
    var data = {
      loai: "tu-van", ho_ten: f.ho_ten.value.trim(), cong_ty: f.cong_ty.value.trim(), vai_tro: f.vai_tro.value.trim(),
      dien_thoai: dt, email: em, so_hoc_vien: f.so_hoc_vien.value, phong_ban: chon("phong_ban"), hinh_thuc: (chon("hinh_thuc")[0] || ""),
      thoi_gian: f.thoi_gian.value, nhu_cau: f.nhu_cau.value.trim(), goi: f.goi.value, dong_y: true, website: f.website.value
    };
    nut.disabled = true; nut.textContent = "Đang gửi…"; bao(msg, "");
    gui(data).then(function (j) {
      form.reset();
      bao(msg, "Đã nhận đăng ký" + (j.ma ? " (mã " + j.ma + ")" : "") + ". Sakédemy sẽ liên hệ để hẹn buổi trao đổi.", "ok");
      nut.textContent = "Gửi thêm đăng ký khác";
      setTimeout(function () { location.href = "/cam-on/" + (j.ma ? "?ma=" + encodeURIComponent(j.ma) : ""); }, 900);
    }).catch(function (e) { bao(msg, e.message + "." + duongLui(), "loi"); nut.textContent = "Đăng ký tư vấn"; })
      .finally(function () { nut.disabled = false; });
  });
})();

// Form gọi lại: tên + số + đồng ý.
(function () {
  var f = document.getElementById("form-goi-lai");
  if (!f) return;
  var msg = f.querySelector(".form-msg"), nut = f.querySelector("button");
  f.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var ten = f.ho_ten.value.trim(), dt = f.dien_thoai.value.trim(), loi = null, dtSai = !/^[0-9+().\s-]{8,20}$/.test(dt);
    f.ho_ten.setAttribute("aria-invalid", ten ? "false" : "true");
    f.dien_thoai.setAttribute("aria-invalid", dtSai ? "true" : "false");
    if (!ten) loi = [f.ho_ten, "Bạn điền họ tên nhé."];
    else if (dtSai) loi = [f.dien_thoai, "Số điện thoại chưa đúng."];
    else if (!f.dong_y.checked) loi = [f.dong_y, "Bạn cần tick ô đồng ý để chúng tôi gọi lại."];
    if (loi) { bao(msg, loi[1], "loi"); loi[0].focus(); return; }
    nut.disabled = true; nut.textContent = "Đang gửi…";
    gui({ loai: "goi-lai", ho_ten: ten, dien_thoai: dt, dong_y: true, website: f.website.value })
      .then(function (j) { f.reset(); bao(msg, "Đã nhận" + (j.ma ? " (mã " + j.ma + ")" : "") + ". Chúng tôi gọi lại trong giờ làm việc.", "ok"); nut.textContent = "Đã gửi"; })
      .catch(function (e) { bao(msg, e.message + "." + duongLui(), "loi"); nut.textContent = "Gọi lại cho tôi"; })
      .finally(function () { nut.disabled = false; });
  });
})();

// Form học thử: email + đồng ý.
(function () {
  var f = document.getElementById("form-hoc-thu");
  if (!f) return;
  var msg = f.querySelector(".form-msg"), nut = f.querySelector("button");
  f.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var em = f.email.value.trim(), sai = !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em);
    f.email.setAttribute("aria-invalid", sai ? "true" : "false");
    if (sai) { bao(msg, "Email chưa đúng.", "loi"); f.email.focus(); return; }
    if (!f.dong_y.checked) { bao(msg, "Bạn cần tick ô đồng ý để nhận bài học thử.", "loi"); f.dong_y.focus(); return; }
    nut.disabled = true; nut.textContent = "Đang gửi…";
    gui({ loai: "hoc-thu", email: em, dong_y: true, website: f.website.value })
      .then(function (j) {
        f.reset();
        bao(msg, CFG.link_hoc_thu ? "Đã nhận. Đang mở bài học thử…" : "Đã nhận" + (j.ma ? " (mã " + j.ma + ")" : "") + ". Sakédemy gửi đường vào bài học thử qua email của bạn.", "ok");
        nut.textContent = "Đã gửi";
        if (CFG.link_hoc_thu) setTimeout(function () { location.href = CFG.link_hoc_thu; }, 900);
      })
      .catch(function (e) { bao(msg, e.message + "." + duongLui(), "loi"); nut.textContent = "Nhận bài học thử"; })
      .finally(function () { nut.disabled = false; });
  });
})();

// Gợi ý lộ trình: ba câu, điền sẵn form chính.
(function () {
  var f = document.getElementById("tinh-goi");
  if (!f) return;
  var kq = f.querySelector(".tinh-kq");
  var TEN = { marketing: "marketing và truyền thông", "kinh-doanh": "kinh doanh và chăm sóc khách", "van-hanh": "vận hành, hành chính, nhân sự", "lanh-dao": "ban lãnh đạo", "ngan-hang": "chi nhánh ngân hàng", khac: "nhiều phòng ban" };
  function goiY() {
    var p = f.phong.value, m = f.muc.value, s = f.so.value;
    var dau = m === "chua" ? "buổi nền tảng: AI làm được gì, cách giao việc cho AI bằng câu lệnh rõ ràng"
      : m === "le" ? "buổi đưa AI vào ba đầu việc tốn thời gian nhất của " + TEN[p]
      : "buổi chuyên sâu: quy trình nhiều bước và trợ lý AI riêng cho " + TEN[p];
    var chia = (s === "50 đến 100 người" || s === "Trên 100 người") ? " Với " + s.toLowerCase() + ", nên chia lớp theo phòng ban để mỗi lớp thực hành được." : "";
    if (p === "lanh-dao") dau = "buổi cho lãnh đạo: chọn việc giao cho AI trước và đặt luật dùng AI trong công ty";
    return { goi: p + "/" + m, txt: "Gợi ý: bắt đầu bằng <b>" + dau + "</b>, sau đó may tiếp theo kết quả khảo sát đầu vào." + chia };
  }
  function ve() { var g = goiY(); kq.innerHTML = g.txt; return g; }
  f.addEventListener("change", ve); ve();
  f.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var g = ve(), b = document.getElementById("form-brief");
    if (!b) return;
    b.elements.goi.value = g.goi;
    b.elements.so_hoc_vien.value = f.so.value;
    b.querySelectorAll('input[name="phong_ban"]').forEach(function (x) { x.checked = x.value === f.phong.value; });
    if (!b.elements.nhu_cau.value) b.elements.nhu_cau.value = "Phòng ban: " + TEN[f.phong.value] + ". Mức dùng AI hiện tại: " + f.muc.options[f.muc.selectedIndex].text.toLowerCase() + ".";
    document.getElementById("dang-ky").scrollIntoView({ behavior: "smooth" });
    setTimeout(function () { b.elements.ho_ten.focus({ preventScroll: true }); }, 400);
  });
})();

// Cấu hình: điền ở cau-hinh.json, null thì giữ chữ an toàn. Nút Zalo nổi chỉ hiện khi có số thật.
fetch("/cau-hinh.json").then(function (r) { return r.ok ? r.json() : {}; }).then(function (c) {
  CFG = c || {};
  Object.keys(CFG).forEach(function (k) {
    if (k[0] === "_" || CFG[k] == null || CFG[k] === "" || typeof CFG[k] !== "string") return;
    document.querySelectorAll('[data-cfg="' + k + '"]').forEach(function (el) { el.textContent = CFG[k]; el.removeAttribute("data-can-xac-nhan"); });
  });
  if (CFG.link_hoc_thu) document.querySelectorAll("[data-link-hoc-thu]").forEach(function (a) { a.href = CFG.link_hoc_thu; });
  if (CFG.zalo) {
    var a = document.createElement("a");
    a.className = "zalo-noi co"; a.href = "https://zalo.me/" + String(CFG.zalo).replace(/\D/g, ""); a.target = "_blank"; a.rel = "noopener";
    a.textContent = "Nhắn Zalo"; a.setAttribute("aria-label", "Nhắn Zalo cho Sakédemy");
    document.body.appendChild(a);
    var f = document.getElementById("form-brief");
    if (f && "IntersectionObserver" in window) new IntersectionObserver(function (e) { a.classList.toggle("an", e[0].isIntersecting); }).observe(f);
  }
}).catch(function () {});
