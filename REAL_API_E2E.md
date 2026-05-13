# Real API E2E Testing

To run Playwright end-to-end tests against the real backend API (no stubs), set the environment variable `REAL_API_E2E=1` when running the test command. This will disable Playwright's API stubbing and send real requests to your backend.

**Steps:**

1. **Start the backend server** (in a separate terminal):
   ```bash
   # Example: FastAPI backend
   uvicorn api_server:app --host 127.0.0.1 --port 8000
   # Or your backend start command
   ```

2. **Start the frontend dev server** (if not using Playwright's webServer):
   ```bash
   npm run dev
   # Or let Playwright auto-start it (default)
   ```

3. **Run Playwright e2e with real API:**
   ```bash
   REAL_API_E2E=1 npm run test:e2e
   ```

- If `REAL_API_E2E` is not set, tests will use stubbed API responses (default, fast, safe for CI).
- If `REAL_API_E2E=1`, tests will hit the real backend API endpoints.

**Note:**
- Make sure your backend is running and accessible at the expected API base URL.
- You can customize the API base URL in `playwright.config.js` if needed.

---

## Troubleshooting
- If tests fail with network errors, check that both frontend and backend servers are running and reachable.
- For debugging, use `npm run test:e2e:headed` to see the browser UI.

---

See `e2e/frontend-smoke.spec.js` for the test logic and how the flag is used.
