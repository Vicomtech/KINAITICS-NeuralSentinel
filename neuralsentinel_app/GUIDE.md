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
- `.zip` (plugin library package)

Plugin lifecycle:

1. Upload in **Plugins**
2. Reload plugin registry
3. Confirm plugin appears in its category
4. Use it from **Evaluation**

A plugin should provide:

- Metadata/manifest
- Metric execution implementation
- Optional visualization output

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

### Missing or broken visualizations

- Not all metrics produce charts
- If chart generation fails, inspect plugin errors in logs

## 11. Security and Data Handling

- All data processing is local
- No mandatory external service integration
- Keep sensitive datasets/models on trusted machines only
- Use exported result files according to your organization policies

## 12. Building Distributable Packages

Windows:

```bash
npm run build:win
```

Linux:

```bash
npm run build:linux
```

Artifacts are generated under `dist/`.

## 13. Maintenance Recommendations

- Keep Python and Node dependencies updated
- Version-control custom plugins
- Back up the `data/` folder periodically if you need historical evaluations
- Validate plugin compatibility after major dependency upgrades

## 14. License

NeuralSentinel is distributed under the MIT License. See `LICENSE.txt` for full terms.
