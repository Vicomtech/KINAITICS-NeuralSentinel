# NeuralSentinel: Complete Installation and Usage Guide

## 1. Purpose of This Guide

This document explains, step by step, how to install, configure, launch, and use NeuralSentinel for local machine learning model auditing.

It is written for developers, security analysts, and data/ML teams who want to run model evaluations fully on their own machine.

## 2. What NeuralSentinel Does

NeuralSentinel is a desktop tool that audits ML models through:

- **Security** metrics
- **Privacy** metrics
- **Fairness** metrics

You can:

- Upload models and datasets
- Select plugin-based metrics
- Execute evaluations with live progress/logs
- Review detailed results and export outputs

## 3. System Requirements

Minimum requirements:

- Windows 10/11 or Linux
- Node.js 16+
- Python 3.11+
- 4 GB RAM
- 2 GB free disk space

Recommended for larger models:

- Node.js 18+
- 8 GB RAM or more
- 5+ GB free disk space
- CPU/GPU environment compatible with your ML framework

## 4. Installation Options

### 4.1 Quick installation (recommended)

#### Windows

Run from project root:

```bat
install.bat
```

#### Linux

```bash
chmod +x install.sh
./install.sh
```

This setup installs frontend dependencies and backend Python requirements.

### 4.2 Manual installation

From project root:

1. Install frontend dependencies:

```bash
npm install
```

2. Create backend virtual environment:

```bash
cd backend
python -m venv venv
```

3. Activate the virtual environment:

Windows:

```bat
venv\Scripts\activate
```

Linux:

```bash
source venv/bin/activate
```

4. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## 5. How to Run the App

NeuralSentinel runs as **two cooperating processes**:

- **Backend** — Flask API + plugin engine (`backend/app.py`) on `http://localhost:5000`.
  In a packaged build this is the bundled `backend/app.exe`.
- **Frontend** — Electron desktop app (`main.js` → `index.html`) that talks to the
  backend over local HTTP only.

In development you start both yourself (5.1); the `start` scripts (5.2) launch both
for you. The backend must be up before the frontend can run evaluations, and it
installs any plugin-pack dependencies on startup (see Section 8.3).

## 5.1 Development mode (two terminals)

### Terminal A: backend

```bash
cd backend
python app.py
```

### Terminal B: desktop app

```bash
npm run dev
```

## 5.2 Production/start scripts

### Windows

```bat
start.bat
```

### Linux

```bash
chmod +x start.sh
./start.sh
```

## 6. User Interface Overview

Main sections in the application:

- **Dashboard:** high-level project and activity summary
- **Models:** upload/view/delete model files
- **Datasets:** upload/view/delete datasets and previews
- **Evaluation:** configure and execute metric runs
- **Results:** review scorecards, technical details, and exports
- **Plugins:** inspect, upload, reload, and delete metric plugins
- **Settings:** runtime display/basic app settings

## 7. End-to-End Usage Workflow

### Step 1: Upload a model

1. Go to **Models**
2. Click **Upload Model**
3. Provide:
   - Name
   - Framework (`tensorflow` or `pytorch`)
   - Model file
   - Optional description
4. Save/upload

### Step 2: Upload a dataset

1. Go to **Datasets**
2. Click **Upload Dataset**
3. Provide:
   - Dataset name
   - Data file (`.npy` / `.npz`)
   - Optional labels file (`.npy` / `.npz`)
   - Optional description
4. Confirm upload
5. Use **View** to inspect preview and metadata

### Step 3: Configure evaluation

1. Open **Evaluation**
2. Select one uploaded model
3. Select one uploaded dataset
4. Choose one or more metrics (security/privacy/fairness tabs)
5. Click **Start Audit**

### Step 4: Monitor execution

During execution, the page shows:

- Global progress percentage
- Metric-by-metric status cards
- Live Python log stream
- Cancel button for running evaluations

### Step 5: Analyze results

Open **Results** to:

