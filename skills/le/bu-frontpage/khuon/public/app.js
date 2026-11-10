// Form gửi brief: kiểm phía khách, gửi JSON về /api/brief, giữ nguồn (utm, ?kenh=).
(function () {
  var form = document.getElementById("form-brief");
  if (!form) return;
  var msg = form.querySelector(".form-msg");
  var hint = document.getElementById("hint-lienhe");
  var nut = form.querySelector('button[type="submit"]');
  var q = new URLSearchParams(location.search);
  var nguon = {};
  ["kenh", "ref", "utm_source", "utm_medium", "utm_campaign", "utm_content"].forEach(function (k) {
    if (q.get(k)) nguon[k] = q.get(k).slice(0, 80);
  });
  try {
    if (Object.keys(nguon).length) sessionStorage.setItem("ifa_nguon", JSON.stringify(nguon));
    else nguon = JSON.parse(sessionStorage.getItem("ifa_nguon") || "{}");
  } catch (e) {}

  function bao(t, loai) { msg.textContent = t; msg.className = "form-msg " + (loai || ""); }

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var f = form.elements;
    var loi = [];
    [f.ho_ten, f.cong_ty].forEach(function (el) {
      var sai = !el.value.trim();
      el.setAttribute("aria-invalid", sai ? "true" : "false");
      if (sai) loi.push(el);
    });
    var dt = f.dien_thoai.value.trim(), em = f.email.value.trim();
    var dtSai = dt && !/^[0-9+().\s-]{8,20}$/.test(dt);
    var emSai = em && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em);
    var thieu = !dt && !em;
    f.dien_thoai.setAttribute("aria-invalid", dtSai || thieu ? "true" : "false");
    f.email.setAttribute("aria-invalid", emSai || thieu ? "true" : "false");
    hint.classList.toggle("loi", thieu || dtSai || emSai);
    hint.textContent = thieu ? "Cần ít nhất một trong hai: điện thoại hoặc email."
      : dtSai ? "Số điện thoại chưa đúng." : emSai ? "Email chưa đúng." : "Cần ít nhất một trong hai: điện thoại hoặc email.";
    if (thieu || dtSai || emSai) loi.push(dtSai || thieu ? f.dien_thoai : f.email);
    if (!f.dong_y.checked) { loi.push(f.dong_y); }
    if (loi.length) {
      bao(!f.dong_y.checked && loi.length === 1 ? "Bạn cần tick ô đồng ý để chúng tôi liên hệ." : "Bạn kiểm lại các ô được đánh dấu nhé.", "loi");
      loi[0].focus();
      return;
    }
    var data = {
      ho_ten: f.ho_ten.value.trim(), cong_ty: f.cong_ty.value.trim(),
      dien_thoai: dt, email: em,
      ngay_su_kien: f.ngay_su_kien.value, so_khach: f.so_khach.value, ngan_sach: f.ngan_sach.value,
      giai_phap: Array.prototype.filter.call(form.querySelectorAll('input[name="giai_phap"]'), function (x) { return x.checked; }).map(function (x) { return x.value; }),
      brief: f.brief.value.trim(), goi: f.goi.value, dong_y: true, website: f.website.value,
      nguon: nguon, trang: location.pathname
    };
    nut.disabled = true; nut.textContent = "Đang gửi…"; bao("");
    fetch("/api/brief", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (k) {
        if (!k.ok) throw new Error(k.j.loi || "Gửi chưa được");
        form.reset();
        bao("Đã nhận brief của bạn" + (k.j.ma ? " (mã " + k.j.ma + ")" : "") + ". Chúng tôi sẽ liên hệ trong 1 ngày làm việc.", "ok");
        nut.textContent = "Gửi thêm brief khác";
        if (!form.hasAttribute("data-o-lai")) setTimeout(function () { location.href = "/cam-on/" + (k.j.ma ? "?ma=" + encodeURIComponent(k.j.ma) : ""); }, 900);
      })
      .catch(function (e) {
        bao(e.message + ". Bạn thử lại, hoặc nhắn Zalo 0904 106 143.", "loi");
        nut.textContent = "Gửi brief";
      })
      .finally(function () { nut.disabled = false; });
  });
})();

// Cấu hình giá/thời gian: điền ở cau-hinh.json, null thì giữ chữ mặc định.
fetch("/cau-hinh.json").then(function (r) { return r.ok ? r.json() : {}; }).then(function (c) {
  Object.keys(c || {}).forEach(function (k) {
    if (k[0] === "_" || c[k] == null || c[k] === "") return;
    document.querySelectorAll('[data-cfg="' + k + '"]').forEach(function (el) { el.textContent = c[k]; el.removeAttribute("data-can-xac-nhan"); });
  });
}).catch(function () {});

