# Minimal Playwright smoke suite

Copy, fill in the two placeholders (`PORT`, the feature path), run. The
suite is deliberately small: it proves the app is alive and that one
feature works, so it stays green and fast enough to run on every change.

## Install (Node)

```bash
npm i -D @playwright/test
npx playwright install chromium
```

## `playwright.config.ts`

```ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  retries: 0,
  reporter: 'line',
  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:PORT',
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
});
```

Setting `baseURL` from an env var lets one suite target a local server,
a preview deploy, or a moved port without edits.

## `e2e/smoke.spec.ts`

```ts
import { test, expect, Page } from '@playwright/test';

function watchErrors(page: Page) {
  const errors: string[] = [];
  page.on('pageerror', e => errors.push(`pageerror: ${e.message}`));
  page.on('console', m => {
    if (m.type() === 'error') errors.push(`console.error: ${m.text()}`);
  });
  return errors;
}

test('root loads with a heading and no errors', async ({ page }) => {
  const errors = watchErrors(page);
  const res = await page.goto('/');
  expect(res?.status()).toBe(200);
  await expect(page.getByRole('heading').first()).toBeVisible();
  expect(errors).toEqual([]);
});

test('every top-level nav item renders a page', async ({ page }) => {
  await page.goto('/');
  const nav = page.getByRole('navigation').first();
  const count = await nav.getByRole('link').count();
  expect(count).toBeGreaterThan(0);
  for (let i = 0; i < count; i++) {
    const errors = watchErrors(page);
    await nav.getByRole('link').nth(i).click();
    await page.waitForLoadState('networkidle');
    await expect(page.locator('body')).not.toBeEmpty();
    expect(errors).toEqual([]);
  }
});

test('the API the UI depends on answers', async ({ request }) => {
  // Replace with the one call the first screen cannot render without.
  const res = await request.get('/api/health');
  expect(res.status()).toBe(200);
  expect(await res.json()).toMatchObject({ status: expect.any(String) });
});

test('feature under test: full user path', async ({ page }) => {
  const errors = watchErrors(page);
  await page.goto('/');
  // 1. Entry point, by role and accessible name, never by CSS class.
  // await page.getByRole('link', { name: /feature/i }).click();
  // 2. Action.
  // await page.getByRole('button', { name: /save/i }).click();
  // 3. Observable result, read back through the user path.
  // await expect(page.getByText(/saved/i)).toBeVisible();
  await page.screenshot({ path: 'e2e-results/feature-end-state.png', fullPage: true });
  expect(errors).toEqual([]);
});
```

## Run

```bash
BASE_URL=http://localhost:PORT npx playwright test e2e/smoke.spec.ts --reporter=line
```

Paste the full output into the report. On failure,
`npx playwright show-trace test-results/**/trace.zip` opens the recorded
trace.

## Selector rules

- Prefer `getByRole` with an accessible name, then `getByLabel`,
  `getByPlaceholder`, `getByText`, then `data-testid`. Never CSS classes
  or coordinates.
- Use `exact: true` when a loose regex would also match a badge or a
  toast ("Saved" vs "Unsaved changes").
- Assert on shape and non-emptiness for live data, never on specific
  records that ingestion or time will change.

## Python equivalent

```bash
pip install pytest-playwright
playwright install chromium
```

```python
# tests/e2e/test_smoke.py
import os
from playwright.sync_api import Page, expect

BASE = os.environ.get("BASE_URL", "http://localhost:PORT")


def test_root_loads(page: Page):
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    resp = page.goto(BASE + "/")
    assert resp.status == 200
    expect(page.get_by_role("heading").first).to_be_visible()
    assert errors == []
```

Run with `pytest tests/e2e -q` and paste the output.

## Exhaustive sweep (optional, slow)

When a feature adds many controls, a scenario spec covers only the path
you wrote. A sweep spec discovers every visible `button`, `a[href]`,
`[role=tab]`, `input`, `select` on each top-level page, clicks each,
and fails on any page error. Tag it (`@exhaustive`) and exclude it from
the fast loop with `--grep-invert @exhaustive`. Keep a denylist of
destructive names (delete, remove, clear, sign out, wipe) so the sweep
skips them. An early click that mutates the DOM can make a later
element stale; treat that as "triage by hand", not as a bug.
