
import { test, expect } from '@playwright/test';
import { isRealApiE2e } from './e2e-util.js';


test('frontend smoke: renders app and runs routing playground', async ({ page }) => {
  if (!isRealApiE2e()) {
    await page.route('**/api/route', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          selected_model: 'openrouter-llama',
          tier: 'cloud_fast',
          reason: 'Free cloud model selected',
          estimated_latency_ms: 280,
        }),
      });
    });

    await page.route('**/api/generate', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          response: 'OPENROUTER_OK',
        }),
      });
    });
  }

  await page.goto('/');

  await expect(page.getByRole('heading', { name: 'Edge LLM Architect' })).toBeVisible();
  await expect(page.getByText('Free LLMs for Mobile & Edge Deployment')).toBeVisible();

  await page.getByPlaceholder('Type a prompt to test routing...').fill('Say OPENROUTER_OK');
  await page.getByRole('button', { name: 'Run Routing Test' }).click();

  if (!isRealApiE2e()) {
    await expect(page.getByText('openrouter-llama')).toBeVisible();
    await expect(page.getByText('cloud_fast')).toBeVisible();
    await expect(page.getByText('Free cloud model selected')).toBeVisible();
    await expect(page.locator('.test-response p')).toHaveText('OPENROUTER_OK');
  } else {
    // Real API: check for presence of expected fields, not stubbed values
    // Model name: should be visible (any non-empty string)
    const modelText = await page.locator('.test-model').textContent();
    expect(modelText).toBeTruthy();
    // Tier: should be visible (e.g., 'local', 'cloud_fast', etc.)
    const tierText = await page.locator('.test-tier').textContent();
    expect(tierText).toBeTruthy();
    // Reason: should be visible (any non-empty string)
    const reasonText = await page.locator('.test-reason').textContent();
    expect(reasonText).toBeTruthy();
    // Response: should be visible (any non-empty string)
    const responseText = await page.locator('.test-response p').textContent();
    expect(responseText).toBeTruthy();
  }
});
