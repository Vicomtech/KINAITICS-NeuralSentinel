# NeuralSentinel

NeuralSentinel is a cross-platform **Electron-based desktop application** for managing, visualizing, and evaluating AI datasets and trained models.
It integrates a **local Python backend** for metric computation (via plugins) with a **modern JavaScript frontend**.

---

## Features

- **Dataset & Model Management**

  - Upload datasets (`.csv`, `.xls`, `.xlsx`, `.npy`)
  - Upload trained models (`.h5`)
  - Files stored under `userData/uploads/`
- **Dashboard**

  - Interactive sidebar listing datasets and models
  - Collapsible sidebar for larger view area
  - File selection highlights active item
- **Visualization**

  - CSV/Excel/NumPy data preview
  - Model summaries for `.h5` files via `h5_visualizer.py`
- **Metrics & Plugins**

  - Extensible plugin architecture (`python_backend/plugins/`)
  - Execute metrics and visualizations dynamically (`run_plugins.py`)
  - Plugin tabs are auto-injected into the dashboard
- **Export**

  - Export computed metrics to `.xlsx` or `.csv`

---

## Development Setup

This guide describes how to configure, run, and build the application in a reproducible environment using **Conda** and **Node.js**.

### Prerequisites

- **Node.js** ≥ 18
- **Anaconda** or **Miniconda**
- `requirements.txt` file in the project root

---

### 1. Install Node.js Dependencies

```bash
git clone https://gitlab.com/rfernandez10/neuralsentinel.git
cd neuralsentinel
npm install
```

---

### 2. Create and Configure the Conda Environment

```bash
# Create environment
conda create -n neuralsentinel_dev python=3.9.22

# Activate environment
conda activate neuralsentinel_dev

# Install Python dependencies
pip install -r requirements.txt
```

---

### 3. Run the Application (Development Mode)

#### Windows / Linux

```bash
conda activate neuralsentinel_dev
npm start
```

The application runs using the Python environment `neuralsentinel_dev`.

---

## Building for Production

### 1. Prepare the Embedded Python Environment

Before building, create a self-contained Python environment for packaging.

```bash
# Activate the environment
conda activate neuralsentinel_dev

# Create embedded environment directory
mkdir -p python_backend/python_embedded
```

Copy the entire Conda environment directory (e.g.`C:\Users\<User>\Anaconda3\envs\neuralsentinel_dev`)into `python_backend/python_embedded`.

> Perform this process separately for each target OS (Windows → Windows, Linux → Linux).

---

### 2. Build the Installer

```bash
npm run build
```

Build artifacts and installers are generated in the `/dist` directory.

---

## Customization & Plugins

### Adding a Plugin

Create a new folder under `python_backend/plugins/{plugin_name}` containing:

- `visualizer.py` → Renders HTML for dashboard tab
- Any additional dependencies in the same folder

Then update `plugin_config.yaml` to enable your plugin.

### Plugin Execution

Plugins are discovered and executed dynamically at runtime via:

```bash
python python_backend/run_plugins.py
```

Each plugin can expose metrics, charts, or visual components directly to the frontend.

---

## Project Structure

```
neuralsentinel/
├── main.js                  # Electron main process
├── preload.js               # Safe bridge between frontend and backend
├── package.json             # Node.js dependencies & build scripts
├── renderer/                # Frontend code (HTML/CSS/JS)
│   ├── views/               # UI pages: upload.html, dashboard.html, etc.
│   ├── controllers/         # View controllers: upload.js, dashboard.js
│   └── styles/              # Global styles
├── python_backend/          # Python backend
│   ├── plugins/             # Metric plugins
│   ├── python_embedded/     # Bundled Python env (for production)
│   ├── run_plugins.py       # Entrypoint for plugin execution
│   ├── h5_visualizer.py     # Model summary generator
│   └── requirements.txt     # Python dependencies
├── dist/                    # Build output
└── README.md                # Project documentation
```

---

## Live Updates & Quick Builds

- `npm start` — run in development mode with live reloading
- `npm run dist` — generate an unpacked build (for fast testing)
- `npm run build` — generate full production installer

---

## Contributing

- Report bugs or request features via GitLab Issues
- Fork and submit Merge Requests
- Follow code style:
  - JavaScript: ES6+, 2-space indentation
  - Python: PEP8 compliance and test coverage for plugins

---

## License

This project is licensed under the **MIT License**.
