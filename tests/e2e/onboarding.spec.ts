import { test, expect } from '@playwright/test';

/**
 * End-to-end test for the onboarding flow
 */
test.describe('Onboarding flow', () => {
  // Test login and automatic redirection to onboarding
  test('should redirect to onboarding after login', async ({ page }) => {
    // Start from login page
    await page.goto('/login');
    
    // Fill login form
    await page.fill('input[aria-label="Email"]', 'test@example.com');
    await page.fill('input[aria-label="Hasło"]', 'password123');
    
    // Submit form
    await page.click('button:has-text("Zaloguj się")');
    
    // Verify redirection to onboarding
    await expect(page).toHaveURL('/onboarding');
    await expect(page.locator('h2:has-text("Wybierz od 1 do 5 kategorii")')).toBeVisible();
  });
  
  // Test onboarding category selection
  test('should allow selecting categories and validate selection count', async ({ page }) => {
    // Mock authentication
    await page.addInitScript(() => {
      localStorage.setItem('auth_token', 'demo_token');
    });
    
    // Go to onboarding
    await page.goto('/onboarding');
    
    // Check initial state
    const continueButton = page.locator('button:has-text("Kontynuuj")');
    await expect(continueButton).toBeDisabled();
    
    // Select 3 categories
    const categories = page.locator('.v-chip');
    
    // Check initial selection count
    await expect(page.locator('.selection-count')).toContainText('Wybrano: 0/5');
    
    // Select first category
    await categories.nth(0).click();
    await expect(page.locator('.selection-count')).toContainText('Wybrano: 1/5');
    await expect(continueButton).toBeEnabled();
    
    // Select more categories
    await categories.nth(1).click();
    await categories.nth(2).click();
    await expect(page.locator('.selection-count')).toContainText('Wybrano: 3/5');
    
    // Try to select more than 5
    await categories.nth(3).click();
    await categories.nth(4).click();
    await expect(page.locator('.selection-count')).toContainText('Wybrano: 5/5');
    
    // Should show max selection warning
    await expect(page.locator('text=Osiągnięto maksymalną liczbę wyborów (5)')).toBeVisible();
    
    // Test deselecting a category
    await categories.nth(0).click();
    await expect(page.locator('.selection-count')).toContainText('Wybrano: 4/5');
    
    // Submit selection and verify redirection
    await continueButton.click();
    await expect(page).toHaveURL('/dashboard');
  });
  
  // Test error handling in onboarding
  test('should handle API errors properly', async ({ page }) => {
    // Mock authentication
    await page.addInitScript(() => {
      localStorage.setItem('auth_token', 'demo_token');
    });
    
    // Mock API error
    await page.route('/categories/suggestions', (route) => {
      route.fulfill({
        status: 502,
        body: JSON.stringify({ error: 'Service unavailable' })
      });
    });
    
    // Go to onboarding
    await page.goto('/onboarding');
    
    // Check if error dialog is displayed
    await expect(page.locator('text=Usługa niedostępna, spróbuj ponownie później')).toBeVisible();
    
    // Test retry button
    const retryButton = page.locator('button:has-text("Spróbuj ponownie")');
    await expect(retryButton).toBeVisible();
    
    // Mock successful response for retry
    await page.unroute('/categories/suggestions');
    await page.route('/categories/suggestions', (route) => {
      route.fulfill({
        status: 200,
        body: JSON.stringify([
          { id: '1', name: 'Jedzenie', usage_count: 120 },
          { id: '2', name: 'Transport', usage_count: 85 }
        ])
      });
    });
    
    // Click retry
    await retryButton.click();
    
    // Check if suggestions are loaded
    await expect(page.locator('.v-chip:has-text("Jedzenie")')).toBeVisible();
  });
  
  // Test keyboard navigation for accessibility
  test('should support keyboard navigation', async ({ page }) => {
    // Mock authentication
    await page.addInitScript(() => {
      localStorage.setItem('auth_token', 'demo_token');
    });
    
    // Go to onboarding
    await page.goto('/onboarding');
    
    // Wait for categories to be visible
    await page.waitForSelector('.v-chip');
    
    // Use tab to navigate to the first category
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Press space to select
    await page.keyboard.press('Space');
    await expect(page.locator('.selection-count')).toContainText('Wybrano: 1/5');
    
    // Navigate to continue button with tab
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press('Tab');
    }
    
    // Press enter to submit
    await page.keyboard.press('Enter');
    await expect(page).toHaveURL('/dashboard');
  });
}); 