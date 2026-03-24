# TestForge Frontend

React + TypeScript frontend for the TestForge QA automation management platform.

## Commands

```bash
npm install
npm run dev
npm run lint
npm run test:run
npm run build
npm run test:e2e
```

## Notes

- Development requests to `/api/*` proxy to `http://localhost:8000`
- Development requests to `/artifacts/*` proxy to `http://localhost:8000`
- The UI supports both premium dark and light execution-console themes
- Playwright smoke coverage uses a preview build for CI and local verification