- Filter by model
- Inspect completed/running/error evaluations
- Open per-metric detail modal
- View warnings and recommendations
- Generate/expand visualizations when available
- Download full evaluation JSON

## 8. Plugin Usage Guide

Supported plugin upload formats:

- `.py` (single Python plugin)
- `.so` (linux compiled plugin)
- `.pyd` (windows compiled plugin)
- `.zip` (plugin **library pack** — recommended for multi-metric packages)
- `.whl` (private/compiled library only, no plugin files)

A plugin should provide:

- Metadata/manifest (`name`, `type`, `version`, `description`, `parameters`)
- Metric execution implementation
- Optional visualization output

### 8.1 Single-file plugins

Upload a `.py`/`.pyd`/`.so` in **Plugins → Upload**. It is stored under
`backend/plugins/custom/`, the registry reloads, and the metric appears in its
category. Use it from **Evaluation**.

### 8.2 Library packs (multiple metrics + dependencies)

A library pack bundles several metrics with the third-party packages they need.
Expected folder layout (this is what you compress into the `.zip`, and also how
it lives under `backend/plugins/` once extracted):

```text
my_library/
├── requirements.txt        # third-party deps for the metrics (optional)
├── my_library-1.0-*.whl    # bundled private/compiled wheel (optional)
├── security/   *.pyd | *.py
├── privacy/    *.pyd | *.py
└── fairness/   *.pyd | *.py
```

A real example ships in the repo at
`backend/plugins/neuralstrength/` (compiled `cp311-win_amd64` metrics + a private
wheel + a `requirements.txt`).

### 8.3 How `requirements.txt` is incorporated (automatic)

You do **not** install pack dependencies by hand. On every plugin discovery —
which happens at **backend startup** and on every **reload/upload** — the backend
(`PluginManager`) does the following for each pack that contains a
`requirements.txt`:

1. Runs `pip install -r requirements.txt --find-links <pack_dir>` into the
   backend's Python environment, **before** importing the metrics. This pulls the
   full dependency tree (e.g. `numba`, `opencv-python`/`cv2`, `seaborn`) so the
   compiled `.pyd` files import cleanly instead of being skipped.
2. `--find-links <pack_dir>` lets a bundled `.whl` (such as a private
   `neuralstrength` library) install **offline** straight from the pack folder.
3. On success it writes a hidden `.deps_installed` marker in the pack folder so
   the same pack is not reinstalled on every reload. **To force a reinstall**,
   edit the pack's `requirements.txt` (or delete its `.deps_installed` file).

Progress is printed to the backend log with a `[Plugin Deps]` prefix, e.g.:

```text
[Plugin Deps] Installing requirements for pack 'neuralstrength': ...
[Plugin Deps] Requirements installed for pack 'neuralstrength'
Loaded plugin: Cohesion (fairness) from cohesion.cp311-win_amd64.pyd
```

### 8.4 Adding a pack — two ways

- **From the UI:** *Plugins → Upload* the `.zip`. The backend extracts it under
  `backend/plugins/<name>/`, installs its `requirements.txt`, reloads, and the
  metrics show up in their categories.
- **From the filesystem:** copy the pack folder into `backend/plugins/`, then use
  *Plugins → Reload* (or restart the backend). The same auto-install runs.

### 8.5 Compatibility and Windows note

- Compiled metrics/wheels are platform- and Python-version specific. The bundled
  `neuralstrength` pack targets **Python 3.11 / Windows x64** (`cp311-win_amd64`);
  other environments require recompiled binaries.
- Dependency install runs while the backend is live. If a pin in
  `requirements.txt` forces pip to *replace* a package the running backend has
  already imported (e.g. `numpy`/`scipy`), it can fail with a Windows locked-file
  error. Reload right after a **fresh backend start**, or install with the backend
  stopped. The failing package is shown in the `[Plugin Deps]` log line.

## 9. API Endpoints (Quick Reference)

