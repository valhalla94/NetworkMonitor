# Network Monitor

A modern, self-hosted network monitoring dashboard built with React and FastAPI. Monitor the uptime, latency, and status of your network devices in real-time with a premium, responsive user interface.

NOW POWERED BY **SQLITE** - Lightweight, efficient, and perfect for low-power devices like Synology NAS or Raspberry Pi.

## 🚀 Features

*   **Real-time Monitoring**: Track latency and uptime for multiple hosts (ICMP/Ping, HTTP, TCP).
*   **🔔 Smart Notifications**: Get instant alerts via multiple platforms (Discord, Telegram, Email, etc.) when a host goes DOWN or comes back UP. Powered by **Apprise**.
*   **Internet Speed Test**: Built-in speed test to check your ISP's performance (Download, Upload, Ping) with historical tracking.
*   **Quick Ping**: Instantly ping any IP or hostname directly from the dashboard without adding it to the monitor.
*   **Network Health**: View global average latency across all monitored hosts for a quick health snapshot.
*   **Public IP Tracking**: Monitor your public IP address, view history of changes, and track duration of the current IP.
*   **Historical Data**: View interactive charts for latency trends over time (1h, 24h, 7d, 30d, 1y). Data is retained for 30 days.
*   **SSL Certificate Monitoring**: Automatically checks and alerts you when SSL certificates are about to expire.
*   **Host Management**: Add, edit, and delete hosts via a password-protected settings interface.
*   **Responsive Design**: "Premium" glassmorphism UI that looks great on desktop and mobile.
*   **Dockerized**: Easy deployment with Docker Compose.

## 🛠️ Tech Stack

*   **Frontend**: React, Vite, TailwindCSS, Recharts, Lucide React.
*   **Backend**: Python FastAPI, APScheduler, SQLAlchemy.
*   **Database**: SQLite (Lightweight, file-based storage).
*   **Notifications**: Apprise (Python library).
*   **Containerization**: Docker, Docker Compose.

## 📋 Prerequisites

*   [Docker](https://www.docker.com/get-started) and Docker Compose installed on your machine.

## ⚡ Quick Start

1.  **Clone the repository** (or download the files):
    ```bash
    git clone <repository-url>
    cd network-monitor
    ```

2.  **Start the application**:
    ```bash
    docker-compose up -d --build
    ```

3.  **Access the Dashboard**:
    Open your browser and navigate to `http://localhost:3200`.

## ⚙️ Configuration

### Docker Compose
You can configure ports and environment variables in `docker-compose.yml`.

| Service | Default Port | Description |
| :--- | :--- | :--- |
| **Frontend** | `3200` | The main dashboard UI. |
| **Backend** | `8100` | The API server (internal use mostly). |

### Environment Variables
*   `VITE_API_URL`: URL of the backend API (handled automatically by proxy in production).
*   `VITE_ADMIN_PASSWORD`: Password for the settings area (Default: `admin`). *Note: To change this in Docker, you must rebuild the image with build arguments.*

### Notifications
Configure your notification URL in the **Settings** page of the dashboard.
Example URLs:
- **Discord**: `discord://webhook_id/webhook_token`
- **Telegram**: `tgram://bot_token/chat_id`
- **Email**: `mailto://user:password@gmail.com`

See [Apprise Documentation](https://github.com/caronc/apprise) for all supported services.

## 🖥️ Development

To run the project locally for development:

**1. Start Backend:**
```bash
docker-compose up -d backend
```

**2. Start Frontend:**
```bash
cd frontend
npm install
npm run dev
```
The frontend will be available at `http://localhost:5173`.

## 📦 Deployment on Synology NAS

This project is optimized for deployment on Synology NAS using Container Manager.
See [DEPLOY_SYNOLOGY.md](./DEPLOY_SYNOLOGY.md) for detailed instructions.

## 🔄 Recent Updates

*   **Refactor**: Migrated from InfluxDB to **SQLite** for significantly lower resource usage (RAM/CPU).
*   **Feature**: Added **Notification System** for status changes and SSL warnings.
*   **Feature**: Added Internet Speed Test, Quick Ping, and Network Health cards.
*   **UI/UX**: Improved button interactions, added animations, and refined the glassmorphism design.

## 📝 License

This project is open source. Feel free to modify and distribute.

## Frontend preview

![Frontend UI](UI.jpg)
