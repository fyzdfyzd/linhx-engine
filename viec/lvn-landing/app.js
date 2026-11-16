// Tương tác biểu mẫu và điều hướng cho trang giới thiệu Listening Vietnam
(function () {
  "use strict";

  function initLandingPage() {
    var formEl = document.getElementById("form-lien-he");
    var thankYouEl = document.getElementById("cam-on");
    var thankYouTextEl = document.getElementById("cam-on-noi-dung");
    var resetBtn = document.getElementById("nut-nhap-lai");
    var errorEl = document.getElementById("loi-email");
    var emailInput = formEl ? formEl.querySelector('input[type="email"]') : null;
    var companyInput = formEl ? formEl.querySelector('input[name="cong_ty"]') : null;

    // Khởi tạo: đảm bảo hộp cảm ơn luôn ẩn khi mới tải trang
    if (thankYouEl) {
      thankYouEl.hidden = true;
    }

    var EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

    function showEmailError(message) {
      if (emailInput) {
        emailInput.setAttribute("aria-invalid", "true");
      }
      if (errorEl) {
        errorEl.textContent = message;
        errorEl.hidden = false;
      }
    }

    function clearEmailError() {
      if (emailInput) {
        emailInput.removeAttribute("aria-invalid");
      }
      if (errorEl) {
        errorEl.textContent = "";
        errorEl.hidden = true;
      }
    }

    function isValidEmail(rawValue) {
      var trimmed = (rawValue || "").trim();
      if (!trimmed) {
        return false;
      }
      if (emailInput && typeof emailInput.checkValidity === "function" && !emailInput.checkValidity()) {
        return false;
      }
      return EMAIL_REGEX.test(trimmed);
    }

    // Điều hướng tức thời từ các nút CTA tới biểu mẫu để thao tác điền diễn ra ngay lập tức
    document.addEventListener("click", function (event) {
      var targetNode = event.target;
      if (!targetNode || typeof targetNode.closest !== "function") {
        return;
      }

      var ctaTrigger = targetNode.closest(
        '[data-cta="bao-cao-mau"], a[href="#lien-he"], a[href="#form-lien-he"]'
      );
      if (!ctaTrigger) {
        return;
      }

      var destination = document.getElementById("form-lien-he") || document.getElementById("lien-he");
      if (!destination) {
        return;
      }

      event.preventDefault();

      if (formEl && thankYouEl && formEl.hidden) {
        formEl.hidden = false;
        thankYouEl.hidden = true;
      }

      destination.scrollIntoView({ behavior: "auto", block: "start" });

      if (emailInput && typeof emailInput.focus === "function") {
        try {
          emailInput.focus({ preventScroll: true });
        } catch (_err) {
          emailInput.focus();
        }
      }
    });

    if (!formEl || !thankYouEl || !emailInput) {
      return;
    }

    // Bắt sự kiện invalid của HTML5 khi người dùng nhập sai định dạng thư điện tử
    emailInput.addEventListener("invalid", function (event) {
      event.preventDefault();
      thankYouEl.hidden = true;
      showEmailError("Vui lòng nhập đúng định dạng thư điện tử công việc (ví dụ: ten@congty.vn).");
    });

    emailInput.addEventListener("input", function () {
      clearEmailError();
    });

    // Xử lý gửi biểu mẫu tĩnh (không gửi máy chủ, chỉ hiện thông báo cảm ơn khi hợp lệ)
    formEl.addEventListener("submit", function (event) {
      event.preventDefault();

      var emailValue = (emailInput.value || "").trim();
      var companyValue = companyInput ? (companyInput.value || "").trim() : "";

      if (!isValidEmail(emailValue)) {
        thankYouEl.hidden = true;
        showEmailError("Vui lòng nhập đúng định dạng thư điện tử công việc (ví dụ: ten@congty.vn).");
        try {
          emailInput.focus({ preventScroll: true });
        } catch (_err) {
          emailInput.focus();
        }
        return;
      }

      clearEmailError();

      if (thankYouTextEl) {
        thankYouTextEl.textContent = "";
        thankYouTextEl.appendChild(
          document.createTextNode("Cảm ơn bạn đã quan tâm đến Listening Vietnam. Chúng tôi đã ghi nhận yêu cầu")
        );

        if (companyValue) {
          thankYouTextEl.appendChild(document.createTextNode(" của "));
          var companyStrong = document.createElement("strong");
          companyStrong.textContent = companyValue;
          thankYouTextEl.appendChild(companyStrong);
        }

        thankYouTextEl.appendChild(document.createTextNode(" qua địa chỉ "));
        var emailStrong = document.createElement("strong");
        emailStrong.textContent = emailValue;
        thankYouTextEl.appendChild(emailStrong);
        thankYouTextEl.appendChild(
          document.createTextNode(" và sẽ gửi bản báo cáo mẫu phù hợp trong thời gian sớm nhất.")
        );
      }

      formEl.hidden = true;
      thankYouEl.hidden = false;
      thankYouEl.removeAttribute("hidden");

      try {
        thankYouEl.focus({ preventScroll: true });
      } catch (_err) {
        thankYouEl.focus();
      }
    });

    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        thankYouEl.hidden = true;
        formEl.hidden = false;
        clearEmailError();
        try {
          emailInput.focus({ preventScroll: true });
        } catch (_err) {
          emailInput.focus();
        }
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initLandingPage);
  } else {
    initLandingPage();
  }
})();
