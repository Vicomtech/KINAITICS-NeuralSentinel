# Guía de Empaquetado para Windows

## 🎯 Objetivo

Generar un instalador ejecutable (.exe) de ML Auditor para Windows que incluya todo lo necesario para ejecutar la aplicación.

---

## 📋 Requisitos Previos

Antes de empaquetar, asegúrate de tener:

- ✅ Node.js 16+ instalado
- ✅ Python 3.8+ instalado
- ✅ Todas las dependencias del proyecto instaladas

---

## 🚀 Opción 1: Build Automático (Recomendado)

Ejecuta el script que hace todo automáticamente:

```cmd
build-windows.bat
```

Este script:
1. Instala dependencias de Node.js
2. Crea entorno virtual de Python y instala dependencias
3. Construye el ejecutable con electron-builder

**Resultado:** El instalador estará en `dist/ML Auditor-1.0.0-Setup.exe`

---

## 🔧 Opción 2: Build Manual

### Paso 1: Instalar Dependencias

```cmd
npm install
```

### Paso 2: Preparar Backend

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
deactivate
cd ..
```

### Paso 3: Construir

```cmd
npm run build:win
```

---

## 📦 Tipos de Salida

El proceso genera dos tipos de ejecutables:

### 1. **Instalador NSIS** (Recomendado)
- **Archivo:** `ML Auditor-1.0.0-Setup.exe`
- **Tipo:** Instalador completo
- **Características:**
  - Instalación en `C:\Program Files\ML Auditor\`
  - Acceso directo en escritorio y menú inicio
  - Desinstalador incluido
  - Permite elegir directorio de instalación

### 2. **Portable**
- **Archivo:** `ML Auditor-1.0.0-portable.exe`
- **Tipo:** Ejecutable portable
- **Características:**
  - No requiere instalación
  - Ejecutar desde cualquier ubicación
  - Ideal para USB o uso temporal

---

## 📁 Contenido del Paquete

El ejecutable incluye:

```
ML Auditor/
├── Electron App (Frontend)
│   ├── main.js
│   ├── index.html
│   └── src/
├── Backend Python
│   ├── app.py
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

## ⚙️ Configuración de Build

La configuración está en `package.json` bajo la sección `"build"`:

```json
{
  "build": {
    "appId": "com.neuralsentinel.mlauditor",
    "productName": "ML Auditor",
    "win": {
      "target": ["nsis", "portable"],
      "icon": "build/icon.ico"
    }
  }
}
```

### Personalizar Configuración

- **Cambiar versión:** Modifica `"version"` en `package.json`
- **Cambiar nombre:** Modifica `"productName"` en build config
- **Cambiar icono:** Reemplaza `build/icon.ico` (256x256 px recomendado)

---

## 🎨 Icono de la Aplicación

### Formato Requerido
- **Windows:** `.ico` (múltiples tamaños: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256)
- **Linux:** `.png` (512x512 px)

### Generar Icono

Si tienes una imagen PNG, puedes convertirla a ICO:

**Opción 1 - Online:**
- https://convertio.co/es/png-ico/
- https://icoconvert.com/

**Opción 2 - ImageMagick:**
```cmd
magick convert icon.png -define icon:auto-resize=256,128,64,48,32,16 build/icon.ico
```

### Ubicación
Coloca el icono en: `build/icon.ico`

---

## 🔍 Verificar Build

Después del build, verifica:

```cmd
dir dist

# Deberías ver:
# ML Auditor-1.0.0-Setup.exe      (Instalador)
# ML Auditor-1.0.0-portable.exe   (Portable)
# win-unpacked/                    (Carpeta desempaquetada)
```

---

## 🧪 Probar el Instalador

1. **Instalar:**
   ```cmd
   cd dist
   "ML Auditor-1.0.0-Setup.exe"
   ```

2. **Ejecutar desde menú inicio** o acceso directo del escritorio

3. **Verificar:**
   - La aplicación inicia correctamente
   - El backend Python arranca automáticamente
   - Todas las funciones están operativas

---

## 📝 Notas Importantes

### ⚠️ Python Runtime

El ejecutable **NO incluye Python** automáticamente. Los usuarios deben tener Python instalado.

**Alternativa:** Empaquetar Python con PyInstaller:

```cmd
cd backend
pip install pyinstaller
pyinstaller --onefile --add-data "plugins;plugins" app.py
```

Luego actualiza `main.js` para usar el ejecutable generado en `backend/dist/app.exe`

### ⚠️ Dependencias Nativas

Si usas módulos nativos de Python (TensorFlow, PyTorch), asegúrate de que:
- Están instalados en el entorno del usuario
- O están empaquetados con PyInstaller

### ⚠️ Tamaño del Instalador

El instalador puede ser grande (~100-300MB) debido a:
- Electron runtime (~80MB)
- Dependencias de Python
- Modelos pre-cargados (si los hay)

---

## 🐛 Solución de Problemas

### Error: "icon.ico not found"

**Solución:**
```cmd
# Crear carpeta build si no existe
mkdir build

# Crear un icono placeholder o copiar uno existente
copy icon.png build\icon.ico
```

### Error: "Python not found"

**Solución:**
- Asegúrate de que Python esté en el PATH del sistema
- O especifica la ruta completa en `main.js`

### Build muy lento

**Solución:**
- Excluye carpetas innecesarias en `.gitignore` y `package.json`
- Usa `npm run pack` para testing (más rápido)

### Instalador no arranca el backend

**Solución:**
- Verifica que `backend/requirements.txt` esté incluido
- Confirma que el PATH de Python es correcto en el ejecutable

---

## 🎉 Distribución

Una vez generado el instalador:

1. **Prueba en otra máquina Windows limpia**
2. **Documenta requisitos del sistema:**
   - Windows 10/11 (64-bit)
   - Python 3.8+ (si no está embebido)
   - 4GB RAM mínimo
   - 500MB espacio en disco

3. **Distribuye:**
   - Sube a GitHub Releases
   - Comparte el instalador .exe
   - Incluye README con instrucciones

---

## 📚 Referencias

- [Electron Builder Docs](https://www.electron.build/)
- [NSIS Installer](https://nsis.sourceforge.io/)
- [PyInstaller Docs](https://pyinstaller.org/)

---

*Última actualización: Febrero 2026*
