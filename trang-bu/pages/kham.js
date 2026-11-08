import fs from "node:fs";
import path from "node:path";
import { useState } from "react";
import Head from "next/head";

function docKham() {
  const ungVien = [];
  const siteJson = process.env.SITE_JSON;
  if (siteJson && siteJson.trim()) {
    const thuMucSite = path.dirname(path.resolve(siteJson.trim()));
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
  const kham = {
    tieu_de: typeof raw?.tieu_de === "string" ? raw.tieu_de : "T1 Khám",
    cau: Array.isArray(raw?.cau) ? raw.cau : [],
    muc: Array.isArray(raw?.muc) ? raw.muc : [],
  };

  return {
    props: {
      kham,
    },
  };
}

export default function TrangKham({ kham }) {
  const { tieu_de, cau, muc } = kham || {
    tieu_de: "T1 Khám",
    cau: [],
    muc: [],
  };

  const [chon, datChon] = useState({});

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
          margin: 8px 0 36px;
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
            <section className="khoi-tom-tat" data-tom-tat>
              <span className="nhan-ket-qua">
                Tổng điểm: {tongDiem} · Mức đánh giá
              </span>
              <h2>{mucKetQua.ten}</h2>
              <p>{mucKetQua.tom_tat}</p>
            </section>
          )}
        </main>

        <footer className="chan-trang">
          <span>LINHX ENGINE · Tool T1 Khám (LAB113)</span>
        </footer>
      </div>
    </>
  );
}
