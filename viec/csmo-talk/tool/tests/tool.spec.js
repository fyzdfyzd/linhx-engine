const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const { test, expect } = require('@playwright/test');

const TOOL_DIR = path.resolve(__dirname, '..');
const INDEX_HTML_PATH = path.join(TOOL_DIR, 'index.html');
const EVIDENCE_DIR = path.resolve(TOOL_DIR, '..', 'bang-chung', 'csmo-tool');
const MAX_IMAGE_BYTES = 400 * 1024; // <= 400 KB mỗi ảnh

// 134 chữ cái tiếng Việt có dấu (67 chữ thường + 67 chữ hoa)
const VIETNAMESE_LOWER_67 =
  'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ';
const VIETNAMESE_ALL_134 = VIETNAMESE_LOWER_67 + VIETNAMESE_LOWER_67.toUpperCase();

let server;
let baseUrl = '';

test.beforeAll(async () => {
  fs.mkdirSync(EVIDENCE_DIR, { recursive: true });

  // Máy chủ tĩnh nội bộ tiền cảnh để kiểm thử thực tế trên giao thức http://127.0.0.1
  server = http.createServer((req, res) => {
    const cleanUrl = (req.url || '/').split('?')[0];
    if (cleanUrl === '/' || cleanUrl === '/index.html') {
      const html = fs.readFileSync(INDEX_HTML_PATH);
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(html);
      return;
    }
    if (cleanUrl === '/favicon.ico') {
      res.writeHead(204);
      res.end();
      return;
    }
    res.writeHead(404);
    res.end('Not found');
  });

  await new Promise((resolve) => {
    server.listen(0, '127.0.0.1', () => {
      const addr = server.address();
      baseUrl = `http://127.0.0.1:${addr.port}/`;
      resolve();
    });
  });
});

test.afterAll(async () => {
  if (server) {
    await new Promise((resolve) => server.close(resolve));
  }
});

// Chặn phông ngoài khi kiểm thử để chạy nhanh, ổn định và tuyệt đối không phụ thuộc mạng
async function setupOfflineSafePage(page, consoleErrors) {
  page.on('pageerror', (err) => consoleErrors.push(String(err)));
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });
  await page.route('https://fonts.googleapis.com/**', (route) =>
    route.fulfill({ status: 200, contentType: 'text/css', body: '' })
  );
  await page.route('https://fonts.gstatic.com/**', (route) => route.abort());
}

test('1. Tuân thủ luật nội dung: tự chứa, không tên thương hiệu cấm, đủ 134 chữ tiếng Việt có dấu', async ({ page }) => {
  expect(VIETNAMESE_ALL_134.length).toBe(134);

  const htmlSource = fs.readFileSync(INDEX_HTML_PATH, 'utf8');
  expect(htmlSource).not.toContain('\uFFFD');

  // Không nêu tên thương hiệu cấm (ghép động để tránh dương tính giả khi quét chuỗi nguyên văn)
  const forbiddenPatterns = [
    new RegExp('\\b' + 'ur' + 'ah\\b', 'i'),
    new RegExp('\\b' + 'sake' + 'demy\\b', 'i'),
    new RegExp('\\b' + 'tu' + 'va\\b', 'i'),
    new RegExp('\\b' + 'if\\s*' + 'agent\\b', 'i'),
    new RegExp('\\b' + 'bt' + 'mh\\b', 'i')
  ];
  for (const pattern of forbiddenPatterns) {
    expect(htmlSource).not.toMatch(pattern);
  }

  // Không nạp script hay stylesheet ngoài trừ Google Fonts
  const externalTags = htmlSource.match(/<(?:script|link)\b[^>]*(?:src|href)=["']https?:\/\/[^"']+["'][^>]*>/gi) || [];
  for (const tag of externalTags) {
    expect(tag).toMatch(/fonts\.(?:googleapis|gstatic)\.com/i);
  }

  const consoleErrors = [];
  await setupOfflineSafePage(page, consoleErrors);
  await page.goto(baseUrl);

  // Kiểm tra 134 chữ có dấu hiển thị đúng trong trình duyệt (độ rộng glyph > 0, nguyên vẹn chuỗi NFC)
  const glyphAudit = await page.evaluate((chars134) => {
    const probe = document.createElement('div');
    probe.style.fontFamily = getComputedStyle(document.body).fontFamily;
    probe.style.fontSize = '20px';
    probe.textContent = chars134;
    document.body.appendChild(probe);

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.font = `20px ${getComputedStyle(document.body).fontFamily}`;

    const zeroWidth = [];
    for (const ch of chars134) {
      const width = ctx.measureText(ch).width;
      if (!(width > 0)) {
        zeroWidth.push(ch);
      }
    }
    const renderedText = probe.textContent;
    probe.remove();
    return {
      matchesExact: renderedText === chars134 && renderedText.normalize('NFC') === chars134,
      zeroWidthCount: zeroWidth.length
    };
  }, VIETNAMESE_ALL_134);

  expect(glyphAudit.matchesExact).toBe(true);
  expect(glyphAudit.zeroWidthCount).toBe(0);
  expect(consoleErrors).toEqual([]);
});

