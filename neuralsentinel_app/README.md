# NeuralSentinel — ML Model Auditor

<p align="center">
  <img src="assets/icon.png" alt="NeuralSentinel Logo" width="96"/>
</p>

<p align="center">
  <strong>Auditoría de modelos de Machine Learning: seguridad, privacidad y equidad, 100% local.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue" alt="Version"/>
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey" alt="Platform"/>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License"/>
  <img src="https://img.shields.io/badge/electron-28-9cf" alt="Electron"/>
  <img src="https://img.shields.io/badge/python-3.8%2B-yellow" alt="Python"/>
</p>

---

## 📖 Descripción

**NeuralSentinel** es una aplicación de escritorio multiplataforma que permite auditar modelos de Machine Learning de forma completamente local. Combina un frontend basado en **Electron** con un backend en **Python/Flask** para ofrecer evaluaciones exhaustivas de:

- **Seguridad** – robustez ante ataques adversariales.
- **Privacidad** – detección de riesgos de fuga de información y ataques de inferencia.
- **Equidad** – medición de sesgos y fairness en predicciones.

Todo el procesamiento se realiza en el equipo del usuario, sin enviar ningún dato a servidores externos.

---

## ✨ Características Principales

| Característica | Descripción |
|---|---|
| 🔒 Auditoría de Seguridad | Evalúa robustez ante ataques adversariales |
| 🔐 Auditoría de Privacidad | Detecta riesgos de fuga de información y ataques de inferencia |
| ⚖️ Auditoría de Equidad | Mide sesgos y fairness en predicciones del modelo |
| 🔌 Sistema de Plugins | Extensible mediante plugins `.py` o librerías `.zip` personalizadas |
| 📊 Visualizaciones | Gráficas generadas por los plugins (matplotlib) embebidas en los resultados |
| 💾 Exportación | Resultados almacenados en JSON por evaluación |
| 🏠 100% Offline | Sin telemetría, sin conexión requerida |
| 💻 Multiplataforma | Windows 10/11 y Linux (Ubuntu 20.04+) |

---

## 📋 Requisitos del Sistema

| Componente | Mínimo | Recomendado |
|---|---|---|
| **Node.js** | 16.0.0 | 18+ |
| **Python** | 3.11+
| **RAM** | 4 GB | 8 GB |
| **Espacio en disco** | 2 GB | 5 GB |
| **SO** | Windows 10 / Ubuntu 20.04 | Windows 11 / Ubuntu 22.04 |

---

## 🛠️ Instalación

### Opción A — Instalación Rápida (scripts)

**Windows:**
```bat
install.bat
```

**Linux:**
```bash
chmod +x install.sh && ./install.sh
```

Los scripts crean el entorno virtual de Python, instalan todas las dependencias de Python y Node.js, y preparan la estructura de datos necesaria.

### Opción B — Instalación Manual

#### 1. Instalar dependencias de Node.js (Electron)

```bash
npm install
```

#### 2. Crear entorno virtual de Python e instalar dependencias

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

> ⚠️ La instalación de TensorFlow, PyTorch y Foolbox puede tardar varios minutos. Se recomienda una conexión estable.

---

## 🚀 Ejecución

### Modo Desarrollo

Requiere dos terminales:

**Terminal 1 — Backend Python (Flask):**
```bash
cd backend
# (activa el venv si es necesario)
python app.py
```
El backend arrancará en `http://127.0.0.1:5000`.

**Terminal 2 — Frontend Electron:**
```bash
npm run dev
```

La ventana de la aplicación se abrirá automáticamente.

### Modo Producción

```bash
# Windows
start.bat

# Linux
chmod +x start.sh && ./start.sh
```

En modo producción, Electron lanza automáticamente el ejecutable compilado del backend (`backend/app.exe` en Windows) y espera 2 segundos antes de mostrar la ventana.

---

## 📂 Estructura del Proyecto

