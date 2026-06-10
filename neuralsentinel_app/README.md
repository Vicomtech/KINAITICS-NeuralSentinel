# NeuralSentinel

NeuralSentinel is a local-first desktop application for auditing machine learning models across three trust pillars: **security**, **privacy**, and **fairness**.  
It combines an Electron UI with a Python/Flask backend and a plugin-based metric engine.

## Key Features

- Local model and dataset management
- Configurable audits with real-time progress and logs
- Plugin architecture for custom metrics (`.py`, `.so`, `.pyd`, `.zip`)
- Structured results view with score cards and detailed metric drill-down
- JSON export for completed evaluations
- Fully local execution (no cloud dependency)

## Tech Stack

- **Desktop App:** Electron
- **Frontend:** Vanilla JavaScript, HTML, CSS
- **Backend API:** Flask
- **ML Ecosystem:** TensorFlow, PyTorch, NumPy, scikit-learn, Foolbox

## Project Structure

```text
.
├── assets/                     # Icons and static app assets
├── backend/                    # Flask backend and plugin runtime
│   ├── api/                    # REST endpoints (models, datasets, evaluations, plugins)
│   ├── core/                   # Plugin loading/execution infrastructure
│   ├── plugins/                # Built-in metric plugins
│   ├── app.py                  # Backend entry point
│   └── requirements.txt        # Python dependencies
├── data/                       # Runtime storage (models, datasets, evaluations)
├── src/
│   ├── renderer/
│   │   ├── components/         # UI views (dashboard, models, datasets, etc.)
│   │   ├── api.js              # Frontend API client
│   │   └── app.js              # View controller and navigation
│   └── styles/                 # Global and component styles
├── index.html                  # Main renderer shell
├── main.js                     # Electron main process
├── preload.js                  # Secure bridge (contextIsolation)
└── package.json                # Scripts and build config
```

## Requirements

- **Node.js** 16+ (18+ recommended)
- **Python** 3.11+
- **OS:** Windows 10/11 or modern Linux distribution
- Enough disk space for models, datasets, and evaluation artifacts

## Installation

### Option 1: Automated scripts

**Windows**

```bat
install.bat
```

**Linux**

```bash
chmod +x install.sh
./install.sh
```

### Option 2: Manual setup

1. Install Node dependencies:

```bash
npm install
```

2. Create and activate Python virtual environment:

```bash
cd backend
python -m venv venv
```

Windows:

```bat
venv\Scripts\activate
```

Linux:

```bash
source venv/bin/activate
```

3. Install backend dependencies:

```bash
pip install -r requirements.txt
```

## Run the Application

### Development mode

Start backend:

```bash
cd backend
python app.py
```

In another terminal, start Electron:

```bash
npm run dev
```

### Production/startup scripts

Windows:

```bat
start.bat
```

Linux:

```bash
chmod +x start.sh
./start.sh
```

## Main Workflow

1. Upload one or more models in the **Models** section
2. Upload dataset(s) in the **Datasets** section
3. Configure and launch a run in **Evaluation**
4. Monitor progress/log stream while metrics execute
5. Review and export outputs in **Results**

## REST API Overview

Default base URL: `http://localhost:5000/api`

- `/models` – list/upload/delete models
- `/datasets` – list/upload/delete datasets, preview data
- `/evaluations` – create/start/cancel/status/logs/results/history
- `/plugins` – list/upload/reload/delete plugins

## Plugin System

Plugins are loaded by the backend and exposed by type (`security`, `privacy`, `fairness`).

Supported upload formats:

- `.py` – Python plugin file
- `.so` – linux compiled plugin binary
- `.pyd` – windows compiled plugin binary
- `.zip` – plugin library package

Each plugin must provide metadata (`manifest`) and execution logic for the selected metric.

## Build Packages

- Windows build:

```bash
npm run build:win
```

- Linux build:

```bash
npm run build:linux
```

Build outputs are generated in `dist/`.

## Security Notes

- Data remains local unless the user explicitly exports it
- Electron is configured with context isolation
- Backend communication is local HTTP between app and Flask service

## Additional Documentation

For a complete step-by-step setup and usage guide, see:

- `INSTALLATION_AND_USAGE_GUIDE.md`

## License

MIT — see `LICENSE.txt`.
