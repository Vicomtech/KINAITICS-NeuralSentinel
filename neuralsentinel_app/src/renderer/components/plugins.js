// Plugins View
window.renderPlugins = function (container) {
    container.innerHTML = `
        <div class="card mb-2">
            <div class="card-header">
                <h3 class="card-title">Plugins de Métricas</h3>
                <div style="display: flex; gap: 0.5rem;">
                    <button class="btn btn-primary" onclick="showUploadPluginDialog()">
                        <span>📤</span>
                        Cargar Plugin / Librería
                    </button>
                    <button class="btn btn-secondary" onclick="reloadPlugins()">
                        <span>🔄</span>
                        Recargar
                    </button>
                </div>
            </div>
        </div>

        <div id="pluginsContainer"></div>

        <!-- Upload Plugin Modal -->
        <div id="uploadPluginModal" class="hidden" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 1000; display: flex; align-items: center; justify-content: center;">
            <div class="card" style="width: 600px; max-width: 90%;">
                <div class="card-header">
                    <h3 class="card-title">Cargar Nuevo Plugin o Librería</h3>
                    <button onclick="closeUploadPluginDialog()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer;">×</button>
                </div>
                <div class="card-body">
                    <div class="alert alert-info" style="margin-bottom: 1rem;">
                        <span>ℹ️</span>
                        <div>
                            Puedes subir:
                            <ul style="margin: 0.5rem 0 0 1.2rem; padding: 0;">
                                <li><strong>Archivo Individual (.py)</strong>: Un plugin simple.</li>
                                <li><strong>Librería Completa (.zip)</strong>: Un conjunto de plugins/métricas. El ZIP se descomprimirá en el sistema.</li>
                            </ul>
                            <br>
                            Los plugins deben heredar de <code>MetricPlugin</code> e implementar <code>manifest()</code>.
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Archivo (.py / .zip)</label>
                        <input type="file" class="form-input" id="pluginFile" accept=".py,.zip">
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">
                            Sube un archivo Python o un ZIP con múltiples métricas.
                        </div>
                    </div>
                    
                    <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                        <button class="btn btn-secondary" onclick="closeUploadPluginDialog()">Cancelar</button>
                        <button class="btn btn-primary" onclick="uploadPlugin()">Cargar</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    loadPlugins();
};

async function loadPlugins() {
    const container = document.getElementById('pluginsContainer');
    container.innerHTML = '<div class="spinner" style="margin: 2rem auto;"></div>';

    try {
        const plugins = await window.api.getPlugins();

        if (!plugins || plugins.length === 0) {
            container.innerHTML = `
                <div class="card">
                    <div class="empty-state">
                        <div class="empty-state-icon">🔌</div>
                        <div class="empty-state-title">No hay plugins cargados</div>
                        <div class="empty-state-text">
                            Sube un plugin (.py) o una librería (.zip) para empezar.
                        </div>
                    </div>
                </div>
            `;
            return;
        }

        // Group plugins by type
        const pluginsByType = {
            security: plugins.filter(p => p.type === 'security'),
            privacy: plugins.filter(p => p.type === 'privacy'),
            fairness: plugins.filter(p => p.type === 'fairness'),
            other: plugins.filter(p => !['security', 'privacy', 'fairness'].includes(p.type))
        };

        // Icons configuration matching evaluation.js
        const typeLabels = {
            security: {
                name: 'Seguridad',
                icon: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>`,
                colors: { bg: '#fee2e2', border: '#ef4444', text: '#991b1b' } // Red theme
            },
            privacy: {
                name: 'Privacidad',
                icon: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>`,
                colors: { bg: '#dbeafe', border: '#3b82f6', text: '#1e40af' } // Blue theme
            },
            fairness: {
                name: 'Equidad',
                icon: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v19"/><path d="M5 8h14"/><path d="M2 13h4"/><path d="M18 13h4"/></svg>`,
                colors: { bg: '#fef3c7', border: '#f59e0b', text: '#92400e' } // Amber/Yellow theme
            },
            other: {
                name: 'Otros',
                icon: '❓',
                colors: { bg: '#f3f4f6', border: '#9ca3af', text: '#374151' } // Gray theme
            }
        };

        container.innerHTML = Object.entries(pluginsByType)
            .filter(([type, list]) => list.length > 0)
            .map(([type, list]) => {
                const typeInfo = typeLabels[type] || typeLabels.other;
                return `
                    <div class="card mb-2">
                        <div class="card-header">
                            <h3 class="card-title" style="display: flex; align-items: center; gap: 0.5rem;">
                                <span style="display: flex; align-items: center; color: ${typeInfo.colors.border};">
                                    ${typeInfo.icon}
                                </span>
                                ${typeInfo.name} (${list.length})
                            </h3>
                        </div>
                        <div class="card-body">
                            <div class="grid grid-cols-1" style="gap: 1rem;">
                                ${list.map(plugin => `
                                    <div style="padding: 1rem; background: var(--bg-light); border-radius: var(--radius-md); border-left: 4px solid ${typeInfo.colors.border};">
                                        <div style="display: flex; justify-content: space-between; align-items: start;">
                                            <div style="flex: 1;">
                                                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; flex-wrap: wrap;">
                                                    <div style="font-weight: 700; font-size: 1.05rem;">${plugin.name}</div>
                                                    ${plugin.library ? `<span class="badge" style="background: #f3f4f6; color: #4b5563; border: 1px solid #d1d5db; font-size: 0.75rem; font-weight: normal;">📚 ${plugin.library}</span>` : ''}
                                                    <span class="badge" style="background: ${typeInfo.colors.bg}; color: ${typeInfo.colors.text}; border: 1px solid ${typeInfo.colors.border};">${plugin.version}</span>
                                                </div>
                                                <div style="color: var(--text-secondary); margin-bottom: 0.75rem;">
                                                    ${plugin.description}
                                                </div>
                                                ${plugin.author ? `<div style="font-size: 0.875rem; color: var(--text-light);">Autor: ${plugin.author}</div>` : ''}
                                                ${Object.keys(plugin.parameters || {}).length > 0 ? `
                                                    <details style="margin-top: 0.5rem;">
                                                        <summary style="cursor: pointer; font-weight: 600; font-size: 0.9rem;">
                                                            Parámetros configurables (${Object.keys(plugin.parameters).length})
                                                        </summary>
                                                        <div style="margin-top: 0.5rem; padding-left: 1rem;">
                                                            ${Object.entries(plugin.parameters).map(([key, param]) => `
                                                                <div style="margin-bottom: 0.5rem;">
                                                                    <strong>${key}</strong> (${param.type}): ${param.description}
                                                                    <br><small style="color: var(--text-secondary);">Default: ${param.default}</small>
                                                                </div>
                                                            `).join('')}
                                                        </div>
                                                    </details>
                                                ` : ''}
                                            </div>
                                            
                                            <!-- Delete Button -->
                                            <button 
                                                class="btn-icon danger" 
                                                onclick="confirmDeletePlugin('${plugin.name}')" 
                                                title="Eliminar Plugin"
                                                style="background: #fee2e2; border: 1px solid #ef4444; color: #ef4444; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; border-radius: 4px; cursor: pointer; margin-left: 1rem;"
                                            >
                                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                                            </button>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');

    } catch (error) {
        console.error(error);
        container.innerHTML = `
            <div class="alert alert-danger">
                <span>⚠️</span>
                <div>Error al cargar plugins: ${error.message}</div>
            </div>
        `;
    }
}