```
local_app/
├── main.js                  # Proceso principal de Electron (gestión de ventana y backend Python)
├── preload.js               # Puente IPC seguro (contextBridge)
├── index.html               # Punto de entrada HTML
├── package.json             # Configuración de Electron y electron-builder
│
├── src/
│   ├── renderer/            # Lógica del frontend (JavaScript)
│   │   ├── app.js           # Aplicación principal del renderer
│   │   ├── api.js           # Cliente HTTP para el backend Flask
│   │   └── components/      # Componentes de UI (modelos, datasets, evaluaciones, plugins…)
│   └── styles/              # Estilos CSS
│
├── backend/
│   ├── app.py               # Aplicación Flask — registro de blueprints y configuración
│   ├── requirements.txt     # Dependencias Python
│   ├── app.exe              # Backend compilado (solo distribución)
│   │
│   ├── api/                 # Blueprints de la API REST
│   │   ├── models.py        # Gestión de modelos ML
│   │   ├── datasets.py      # Gestión de datasets
│   │   ├── evaluations.py   # Ciclo de vida de evaluaciones
│   │   └── plugins.py       # Gestión de plugins
│   │
│   ├── core/
│   │   └── plugin_system.py # PluginManager: descubrimiento y carga de plugins
│   │
│   └── plugins/             # Plugins de métricas incluidos
│       ├── base.py          # Clase base abstracta MetricPlugin
│       ├── neuralstrength/  # Librería de métricas de seguridad
│       └── neuralstrength_lite/ # Versión ligera de NeuralStrength
│
├── data/                    # Datos locales (generados en tiempo de ejecución)
│   ├── models/              # Modelos ML subidos (+ metadata.json)
│   ├── datasets/            # Datasets subidos (+ metadata.json)
│   └── evaluations/         # Resultados de evaluaciones (JSON por evaluación + history.json)
│
├── assets/                  # Iconos y recursos de la aplicación
├── build/                   # Recursos para electron-builder
├── install.bat / install.sh # Scripts de instalación
├── start.bat / start.sh     # Scripts de arranque en producción
└── build-windows.bat        # Script de construcción del instalador
```

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                  Electron (main.js)                 │
│  - Gestión de ventana principal                     │
│  - Arranque del backend Python en producción        │
│  - IPC: get-backend-url, app-version                │
└──────────────────┬──────────────────────────────────┘
                   │ contextBridge (preload.js)
┌──────────────────▼──────────────────────────────────┐
│              Renderer Process (src/)                │
│  app.js  │  api.js  │  components/                  │
│  Comunicación HTTP con Flask en localhost:5000       │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP REST
┌──────────────────▼──────────────────────────────────┐
│              Flask Backend (backend/)               │
│                                                     │
│  /api/models       — Gestión de modelos ML          │
│  /api/datasets     — Gestión de datasets            │
│  /api/evaluations  — Evaluaciones (fondo)           │
│  /api/plugins      — Gestión de plugins             │
│                                                     │
│  PluginManager ——► MetricPlugin (base.py)           │
│       └── Descubrimiento recursivo de plugins       │
└─────────────────────────────────────────────────────┘
```

---

## 🌐 API REST

El backend expone una API REST en `http://127.0.0.1:5000`. A continuación se detallan todos los endpoints disponibles.

### `GET /api/health`
Comprueba el estado del servidor.

**Respuesta:**
```json
{
  "status": "healthy",
  "plugins_loaded": 3,
  "data_dir": "/ruta/al/directorio/data"
}
```

---

### Modelos — `/api/models`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/models` | Lista todos los modelos registrados |
| `GET` | `/api/models/<model_id>` | Obtiene un modelo específico |
| `POST` | `/api/models/upload` | Sube un nuevo modelo ML |
| `GET` | `/api/models/<model_id>/architecture` | Devuelve la arquitectura del modelo |
| `DELETE` | `/api/models/<model_id>` | Elimina un modelo |

**Formatos de modelo soportados:** `.h5`, `.keras` (TensorFlow/Keras), `.pt`, `.pth` (PyTorch)

**Upload — `POST /api/models/upload`** (multipart/form-data):
```
file        — Archivo del modelo (obligatorio)
name        — Nombre descriptivo (obligatorio)
framework   — 'tensorflow' | 'pytorch' (por defecto: 'tensorflow')
description — Descripción opcional
```

---

### Datasets — `/api/datasets`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/datasets/` | Lista todos los datasets |
| `GET` | `/api/datasets/<dataset_id>` | Obtiene información de un dataset |
| `POST` | `/api/datasets/upload` | Sube un nuevo dataset |
| `GET` | `/api/datasets/<dataset_id>/preview` | Previsualiza imágenes o datos tabulares |
| `DELETE` | `/api/datasets/<dataset_id>` | Elimina un dataset |

**Formatos soportados:** `.npy`, `.npz`

**Upload — `POST /api/datasets/upload`** (multipart/form-data):
```
data_file   — Archivo de datos NumPy (obligatorio)
labels_file — Archivo de etiquetas NumPy (opcional)
name        — Nombre del dataset
description — Descripción opcional
```

> ℹ️ Si se proporcionan datos y etiquetas, se valida que tengan la misma longitud.

**Preview:** Detecta automáticamente si los datos son imágenes (4D/3D) o datos tabulares y devuelve hasta 20 muestras codificadas en base64 (imágenes) o como lista (tabular).

---

