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
Each plugin must provide metadata (`manifest`) and execution logic for the selected metric.

Supported upload formats:

- `.py` – Python plugin file
- `.so` – linux compiled plugin binary
- `.pyd` – windows compiled plugin binary
- `.zip` – plugin **library pack** (recommended for multi-metric packages)

### Library packs and their `requirements.txt`

A library pack groups several metrics plus their dependencies. Expected layout
(inside the `.zip`, or as a folder under `backend/plugins/`):

```text
my_library/
├── requirements.txt        # third-party deps for the metrics (optional)
├── my_library-1.0-*.whl    # bundled private/compiled wheel (optional)
├── security/   *.pyd | *.py
├── privacy/    *.pyd | *.py
└── fairness/   *.pyd | *.py
```

**Dependencies are incorporated automatically.** Whenever the plugin registry is
discovered or reloaded — at backend startup *and* after any upload —
`PluginManager` looks for a `requirements.txt` next to each pack and installs it
into the backend's Python environment **before** importing the plugins, so the
compiled metrics can `import` what they need (e.g. `numba`, `opencv-python`,
`seaborn`) instead of being skipped. The install:

- resolves the **full** dependency tree (no `--no-deps`);
- runs with `--find-links <pack_dir>`, so a bundled `.whl` (e.g. a private
  `neuralstrength` library) is installed offline from inside the pack;
- writes a `.deps_installed` marker in the pack folder on success, so an
  unchanged pack is **not** reinstalled on every reload/restart (edit
  `requirements.txt` to force a fresh install).

You add a pack in one of two ways:

1. **UI:** *Plugins → Upload* the `.zip`. The backend extracts it, installs its
   `requirements.txt`, reloads, and the metrics appear in their categories.
2. **Filesystem:** drop the pack folder under `backend/plugins/` and hit
   *Plugins → Reload* (or restart the backend).

> **Windows note:** dependency install happens while the backend is running. If
> a pin in `requirements.txt` forces pip to *replace* a package the live process
> already imported (e.g. `numpy`/`scipy`), it can fail with a locked-file error.
> In that case reload right after a fresh backend start, or install while the
> backend is stopped. Watch for `[Plugin Deps]` lines in the backend log.

## Deployment Overview

NeuralSentinel runs as **two cooperating processes**:

| Process | What it is | How it starts |
| --- | --- | --- |
| **Backend** | Flask API + plugin engine (`backend/app.py`), served on `http://localhost:5000` | `python app.py` (dev) or the bundled `backend/app.exe` (packaged) |
| **Frontend** | Electron desktop app (`main.js` → `index.html`) | `npm run dev` (dev) or the installed app (packaged) |

The Electron renderer talks to the backend over local HTTP only.

**Local development** — install once (`install.bat` / `install.sh`, or the manual
steps above), then launch both processes with `start.bat` / `start.sh` (they open
the backend venv and the Electron app for you). Plugin **library packs** placed
under `backend/plugins/` have their `requirements.txt` installed automatically on
the next backend start/reload (see [Plugin System](#plugin-system)).

**Packaged distribution** — `build-windows.bat` compiles the Flask backend to a
single `backend/app.exe` with PyInstaller and then runs `npm run build:win`
(electron-builder) to produce the installer. In a packaged build the backend exe
is spawned by `main.js` and its plugins/requirements live alongside the bundled
app, so end users do **not** need Python or Node installed.

## Build Packages

- Windows build (full pipeline: backend exe + installer):

```bash
build-windows.bat
```

- Windows app only:

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

- [`GUIDE.md`](GUIDE.md)

## License

MIT — see `LICENSE.txt`.