test('2. Luồng E2E đầy đủ: 2 câu đầu trang -> Bước 1 -> Bước 2 -> Bước 3 -> Bước 4 (điểm & "bước X" & tải .md)', async ({ page }) => {
  const consoleErrors = [];
  const externalRequests = [];
  await setupOfflineSafePage(page, consoleErrors);

  page.on('request', (req) => {
    const url = req.url();
    if (!url.startsWith('http://127.0.0.1') && !url.startsWith('blob:') && !url.includes('fonts.g')) {
      externalRequests.push(url);
    }
  });

  await page.goto(baseUrl);

  // Kiểm tra hàm guiKetQua() tồn tại ở window để chờ nối máy chủ sau
  const hasGuiKetQua = await page.evaluate(() => typeof window.guiKetQua === 'function');
  expect(hasGuiKetQua).toBe(true);

  // Đầu trang: 2 câu đo cảm nhận
  await page.locator('.scale-btn[data-rating="2"]').click();
  await page.fill('#monday-action-input', 'Đặt Bảng sự thật bằng chữ lên trang giới thiệu trước sáng thứ Hai');
  await page.click('#save-pulse-btn');
  await expect(page.locator('#pulse-status')).toBeVisible();

  // Kiểm tra bắt lỗi khi bấm sang Bước 2 mà để trống Bước 1
  await page.click('#to-step-2-btn');
  await expect(page.locator('#err-brand-name')).toBeVisible();

  // Điền Bước 1
  await page.fill('#brand-name', 'Trà Bản Mộc');
  await page.fill('#industry', 'quà tặng trà đặc sản cho doanh nghiệp');
  await page.fill('#target-customer', 'trưởng phòng nhân sự và hành chính tại công ty 100–500 người');
  await page.fill('#competitor', 'Trà Việt Cổ');
  await page.fill('#fact-1', 'Cung cấp quà tết cho 420 doanh nghiệp tính đến 11/2026, danh sách công khai trên web');
  await page.fill('#fact-2', 'Đạt chứng nhận ISO 22000:2018, bảng giá niêm yết từ 350.000đ đến 1.200.000đ/hộp');
  await page.fill('#fact-3', '4,8/5 trên 1.450 đánh giá xác thực, 98% đơn bù đổi xử lý trong 24 giờ');

  // Tải lại trang kiểm tra lưu và đọc localStorage
  await page.reload();
  await expect(page.locator('#brand-name')).toHaveValue('Trà Bản Mộc');
  await expect(page.locator('.scale-btn[data-rating="2"]')).toHaveAttribute('aria-pressed', 'true');
  await expect(page.locator('#monday-action-input')).toHaveValue(
    'Đặt Bảng sự thật bằng chữ lên trang giới thiệu trước sáng thứ Hai'
  );

  // Sang Bước 2 kiểm tra nguyên văn 3 câu hỏi từ KICH-BAN-v5.md
  await page.click('#to-step-2-btn');
  await expect(page.locator('#step-2')).toBeVisible();

  await expect(page.locator('#prompt-presence')).toHaveText(
    'Tôi đang tìm quà tặng trà đặc sản cho doanh nghiệp tại Việt Nam cho trưởng phòng nhân sự và hành chính tại công ty 100–500 người. Giới thiệu 5 lựa chọn đáng cân nhắc nhất và lý do.'
  );
  await expect(page.locator('#prompt-accuracy')).toHaveText(
    'Trà Bản Mộc là ai, làm gì, bán gì, cho ai, giá khoảng bao nhiêu? Nêu nguồn.'
  );
  await expect(page.locator('#prompt-recommendation')).toHaveText(
    'So sánh Trà Bản Mộc với Trà Việt Cổ. Nếu tôi là trưởng phòng nhân sự và hành chính tại công ty 100–500 người, bạn khuyên chọn bên nào, vì sao?'
  );

  await expect(page.locator('#open-chatgpt-link')).toHaveAttribute('href', 'https://chatgpt.com');
  await expect(page.locator('#open-gemini-link')).toHaveAttribute('href', 'https://gemini.google.com');

  await page.locator('.copy-prompt-btn[data-prompt-id="presence"]').click();
  await expect(page.locator('#copy-status')).toBeVisible();

  // Sang Bước 3: mặc định 0 lần có mặt -> Bước 4 báo "đang rơi ở bước 1"
  await page.click('#to-step-3-btn');
  await expect(page.locator('#step-3')).toBeVisible();
  await page.click('#to-step-4-btn');
  await expect(page.locator('#step-4')).toBeVisible();
  await expect(page.locator('#score-presence')).toHaveText('0');
  await expect(page.locator('#diagnosis-headline')).toContainText('đang rơi ở bước 1');

  // Quay lại Bước 3 tích kịch bản rơi ở bước 2 và 3 (Có mặt 3/6 = 50, 2 đúng + 1 sai = 67, Không khuyên = 0, Khác nhau = 0)
  await page.locator('[data-step-jump="3"]').click();
  await page.locator('.presence-btn[data-presence-index="0"]').click();
  await page.locator('.presence-btn[data-presence-index="1"]').click();
  await page.locator('.presence-btn[data-presence-index="3"]').click();
  await page.locator('.fact-status-btn[data-fact-index="0"][data-fact-val="dung"]').click();
  await page.locator('.fact-status-btn[data-fact-index="1"][data-fact-val="dung"]').click();
  await page.locator('.fact-status-btn[data-fact-index="2"][data-fact-val="sai"]').click();
  await page.locator('.recommended-btn[data-rec-val="khong"]').click();
  await page.locator('.consistent-btn[data-cons-val="khac"]').click();

  await page.click('#to-step-4-btn');
  await expect(page.locator('#score-presence')).toHaveText('50');
  await expect(page.locator('#score-accuracy')).toHaveText('67');
  await expect(page.locator('#score-recommendation')).toHaveText('0');
  await expect(page.locator('#score-consistency')).toHaveText('0');
  await expect(page.locator('#diagnosis-headline')).toContainText('đang rơi ở bước 2 và 3');

  // Kiểm tra kịch bản rơi ở bước 4 và 5 (Có mặt 6/6 = 100, Đúng 3/3 = 100, Giống = 100, Không khuyên = 0)
  await page.locator('[data-step-jump="3"]').click();
  await page.locator('.presence-btn[data-presence-index="2"]').click();
  await page.locator('.presence-btn[data-presence-index="4"]').click();
  await page.locator('.presence-btn[data-presence-index="5"]').click();
  await page.locator('.fact-status-btn[data-fact-index="2"][data-fact-val="dung"]').click();
  await page.locator('.consistent-btn[data-cons-val="giong"]').click();
  await page.click('#to-step-4-btn');
  await expect(page.locator('#score-presence')).toHaveText('100');
  await expect(page.locator('#score-accuracy')).toHaveText('100');
  await expect(page.locator('#score-consistency')).toHaveText('100');
  await expect(page.locator('#score-recommendation')).toHaveText('0');
  await expect(page.locator('#diagnosis-headline')).toContainText('đang rơi ở bước 4 và 5');

  // Kiểm tra tải mẫu "Bảng sự thật 1 trang" (.md) tạo ngay trong trình duyệt
  const downloadPromise = page.waitForEvent('download');
  await page.click('#download-truth-sheet-btn');
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe('bang-su-that-1-trang-tra-ban-moc.md');

  const downloadPath = await download.path();
  const mdText = fs.readFileSync(downloadPath, 'utf8');
  expect(mdText).toContain('# BẢNG SỰ THẬT THƯƠNG HIỆU (1 TRANG)');
  expect(mdText).toContain('Trà Bản Mộc');
  expect(mdText).toContain('Cung cấp quà tết cho 420 doanh nghiệp');

  // Không gọi bất kỳ API AI hay máy chủ ngoài nào
  expect(externalRequests).toEqual([]);
  expect(consoleErrors).toEqual([]);
});