// Tính gói: ba câu → gợi ý gói, điền sẵn form brief.
(function () {
  var f = document.getElementById("tinh-goi");
  if (!f) return;
  var kq = f.querySelector(".tinh-kq");
  var TEN = { "gian-hang": "Gian hàng", "activation": "Activation", "hoi-nghi": "Hội nghị" };
  var GP = { "gian-hang": ["photobooth", "minigame"], "activation": ["nhan-vat-ai", "photobooth"], "hoi-nghi": ["nhan-vat-ai", "minigame"] };
  function goiY() {
    var loai = f.loai.value, muc = f.muc_tieu.value, khach = f.khach.value;
    var goi = loai;
    if (loai === "gian-hang" && muc === "san-pham") goi = "activation";
    if (loai === "activation" && (khach === "1.000 đến 5.000" || khach === "Trên 5.000") && muc === "lead") goi = "hoi-nghi";
    var ly = muc === "lead" ? "mỗi lượt chơi đổi lấy liên hệ có đồng ý" : muc === "chu-y" ? "ảnh và bảng xếp hạng kéo khách dừng lại" : "nhân vật AI giải thích sản phẩm thay người đứng quầy";
    return { goi: goi, ly: ly };
  }
  var daDoi = false;
  function ve() {
    var g = goiY();
    kq.innerHTML = "Gợi ý: <b>gói " + TEN[g.goi] + "</b>, vì " + g.ly + ".";
    document.querySelectorAll(".goi-item").forEach(function (el) { el.classList.toggle("chon", daDoi && el.getAttribute("data-goi") === g.goi); });
    return g;
  }
  f.addEventListener("change", function () { daDoi = true; ve(); }); ve();
  f.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var g = ve(), b = document.getElementById("form-brief");
    if (!b) return;
    b.elements.goi.value = g.goi;
    b.elements.so_khach.value = f.khach.value;
    b.querySelectorAll('input[name="giai_phap"]').forEach(function (x) { x.checked = GP[g.goi].indexOf(x.value) > -1; });
    if (!b.elements.brief.value) b.elements.brief.value = "Quan tâm gói " + TEN[g.goi] + ". Loại sự kiện: " + f.loai.options[f.loai.selectedIndex].text + ".";
    document.getElementById("brief").scrollIntoView({ behavior: "smooth" });
    setTimeout(function () { b.elements.ho_ten.focus({ preventScroll: true }); }, 400);
  });
})();

// Nút Zalo nổi trên điện thoại, ẩn khi đang ở vùng form.
(function () {
  var a = document.createElement("a");
  a.className = "zalo-noi"; a.href = "https://zalo.me/0904106143"; a.target = "_blank"; a.rel = "noopener";
  a.textContent = "Nhắn Zalo"; a.setAttribute("aria-label", "Nhắn Zalo cho IF Agent, số 0904 106 143");
  document.body.appendChild(a);
  var f = document.getElementById("form-brief");
  if (f && "IntersectionObserver" in window) new IntersectionObserver(function (e) { a.classList.toggle("an", e[0].isIntersecting); }).observe(f);
})();

// Form gọi lại: chỉ tên + số + đồng ý, cùng máy nhận lead, loai = goi-lai.
(function () {
  var f = document.getElementById("form-goi-lai");
  if (!f) return;
  var msg = f.querySelector(".form-msg"), nut = f.querySelector("button");
  var nguon = {}; try { nguon = JSON.parse(sessionStorage.getItem("ifa_nguon") || "{}"); } catch (e) {}
  f.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var ten = f.ho_ten.value.trim(), dt = f.dien_thoai.value.trim(), loi = null;
    f.ho_ten.setAttribute("aria-invalid", ten ? "false" : "true");
    var dtSai = !/^[0-9+().\s-]{8,20}$/.test(dt);
    f.dien_thoai.setAttribute("aria-invalid", dtSai ? "true" : "false");
    if (!ten) loi = [f.ho_ten, "Bạn điền họ tên nhé."];
    else if (dtSai) loi = [f.dien_thoai, "Số điện thoại chưa đúng."];
    else if (!f.dong_y.checked) loi = [f.dong_y, "Bạn cần tick ô đồng ý để chúng tôi gọi lại."];
    if (loi) { msg.textContent = loi[1]; msg.className = "form-msg loi"; loi[0].focus(); return; }
    nut.disabled = true; nut.textContent = "Đang gửi…";
    fetch("/api/brief", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ loai: "goi-lai", ho_ten: ten, dien_thoai: dt, dong_y: true, website: f.website.value, nguon: nguon, trang: location.pathname }) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (k) {
        if (!k.ok) throw new Error(k.j.loi || "Gửi chưa được");
        f.reset(); msg.className = "form-msg ok";
        msg.textContent = "Đã nhận" + (k.j.ma ? " (mã " + k.j.ma + ")" : "") + ". Chúng tôi gọi lại trong giờ làm việc.";
        nut.textContent = "Đã gửi";
      })
      .catch(function (e) { msg.className = "form-msg loi"; msg.textContent = e.message + ". Bạn nhắn Zalo 0904 106 143 giúp chúng tôi."; nut.textContent = "Gọi lại cho tôi"; })
      .finally(function () { nut.disabled = false; });
  });
})();
