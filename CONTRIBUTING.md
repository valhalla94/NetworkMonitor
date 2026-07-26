# Contributing to NetworkMonitor

Thank you for your interest in contributing to **NetworkMonitor**! We welcome bug reports, feature proposals, pull requests, and documentation improvements.

---

## 🛠️ Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 22+
- Docker & Docker Compose (optional for container testing)

### Setting Up Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt ruff
SECRET_KEY=dev-secret ADMIN_PASSWORD=devpassword uvicorn main:app --reload
```

### Setting Up Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing & Code Quality Guidelines

Before submitting a Pull Request, please ensure all automated tests and linters pass cleanly.

### Run Linters
- **Backend (Ruff)**: `ruff check backend/`
- **Frontend (ESLint)**: `cd frontend && npm run lint`

### Run Test Suites
- **Backend (`pytest`)**: `backend/.venv/bin/pytest`
- **Frontend (`vitest`)**: `cd frontend && npm run test`

---

## 🚀 Pull Request Workflow

1. Fork the repository and create your feature branch (`git checkout -b feature/amazing-feature`).
2. Commit your changes with clear, descriptive commit messages.
3. Push to your fork (`git push origin feature/amazing-feature`).
4. Open a Pull Request on GitHub. Use the provided PR Template to document your changes.