test('3. Bền vững khi localStorage bị chặn (try/catch an toàn)', async ({ context }) => {
  const page = await context.newPage();
  const consoleErrors = [];
  await setupOfflineSafePage(page, consoleErrors);

  await page.addInitScript(() => {
    Object.defineProperty(window, 'localStorage', {
      get() {
        throw new Error('Blocked Storage');
      }
    });
  });

  await page.goto(baseUrl);
  await page.fill('#brand-name', 'Gốm Minh Châu');
  await page.fill('#industry', 'gốm sứ bàn ăn khách sạn');
  await page.fill('#target-customer', 'bếp trưởng nhà hàng 4–5 sao');
  await page.fill('#competitor', 'Gốm Đông Phương');
  await page.fill('#fact-1', 'Cung cấp cho 85 khách sạn tại 12 tỉnh thành');
  await page.fill('#fact-2', 'Đạt kiểm định không chì tiêu chuẩn châu Âu');
  await page.fill('#fact-3', 'Bảo hành mẻ cạnh 12 tháng đổi mới');
  await page.click('#to-step-2-btn');
  await expect(page.locator('#prompt-accuracy')).toContainText('Gốm Minh Châu là ai');
  expect(consoleErrors).toEqual([]);
  await page.close();
});

test('4. Chuẩn 360px & 1280px (chữ >= 16px, nút >= 44px, không cuộn ngang, axe WCAG AA) và xuất ảnh bằng chứng <= 400 KB', async ({ browser }) => {
  const viewports = [
    { label: '360', width: 360, height: 800 },
    { label: '1280', width: 1280, height: 860 }
  ];

  // Thử nạp axe-core nếu có sẵn trong môi trường kiểm thử
  let axeSource = null;
  try {
    const axePath = require.resolve('axe-core/axe.min.js');
    axeSource = fs.readFileSync(axePath, 'utf8');
  } catch (_) {
    axeSource = null;
  }

  const hashes = new Set();

  for (const vp of viewports) {
    const context = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
      deviceScaleFactor: 1
    });
    const page = await context.newPage();
    const consoleErrors = [];
    await setupOfflineSafePage(page, consoleErrors);

    await page.goto(baseUrl);

    // Điền dữ liệu thực tế rõ nghĩa để chụp từng bước
    await page.locator('.scale-btn[data-rating="3"]').click();
    await page.fill('#monday-action-input', 'Viết Bảng sự thật một trang đặt lên web bằng chữ');
    await page.fill('#brand-name', 'Trà Bản Mộc');
    await page.fill('#industry', 'quà tặng trà đặc sản cho doanh nghiệp');
    await page.fill('#target-customer', 'trưởng phòng nhân sự tại công ty 100–500 người');
    await page.fill('#competitor', 'Trà Việt Cổ');
    await page.fill('#fact-1', 'Phục vụ 420 doanh nghiệp tính đến 11/2026, danh sách công khai trên website');
    await page.fill('#fact-2', 'Đạt ISO 22000:2018, giá niêm yết công khai từ 350.000đ/hộp');
    await page.fill('#fact-3', '4,8/5 trên 1.450 đánh giá, 98% khiếu nại xử lý trong 24 giờ');

    for (const stepNum of [1, 2, 3, 4]) {
      if (stepNum === 2) {
        // Từ Bước 2 thu gọn khối cảm nhận đầu trang để ảnh tập trung vào từng bước
        await page.click('#toggle-pulse-btn');
        await page.click('#to-step-2-btn');
      } else if (stepNum === 3) {
        await page.click('#to-step-3-btn');
        await page.locator('.presence-btn[data-presence-index="0"]').click();
        await page.locator('.presence-btn[data-presence-index="1"]').click();
        await page.locator('.presence-btn[data-presence-index="3"]').click();
        await page.locator('.fact-status-btn[data-fact-index="0"][data-fact-val="dung"]').click();
        await page.locator('.fact-status-btn[data-fact-index="1"][data-fact-val="dung"]').click();
        await page.locator('.fact-status-btn[data-fact-index="2"][data-fact-val="sai"]').click();
        await page.locator('.recommended-btn[data-rec-val="khong"]').click();
        await page.locator('.consistent-btn[data-cons-val="khac"]').click();
      } else if (stepNum === 4) {
        await page.click('#to-step-4-btn');
      }

      // Kiểm tra không cuộn ngang, chữ >= 16px, vùng chạm nút >= 44px
      const layoutAudit = await page.evaluate(() => {
        const docWidth = document.documentElement.scrollWidth;
        const winWidth = window.innerWidth;

        const smallFonts = [];
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let node;
        while ((node = walker.nextNode())) {
          if (!node.nodeValue || !node.nodeValue.trim()) continue;
          const el = node.parentElement;
          if (!el) continue;
          const rect = el.getBoundingClientRect();
          if (rect.width === 0 || rect.height === 0) continue;
          const fsPx = parseFloat(window.getComputedStyle(el).fontSize);
          if (fsPx < 16) {
            smallFonts.push({ tag: el.tagName, text: node.nodeValue.trim().slice(0, 30), fsPx });
          }
        }

        const smallTargets = [];
        document.querySelectorAll('button, a.btn, input, textarea').forEach((el) => {
          const rect = el.getBoundingClientRect();
          if (rect.width === 0 || rect.height === 0) return;
          if (rect.height < 44 || rect.width < 44) {
            smallTargets.push({
              tag: el.tagName,
              id: el.id || el.textContent.trim().slice(0, 25),
              w: Math.round(rect.width),
              h: Math.round(rect.height)
            });
          }
        });

        return { docWidth, winWidth, smallFonts, smallTargets };
      });

      expect(layoutAudit.docWidth).toBeLessThanOrEqual(layoutAudit.winWidth);
      expect(layoutAudit.smallFonts).toEqual([]);
      expect(layoutAudit.smallTargets).toEqual([]);

      // Kiểm tra axe WCAG 2.2 AA (0 serious / critical) nếu có axe-core
      if (axeSource) {
        const hasAxe = await page.evaluate(() => typeof window.axe !== 'undefined');
        if (!hasAxe) {
          await page.addScriptTag({ content: axeSource });
        }
        const axeResults = await page.evaluate(async () => {
          const res = await window.axe.run(document, {
            runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'] }
          });
          return res.violations.filter((v) => v.impact === 'serious' || v.impact === 'critical');
        });
        expect(axeResults).toEqual([]);
      }

      // Chụp ảnh PNG từng bước vào viec/csmo-talk/bang-chung/csmo-tool/
      const shotPath = path.join(EVIDENCE_DIR, `buoc-${stepNum}-${vp.label}.png`);
      await page.screenshot({ path: shotPath, fullPage: true });

      const stat = fs.statSync(shotPath);
      expect(stat.size).toBeGreaterThan(1000);
      expect(stat.size).toBeLessThanOrEqual(MAX_IMAGE_BYTES);

      const digest = crypto.createHash('sha256').update(fs.readFileSync(shotPath)).digest('hex');
      expect(hashes.has(digest)).toBe(false);
      hashes.add(digest);
    }

    expect(consoleErrors).toEqual([]);
    await context.close();
  }
});
