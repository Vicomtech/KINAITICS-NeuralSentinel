# 🚀 Instrucciones para Generar el Ejecutable de Windows

## Método Rápido (Script Automático)

### Opción 1: Usar el Script de Build

```cmd
build-windows.bat
```

Este script instala todo y genera el ejecutable automáticamente.

---

## Método Manual (Paso a Paso)

Si el script automático no funciona, sigue estos pasos:

### Paso 1: Habilitar Scripts de PowerShell (Solo si hay error)

Si ves error "scripts is disabled", ejecuta esto **como Administrador**:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Paso 2: Instalar Dependencias

```cmd
npm install
```

### Paso 3: Construir el Ejecutable

```cmd
npm run build:win
```

Espera 2-5 minutos mientras se genera el instalador.

### Paso 4: Encontrar el Instalador

El ejecutable estará en:
```
dist\ML Auditor-1.0.0-Setup.exe
```

---

## 📦 Archivos Generados

Después del build encontrarás en `dist/`:

- **ML Auditor-1.0.0-Setup.exe** ← Instalador (recomendado)
- **ML Auditor-1.0.0-portable.exe** ← Versión portable
- **win-unpacked/** ← Versión desempaquetada (para testing)

---

## ✅ Probar el Instalador

1. Ve a la carpeta `dist`
2. Ejecuta `ML Auditor-1.0.0-Setup.exe`
3. Sigue el asistente de instalación
4. La aplicación se instalará en `C:\Program Files\ML Auditor\`

---

## ⚠️ Notas Importantes

### Python Requerido

El ejecutable **NO incluye Python**. Los usuarios deben tener:
- Python 3.8 o superior instalado
- Las dependencias de `backend/requirements.txt` instaladas

### Primera Ejecución

Al ejecutar por primera vez:
1. El backend Python iniciará automáticamente
2. Electron abrirá la interfaz
3. Puede tardar 10-15 segundos en cargar

---

## 🐛 Si hay Problemas

### Error: "npm command not found"
**Solución:** Instala Node.js desde https://nodejs.org/

### Error: "icon.ico not found"
**Solución:** Ya está solucionado, se genera automáticamente

### Error: Build muy lento
**Solución:** Normal, puede tardar 5-10 minutos en la primera vez

### El instalador no arranca
**Solución:** 
- Verifica que Python esté en el PATH
- Reinstala las dependencias: `cd backend && pip install -r requirements.txt`

---

## 📊 Tamaño Estimado

- **Instalador:** ~150-200 MB
- **Instalación completa:** ~300-400 MB

---

**¿Necesitas ayuda?** Revisa `BUILD.md` para la guía completa.