Base URL: `http://localhost:5000/api`

- `GET /models`
- `POST /models/upload`
- `DELETE /models/{id}`
- `GET /datasets`
- `POST /datasets/upload`
- `GET /datasets/{id}/preview`
- `DELETE /datasets/{id}`
- `POST /evaluations`
- `POST /evaluations/{id}/start`
- `POST /evaluations/{id}/cancel`
- `GET /evaluations/{id}/status`
- `GET /evaluations/{id}/logs`
- `GET /evaluations/{id}/results`
- `GET /evaluations/history`
- `GET /plugins`
- `POST /plugins/upload`
- `POST /plugins/reload`
- `DELETE /plugins/{name}`

## 10. Troubleshooting

### Backend connection error

- Make sure `backend/app.py` is running
- Verify local URL/port availability (`localhost:5000`)
- Confirm Python environment has all dependencies

### Upload errors (model/dataset/plugin)

- Check file extension is supported
- Verify file is not corrupted
- Confirm write permission in project `data/` folders

### Evaluation does not start

- Ensure at least one model, one dataset, and one metric are selected
- Check backend logs for plugin/runtime exceptions
- Reload plugins and retry

### Metrics are skipped on load (`ModuleNotFoundError` / import errors)

The backend log shows lines like
`[Plugin Discovery] Skipping <metric>.pyd: ModuleNotFoundError: No module named '<x>'`.
This means the pack's dependencies were not installed.

- Confirm the pack has a `requirements.txt` and that `<x>` is listed in it.
- Trigger install: *Plugins → Reload* or restart the backend; watch for
  `[Plugin Deps] Installing requirements ...` followed by `[Plugin Deps]
  Requirements installed`.
- If it is being skipped because a previous run already wrote a `.deps_installed`
  marker, edit the pack's `requirements.txt` (or delete the marker) to force a
  reinstall.
- On Windows, if `[Plugin Deps] pip install FAILED ... Access is denied`, a base
  package is locked by the running backend — install with the backend stopped.

### Long evaluations / "timeout"

- Heavy metrics (e.g. `numba`-compiled) can take several minutes; the **first**
  run also pays a one-time JIT compilation cost and may emit no logs meanwhile —
  this is expected.
- The UI no longer aborts long-but-progressing runs. It keeps polling while the
  backend reports the evaluation as alive and only stops if the backend becomes
  **unreachable** for several consecutive attempts. The evaluation also keeps
  running on the backend even if you navigate away.
- Use **Cancel** to stop a run you no longer need.

### Missing or broken visualizations

- Not all metrics produce charts
- If chart generation fails, inspect plugin errors in logs

## 11. Security and Data Handling

- All data processing is local
- No mandatory external service integration
- Keep sensitive datasets/models on trusted machines only
- Use exported result files according to your organization policies

## 12. Building Distributable Packages

**Windows (full pipeline).** `build-windows.bat` does everything: installs npm
deps, prepares the Python venv, compiles the Flask backend to a single
`backend/app.exe` with PyInstaller, then runs electron-builder:

```bat
build-windows.bat
```

To build only the Electron app (when `backend/app.exe` already exists):

```bash
npm run build:win
```

Linux:

```bash
npm run build:linux
```

Artifacts are generated under `dist/`. In a packaged build the backend exe is
spawned by the Electron app, so end users need neither Python nor Node installed.

> Plugin library packs and their `requirements.txt` (Section 8) are resolved at
> runtime against the environment that runs the backend. For a packaged build,
> make sure any premium/compiled packs are compatible with the bundled Python
> version and included in `backend/plugins/` before building.

## 13. Maintenance Recommendations

- Keep Python and Node dependencies updated
- Version-control custom plugins
- Back up the `data/` folder periodically if you need historical evaluations
- Validate plugin compatibility after major dependency upgrades

## 14. License

NeuralSentinel is distributed under the MIT License. See `LICENSE.txt` for full terms.
