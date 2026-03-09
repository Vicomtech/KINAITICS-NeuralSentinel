# 🚀 Quick Build Guide — Windows Executable

## Method 1: Automatic Build Script (Recommended)

```cmd
build-windows.bat
```

This script installs all dependencies and generates the installer automatically.

---

## Method 2: Manual Build (Step by Step)

Use this if the automatic script fails.

### Step 1: Enable PowerShell Scripts (only if you see a script error)

If you get a "scripts is disabled" error, run this **as Administrator**:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2: Install Node.js Dependencies

```cmd
npm install
```

### Step 3: Build the Executable

```cmd
npm run build:win
```

Wait 2–5 minutes for the installer to be generated.

### Step 4: Locate the Installer

The output will be at:
```
dist\NeuralSentinel-1.0.0-Setup.exe
```

---

## 📦 Generated Files

After the build you will find the following in `dist/`:

- **NeuralSentinel-1.0.0-Setup.exe** ← Full installer (recommended)
- **NeuralSentinel-1.0.0-portable.exe** ← Portable version
- **win-unpacked/** ← Unpacked directory (useful for testing)

---

## ✅ Testing the Installer

1. Navigate to the `dist` folder.
2. Run `NeuralSentinel-1.0.0-Setup.exe`.
3. Follow the installation wizard.
4. The application will be installed in `C:\Program Files\NeuralSentinel\`.

---

## ⚠️ Important Notes

### Python Runtime

The Electron installer **does NOT bundle Python**. End users must have:
- Python 3.11 or higher installed and available on `PATH`
- All dependencies from `backend/requirements.txt` installed

### First Launch

On the first run:
1. The Python backend starts automatically.
2. Electron opens the UI window.
3. Initial load may take 10–15 seconds.

---

## 🐛 Common Issues

| Error | Solution |
|---|---|
| `npm command not found` | Install Node.js from https://nodejs.org/ |
| `icon.ico not found` | Already handled — generated automatically |
| Build is very slow | Normal on first run; may take 5–10 minutes |
| Installer does not launch backend | Verify Python is on `PATH`; reinstall deps: `cd backend && pip install -r requirements.txt` |

---

## 📊 Size Estimates

- **Installer:** ~150–200 MB
- **Installed application:** ~300–400 MB

---

> For the full build guide, see [BUILD.md](BUILD.md).
