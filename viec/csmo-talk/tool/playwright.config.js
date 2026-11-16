const os = require('os');
const path = require('path');
const { defineConfig } = require('@playwright/test');

// Xuất thư mục tạm ra os.tmpdir() để giữ sạch cây git
module.exports = defineConfig({
  testDir: path.join(__dirname, 'tests'),
  outputDir: path.join(os.tmpdir(), 'csmo-tool-pw-results'),
  timeout: 30000,
  fullyParallel: false,
  workers: 1,
  reporter: 'list',
  use: {
    headless: true,
    viewport: { width: 360, height: 800 },
    acceptDownloads: true
  }
});
