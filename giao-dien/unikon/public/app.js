// Unikon: ba form lead (brief pitch, gọi lại, tải bộ kiểm) gửi JSON về /api/brief, giữ nguồn (?kenh=, utm) theo phiên.
var UK = { cfg: {} };
(function () {
  var q = new URLSearchParams(location.search), nguon = {};
  ["kenh", "ref", "utm_source", "utm_medium", "utm_campaign", "utm_content"].forEach(function (k) { if (q.get(k)) nguon[k] = q.get(k).slice(0, 80); });
  try {
    if (Object.keys(nguon).length) sessionStorage.setItem("uk_nguon", JSON.stringify(nguon));
    else nguon = JSON.parse(sessionStorage.getItem("uk_nguon") || "{}");
  } catch (e) {}
  UK.nguon = nguon;
})();

// Đường lùi khi gửi lỗi: Zalo nếu đã có trong cau-hinh.json, chưa có thì mời để lại số ở form gọi lại.
UK.duongLui = function () {
  return UK.cfg.zalo ? "Bạn thử lại, hoặc nhắn Zalo " + UK.cfg.zalo + "." : "Bạn thử lại sau ít phút giúp chúng tôi.";
};
UK.gui = function (data) {
  data.nguon = UK.nguon; data.trang = location.pathname;
  return fetch("/api/brief", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
    .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, j: j }; }); })
    .then(function (k) { if (!k.ok) throw new Error(k.j.loi || "Gửi chưa được"); return k.j; });
};
var SDT = /^[0-9+().\s-]{8,20}$/, EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Form brief pitch
(function () {
  var form = document.getElementById("form-brief");
  if (!form) return;
  var msg = form.querySelector(".form-msg"), hint = document.getElementById("hint-lienhe"), nut = form.querySelector('button[type="submit"]');
  function bao(t, loai) { msg.textContent = t; msg.className = "form-msg " + (loai || ""); }
  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var f = form.elements, loi = [];
    [f.ho_ten, f.cong_ty].forEach(function (el) { var sai = !el.value.trim(); el.setAttribute("aria-invalid", sai ? "true" : "false"); if (sai) loi.push(el); });
    var dt = f.dien_thoai.value.trim(), em = f.email.value.trim();
    var dtSai = dt && !SDT.test(dt), emSai = em && !EMAIL.test(em), thieu = !dt && !em;
    f.dien_thoai.setAttribute("aria-invalid", dtSai || thieu ? "true" : "false");
    f.email.setAttribute("aria-invalid", emSai || thieu ? "true" : "false");
    if (hint) {
      hint.classList.toggle("loi", thieu || dtSai || emSai);
      hint.textContent = dtSai ? "Số điện thoại chưa đúng." : emSai ? "Email chưa đúng." : "Cần ít nhất một trong hai: điện thoại hoặc email.";
    }
    if (thieu || dtSai || emSai) loi.push(dtSai || thieu ? f.dien_thoai : f.email);
    if (!f.dong_y.checked) loi.push(f.dong_y);
    if (loi.length) { bao(!f.dong_y.checked && loi.length === 1 ? "Bạn cần tick ô đồng ý để chúng tôi liên hệ." : "Bạn kiểm lại các ô được đánh dấu nhé.", "loi"); loi[0].focus(); return; }
    var data = {
      loai: "brief", ho_ten: f.ho_ten.value.trim(), cong_ty: f.cong_ty.value.trim(), dien_thoai: dt, email: em,
      vai_tro: f.vai_tro ? f.vai_tro.value : "", han_pitch: f.han_pitch ? f.han_pitch.value : "",
      khach_hang: f.khach_hang ? f.khach_hang.value.trim() : "", an_ten_khach: !!(f.an_ten_khach && f.an_ten_khach.checked),
      loai_asset: Array.prototype.filter.call(form.querySelectorAll('input[name="loai_asset"]'), function (x) { return x.checked; }).map(function (x) { return x.value; }),
      ngan_sach: f.ngan_sach ? f.ngan_sach.value : "", brief: f.brief ? f.brief.value.trim() : "", goi: f.goi ? f.goi.value : "",
      dong_y: true, website: f.website.value
    };
    nut.disabled = true; nut.textContent = "Đang gửi…"; bao("");
    UK.gui(data).then(function (j) {
      form.reset();
      bao("Đã nhận brief của bạn" + (j.ma ? " (mã " + j.ma + ")" : "") + ". Chúng tôi sẽ liên hệ lại sớm.", "ok");
      nut.textContent = "Gửi thêm brief khác";
      if (!form.hasAttribute("data-o-lai")) setTimeout(function () { location.href = "/cam-on/" + (j.ma ? "?ma=" + encodeURIComponent(j.ma) : ""); }, 900);
    }).catch(function (e) { bao(e.message + ". " + UK.duongLui(), "loi"); nut.textContent = "Gửi brief pitch"; })
      .finally(function () { nut.disabled = false; });
  });
})();

