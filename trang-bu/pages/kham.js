import fs from "node:fs";
import path from "node:path";
import { useState } from "react";
import Head from "next/head";

function docKham() {
  const ungVien = [];
  const siteJson = process.env.SITE_JSON;
  if (siteJson && siteJson.trim()) {
    const pSite = path.resolve(siteJson.trim());
    const thuMucSite = path.dirname(pSite);
    ungVien.push(path.join(thuMucSite, "kham.json"));
  }
  ungVien.push(path.resolve(process.cwd(), "..", "sites", "ifagent", "kham.json"));

  for (const p of ungVien) {
    if (fs.existsSync(p)) {
      const raw = fs.readFileSync(p, "utf-8");
      return JSON.parse(raw);
    }
  }

  return {
    tieu_de: "T1 Khám",
    cau: [],
    muc: [],
  };
}

export async function getStaticProps() {
  const raw = docKham();
  const apiGoc =
    typeof process.env.API_GOC === "string"
      ? process.env.API_GOC.trim().replace(/\/+$/, "")
      : "";
  const kham = {
    tieu_de: typeof raw?.tieu_de === "string" ? raw.tieu_de : "T1 Khám",
    cau: Array.isArray(raw?.cau)
      ? raw.cau.map((c) => ({
          ma: String(c?.ma || ""),
          hoi: String(c?.hoi || ""),
          lua_chon: Array.isArray(c?.lua_chon)
            ? c.lua_chon.map((l) => ({
                nhan: String(l?.nhan || ""),
                diem: Number(l?.diem ?? 0),
              }))
            : [],
        }))
      : [],
    muc: Array.isArray(raw?.muc)
      ? raw.muc.map((m) => ({
          tu: Number(m?.tu ?? 0),
          den: Number(m?.den ?? 0),
          ten: String(m?.ten || ""),
          tom_tat: String(m?.tom_tat || ""),
        }))
      : [],
  };

  return {
    props: {
      kham,
      apiGoc,
    },
  };
}

