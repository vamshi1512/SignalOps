# SignalOps Frontend

React + TypeScript frontend for the SignalOps operations platform.

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
- The UI is optimized for a premium dark-mode operations console workflow
- Playwright smoke coverage uses a preview build for CI and local verification