// Form gọi lại: tên + số + đồng ý, loai = goi-lai.
(function () {
  var f = document.getElementById("form-goi-lai");
  if (!f) return;
  var msg = f.querySelector(".form-msg"), nut = f.querySelector("button");
  f.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var ten = f.ho_ten.value.trim(), dt = f.dien_thoai.value.trim(), loi = null, dtSai = !SDT.test(dt);
    f.ho_ten.setAttribute("aria-invalid", ten ? "false" : "true");
    f.dien_thoai.setAttribute("aria-invalid", dtSai ? "true" : "false");
    if (!ten) loi = [f.ho_ten, "Bạn điền họ tên nhé."];
    else if (dtSai) loi = [f.dien_thoai, "Số điện thoại chưa đúng."];
    else if (!f.dong_y.checked) loi = [f.dong_y, "Bạn cần tick ô đồng ý để chúng tôi gọi lại."];
    if (loi) { msg.textContent = loi[1]; msg.className = "form-msg loi"; loi[0].focus(); return; }
    nut.disabled = true; nut.textContent = "Đang gửi…";
    UK.gui({ loai: "goi-lai", ho_ten: ten, dien_thoai: dt, dong_y: true, website: f.website.value }).then(function (j) {
      f.reset(); msg.className = "form-msg ok";
      msg.textContent = "Đã nhận" + (j.ma ? " (mã " + j.ma + ")" : "") + ". Chúng tôi gọi lại trong giờ làm việc.";
      nut.textContent = "Đã gửi";
    }).catch(function (e) { msg.className = "form-msg loi"; msg.textContent = e.message + ". " + UK.duongLui(); nut.textContent = "Gọi lại cho tôi"; })
      .finally(function () { nut.disabled = false; });
  });
})();

// Form tải Bộ kiểm an toàn thương hiệu: đổi email, loai = tai-bo-kiem. PDF chưa có nên chỉ ghi danh sách chờ.
(function () {
  var f = document.getElementById("form-bo-kiem");
  if (!f) return;
  var msg = f.querySelector(".form-msg"), nut = f.querySelector("button");
  f.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var ten = f.ho_ten.value.trim(), em = f.email.value.trim(), loi = null, emSai = !EMAIL.test(em);
    f.ho_ten.setAttribute("aria-invalid", ten ? "false" : "true");
    f.email.setAttribute("aria-invalid", emSai ? "true" : "false");
    if (!ten) loi = [f.ho_ten, "Bạn điền họ tên nhé."];
    else if (emSai) loi = [f.email, "Email chưa đúng."];
    else if (!f.dong_y.checked) loi = [f.dong_y, "Bạn cần tick ô đồng ý để chúng tôi gửi email."];
    if (loi) { msg.textContent = loi[1]; msg.className = "form-msg loi"; loi[0].focus(); return; }
    nut.disabled = true; nut.textContent = "Đang gửi…";
    UK.gui({ loai: "tai-bo-kiem", ho_ten: ten, email: em, cong_ty: f.cong_ty ? f.cong_ty.value.trim() : "", dong_y: true, website: f.website.value }).then(function (j) {
      f.reset(); msg.className = "form-msg ok";
      msg.textContent = "Đã ghi email của bạn" + (j.ma ? " (mã " + j.ma + ")" : "") + ".";
      setTimeout(function () { location.href = "/cam-on/?loai=bo-kiem" + (j.ma ? "&ma=" + encodeURIComponent(j.ma) : ""); }, 900);
    }).catch(function (e) { msg.className = "form-msg loi"; msg.textContent = e.message + ". " + UK.duongLui(); nut.textContent = "Nhận bộ kiểm qua email"; })
      .finally(function () { nut.disabled = false; });
  });
})();

