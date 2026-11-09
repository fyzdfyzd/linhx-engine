import fs from "node:fs";
import path from "node:path";
import { useState } from "react";
import Head from "next/head";

async function docNoiDung() {
  const url = process.env.NOI_DUNG_URL;
  if (url && url.trim()) {
    const res = await fetch(url.trim(), {
      cache: "no-store",
      headers: { Connection: "close" },
    });
    if (!res.ok) {
      throw new Error(`Không đọc được NOI_DUNG_URL (${res.status}): ${url}`);
    }
    const data = await res.json();
    return data?.noi_dung || data;
  }

  const siteJson = process.env.SITE_JSON;
  if (siteJson && siteJson.trim()) {
    const p = path.resolve(siteJson.trim());
    if (fs.existsSync(p)) {
      const raw = fs.readFileSync(p, "utf-8");
      const data = JSON.parse(raw);
      return data?.noi_dung || data;
    }
  }

  const mauPath = path.join(process.cwd(), "noi-dung.mau.json");
  const raw = fs.readFileSync(mauPath, "utf-8");
  const data = JSON.parse(raw);
  return data?.noi_dung || data;
}

export async function getStaticProps() {
  const raw = await docNoiDung();
  const noiDung = {
    tieu_de: typeof raw?.tieu_de === "string" ? raw.tieu_de : "Trang BU",
    mo_ta: typeof raw?.mo_ta === "string" ? raw.mo_ta : "",
    muc: Array.isArray(raw?.muc)
      ? raw.muc.map((m) => ({
          ten: typeof m?.ten === "string" ? m.ten : "",
          mo_ta: typeof m?.mo_ta === "string" ? m.mo_ta : "",
        }))
      : [],
  };
  const apiGoc =
    typeof process.env.API_GOC === "string"
      ? process.env.API_GOC.trim().replace(/\/+$/, "")
      : "";

  return {
    props: {
      noiDung,
      apiGoc,
    },
  };
}

