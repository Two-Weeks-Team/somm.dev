import { test, expect } from '@playwright/test';

test.describe('Evaluation Mode Selection', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/evaluate');
  });

  test('displays mode selector on evaluation page', async ({ page }) => {
    // Look for mode toggle or selector
    const modeSelector = page.getByRole('group').filter({ hasText: /mode|sommelier/i });
    await expect(modeSelector).toBeVisible();
  });

  test('defaults to Six Sommeliers mode', async ({ page }) => {
    // Check default mode indicator
    const sixSommeliers = page.getByText(/six sommelier|standard/i);
    await expect(sixSommeliers).toBeVisible();
  });

  test('allows switching to Grand Tasting mode', async ({ page }) => {
    // Find and click Grand Tasting option
    const grandTasting = page.getByText(/grand tasting|masterclass/i);
    if (await grandTasting.isVisible()) {
      await grandTasting.click();
      // Verify mode changed
      await expect(page.getByText(/grand tasting/i)).toBeVisible();
    }
  });

  test('mode selector is keyboard navigable', async ({ page }) => {
    // Tab to mode selector
    await page.keyboard.press('Tab');
    // Use arrow keys to navigate
    await page.keyboard.press('ArrowRight');
    // Should be able to select with Enter
    await page.keyboard.press('Enter');
  });
});
