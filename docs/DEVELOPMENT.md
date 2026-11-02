# Developer Guide & Workflow

## 1. Setup & Installation

### Prerequisites
- Python 3.12+
- `uv` (recommended) or standard `pip`
- Node.js 18+ & npm for the React dashboard

### Backend Setup
```powershell
# Create virtual environment using uv with local cache
uv venv --python 3.12 --cache-dir .uv-cache .venv

# Activate virtual environment
.\.venv\Scripts\activate

# Install backend dependencies
uv pip install -e "backend[dev]" --cache-dir .uv-cache

# Copy environment template
cp .env.example .env
```

### Database Initialization
```powershell
python main.py --init-db
```

---

## 2. CLI Usage

The system is manually operated via the command line or the web dashboard.

```powershell
# Run a full discovery and collection run across all enabled sources
python main.py --run

# Run against a specific source
python main.py --run --source outlier
python main.py --run --source remotive

# Run filtered by category
python main.py --run --category computer-vision
python main.py --run --category large-language-models

# Run the Source Discovery Engine to find new platforms
python main.py --discover-sources

# Health check all connectors
python main.py --health-check

# Launch Outlier account login helper (user-controlled browser)
python main.py --login-account outlier

# Inspect authenticated Outlier account for active projects
python main.py --inspect-account outlier

# Start FastAPI backend server
python main.py --serve
```

---

## 3. Running Tests
```powershell
pytest backend/tests -v
```

---

## 4. Frontend Setup & Run
```powershell
cd frontend
npm install
npm run dev
```
Access the dashboard at `http://localhost:5173`.

