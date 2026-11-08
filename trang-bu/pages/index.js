import fs from "node:fs";
import path from "node:path";
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

  return {
    props: {
      noiDung,
    },
  };
}

export default function TrangBU({ noiDung }) {
  const { tieu_de, mo_ta, muc } = noiDung || {
    tieu_de: "Trang BU",
    mo_ta: "",
    muc: [],
  };

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
          padding: 16px 0 48px;
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
        </main>

        <footer className="chan-trang">
          <span>LINHX ENGINE · Khuôn Trang BU tĩnh</span>
        </footer>
      </div>
    </>
  );
}