### Evaluaciones — `/api/evaluations`

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/evaluations/` | Crea una nueva evaluación |
| `POST` | `/api/evaluations/<eval_id>/start` | Inicia la ejecución en background |
| `GET` | `/api/evaluations/<eval_id>/status` | Consulta el estado y progreso |
| `GET` | `/api/evaluations/<eval_id>/logs` | Obtiene los logs en tiempo real |
| `GET` | `/api/evaluations/<eval_id>/results` | Obtiene los resultados completos |
| `POST` | `/api/evaluations/<eval_id>/cancel` | Cancela una evaluación en curso |
| `DELETE` | `/api/evaluations/<eval_id>` | Elimina una evaluación del historial |
| `GET` | `/api/evaluations/history` | Lista el historial de todas las evaluaciones |
| `GET` | `/api/evaluations/<eval_id>/visualize/<metric_name>` | Genera visualización de una métrica |
| `GET` | `/api/evaluations/<eval_id>/images/<filename>` | Sirve imágenes generadas |

**Crear evaluación — `POST /api/evaluations/`**:
```json
{
  "model_id": "uuid-del-modelo",
  "dataset_id": "uuid-del-dataset",
  "metrics": ["NeuralStrength", "OtraMetrica"]
}
```

**Ciclo de vida de una evaluación:**
```
pending → running → completed
                 → cancelled
                 → error
```

**Respuesta de estado (evaluación completada):**
```json
{
  "id": "uuid",
  "status": "completed",
  "progress": 100,
  "results": {
    "NeuralStrength": {
      "status": "completed",
      "score": 72.5,
      "category": "security",
      "details": {},
      "warnings": [],
      "recommendations": [],
      "visualization": "/api/evaluations/uuid/images/NeuralStrength.png"
    }
  }
}
```

> ℹ️ Las evaluaciones se ejecutan en un hilo de fondo. Los logs de los plugins se capturan en tiempo real y se pueden consultar con el endpoint `/logs?since=<index>`.

---

### Plugins — `/api/plugins`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/plugins` | Lista todos los plugins cargados |
| `GET` | `/api/plugins/<plugin_name>` | Obtiene el manifest de un plugin |
| `POST` | `/api/plugins/upload` | Sube un plugin (`.py` o `.zip`) |
| `POST` | `/api/plugins/reload` | Recarga todos los plugins |
| `DELETE` | `/api/plugins/<plugin_name>` | Elimina un plugin |

---

## 🔌 Sistema de Plugins

Los plugins son la pieza central del sistema de evaluación. El `PluginManager` escanea recursivamente el directorio `backend/plugins/` al iniciar la aplicación y los registra automáticamente.

### Clase Base `MetricPlugin`

Todos los plugins deben heredar de `MetricPlugin` (en `backend/plugins/base.py`) e implementar los métodos obligatorios:

```python
from plugins.base import MetricPlugin

class MiMetrica(MetricPlugin):

    def manifest(self) -> dict:
        """Metadatos del plugin (obligatorio)."""
        return {
            'name': 'Mi Métrica',          # Nombre único del plugin
            'type': 'security',             # 'security' | 'privacy' | 'fairness'
            'version': '1.0.0',
            'description': 'Descripción de la métrica',
            'parameters': {},               # Parámetros configurables
            'author': 'Tu Nombre',          # Opcional
            'requirements': ['numpy']       # Opcional
        }

    def build(self, model, config: dict):
        """Prepara el plugin con el modelo y configuración."""
        self.model = model

    def call(self, dataset) -> dict:
        """
        Calcula la métrica sobre el dataset.
        
        También puedes implementar __call__ en lugar de call.
        El plugin puede recibir (dataset,) o (dataset, labels)
        según la firma de __call__.
        """
        return {
            'score': 0.85,              # float en [0, 1] — se normaliza a [0, 100]
            'details': {},              # Información adicional
            'warnings': [],             # Alertas
            'recommendations': []       # Sugerencias de mejora
        }

    def view(self):
        """Opcional: devuelve una figura matplotlib para visualización."""
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.plot(self.scores)
        return fig
```

### Despliegue de Plugins

| Tipo | Ubicación | Descripción |
|---|---|---|
| Plugin único | `backend/plugins/custom/mi_plugin.py` | Archivo Python suelto |
| Librería | `backend/plugins/mi_libreria/` | Carpeta con varios módulos |
| Upload vía UI | Subir `.py` o `.zip` desde la interfaz | Se extrae y recarga automáticamente |

### Plugins Incluidos

| Plugin | Tipo | Descripción |
|---|---|---|
| **NeuralStrength** | `security` | Evaluación de robustez adversarial con análisis avanzado |
| **NeuralStrength Lite** | `security` | Versión ligera de NeuralStrength |

---

## 📦 Construcción para Distribución

### Windows (instalador NSIS + portable)
```bash
npm run build:win
# o usando el script
build-windows.bat
```

