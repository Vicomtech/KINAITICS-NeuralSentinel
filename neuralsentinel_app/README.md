# NeuralSentinel Desktop Application

NeuralSentinel is a cross-platform Electron-based desktop app for managing, visualizing, and evaluating AI datasets and trained models. It integrates a local Python backend for computing metrics (via plugins) with a modern JavaScript front-end.

## Features

- **File Upload & Management**  
  - Upload datasets (`.csv`, `.xls`, `.xlsx`, `.npy`).  
  - Upload trained models (`.h5`).  
  - Files are stored under the userData/uploads directory.
- **Dashboard**  
  - Interactive sidebar listing uploaded Datasets and Models.  
  - Selected file is highlighted; click to load and visualize.  
  - Collapsible sidebar for more screen space.
- **Visualization**  
  - Data previews: CSV table, Excel sheet, NumPy `.npy` preview.  
  - Model summaries for `.h5` files (via `h5_visualizer.py`).
- **Metrics & Plugins**  
  - Extensible plugin architecture: run `run_plugins.py` to compute custom metrics.  
  - Plugin tabs injected dynamically into the dashboard.  
- **Export**  
  - Export computed metrics to Excel (`.xlsx`) or CSV.

## Live Updates & Hot Reload

- `npm start` launches in development mode, loading Python scripts directly from `python_backend/` without packaging.
- Use `npm run dist` (electron-builder --dir) to quickly generate an unpacked build in `dist/` for testing the packaged app.

## Requirements

- **Node.js** LTS or newer.  
- **Python 3.7+** (for development mode) with required packages installed via:

    cd python_backend  
    pip install -r requirements.txt

> **Note:** In packaged builds, an embedded Python distribution is bundled automatically (no external Python install needed).

## Project Structure

    ├── main.js                # Electron main process; IPC handlers
    ├── preload.js             # Safe bridge for renderer
    ├── package.json           # Dependencies & build scripts
    ├── renderer/              # Front-end HTML, CSS, JS
    │   ├── views/             # upload.html, dashboard.html, login.html
    │   ├── controllers/       # upload.js, dashboard.js
    │   └── styles/            # styles.css
    ├── python_backend/        # Python scripts and plugins
    │   ├── python_embedded/   # Bundled embeddable Python (for production)
    │   ├── plugins/           # Plugin folders with visualizer.py
    │   ├── run_plugins.py     # Entrypoint for computing metrics
    │   ├── h5_visualizer.py      # Model summary script
    │   └── requirements.txt   # Python dev dependencies
    └── scripts/               # Build helper scripts (e.g., disable-fuses.js)

## Installation & Setup

1. **Clone the repo**:

    git clone https://gitlab.com/rfernandez10/neuralsentinel.git  
    cd neuralsentinel

2. **Install Node dependencies**:

    npm install

3. **(Optional) Python env for development**:

    cd python_backend  
    python -m venv venv  
    source venv/bin/activate   # Linux/macOS  
    .\venv\Scripts\activate    # Windows  
    pip install -r requirements.txt

4. **Run in development** with hot reload:

    npm start

5. **Quick unpacked build for testing**:

    npm run dist

6. **Full installer build**:

    npm run build

Installers/output appear in `dist/`.

## Customization & Plugins

- **Adding a plugin**: Create a new folder under `python_backend/plugins/{plugin_name}` containing:  
  - `visualizer.py` (renders HTML for dashboard tab)  
  - Any dependencies under `python_backend/plugins/{plugin_name}/`.
- Update `plugin_config.yaml` to enable your plugin.

## Contributing

- Report issues or request features via GitLab issues.  
- Fork, fix, and submit merge requests.  
- Follow code style: ES6+, consistent indent (2 spaces), and TDD for Python scripts.