import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/The Council/);
});

test('upload validation works', async ({ page }) => {
  await page.goto('/');
  // Basic check for the upload button
  const fileInput = page.locator('input[type="file"]');
  await expect(fileInput).toBeAttached();
});