async function confirmDeletePlugin(pluginName) {
    if (confirm(`¿Estás seguro de que quieres eliminar el plugin "${pluginName}"?\n\nEsta acción también eliminará el archivo original del sistema.`)) {
        try {
            await window.api.deletePlugin(pluginName);
            // Refresh list
            loadPlugins();
            // Show toast or alert
            // alert('Plugin eliminado correctamente');
        } catch (error) {
            alert('Error al eliminar plugin: ' + error.message);
        }
    }
}

async function reloadPlugins() {
    try {
        await window.api.reloadPlugins();
        loadPlugins();
        alert('Plugins y librerías recargados exitosamente');
    } catch (error) {
        alert('Error al recargar plugins: ' + error.message);
    }
}

function showUploadPluginDialog() {
    document.getElementById('uploadPluginModal').classList.remove('hidden');
}

function closeUploadPluginDialog() {
    document.getElementById('uploadPluginModal').classList.add('hidden');
    const fileInput = document.getElementById('pluginFile');
    if (fileInput) fileInput.value = '';
}

async function uploadPlugin() {
    const fileInput = document.getElementById('pluginFile');
    const file = fileInput.files[0];

    if (!file) {
        alert('Por favor selecciona un archivo');
        return;
    }

    if (!file.name.endsWith('.py') && !file.name.endsWith('.zip')) {
        alert('Solo se permiten archivos .py (plugins individuales) o .zip (librerías completas)');
        return;
    }

    const formData = new FormData();
    // Category is automatically determined by the backend/manifest now
    formData.append('file', file);

    try {
        const result = await window.api.uploadPlugin(formData);
        console.log('Upload result:', result);

        closeUploadPluginDialog();
        await reloadPlugins();

        const type = file.name.endsWith('.zip') ? 'Librería' : 'Plugin';
        alert(`${type} cargado exitosamente.`);

    } catch (error) {
        console.error(error);
        alert('Error al cargar: ' + error.message);
    }
}

window.reloadPlugins = reloadPlugins;
window.showUploadPluginDialog = showUploadPluginDialog;
window.closeUploadPluginDialog = closeUploadPluginDialog;
window.uploadPlugin = uploadPlugin;
window.confirmDeletePlugin = confirmDeletePlugin;
