# Frontend – Network Monitor

This directory contains the **React + Vite** frontend for the Network Monitor application. It provides a premium, glass‑morphism UI that displays real‑time network status, host metrics, and public IP# Frontend – Network Monitor

This directory contains the **React + Vite** frontend for the Network Monitor application. It provides a premium, glass‑morphism UI that displays real‑time network status, host metrics, and public IP monitoring.

## Features
- Modern React UI with Vite for fast hot‑module replacement.
- Tailwind‑based styling with custom glass panels.
{{ ... }}
- Open the app in a browser and verify the dashboard loads.
- Check the **Public IP** card shows the current IP, last checked time, and duration badge.
- Use the Settings page to log in with the admin password.

---
*Happy monitoring!*ion
```bash
npm run build   # creates a production build in ./dist
```
The Dockerfile copies the `dist` folder into an Nginx image, which is used in the Docker Compose setup.

## Environment Variables
The frontend reads variables prefixed with `VITE_` at **build time**:
- `VITE_API_URL` – Base URL for the backend API (default `/api`).
- `VITE_ADMIN_PASSWORD` – Admin password for the Settings page.

These are defined in `docker-compose.yml` under the `frontend` service. If you change them, rebuild the image (`docker-compose up --build`).

## Running with Docker Compose
The full application (frontend, backend, InfluxDB) can be started with:
```bash
docker-compose up -d --build
```
Then open the dashboard at `http://<NAS‑IP>:3200` (or the port you configured).

## Testing
- Open the app in a browser and verify the dashboard loads.
- Check the **Public IP** card shows the current IP, last checked time, and duration badge.
- Use the Settings page to log in with the admin password.

---
*Happy monitoring!*
