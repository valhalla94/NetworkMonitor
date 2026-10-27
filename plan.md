1. **Add `type="button"` to non-submit buttons in `Dashboard.jsx`, `HostManager.jsx`, and `SettingsPage.jsx`**:
   - `frontend/src/components/Dashboard.jsx`: Add `type="button"` to clear filters button, chart type toggles, export CSV button, time range buttons, and status filter buttons.
   - `frontend/src/components/HostManager.jsx`: Add `type="button"` to the Save Edit, Cancel Edit, Edit Host, Delete Host, Add Host (header), Close Add Panel, Add First Host buttons.
   - `frontend/src/components/SettingsPage.jsx`: Add `type="button"` to the Dashboard back button and Logout button.
2. **Verify Frontend**:
   - Read the files to ensure changes are applied.
   - Run tests (`cd frontend && pnpm run test --run`).
   - Run linter (`cd frontend && pnpm run lint`).
3. **Verify Backend**:
   - No backend changes, but will run Python tests and ruff to be safe (`cd backend && ruff check . && pip install -r requirements.txt -r requirements-dev.txt && PYTHONPATH=. python -m pytest tests/`).
4. **Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.**
5. **Submit PR**.
