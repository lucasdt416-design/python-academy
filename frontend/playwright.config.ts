import {defineConfig} from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 90000,
  use: {
    baseURL: 'http://127.0.0.1:3000',
    // Opt-in only for isolated test environments with an HTTPS inspection proxy.
    ignoreHTTPSErrors: process.env.TEST_IGNORE_HTTPS_ERRORS === '1',
    browserName: 'chromium',
    launchOptions: process.env.CHROMIUM_PATH ? {
      executablePath: process.env.CHROMIUM_PATH,
      args: ['--no-sandbox', '--disable-dev-shm-usage'],
      ...(process.env.HTTPS_PROXY ? {proxy: {server: process.env.HTTPS_PROXY, bypass: '127.0.0.1,localhost'}} : {}),
    } : {},
  },
  webServer: {
    command: 'npm start -- --port 3000',
    url: 'http://127.0.0.1:3000',
    reuseExistingServer: !process.env.CI,
  },
});
