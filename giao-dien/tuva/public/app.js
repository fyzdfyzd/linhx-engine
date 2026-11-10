// TUVA: ba form lead (trao đổi dự án, gọi lại, tải bộ quy tắc AI), công cụ tự chấm mức sẵn sàng AI, cấu hình từ cau-hinh.json.
(function () {
  var EN = document.documentElement.lang === "en";
  var T = EN ? {
    canLH: "Please give at least a phone number or an email.", dtSai: "The phone number does not look right.", emSai: "The email does not look right.",
    tick: "Please tick the consent box so we can contact you.", kiemLai: "Please check the highlighted fields.", dangGui: "Sending…",
    daNhan: "Received", lienHe: ". We will get back to you within one working day.", thuLai: ". Please try again in a few minutes.",
    tenTrong: "Please enter your name.", tickGoi: "Please tick the consent box so we can call you.", goiLai: ". We will call you back during working hours.",
    emailCan: "Please enter your work email.", taiOk: ". We will email the AI rules to you as soon as the first version is ready.", taiLink: "Download the AI rules",
    camOn: "/en/thank-you/", loiMay: "Could not send", nutNoi: "Talk to us"
  } : {
    canLH: "Cần ít nhất một trong hai: điện thoại hoặc email.", dtSai: "Số điện thoại chưa đúng.", emSai: "Email chưa đúng.",
    tick: "Bạn cần tick ô đồng ý để chúng tôi liên hệ.", kiemLai: "Bạn kiểm lại các ô được đánh dấu nhé.", dangGui: "Đang gửi…",
    daNhan: "Đã nhận", lienHe: ". Chúng tôi sẽ liên hệ trong 1 ngày làm việc.", thuLai: ". Bạn thử lại sau ít phút nhé.",
    tenTrong: "Bạn điền họ tên nhé.", tickGoi: "Bạn cần tick ô đồng ý để chúng tôi gọi lại.", goiLai: ". Chúng tôi gọi lại trong giờ làm việc.",
    emailCan: "Bạn điền email công việc nhé.", taiOk: ". Chúng tôi gửi bộ quy tắc qua email ngay khi có bản đầu tiên.", taiLink: "Tải bộ quy tắc AI",
    camOn: "/cam-on/", loiMay: "Gửi chưa được", nutNoi: "Trao đổi dự án"
  };
  var CFG = {};
  var RE_DT = /^[0-9+().\s-]{8,20}$/, RE_EM = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  // Giữ nguồn (?kenh=, ref, utm_*) theo phiên.
  var q = new URLSearchParams(location.search), nguon = {};
  ["kenh", "ref", "utm_source", "utm_medium", "utm_campaign", "utm_content"].forEach(function (k) { if (q.get(k)) nguon[k] = q.get(k).slice(0, 80); });
  try {
    if (Object.keys(nguon).length) sessionStorage.setItem("tuva_nguon", JSON.stringify(nguon));
    else nguon = JSON.parse(sessionStorage.getItem("tuva_nguon") || "{}");
  } catch (e) {}

  function gui(data) {
    data.nguon = nguon; data.trang = location.pathname; data.ngon_ngu = EN ? "en" : "vi";
    return fetch("/api/brief", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (k) { if (!k.ok) throw new Error(k.j.loi || T.loiMay); return k.j; });
  }
  function duongLui() { return CFG.email_cong_khai ? (EN ? " Or email " : " Hoặc gửi email tới ") + CFG.email_cong_khai + "." : ""; }
  function bao(msg, t, loai) { msg.textContent = t; msg.className = "form-msg " + (loai || ""); }
  function danh(el, sai) { el.setAttribute("aria-invalid", sai ? "true" : "false"); }

  // 1. Form trao đổi dự án / đề xuất
  (function () {
    var form = document.getElementById("form-brief");
    if (!form) return;
    var msg = form.querySelector(".form-msg"), hint = document.getElementById("hint-lienhe"), nut = form.querySelector('button[type="submit"]'), chuNut = nut.textContent;
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var f = form.elements, loi = [];
      [f.ho_ten, f.cong_ty].forEach(function (el) { var sai = !el.value.trim(); danh(el, sai); if (sai) loi.push(el); });
      var dt = f.dien_thoai.value.trim(), em = f.email.value.trim();
      var dtSai = dt && !RE_DT.test(dt), emSai = em && !RE_EM.test(em), thieu = !dt && !em;
      danh(f.dien_thoai, dtSai || thieu); danh(f.email, emSai || thieu);
      if (hint) { hint.classList.toggle("loi", thieu || dtSai || emSai); hint.textContent = thieu ? T.canLH : dtSai ? T.dtSai : emSai ? T.emSai : T.canLH; }
      if (thieu || dtSai || emSai) loi.push(dtSai || thieu ? f.dien_thoai : f.email);
      if (!f.dong_y.checked) loi.push(f.dong_y);
      if (loi.length) { bao(msg, !f.dong_y.checked && loi.length === 1 ? T.tick : T.kiemLai, "loi"); loi[0].focus(); return; }
      var data = { loai: "brief", ho_ten: f.ho_ten.value.trim(), cong_ty: f.cong_ty.value.trim(), dien_thoai: dt, email: em,
        vai_tro: f.vai_tro.value, linh_vuc: f.linh_vuc.value, han_nop: f.han_nop.value, nha_tai_tro: f.nha_tai_tro.value.trim(),
        ngan_sach: f.ngan_sach.value, brief: f.brief.value.trim(), ket_qua: f.ket_qua ? f.ket_qua.value : "", dong_y: true, website: f.website.value };
      nut.disabled = true; nut.textContent = T.dangGui; bao(msg, "");
      gui(data).then(function (j) {
        form.reset();
        bao(msg, T.daNhan + (j.ma ? " (" + j.ma + ")" : "") + T.lienHe, "ok");
        nut.textContent = chuNut;
        if (!form.hasAttribute("data-o-lai")) setTimeout(function () { location.href = T.camOn + (j.ma ? "?ma=" + encodeURIComponent(j.ma) : ""); }, 900);
      }).catch(function (e) { bao(msg, e.message + T.thuLai + duongLui(), "loi"); nut.textContent = chuNut; })
        .finally(function () { nut.disabled = false; });
    });
  })();

  // 2. Form gọi lại: tên + số + đồng ý
  (function () {
    var f = document.getElementById("form-goi-lai");
    if (!f) return;
    var msg = f.querySelector(".form-msg"), nut = f.querySelector('button[type="submit"]'), chuNut = nut.textContent;
    f.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var ten = f.ho_ten.value.trim(), dt = f.dien_thoai.value.trim(), loi = null, dtSai = !RE_DT.test(dt);
      danh(f.ho_ten, !ten); danh(f.dien_thoai, dtSai);
      if (!ten) loi = [f.ho_ten, T.tenTrong];
      else if (dtSai) loi = [f.dien_thoai, T.dtSai];
      else if (!f.dong_y.checked) loi = [f.dong_y, T.tickGoi];
      if (loi) { bao(msg, loi[1], "loi"); loi[0].focus(); return; }
      nut.disabled = true; nut.textContent = T.dangGui;
      gui({ loai: "goi-lai", ho_ten: ten, dien_thoai: dt, dong_y: true, website: f.website.value }).then(function (j) {
        f.reset(); bao(msg, T.daNhan + (j.ma ? " (" + j.ma + ")" : "") + T.goiLai, "ok"); nut.textContent = chuNut;
      }).catch(function (e) { bao(msg, e.message + T.thuLai + duongLui(), "loi"); nut.textContent = chuNut; })
        .finally(function () { nut.disabled = false; });
    });
  })();

  // 3. Form tải bộ quy tắc AI (đổi email)
  (function () {
    var f = document.getElementById("form-tai");
    if (!f) return;
    var msg = f.querySelector(".form-msg"), nut = f.querySelector('button[type="submit"]'), chuNut = nut.textContent;
    f.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var ten = f.ho_ten.value.trim(), em = f.email.value.trim(), loi = null, emSai = !RE_EM.test(em);
      danh(f.ho_ten, !ten); danh(f.email, emSai);
      if (!ten) loi = [f.ho_ten, T.tenTrong];
      else if (emSai) loi = [f.email, em ? T.emSai : T.emailCan];
      else if (!f.dong_y.checked) loi = [f.dong_y, T.tick];
      if (loi) { bao(msg, loi[1], "loi"); loi[0].focus(); return; }
      nut.disabled = true; nut.textContent = T.dangGui;
      gui({ loai: "tai-bo-quy-tac", ho_ten: ten, email: em, cong_ty: f.cong_ty.value.trim(), ket_qua: f.ket_qua.value, dong_y: true, website: f.website.value }).then(function (j) {
        f.reset();
        msg.className = "form-msg ok"; msg.textContent = "";
        if (CFG.pdf_bo_quy_tac) {
          msg.appendChild(document.createTextNode(T.daNhan + (j.ma ? " (" + j.ma + "). " : ". ")));
          var a = document.createElement("a"); a.href = CFG.pdf_bo_quy_tac; a.textContent = T.taiLink; a.setAttribute("download", ""); msg.appendChild(a);
        } else msg.textContent = T.daNhan + (j.ma ? " (" + j.ma + ")" : "") + T.taiOk;
        nut.textContent = chuNut;
      }).catch(function (e) { bao(msg, e.message + T.thuLai + duongLui(), "loi"); nut.textContent = chuNut; })
        .finally(function () { nut.disabled = false; });
    });
  })();

  // 4. Tự chấm mức sẵn sàng AI: 10 câu, 0/1/2 điểm, ra mức + 3 gợi ý, mời để lại email nhận bản đầy đủ.
  (function () {
    var box = document.getElementById("cham");
    if (!box || EN) return;
    var C = [
      ["Tổ chức đã có quy định bằng văn bản về việc nhân viên dùng công cụ AI chưa?", "Viết một trang quy định dùng AI: việc được làm, việc không được làm, ai trả lời khi có thắc mắc."],
      ["Nhân viên có biết dữ liệu nào không được đưa vào công cụ AI, như tên, ảnh, hồ sơ người thụ hưởng?", "Lập danh sách dữ liệu cấm đưa vào AI và nhắc lại trong buổi giao ban đầu tiên."],
      ["Có người chịu trách nhiệm duyệt nội dung có AI hỗ trợ trước khi đăng hoặc gửi cho nhà tài trợ?", "Giao một người duyệt cho từng loại nội dung: bài đăng, báo cáo, thư gửi nhà tài trợ."],
      ["Khi công bố, nội dung có AI hỗ trợ có được ghi nhãn không?", "Thống nhất một câu ghi nhãn ngắn cho ảnh và bài viết có AI hỗ trợ."],
      ["Đội ngũ đã được tập huấn dùng AI cho việc chuyên môn như viết, tóm tắt, dịch, phân tích?", "Tổ chức một buổi tập huấn theo vai trò, dùng chính tài liệu dự án đã ẩn danh."],
      ["Tổ chức có danh sách công cụ AI được phép dùng, đăng ký bằng tài khoản của tổ chức?", "Chọn hai đến ba công cụ, mở tài khoản của tổ chức, ngừng dùng tài khoản cá nhân cho việc dự án."],
      ["Số liệu và trích dẫn do AI đưa ra có được kiểm chứng trước khi dùng không?", "Thêm bước kiểm nguồn cho mọi con số và trích dẫn do AI gợi ý."],
      ["Dữ liệu dự án như báo cáo, khảo sát, phản hồi cộng đồng có được lưu gọn để phân tích được không?", "Gom báo cáo và khảo sát vào một thư mục chung, đặt tên thống nhất theo năm và dự án."],
      ["Tổ chức đã thử theo dõi dư luận mạng xã hội về vấn đề dự án theo đuổi chưa?", "Thử một đợt lắng nghe mạng xã hội ngắn quanh chủ đề chính của dự án."],
      ["Đề xuất tài trợ gần nhất có dòng ngân sách cho năng lực số, dữ liệu hoặc AI không?", "Ở đề xuất tới, viết riêng một hạng mục năng lực AI có chỉ số trong logframe."]
    ];
    var MUC = [[5, "Mức 1 · Bắt đầu", "Tổ chức chưa có nền cho AI. Rủi ro lớn nhất là nhân viên tự dùng công cụ AI với dữ liệu dự án mà không ai biết."],
               [10, "Mức 2 · Thử nghiệm", "Đã có người dùng AI nhưng mỗi người một kiểu. Một bộ quy tắc chung sẽ giúp cả tổ chức dùng an toàn và nhanh hơn."],
               [15, "Mức 3 · Có nề nếp", "Tổ chức đã có quy tắc và thói quen tốt. Bước tiếp là đưa AI vào chương trình và vào đề xuất tài trợ."],
               [20, "Mức 4 · Sẵn sàng mở rộng", "Tổ chức có thể dẫn dắt đối tác. Hợp phần AI có thể thành một đầu ra riêng của dự án, có chỉ số đo được."]];
    var than = box.querySelector(".cham-than"), tien = box.querySelector(".cham-tien i"), lui = box.querySelector(".cham-lui"), d = [];
    function ve() {
      var i = d.length;
      tien.style.width = Math.max(10, i * 10) + "%";
      lui.hidden = i === 0 || i >= C.length;
      if (i < C.length) {
        than.querySelector(".cham-so").textContent = "Câu " + (i + 1) + " trên " + C.length;
        than.querySelector(".cham-hoi").textContent = C[i][0];
        return;
      }
      var tong = d.reduce(function (a, b) { return a + b; }, 0), m = MUC.filter(function (x) { return tong <= x[0]; })[0];
      var yeu = d.map(function (v, k) { return [v, k]; }).sort(function (a, b) { return a[0] - b[0] || a[1] - b[1]; }).slice(0, 3).filter(function (x) { return x[0] < 2; });
      var kq = m[1] + " (" + tong + "/20)";
      than.innerHTML = '<div class="cham-kq"><p class="cham-so">Kết quả của bạn</p><p class="cham-muc"></p><p class="cham-nx"></p><ul></ul>' +
        '<div class="cta-row"><a class="btn btn-nau" href="#bo-quy-tac">Nhận bản đầy đủ qua email</a><button type="button" class="btn btn-vien cham-lai">Làm lại</button></div></div>';
      than.querySelector(".cham-muc").textContent = kq;
      than.querySelector(".cham-nx").textContent = m[2];
      var ul = than.querySelector("ul");
      (yeu.length ? yeu : [[2, 9]]).forEach(function (x) { var li = document.createElement("li"); li.textContent = C[x[1]][1]; ul.appendChild(li); });
      var tai = document.getElementById("form-tai");
      if (tai) {
        tai.elements.ket_qua.value = kq + "; điểm từng câu: " + d.join(",");
        var ghi = tai.querySelector(".tai-kq"); if (ghi) { ghi.textContent = "Kèm kết quả tự chấm: " + kq + ". Bản đầy đủ có gợi ý cho từng câu."; ghi.hidden = false; }
      }
      var b = document.getElementById("form-brief"); if (b && b.elements.ket_qua) b.elements.ket_qua.value = kq;
      var a = than.querySelector('a[href="#bo-quy-tac"]');
      if (!document.getElementById("bo-quy-tac")) a.href = "/bo-quy-tac-ai/?kenh=tu-cham";
      than.querySelector(".cham-lai").addEventListener("click", function () { d = []; dung(); });
      try { sessionStorage.setItem("tuva_tu_cham", kq); } catch (e) {}
    }
    function dung() {
      than.innerHTML = '<p class="cham-so"></p><p class="cham-hoi"></p><div class="cham-chon" role="group" aria-label="Chọn câu trả lời">' +
        '<button type="button" data-d="0">Chưa có</button><button type="button" data-d="1">Đang bàn hoặc mới có một phần</button><button type="button" data-d="2">Đã có và mọi người đang làm theo</button></div>';
      ve();
    }
    than.addEventListener("click", function (ev) {
      var b = ev.target.closest(".cham-chon button"); if (!b) return;
      d.push(+b.getAttribute("data-d")); ve();
      var h = than.querySelector(".cham-hoi, .cham-muc"); if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
    });
    lui.addEventListener("click", function () { d.pop(); ve(); });
  })();

  // 5. Cấu hình: điền ở cau-hinh.json, null thì giữ chữ an toàn. Nút nổi trên điện thoại.
  function nutNoi() {
    var a = document.createElement("a"), f = document.getElementById("form-brief");
    a.className = "nut-noi";
    if (CFG.zalo) { a.href = "https://zalo.me/" + String(CFG.zalo).replace(/\D/g, ""); a.target = "_blank"; a.rel = "noopener"; a.textContent = "Zalo"; a.setAttribute("aria-label", "Nhắn Zalo cho TUVA"); }
    else { a.href = f ? "#brief" : (EN ? "/en/#brief" : "/?kenh=nut-noi#brief"); a.textContent = T.nutNoi; }
    document.body.appendChild(a);
    // Ẩn khi màn đầu còn trên màn hình (đầu trang đã có nút) và khi đang ở vùng form.
    var hero = document.querySelector(".hero"), oHero = !!hero, oForm = false;
    function capNhat() { a.classList.toggle("an", oHero || oForm); }
    capNhat();
    if ("IntersectionObserver" in window) {
      if (hero) new IntersectionObserver(function (e) { oHero = e[0].isIntersecting; capNhat(); }).observe(hero);
      if (f) new IntersectionObserver(function (e) { oForm = e[0].isIntersecting; capNhat(); }).observe(f);
    } else { oHero = false; capNhat(); }
  }
  fetch("/cau-hinh.json").then(function (r) { return r.ok ? r.json() : {}; }).then(function (c) {
    CFG = c || {};
    Object.keys(CFG).forEach(function (k) {
      if (k[0] === "_" || CFG[k] == null || CFG[k] === "" || typeof CFG[k] === "object") return;
      document.querySelectorAll('[data-cfg="' + k + '"]').forEach(function (el) { el.textContent = CFG[k]; el.removeAttribute("data-can-xac-nhan"); });
    });
  }).catch(function () {}).then(nutNoi);
})();
