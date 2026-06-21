# Network Monitor

[![CI](https://github.com/valhalla94/NetworkMonitor/actions/workflows/ci.yml/badge.svg)](https://github.com/valhalla94/NetworkMonitor/actions/workflows/ci.yml)

A self-hosted network monitoring dashboard built with React 19 and FastAPI. Monitor uptime, latency, and status of your network devices in real-time. Optimized for low-power devices like Synology NAS or Raspberry Pi.

## Features

- **Real-time Monitoring**: Latency and uptime for multiple hosts (ICMP/Ping, HTTP, TCP) via Server-Sent Events
- **Smart Notifications**: Alerts via Discord, Telegram, Email, and more when a host goes DOWN or UP. Powered by **Apprise**
- **Internet Speed Test**: Built-in speed test (Download, Upload, Ping) with historical tracking
- **Quick Ping**: Instantly ping any IP or hostname without adding it to the monitor
- **Network Health**: Global average latency across all monitored hosts
- **Public IP Tracking**: Monitor public IP address and view change history
- **Historical Charts**: Interactive latency charts (1h, 24h, 7d, 30d, 1y). Data retained 30 days
- **SSL Certificate Monitoring**: Alerts when certificates are about to expire
- **Host Management**: Add, edit, and delete hosts via a JWT-authenticated settings interface
- **Dark/Light Theme**: Toggle between themes with persistent preference
- **Audit Log**: Track all configuration changes
- **Responsive Design**: Glassmorphism UI, works on desktop and mobile
- **Dockerized**: Single `docker-compose up` deployment

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React 19, Vite 7, TailwindCSS 3, Recharts 3, React Router 7 |
| **Backend** | Python 3.11, FastAPI 0.109, APScheduler 3.10, SQLAlchemy 2 |
| **Auth** | JWT (python-jose), bcrypt, rate limiting (slowapi) |
| **Database** | SQLite with WAL mode |
| **Notifications** | Apprise |
| **Deploy** | Docker Compose, Nginx reverse proxy |

## Quick Start

**Prerequisites**: Docker and Docker Compose installed.

1. Clone the repository:
   ```bash
   git clone https://github.com/valhalla94/NetworkMonitor.git
   cd NetworkMonitor
   ```

2. Set required environment variables (create a `.env` file):
   ```bash
   SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
   ADMIN_PASSWORD=your-strong-password
   FRONTEND_ORIGIN=http://localhost:3200
   ```

3. Start the application:
   ```bash
   docker-compose up -d --build
   ```

4. Open `http://localhost:3200` in your browser.

## Configuration

### Environment Variables

Set these in your `.env` file or `docker-compose.yml` environment section:

| Variable | Required | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | **Yes** | JWT signing key. Generate: `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `ADMIN_PASSWORD` | **Yes** | Dashboard login password. Default `admin` — change before production |
| `FRONTEND_ORIGIN` | No | CORS origin for the frontend. Default: `http://localhost:3200` |

### Ports

| Service | Default Port |
| :--- | :--- |
| **Frontend** | `3200` |
| **Backend** | `8100` |

### Notifications

Configure notification URLs in the **Settings** page of the dashboard.

Examples:
- **Discord**: `discord://webhook_id/webhook_token`
- **Telegram**: `tgram://bot_token/chat_id`
- **Email**: `mailto://user:password@gmail.com`

See [Apprise Documentation](https://github.com/caronc/apprise) for all supported services.

## Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
SECRET_KEY=dev-key ADMIN_PASSWORD=devpassword uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173` — Backend: `http://localhost:8000`

**Tests:**
```bash
# Backend
cd backend && pytest tests/ -v

# Frontend
cd frontend && npm run test
```

## Deployment on Synology NAS

See [DEPLOY_SYNOLOGY.md](./DEPLOY_SYNOLOGY.md) for detailed instructions.

## License

Open source. Free to modify and distribute.

## Preview

![Frontend UI](UI.jpg)
