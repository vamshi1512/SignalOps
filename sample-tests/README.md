# Sample Test Suites

The platform seeds suite commands that mirror the files in this directory.

- API suites use `pytest` and target the FastAPI mock routes under `/api/v1/target-api`.
- UI suites use Playwright and target the mock HTML pages under `/api/v1/target-ui`.

Examples:

```bash
TARGET_BASE_URL=http://localhost:8000/api/v1/target-api pytest sample-tests/api/tests/test_checkout_api.py -m smoke
TARGET_UI_BASE_URL=http://localhost:8000/api/v1/target-ui npx playwright test sample-tests/ui/tests/checkout-journey.spec.ts
```