### Linux (AppImage + .deb)
```bash
npm run build:linux
```

Los instaladores se generan en la carpeta `dist/`.

**Configuración de empaquetado** (en `package.json`):
- **AppId:** `com.neuralsentinel.mlauditor`
- **Windows:** instalador NSIS y versión portable
- **Linux:** AppImage y paquete .deb
- El backend compilado (`app.exe`) se incluye en `extraResources`

> ℹ️ Ver `BUILD.md` y `BUILD_QUICK.md` para instrucciones detalladas sobre la compilación del backend Python con PyInstaller.

---

## 🧪 Uso Básico

### Paso 1 — Cargar un Modelo

1. Navega a la sección **Modelos**.
2. Haz clic en **Subir Modelo**.
3. Selecciona un archivo `.h5` / `.keras` (TensorFlow) o `.pt` / `.pth` (PyTorch).
4. Asigna un nombre descriptivo y elige el framework.

### Paso 2 — Cargar un Dataset

1. Navega a la sección **Datasets**.
2. Haz clic en **Subir Dataset**.
3. Selecciona el archivo de datos (`.npy` o `.npz`).
4. Opcionalmente, añade un archivo de etiquetas (`.npy`).

> El dataset debe contener los datos de test en formato NumPy. Si el dataset es de imágenes, el sistema lo detecta automáticamente y muestra una previsualización de las primeras 20 muestras.

### Paso 3 — Crear una Evaluación

1. Navega a la sección **Evaluación**.
2. Selecciona el modelo y el dataset previamente cargados.
3. Selecciona las métricas (plugins) a aplicar.
4. Haz clic en **Iniciar Evaluación**.

La evaluación se ejecuta en segundo plano. Puedes monitorizar el progreso y los logs en tiempo real desde la misma pantalla.

### Paso 4 — Ver Resultados

1. Navega a la sección **Resultados** o al historial de evaluaciones.
2. Consulta la puntuación (0–100), detalles, warnings y recomendaciones de cada métrica.
3. Visualiza los gráficos generados por los plugins (si los tienen).

---

## 🔒 Seguridad y Privacidad

- ✅ **100% Local**: todos los datos (modelos, datasets, resultados) permanecen en tu equipo.
- ✅ **Sin Telemetría**: no se envía ningún dato a servidores externos.
- ✅ **Context Isolation**: el proceso renderer de Electron ejecuta con `nodeIntegration: false` y `contextIsolation: true`.
- ✅ **Backend local**: Flask escucha únicamente en `127.0.0.1:5000` (loopback).

---

## 🐍 Dependencias Python

| Paquete | Versión | Uso |
|---|---|---|
| Flask | 3.0.0 | Servidor web backend |
| flask-cors | 4.0.0 | CORS para el frontend Electron |
| numpy | 1.26.4 | Manipulación de arrays |
| pandas | 3.0.0 | Análisis de datos tabulares |
| tensorflow | 2.18.0 | Carga y evaluación de modelos TF/Keras |
| torch | ≥2.2.0 | Soporte de modelos PyTorch |
| Pillow | ≥10.0.0 | Procesamiento de imágenes |
| matplotlib | 3.7.5 | Generación de visualizaciones |
| scikit-learn | 1.8.0 | Métricas y utilidades ML |
| foolbox | 3.3.2 | Ataques adversariales |
| umap-learn | 0.5.11 | Reducción de dimensionalidad |
| seaborn | 0.13.2 | Visualización estadística |
| scipy | 1.10.1 | Cómputo científico |
| scikit-image | 0.21.0 | Procesamiento de imágenes |
| tqdm | 4.66.4 | Barras de progreso |

---

## 🤝 Contribución

### Añadir un nuevo plugin

1. Crea un archivo Python en `backend/plugins/<tu_libreria>/`.
2. Implementa la clase heredando de `MetricPlugin`.
3. Define `manifest()`, `build()` y `call()` (o `__call__()`).
4. Reinicia la aplicación o usa el endpoint `/api/plugins/reload`.

### Subir un plugin desde la interfaz

1. Empaqueta tu plugin como archivo `.py` o como `.zip` (nombre del zip = nombre de la librería).
2. Navega a la sección **Plugins** y usa el botón de subida.
3. El sistema extraerá, validará y cargará el plugin automáticamente.

---

## 📝 Licencia

MIT License — ver [LICENSE.txt](LICENSE.txt) para más detalles.

---

## 👥 Soporte

Para reportar problemas o sugerencias, contacta al equipo de **NeuralSentinel**.

---

**Versión:** 2.0.0 · **Última actualización:** Marzo 2026 · **Plataformas:** Windows 10/11, Linux (Ubuntu 20.04+)
