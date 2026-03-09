# Windows Packaging Guide

## 🎯 Goal

Generate a self-contained Windows installer (`.exe`) for NeuralSentinel that includes everything needed to run the application.

---

## 📋 Prerequisites

Before packaging, make sure you have:

- ✅ Node.js 16+ installed
- ✅ Python 3.11+ installed
- ✅ All project dependencies installed

---

## 🚀 Option 1: Automated Build (Recommended)

Run the script that handles everything automatically:

```cmd
build-windows.bat
```

This script:
1. Installs Node.js dependencies
2. Creates a Python virtual environment and installs dependencies
3. Builds the installer with electron-builder

**Output:** The installer will be at `dist/NeuralSentinel-1.0.0-Setup.exe`

---

## 🔧 Option 2: Manual Build

### Step 1: Install Node.js Dependencies

```cmd
npm install
```

### Step 2: Prepare the Python Backend

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
deactivate
cd ..
```

### Step 3: Build

```cmd
npm run build:win
```

---

## 📦 Output Types

The build process produces two executables:

### 1. NSIS Installer (Recommended)
- **File:** `NeuralSentinel-1.0.0-Setup.exe`
- **Type:** Full installer
- **Features:**
  - Installs to `C:\Program Files\NeuralSentinel\`
  - Creates desktop and Start Menu shortcuts
  - Includes an uninstaller
  - Allows user to choose installation directory

### 2. Portable Executable
- **File:** `NeuralSentinel-1.0.0-portable.exe`
- **Type:** Portable standalone
- **Features:**
  - No installation required
  - Can be run from any location (USB drive, etc.)
  - Ideal for temporary or restricted environments

---

## 📁 Package Contents

The installer includes:

```
NeuralSentinel/
├── Electron App (Frontend)
│   ├── main.js
│   ├── index.html
│   └── src/
├── Python Backend
│   ├── app.py  (or app.exe if compiled with PyInstaller)
│   ├── api/
│   ├── core/
│   ├── plugins/
│   └── requirements.txt
└── Data Directories
    ├── models/
    ├── datasets/
    └── evaluations/
```

---

## ⚙️ Build Configuration

The build configuration is defined in `package.json` under the `"build"` key:

```json
{
  "build": {
    "appId": "com.neuralsentinel.mlauditor",
    "productName": "NeuralSentinel",
    "win": {
      "target": ["nsis", "portable"],
      "icon": "assets/icon.ico"
    }
  }
}
```

### Customization

| Setting | How to change |
|---|---|
| App version | Modify `"version"` in `package.json` |
| Product name | Modify `"productName"` in the build config |
| App icon | Replace `assets/icon.ico` (256×256 px recommended) |

---

## 🎨 Application Icon

### Required Formats
- **Windows:** `.ico` (multiple sizes: 16×16, 32×32, 48×48, 64×64, 128×128, 256×256)
- **Linux:** `.png` (512×512 px)

### Converting a PNG to ICO

**Option 1 — Online tools:**
- https://convertio.co/png-ico/
- https://icoconvert.com/

**Option 2 — ImageMagick:**
```cmd
magick convert icon.png -define icon:auto-resize=256,128,64,48,32,16 assets/icon.ico
```

Place the resulting file at: `assets/icon.ico`

---

## 🔍 Verifying the Build

After the build completes, check the output:

```cmd
dir dist

# You should see:
# NeuralSentinel-1.0.0-Setup.exe      (Installer)
# NeuralSentinel-1.0.0-portable.exe   (Portable)
# win-unpacked\                        (Unpacked directory)
```

---

## 🧪 Testing the Installer

1. **Install:**
   ```cmd
   cd dist
   "NeuralSentinel-1.0.0-Setup.exe"
   ```

2. **Launch** from the Start Menu or desktop shortcut.

3. **Verify:**
   - Application starts correctly
   - Python backend launches automatically
   - All features are functional

---

## 📝 Important Notes

### ⚠️ Python Runtime

The Electron installer **does NOT automatically bundle Python**. End users must have Python installed on their system.

**Alternative — Bundle Python with PyInstaller:**

```cmd
cd backend
pip install pyinstaller
pyinstaller --onefile --add-data "plugins;plugins" app.py
```

Then update `main.js` to use the generated executable at `backend/dist/app.exe`.

### ⚠️ Native Python Dependencies

If you use native Python modules (TensorFlow, PyTorch), ensure that:
- They are installed in the end user's environment, **or**
- They are bundled via PyInstaller

### ⚠️ Installer Size

The installer may be large (~100–300 MB) due to:
- Electron runtime (~80 MB)
- Python dependencies
- Any pre-loaded models

---

## 🐛 Troubleshooting

### Error: `icon.ico not found`

```cmd
# Create the build folder if it doesn't exist
mkdir assets

# Copy an existing icon or create a placeholder
copy icon.png assets\icon.ico
```

### Error: `Python not found`

- Make sure Python is on the system `PATH`
- Or specify the full Python path in `main.js`

### Build is very slow

- Exclude unnecessary folders via `.gitignore` and `package.json` `files` filter
- Use `npm run pack` for faster test builds (no installer generated)

### Installer does not start the backend

- Verify `backend/requirements.txt` is included in the package
- Confirm the Python `PATH` is correctly resolved in the executable

---

## 🎉 Distribution

Once the installer is ready:

1. **Test on a clean Windows machine** (without your development setup)
2. **Document system requirements:**
   - Windows 10/11 (64-bit)
   - Python 3.11+ (if not bundled)
   - 4 GB RAM minimum
   - 500 MB available disk space
3. **Distribute:**
   - Upload to GitHub Releases
   - Share the `.exe` installer
   - Include a README with setup instructions

---

## 📚 References

- [Electron Builder Documentation](https://www.electron.build/)
- [NSIS Installer](https://nsis.sourceforge.io/)
- [PyInstaller Documentation](https://pyinstaller.org/)

---

*Last updated: March 2026*