// Ba câu gợi ý cách bắt đầu, điền sẵn form brief.
(function () {
  var f = document.getElementById("tinh-goi");
  if (!f) return;
  var kq = f.querySelector(".tinh-kq");
  var ASSET = { anh: "anh", video: "video", "nhan-vat": "nhan-vat", "chua-ro": "chua-ro" };
  function goiY() {
    var han = f.han.value, nhip = f.nhip.value;
    if (nhip === "deu") return { goi: "brand-kit", ten: "Brand kit hằng tháng", ly: "nhãn chạy nội dung đều thì giữ một bộ quy tắc hình ảnh sẽ nhanh và đồng bộ hơn" };
    if (han === "khong") return { goi: "job", ten: "sản xuất theo job", ly: "ý tưởng đã chốt, chỉ cần báo giá và lịch sản xuất" };
    if (han === "gap") return { goi: "pitch-48", ten: "pitch mẫu 48 giờ", ly: "hạn sát, bạn gửi brief ngay để chúng tôi báo lại có kịp hay không" };
    return { goi: "pitch-48", ten: "pitch mẫu 48 giờ", ly: "bạn có ba hướng có hình để khách chọn trước ngày pitch" };
  }
  function ve() { var g = goiY(); kq.innerHTML = "Gợi ý: <b>" + g.ten + "</b>, vì " + g.ly + "."; return g; }
  f.addEventListener("change", ve); ve();
  f.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var g = ve(), b = document.getElementById("form-brief");
    if (!b) return;
    b.elements.goi.value = g.goi;
    b.querySelectorAll('input[name="loai_asset"]').forEach(function (x) { x.checked = x.value === ASSET[f.asset.value]; });
    if (!b.elements.brief.value) b.elements.brief.value = "Quan tâm: " + g.ten + ". Hạn pitch: " + f.han.options[f.han.selectedIndex].text + ".";
    document.getElementById("brief").scrollIntoView({ behavior: "smooth" });
    setTimeout(function () { b.elements.ho_ten.focus({ preventScroll: true }); }, 400);
  });
})();

// Nút nổi trên điện thoại: Zalo khi đã có số, chưa có thì dẫn tới form gọi lại. Ẩn khi đang ở vùng form.
(function () {
  var a = document.createElement("a");
  a.className = "noi-goi"; a.href = document.getElementById("form-goi-lai") ? "#form-goi-lai" : "/lien-he/#form-goi-lai";
  a.textContent = "Để lại số, chúng tôi gọi"; a.setAttribute("aria-label", "Để lại số điện thoại, Unikon gọi lại");
  document.body.appendChild(a);
  UK.noi = a;
  // Ẩn khi đang ở màn đầu (đã có nút gửi brief) hoặc ở vùng form.
  var vung = [document.querySelector(".hero"), document.getElementById("brief") || document.getElementById("form-brief") || document.getElementById("form-goi-lai")].filter(Boolean), thay = new Map();
  if (vung.length && "IntersectionObserver" in window) {
    a.classList.add("an");
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { thay.set(e.target, e.isIntersecting); }); var c = false; thay.forEach(function (v) { c = c || v; }); a.classList.toggle("an", c); });
    vung.forEach(function (v) { io.observe(v); });
  }
})();

// Cấu hình (cau-hinh.json): giá, liên hệ, pháp nhân. null thì trang giữ chữ an toàn.
fetch("/cau-hinh.json").then(function (r) { return r.ok ? r.json() : {}; }).then(function (c) {
  UK.cfg = c || {};
  Object.keys(UK.cfg).forEach(function (k) {
    if (k[0] === "_" || UK.cfg[k] == null || UK.cfg[k] === "" || typeof UK.cfg[k] !== "string") return;
    document.querySelectorAll('[data-cfg="' + k + '"]').forEach(function (el) { el.textContent = UK.cfg[k]; el.removeAttribute("data-can-xac-nhan"); });
  });
  if (UK.cfg.zalo && UK.noi) { UK.noi.href = "https://zalo.me/" + String(UK.cfg.zalo).replace(/\D/g, ""); UK.noi.target = "_blank"; UK.noi.rel = "noopener"; UK.noi.textContent = "Nhắn Zalo"; UK.noi.setAttribute("aria-label", "Nhắn Zalo cho Unikon"); }
}).catch(function () {});
