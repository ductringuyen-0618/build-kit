# Frontend skeleton: Vite + React + TypeScript

A description, not a generator. Use only if the prompt needs a UI. In a
three-hour build the frontend is one page with the three flows the issue
names; no router, tab or state switching inside `App.tsx`.

## Layout

```
frontend/
  src/
    main.tsx
    App.tsx                 single page; tab state lives here if needed
    config/api.ts           API_BASE_URL from VITE_API_BASE_URL, same-origin fallback
    components/<Feature>.tsx
    components/ui/          only what is used
  e2e/                      Playwright specs (optional, see verify-feature)
  index.html
  vite.config.ts            server.port fixed, strictPort: true
  tsconfig.json
  .prettierrc               singleQuote, printWidth 80, tabWidth 2, arrowParens avoid, trailingComma es5, endOfLine lf
  package.json
```

## `config/api.ts`

```ts
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? window.location.origin;

// Trailing slashes are deliberate: FastAPI's redirect drops CORS headers.
export const ENDPOINTS = {
  health: `${API_BASE_URL}/health`,
  items: `${API_BASE_URL}/api/items/`,
};
```

On App Platform the frontend is a `static_sites` component and the API
is a `services` component behind an ingress rule on `/api`, so the
same-origin fallback is what production uses. Locally set
`VITE_API_BASE_URL=http://localhost:8000` in `frontend/.env.local`.

## Scripts

```json
{
  "dev": "vite",
  "build": "tsc -b && vite build",
  "typecheck": "tsc --noEmit",
  "lint": "eslint .",
  "format:check": "prettier --check src",
  "verify": "npm run typecheck && npm run lint && npm run format:check && npm run build",
  "test:e2e": "playwright test"
}
```

`npm run verify` is the frontend gate the CI template runs.

## Testing

There is no unit-test runner in this skeleton on purpose. The check is
`npm run verify` plus, if time allows, one Playwright spec per main flow
and the exhaustive click sweep described in `skills/verify-feature`.
Select elements by ARIA role and accessible name.

## Aesthetic

Pick one direction and say it in the README. If the `designer-skills`
pack is installed, `frontend-design` lists named philosophies with
concrete type, colour, spacing and motion rules. Without it: one display
font, one body font, one accent colour, CSS variables for both light and
dark, 44px touch targets, 16px body on mobile.