export default function TrangKham({ kham, apiGoc = "" }) {
  const { tieu_de, cau, muc } = kham || {
    tieu_de: "T1 Khám",
    cau: [],
    muc: [],
  };

  const [chon, datChon] = useState({});
  const [email, datEmail] = useState("");
  const [zalo, datZalo] = useState("");
  const [website, datWebsite] = useState("");
  const [dongYLienHe, datDongYLienHe] = useState(false);
  const [dongYMarketing, datDongYMarketing] = useState(false);
  const [daNhanKetQua, datDaNhanKetQua] = useState(false);
  const [ketQuaDayDuServer, datKetQuaDayDuServer] = useState(null);
  const [thongBaoLoi, datThongBaoLoi] = useState("");

  const soDaChon = cau.filter((c) => typeof chon[c.ma] === "number").length;
  const daTraLoiDu = cau.length > 0 && soDaChon === cau.length;

  const tongDiem = cau.reduce((tong, c) => {
    const idx = chon[c.ma];
    if (typeof idx !== "number" || !Array.isArray(c.lua_chon) || !c.lua_chon[idx]) {
      return tong;
    }
    return tong + Number(c.lua_chon[idx].diem || 0);
  }, 0);

  const mucKetQua = daTraLoiDu
    ? muc.find((m) => Number(m.tu) <= tongDiem && tongDiem <= Number(m.den)) || null
    : null;

  async function guiNhanKetQua(e) {
    e.preventDefault();
    if (!mucKetQua) {
      return;
    }
    if (website.trim()) {
      return;
    }
    const emailTrim = email.trim();
    const zaloTrim = zalo.trim();
    if (!dongYLienHe || (!emailTrim && !zaloTrim)) {
      datDaNhanKetQua(false);
      datThongBaoLoi("Vui lòng nhập Email hoặc Zalo và đồng ý liên hệ để xem kết quả đầy đủ.");
      return;
    }

    datThongBaoLoi("");
    const endpoint = `${apiGoc || ""}/api/method/linhx_core.crm.api_form.nhan_ket_qua_t1`;
    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: emailTrim,
          zalo: zaloTrim,
          tong: Math.round(Number(tongDiem)),
          muc: String(mucKetQua.ten || ""),
          chon,
          dong_y_lien_he: Boolean(dongYLienHe),
          dong_y_marketing: Boolean(dongYMarketing),
        }),
      });
      if (res.status === 200) {
        const payload = await res.json().catch(() => ({}));
        const msg = payload?.message || payload || {};
        datKetQuaDayDuServer(msg?.ket_qua_day_du || null);
        datDaNhanKetQua(true);
      } else {
        datDaNhanKetQua(false);
        datThongBaoLoi("Máy chủ tạm thời chưa ghi nhận được yêu cầu. Vui lòng thử lại.");
      }
    } catch (_err) {
      datDaNhanKetQua(false);
      datThongBaoLoi("Không thể kết nối máy chủ. Vui lòng thử lại.");
    }
  }

  const dsLoTrinh = Array.isArray(ketQuaDayDuServer?.lo_trinh_de_xuat)
    ? ketQuaDayDuServer.lo_trinh_de_xuat
    : [];
  const dsHangMucServer = Array.isArray(ketQuaDayDuServer?.hang_muc)
    ? ketQuaDayDuServer.hang_muc
    : null;

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
          background: var(--bg);
          color: var(--chu);
          font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
            Roboto, sans-serif;
          line-height: 1.55;
          -webkit-font-smoothing: antialiased;
        }
        .khung {
          width: 100%;
          max-width: 860px;
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
        }
        .hero {
          padding: 32px 0 20px;
        }
        .hero h1 {
          font-size: clamp(22px, 4vw, 34px);
          line-height: 1.25;
          margin: 0 0 10px;
          word-break: break-word;
          overflow-wrap: anywhere;
        }
        .hero p {
          font-size: 15px;
          color: var(--phu);
          margin: 0;
          word-break: break-word;
          overflow-wrap: anywhere;
        }
        .ds-cau {
          display: flex;
          flex-direction: column;
          gap: 16px;
          padding: 8px 0 24px;
        }
        .khoi-cau {
          background: var(--mat);
          border: 1px solid var(--vien);
          border-radius: 14px;
          padding: 18px;
          min-width: 0;
        }
        .khoi-cau h2 {
          font-size: 16px;
          margin: 0 0 12px;
          line-height: 1.4;
          word-break: break-word;
          overflow-wrap: anywhere;
        }
        .ds-lua-chon {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        .nhan-lua-chon {
          display: flex;
          align-items: flex-start;
          gap: 10px;
          padding: 10px 12px;
          border: 1px solid var(--vien);
          border-radius: 10px;
          cursor: pointer;
          font-size: 15px;
          line-height: 1.45;
          word-break: break-word;
          overflow-wrap: anywhere;
        }
        .nhan-lua-chon.dang-chon {
          border-color: var(--nhan);
          background: var(--nhan-nhat);
        }
        .nhan-lua-chon input[type="radio"] {
          margin-top: 3px;
          flex-shrink: 0;
        }
        .khoi-tom-tat {
          background: var(--mat);
          border: 2px solid var(--nhan);
          border-radius: 14px;
          padding: 20px;
          margin: 8px 0 20px;
          min-width: 0;
        }
        .nhan-ket-qua {
          display: inline-block;
          font-size: 13px;
          font-weight: 600;
          padding: 4px 10px;
          border-radius: 999px;
          background: var(--xanh-nhat);
          color: var(--xanh);
          margin-bottom: 10px;
        }
        .khoi-tom-tat h2 {
          font-size: 20px;
          margin: 0 0 8px;
          word-break: break-word;
          overflow-wrap: anywhere;
        }
        .khoi-tom-tat p {
          font-size: 15px;
          color: var(--chu);
          margin: 0;
          word-break: break-word;
          overflow-wrap: anywhere;
        }
        .form-nhan-ket-qua {
          background: var(--mat);
          border: 1px solid var(--vien);
          border-radius: 14px;
          padding: 20px;
          margin: 0 0 24px;
          min-width: 0;
        }
        .form-nhan-ket-qua h3 {
          font-size: 18px;
          margin: 0 0 8px;
          word-break: break-word;
          overflow-wrap: anywhere;
        }
        .form-nhan-ket-qua p {
          font-size: 14px;
          color: var(--phu);
          margin: 0 0 14px;
          word-break: break-word;
          overflow-wrap: anywhere;
        }
        .dong-nhap {
          display: flex;
          flex-direction: column;
          gap: 6px;
          margin-bottom: 12px;
        }
        .dong-nhap label {
          font-size: 14px;
          font-weight: 600;
        }
        .dong-nhap input[type="email"],
        .dong-nhap input[type="text"] {
          width: 100%;
          max-width: 100%;
          padding: 10px 12px;
          border: 1px solid var(--vien);
          border-radius: 8px;
          font-size: 15px;
        }
        .dong-tick {
          display: flex;
          align-items: flex-start;
          gap: 8px;
          margin-bottom: 10px;
          font-size: 14px;
          cursor: pointer;
          word-break: break-word;
          overflow-wrap: anywhere;
        }
        .dong-tick input[type="checkbox"] {
          margin-top: 3px;
          flex-shrink: 0;
        }
        .nut-gui-ket-qua {
          display: inline-block;
          margin-top: 6px;
          padding: 10px 18px;
          border: none;
          border-radius: 10px;
          background: var(--nhan);
          color: #ffffff;
          font-size: 15px;
          font-weight: 600;
          cursor: pointer;
        }
        .loi-form {
          color: var(--do);
          font-size: 14px;
          margin-top: 10px;
        }
        .khoi-ket-qua-day-du {
          background: var(--mat);
          border: 2px solid var(--xanh);
          border-radius: 14px;
          padding: 20px;
          margin: 0 0 36px;
          min-width: 0;
        }
        .khoi-ket-qua-day-du h3 {
          font-size: 19px;
          margin: 0 0 12px;
          word-break: break-word;
          overflow-wrap: anywhere;
        }
        .ds-phan-tich {
          list-style: none;
          padding: 0;
          margin: 12px 0 0;
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        .ds-phan-tich li {
          padding: 10px 12px;
          border-radius: 10px;
          background: var(--bg);
          font-size: 14px;
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
          <a href="/" className="logo">
            <i className="cham-logo" aria-hidden="true" />
            <span>ifAgent · LINHX ENGINE</span>
          </a>
          <span className="nhan-bu">T1 Khám · LAB113</span>
        </header>

        <main>
          <section className="hero">
            <h1>{tieu_de}</h1>
            <p>
              Hoàn thành {cau.length} câu hỏi dưới đây để xem ngay bản tóm tắt mức độ
              sẵn sàng của doanh nghiệp ({soDaChon}/{cau.length} câu đã chọn).
            </p>
          </section>

          <section className="ds-cau" aria-label="Danh sách câu hỏi T1 Khám">
            {cau.map((c) => (
              <article key={c.ma} className="khoi-cau" data-cau={c.ma}>
                <h2>{c.hoi}</h2>
                <div className="ds-lua-chon">
                  {(c.lua_chon || []).map((l, idx) => {
                    const daChon = chon[c.ma] === idx;
                    return (
                      <label
                        key={idx}
                        className={`nhan-lua-chon${daChon ? " dang-chon" : ""}`}
                      >
                        <input
                          type="radio"
                          name={`cau_${c.ma}`}
                          value={idx}
                          checked={daChon}
                          onChange={() =>
                            datChon((cu) => ({
                              ...cu,
                              [c.ma]: idx,
                            }))
                          }
                        />
                        <span>{l.nhan}</span>
                      </label>
                    );
                  })}
                </div>
              </article>
            ))}
          </section>

          {daTraLoiDu && mucKetQua && (
            <>
              <section className="khoi-tom-tat" data-tom-tat>
                <span className="nhan-ket-qua">
                  Tổng điểm: {tongDiem} · Mức đánh giá
                </span>
                <h2>{mucKetQua.ten}</h2>
                <p>{mucKetQua.tom_tat}</p>
              </section>

              <form
                className="form-nhan-ket-qua"
                data-nhan-ket-qua
                onSubmit={guiNhanKetQua}
                noValidate
              >
                <h3>Nhận bản phân tích T1 đầy đủ</h3>
                <p>
                  Để lại Email hoặc Zalo để mở khoá chi tiết điểm từng hạng mục và lộ trình
                  tự động hoá đề xuất cho mức <strong>{mucKetQua.ten}</strong>.
                </p>
                <div style={{ display: "none" }} aria-hidden="true">
                  <label htmlFor="t1-website">Website</label>
                  <input
                    id="t1-website"
                    type="text"
                    name="website"
                    tabIndex={-1}
                    autoComplete="off"
                    value={website}
                    onChange={(e) => datWebsite(e.target.value)}
                  />
                </div>
                <div className="dong-nhap">
                  <label htmlFor="t1-email">Email nhận kết quả</label>
                  <input
                    id="t1-email"
                    type="email"
                    name="email"
                    maxLength={254}
                    placeholder="ban@doanhnghiep.vn"
                    value={email}
                    onChange={(e) => datEmail(e.target.value)}
                  />
                </div>
                <div className="dong-nhap">
                  <label htmlFor="t1-zalo">Hoặc số Zalo</label>
                  <input
                    id="t1-zalo"
                    type="text"
                    name="zalo"
                    maxLength={64}
                    placeholder="0912345678"
                    value={zalo}
                    onChange={(e) => datZalo(e.target.value)}
                  />
                </div>
                <label className="dong-tick">
                  <input
                    type="checkbox"
                    name="dong_y_lien_he"
                    checked={dongYLienHe}
                    onChange={(e) => datDongYLienHe(e.target.checked)}
                  />
                  <span>
                    Tôi đồng ý để ifAgent liên hệ tư vấn và gửi kết quả chẩn đoán T1.
                  </span>
                </label>
                <label className="dong-tick">
                  <input
                    type="checkbox"
                    name="dong_y_marketing"
                    checked={dongYMarketing}
                    onChange={(e) => datDongYMarketing(e.target.checked)}
                  />
                  <span>
                    Tôi đồng ý nhận tài liệu và bản tin cập nhật giải pháp AI (tùy chọn).
                  </span>
                </label>
                <button type="submit" className="nut-gui-ket-qua">
                  Xem kết quả đầy đủ
                </button>
                {thongBaoLoi && <div className="loi-form">{thongBaoLoi}</div>}
              </form>

              {daNhanKetQua && (
                <section className="khoi-ket-qua-day-du" data-ket-qua-day-du>
                  <span className="nhan-ket-qua">
                    Báo cáo chi tiết T1 · {ketQuaDayDuServer?.muc || mucKetQua.ten} (
                    {ketQuaDayDuServer?.tong ?? tongDiem} điểm)
                  </span>
                  <h3>Phân tích chi tiết và lộ trình đề xuất</h3>
                  <p>{ketQuaDayDuServer?.tom_tat || mucKetQua.tom_tat}</p>

                  {dsLoTrinh.length > 0 && (
                    <ul className="ds-phan-tich">
                      {dsLoTrinh.map((buoc, i) => (
                        <li key={i}>{buoc}</li>
                      ))}
                    </ul>
                  )}

                  <ul className="ds-phan-tich">
                    {dsHangMucServer
                      ? dsHangMucServer.map((hm) => (
                          <li key={hm.ma}>
                            <strong>{hm.hoi}</strong>
                            <div>
                              Hiện trạng: {hm.nhan} ({hm.diem}/4 điểm)
                            </div>
                            {hm.khuyen_nghi && <div>Khuyến nghị: {hm.khuyen_nghi}</div>}
                          </li>
                        ))
                      : cau.map((c) => {
                          const idx = chon[c.ma];
                          const daChon =
                            typeof idx === "number" && c.lua_chon && c.lua_chon[idx]
                              ? c.lua_chon[idx]
                              : null;
                          return (
                            <li key={c.ma}>
                              <strong>{c.hoi}</strong>
                              <div>
                                Hiện trạng: {daChon ? daChon.nhan : ""} ({daChon ? daChon.diem : 0}/4
                                điểm)
                              </div>
                            </li>
                          );
                        })}
                  </ul>
                </section>
              )}
            </>
          )}
        </main>

        <footer className="chan-trang">
          <span>LINHX ENGINE · Tool T1 Khám (LAB113)</span>
        </footer>
      </div>
    </>
  );
}