export default function TrangBU({ noiDung, apiGoc = "" }) {
  const { tieu_de, mo_ta, muc } = noiDung || {
    tieu_de: "Trang BU",
    mo_ta: "",
    muc: [],
  };

  const [hoTen, datHoTen] = useState("");
  const [dienThoai, datDienThoai] = useState("");
  const [email, datEmail] = useState("");
  const [nhuCau, datNhuCau] = useState("");
  const [website, datWebsite] = useState("");
  const [dongYLienHe, datDongYLienHe] = useState(false);
  const [dongYMarketing, datDongYMarketing] = useState(false);
  const [dangGui, datDangGui] = useState(false);
  const [daGui, datDaGui] = useState(false);
  const [loiForm, datLoiForm] = useState("");

  async function xuLyGuiForm(e) {
    e.preventDefault();
    datLoiForm("");
    if (website.trim()) {
      return;
    }
    if (!dongYLienHe) {
      datLoiForm("Vui lòng đồng ý để chúng tôi liên hệ tư vấn.");
      return;
    }
    if (!dienThoai.trim() && !email.trim()) {
      datLoiForm("Vui lòng nhập ít nhất số điện thoại hoặc email.");
      return;
    }
    datDangGui(true);
    try {
      const goc = typeof apiGoc === "string" ? apiGoc.replace(/\/+$/, "") : "";
      const dich = `${goc}/api/method/linhx_core.crm.api_form.nhan_form`;
      const res = await fetch(dich, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          ho_ten: hoTen,
          dien_thoai: dienThoai,
          email: email,
          nhu_cau: nhuCau,
          dong_y_lien_he: Boolean(dongYLienHe),
          dong_y_marketing: Boolean(dongYMarketing),
        }),
      });
      if (res.status === 429) {
        datLoiForm("Bạn gửi yêu cầu quá nhanh, vui lòng thử lại sau ít phút.");
        return;
      }
      if (!res.ok) {
        datLoiForm("Không gửi được thông tin, vui lòng kiểm tra lại.");
        return;
      }
      datDaGui(true);
    } catch {
      datLoiForm("Lỗi kết nối máy chủ, vui lòng thử lại.");
    } finally {
      datDangGui(false);
    }
  }

  return (
    <>
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{tieu_de}</title>
      </Head>

      <style jsx global>{`
        :root {
          --bg: #f6f5f1;
          --mat: #ffffff;
          --chu: #16181d;
          --phu: #5d6270;
          --vien: #e3e1da;
          --nhan: #1f4fd6;
          --nhan-nhat: #e8eefc;
          --xanh: #0f766e;
          --xanh-nhat: #e6f6f4;
          --do: #b91c1c;
        }
        *,
        *::before,
        *::after {
          box-sizing: border-box;
        }
        html,
        body {
          margin: 0;
          padding: 0;
          width: 100%;
          max-width: 100%;
          overflow-x: hidden;
          background: var(--bg);
          color: var(--chu);
          font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
            Roboto, sans-serif;
          line-height: 1.55;
          -webkit-font-smoothing: antialiased;
        }
        .khung {
          width: 100%;
          max-width: 1080px;
          margin: 0 auto;
          padding: 0 16px;
        }
        .dau-trang {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 18px 0;
          border-bottom: 1px solid var(--vien);
          gap: 12px;
          flex-wrap: wrap;
        }
        .logo {
          font-weight: 700;
          font-size: 16px;
          color: var(--chu);
          text-decoration: none;
          display: inline-flex;
          align-items: center;
          gap: 8px;
        }
        .cham-logo {
          width: 10px;
          height: 10px;
          border-radius: 2px;
          background: var(--nhan);
          display: inline-block;
          flex-shrink: 0;
        }
        .nhan-bu {
          font-size: 12px;
          font-weight: 600;
          padding: 4px 10px;
          border-radius: 999px;
          background: var(--nhan-nhat);
          color: var(--nhan);
          text-decoration: none;
        }
        .nut-kham {
          display: inline-block;
          margin-top: 16px;
          padding: 10px 16px;
          border-radius: 10px;
          background: var(--nhan);
          color: #ffffff;
          font-size: 14px;
          font-weight: 600;
          text-decoration: none;
        }
        .hero {
          padding: 40px 0 28px;
        }
        .hero h1 {
          font-size: clamp(24px, 4.5vw, 40px);
          line-height: 1.2;
          margin: 0 0 14px;
          word-break: break-word;
          overflow-wrap: anywhere;
        }
        .hero p {
          font-size: clamp(15px, 2.2vw, 18px);
          color: var(--phu);
          max-width: 680px;
          margin: 0;
          word-break: break-word;
          overflow-wrap: anywhere;
        }
        .luoi-muc {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
          gap: 16px;
          padding: 16px 0 32px;
        }
        @media (max-width: 420px) {
          .luoi-muc {
            grid-template-columns: 1fr;
          }
        }
        .the-muc {
          background: var(--mat);
          border: 1px solid var(--vien);
          border-radius: 14px;
          padding: 20px;
          min-width: 0;
        }
        .the-muc h2 {
          font-size: 18px;
          margin: 0 0 8px;
          word-break: break-word;
          overflow-wrap: anywhere;
        }
        .the-muc p {
          font-size: 15px;
          color: var(--phu);
          margin: 0;
          word-break: break-word;
          overflow-wrap: anywhere;
        }
        .khu-form {
          padding: 8px 0 48px;
        }
        .khung-form {
          background: var(--mat);
          border: 1px solid var(--vien);
          border-radius: 14px;
          padding: 24px 20px;
          width: 100%;
          max-width: 640px;
          min-width: 0;
        }
        .khung-form h2 {
          font-size: 20px;
          margin: 0 0 6px;
          word-break: break-word;
          overflow-wrap: anywhere;
        }
        .khung-form .mo-ta-form {
          font-size: 14px;
          color: var(--phu);
          margin: 0 0 18px;
        }
        .truong-form {
          margin-bottom: 14px;
          width: 100%;
          min-width: 0;
        }
        .truong-form label {
          display: block;
          font-size: 14px;
          font-weight: 600;
          margin-bottom: 6px;
        }
        .truong-form input[type="text"],
        .truong-form input[type="tel"],
        .truong-form input[type="email"],
        .truong-form textarea {
          width: 100%;
          max-width: 100%;
          min-width: 0;
          padding: 10px 12px;
          font-size: 15px;
          font-family: inherit;
          color: var(--chu);
          background: #ffffff;
          border: 1px solid var(--vien);
          border-radius: 10px;
        }
        .truong-form textarea {
          min-height: 84px;
          resize: vertical;
        }
        .dong-kiem {
          display: flex;
          align-items: flex-start;
          gap: 10px;
          margin-bottom: 10px;
          font-size: 14px;
          color: var(--chu);
          cursor: pointer;
          word-break: break-word;
          overflow-wrap: anywhere;
        }
        .dong-kiem input[type="checkbox"] {
          margin-top: 3px;
          flex-shrink: 0;
        }
        .nut-gui {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 100%;
          max-width: 100%;
          padding: 12px 18px;
          margin-top: 6px;
          font-size: 15px;
          font-weight: 600;
          color: #ffffff;
          background: var(--nhan);
          border: none;
          border-radius: 10px;
          cursor: pointer;
        }
        .nut-gui:disabled {
          opacity: 0.65;
          cursor: not-allowed;
        }
        .loi-form {
          margin: 10px 0 0;
          font-size: 14px;
          color: var(--do);
        }
        .hop-cam-on {
          margin-top: 16px;
          padding: 14px 16px;
          border-radius: 10px;
          background: var(--xanh-nhat);
          color: var(--xanh);
          font-size: 15px;
          font-weight: 600;
          word-break: break-word;
          overflow-wrap: anywhere;
        }
        .chan-trang {
          border-top: 1px solid var(--vien);
          padding: 20px 0 32px;
          font-size: 13px;
          color: var(--phu);
        }
      `}</style>

      <div className="khung">
        <header className="dau-trang">
          <span className="logo">
            <i className="cham-logo" aria-hidden="true" />
            <span>ifAgent · LINHX ENGINE</span>
          </span>
          <span className="nhan-bu">Trang BU</span>
        </header>

        <main>
          <section className="hero">
            <h1 id="tieu-de-trang">{tieu_de}</h1>
            {mo_ta && <p id="mo-ta-trang">{mo_ta}</p>}
            <a href="/kham" className="nut-kham">
              Chạy T1 Khám miễn phí (LAB113)
            </a>
          </section>

          <section className="luoi-muc" aria-label="Danh sách mục">
            {muc.map((item, idx) => (
              <article key={idx} className="the-muc" data-muc={idx}>
                <h2>{item.ten}</h2>
                <p>{item.mo_ta}</p>
              </article>
            ))}
          </section>

          <section className="khu-form" aria-label="Form đăng ký tư vấn">
            <div className="khung-form">
              <h2>Đăng ký nhận tư vấn</h2>
              <p className="mo-ta-form">
                Để lại thông tin liên hệ để đội ngũ tư vấn phản hồi nhanh nhất.
              </p>

              <form data-lead onSubmit={xuLyGuiForm} noValidate>
                <div style={{ display: "none" }} aria-hidden="true">
                  <label htmlFor="lead-website">Website</label>
                  <input
                    id="lead-website"
                    type="text"
                    name="website"
                    tabIndex={-1}
                    autoComplete="off"
                    value={website}
                    onChange={(e) => datWebsite(e.target.value)}
                  />
                </div>

                <div className="truong-form">
                  <label htmlFor="lead-ho-ten">Họ và tên</label>
                  <input
                    id="lead-ho-ten"
                    type="text"
                    name="ho_ten"
                    maxLength={120}
                    value={hoTen}
                    onChange={(e) => datHoTen(e.target.value)}
                    placeholder="Nguyễn Văn A"
                  />
                </div>

                <div className="truong-form">
                  <label htmlFor="lead-dien-thoai">Số điện thoại</label>
                  <input
                    id="lead-dien-thoai"
                    type="tel"
                    name="dien_thoai"
                    maxLength={20}
                    value={dienThoai}
                    onChange={(e) => datDienThoai(e.target.value)}
                    placeholder="0912345678"
                  />
                </div>

                <div className="truong-form">
                  <label htmlFor="lead-email">Email</label>
                  <input
                    id="lead-email"
                    type="email"
                    name="email"
                    maxLength={254}
                    value={email}
                    onChange={(e) => datEmail(e.target.value)}
                    placeholder="ban@doanhnghiep.vn"
                  />
                </div>

                <div className="truong-form">
                  <label htmlFor="lead-nhu-cau">Nhu cầu cần tư vấn</label>
                  <textarea
                    id="lead-nhu-cau"
                    name="nhu_cau"
                    maxLength={2000}
                    value={nhuCau}
                    onChange={(e) => datNhuCau(e.target.value)}
                    placeholder="Mô tả ngắn nhu cầu của bạn"
                  />
                </div>

                <label className="dong-kiem">
                  <input
                    type="checkbox"
                    name="dong_y_lien_he"
                    checked={dongYLienHe}
                    onChange={(e) => datDongYLienHe(e.target.checked)}
                  />
                  <span>Tôi đồng ý để đơn vị liên hệ tư vấn theo thông tin đã cung cấp.</span>
                </label>

                <label className="dong-kiem">
                  <input
                    type="checkbox"
                    name="dong_y_marketing"
                    checked={dongYMarketing}
                    onChange={(e) => datDongYMarketing(e.target.checked)}
                  />
                  <span>Tôi đồng ý nhận bản tin và tài liệu chuyên môn (marketing).</span>
                </label>

                {loiForm && <p className="loi-form">{loiForm}</p>}

                <button type="submit" className="nut-gui" disabled={dangGui}>
                  {dangGui ? "Đang gửi..." : "Gửi thông tin"}
                </button>

                {daGui && (
                  <div className="hop-cam-on" data-cam-on>
                    Cảm ơn bạn! Chúng tôi đã ghi nhận thông tin và sẽ liên hệ sớm.
                  </div>
                )}
              </form>
            </div>
          </section>
        </main>

        <footer className="chan-trang">
          <span>LINHX ENGINE · Khuôn Trang BU tĩnh</span>
        </footer>
      </div>
    </>
  );
}
