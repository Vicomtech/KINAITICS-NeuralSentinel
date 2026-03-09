// Results View (Fixed & Clean)
console.log('[Results.js] Script loading started');

// Global state for filtering
window.allEvaluations = [];

// Icons configuration (Monochromatic / Outline style) - Matching evaluation.js
const resultsMetricTypeConfig = {
    security: {
        icon: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>`,
        label: 'Seguridad'
    },
    privacy: {
        icon: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>`,
        label: 'Privacidad'
    },
    fairness: {
        icon: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v19"/><path d="M5 8h14"/><path d="M2 13h4"/><path d="M18 13h4"/></svg>`,
        label: 'Equidad'
    }
};

window.renderResults = function (container) {
    console.log('[Results] Rendering view...');
    container.innerHTML = `
        <style>
            .pillar-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }
            .pillar-card {
                background: white;
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 1.5rem;
                display: flex;
                flex-direction: column;
            }
            .pillar-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
                padding-bottom: 0.5rem;
                border-bottom: 2px solid var(--border-color);
            }
            .pillar-title {
                font-weight: 600;
                font-size: 1.1rem;
                color: var(--text-primary);
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            .average-score {
                font-size: 2rem;
                font-weight: 700;
                text-align: center;
                margin: 1rem 0;
            }
            .metric-list {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }
            .metric-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.75rem;
                background: var(--bg-secondary);
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.2s;
                border: 1px solid transparent;
            }
            .metric-item:hover {
                background: white;
                border-color: var(--primary-color);
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                transform: translateY(-1px);
            }
            .metric-score-badge {
                font-weight: 700;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.875rem;
            }
            
            /* Modal Styles */
            .modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
                backdrop-filter: blur(2px);
            }
            .modal-content {
                background: white;
                padding: 2rem;
                border-radius: 12px;
                max-width: 600px;
                width: 90%;
                max-height: 90vh;
                overflow-y: auto;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }
            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
                border-bottom: 1px solid var(--border-color);
                padding-bottom: 1rem;
            }
            .close-btn {
                background: none;
                border: none;
                font-size: 1.5rem;
                cursor: pointer;
                color: var(--text-secondary);
            }
            .close-btn:hover { color: var(--text-primary); }
            
            .btn-icon-danger {
                background: none;
                border: none;
                cursor: pointer;
                color: #dc3545;
                padding: 0.5rem;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background-color 0.2s;
            }
            .btn-icon-danger:hover {
                background-color: #fee2e2;
            }
            
            /* Enhanced Details Styles */
            .detail-item {
                padding: 0.5rem 0;
                border-bottom: 1px solid #f3f4f6;
            }
            .detail-row {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 1rem;
            }
            .detail-key {
                color: var(--text-secondary);
                font-size: 0.85rem;
                white-space: nowrap;
            }
            .detail-value {
                font-weight: 600;
                text-align: right;
                word-break: break-all;
                font-family: 'JetBrains Mono', 'Fira Code', monospace;
                font-size: 0.8rem;
            }
            .detail-nested {
                margin-top: 0.5rem;
                padding-left: 1rem;
                border-left: 2px solid var(--border-color);
            }
            .detail-summary {
                cursor: pointer;
                color: var(--primary-color);
                font-weight: 600;
                font-size: 0.85rem;
                display: flex;
                align-items: center;
                gap: 0.25rem;
                user-select: none;
            }
            .detail-summary:hover {
                color: var(--primary-dark);
            }
            .clickable-viz {
                cursor: zoom-in;
                transition: transform 0.2s;
            }
            .clickable-viz:hover {
                transform: scale(1.02);
            }
        </style>

        <div class="card mb-2">
            <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
                <h3 class="card-title" style="margin: 0;">Resultados de Evaluaciones</h3>
                <div style="display: flex; gap: 1rem; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <label for="modelFilter" style="font-weight: 500; font-size: 0.9rem;">Filtrar por Modelo:</label>
                        <select id="modelFilter" class="form-select" style="width: 200px; padding: 0.4rem;" onchange="filterEvaluations()">
                            <option value="all">Todos los modelos</option>
                        </select>
                    </div>
                    <button class="btn btn-secondary" onclick="loadEvaluationHistory()">
                        <span>🔄</span>
                    </button>
                </div>
            </div>
        </div>

        <div id="resultsContent"></div>
    `;

    loadEvaluationHistory();
};

// Helper function for progressive colors
function getScoreColor(score) {
    let hue = 0;
    if (score < 0.5) {
        hue = (score / 0.5) * 30; // Red to Orange
    } else if (score < 0.8) {
        hue = 30 + ((score - 0.5) / 0.3) * 30; // Orange to Yellow
    } else {
        hue = 60 + ((score - 0.8) / 0.2) * 60; // Yellow to Green
    }
    return `hsl(${hue}, 90%, 40%)`;
}

function getScoreBgColor(score) {
    let hue = 0;
    if (score < 0.5) {
        hue = (score / 0.5) * 30;
    } else if (score < 0.8) {
        hue = 30 + ((score - 0.5) / 0.3) * 30;
    } else {
        hue = 60 + ((score - 0.8) / 0.2) * 60;
    }
    return `hsl(${hue}, 90%, 92%)`;
}

async function loadEvaluationHistory() {
    const container = document.getElementById('resultsContent');
    const filterSelect = document.getElementById('modelFilter');

    if (!container) return;

    try {
        container.innerHTML = '<div class="spinner" style="margin: 2rem auto;"></div>';

        // Fetch evaluations and models in parallel
        const [history, models] = await Promise.all([
            window.api.getEvaluationHistory(),
            window.api.getModels()
        ]);

        window.allEvaluations = history || [];

        // Populate filter dropdown
        if (filterSelect) {
            const currentFilter = filterSelect.value;
            const modelMap = new Map();

            // Map model IDs to Names
            models.forEach(m => modelMap.set(m.id, m.name));

            // Find all unique model IDs used in evaluations
            const usedModelIds = new Set(window.allEvaluations.map(e => e.model_id).filter(id => id));

            filterSelect.innerHTML = '<option value="all">Todos los modelos</option>';
            usedModelIds.forEach(id => {
                const name = modelMap.get(id) || `Modelo ${id.substring(0, 8)}...`;
                const option = document.createElement('option');
                option.value = id;
                option.textContent = name;
                filterSelect.appendChild(option);
            });

            // Restore previous selection if valid
            if (usedModelIds.has(currentFilter)) {
                filterSelect.value = currentFilter;
            }
        }

        renderFilteredEvaluations();

    } catch (error) {
        console.error('Error loading evaluation history:', error);
        container.innerHTML = `
            <div class="alert alert-error">
                <strong>Error:</strong> No se pudo cargar el historial: ${error.message}
            </div>
        `;
    }
}

window.filterEvaluations = function () {
    renderFilteredEvaluations();
};

function renderFilteredEvaluations() {
    const container = document.getElementById('resultsContent');
    const filterSelect = document.getElementById('modelFilter');

    if (!container) return;

    const selectedModelId = filterSelect ? filterSelect.value : 'all';
    let filtered = window.allEvaluations;

    if (selectedModelId !== 'all') {
        filtered = filtered.filter(e => e.model_id === selectedModelId);
    }

    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="card">
                <div class="card-body" style="text-align: center; padding: 3rem;">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
                    <h3>No hay evaluaciones ${selectedModelId !== 'all' ? 'para este modelo' : 'completadas'}</h3>
                    <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                        Las evaluaciones que ejecutes aparecerán aquí
                    </p>
                    <button class="btn btn-primary" onclick="window.app.switchView('evaluation')">
                        Crear Nueva Evaluación
                    </button>
                </div>
            </div>
        `;
        return;
    }

    // Sort by date (most recent first)
    filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    // Render evaluations
    container.innerHTML = filtered.map(evaluation => renderEvaluationCard(evaluation)).join('');
}

async function deleteEvaluation(id) {
    if (!confirm('¿Estás seguro de eliminar esta evaluación? Esta acción no se puede deshacer.')) return;

    try {
        await window.api.deleteEvaluation(id);
        // Reload to refresh the list and filters
        loadEvaluationHistory();
    } catch (error) {
        alert('Error al eliminar evaluación: ' + error.message);
    }
}

// Make globally accessible
window.deleteEvaluation = deleteEvaluation;

function renderEvaluationCard(evaluation) {
    const date = new Date(evaluation.created_at);
    const dateStr = date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    const statusBadge = {
        'pending': '<span class="badge badge-warning">⏳ Pendiente</span>',
        'running': '<span class="badge badge-info">🔄 Ejecutando</span>',
        'completed': '<span class="badge badge-success">✓ Completado</span>',
        'error': '<span class="badge badge-danger">✗ Error</span>'
    }[evaluation.status] || '<span class="badge">Desconocido</span>';

    return `
        <div class="card mb-2">
            <div class="card-header">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0;">Evaluación del ${dateStr}</h4>
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem;">
                            ID: ${evaluation.id.substring(0, 8)}...  |  Modelo ID: ${evaluation.model_id ? evaluation.model_id.substring(0, 8) + '...' : 'Desconocido'}
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        ${statusBadge}
                        ${evaluation.status !== 'running' ? `
                            <button class="btn-icon-danger" onclick="window.deleteEvaluation('${evaluation.id}')" title="Eliminar Evaluación">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
            <div class="card-body">
                ${evaluation.status === 'completed' ?
            renderCompletedResults(evaluation) :
            renderPendingResults(evaluation)
        }
            </div>
        </div>
    `;
}

function renderPendingResults(evaluation) {
    if (evaluation.status === 'running') {
        return `
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div class="progress" style="flex-grow: 1; height: 12px; border-radius: 6px;">
                    <div class="progress-bar" style="width: ${evaluation.progress || 0}%;"></div>
                </div>
                <button class="btn btn-primary btn-sm" onclick="window.resumeEvaluation('${evaluation.id}')" style="white-space: nowrap;">
                    Ver progreso
                </button>
            </div>
            <p style="margin-top: 0.5rem; color: var(--text-secondary); font-size: 0.85rem;">
                Estado: Ejecutando métricas... (${evaluation.progress || 0}%)
            </p>
        `;
    }

    if (evaluation.status === 'error') {
        return `
            <div class="alert alert-error">
                <strong>Error en la evaluación:</strong>
                <pre style="margin-top: 0.5rem; white-space: pre-wrap;">${evaluation.error || 'Error desconocido'}</pre>
            </div>
        `;
    }

    return `
        <p style="color: var(--text-secondary);">
            Evaluación pendiente de iniciar
        </p>
    `;
}


function renderCompletedResults(evaluation) {
    const results = evaluation.results || {};
    const metricsCount = Object.keys(results).length;

    if (metricsCount === 0) {
        return '<p style="color: var(--text-secondary);">No hay resultados disponibles</p>';
    }

    // Group metrics by category
    const groupedResults = {
        security: [],
        privacy: [],
        fairness: [],
        unknown: []
    };

    Object.entries(results).forEach(([metricName, result]) => {
        let category = result.category || result.details?.metric_category;

        if (!category || category === 'unknown') {
            const lowerName = metricName.toLowerCase();
            if (lowerName.includes('robustness') || lowerName.includes('adversarial') || lowerName.includes('poisoning')) category = 'security';
            else if (lowerName.includes('privacy') || lowerName.includes('inference') || lowerName.includes('extraction')) category = 'privacy';
            else if (lowerName.includes('fairness') || lowerName.includes('bias') || lowerName.includes('disparate')) category = 'fairness';
            else category = 'unknown';
        }

        const item = { name: metricName, ...result };

        if (groupedResults[category]) {
            groupedResults[category].push(item);
        } else {
            groupedResults.unknown.push(item);
        }
    });

    // Save for modal access
    window.currentEvaluationResults = groupedResults;

    const evalId = evaluation.id;

    return `
        <div class="pillar-grid">
            ${renderPillarColumn(resultsMetricTypeConfig.security.icon + ' Seguridad', groupedResults.security, evalId)}
            ${renderPillarColumn(resultsMetricTypeConfig.privacy.icon + ' Privacidad', groupedResults.privacy, evalId)}
            ${renderPillarColumn(resultsMetricTypeConfig.fairness.icon + ' Equidad', groupedResults.fairness, evalId)}
        </div>
        
        ${groupedResults.unknown.length > 0 ? renderPillarColumn('❓ Otros', groupedResults.unknown, evalId) : ''}

        <div style="display: flex; gap: 0.5rem; justify-content: flex-end; margin-top: 1rem; border-top: 1px solid var(--border-color); padding-top: 1rem;">
            <button class="btn btn-secondary btn-sm" onclick="viewEvaluationDetails('${evaluation.id}')">
                👁️ Ver JSON Completo
            </button>
            <button class="btn btn-primary btn-sm" onclick="downloadResults('${evaluation.id}')">
                📥 Descargar Informe
            </button>
        </div>
    `;
}

function renderPillarColumn(title, metrics, evalId) {
    // Calculate average score
    let averageScore = 0;
    let scoreText = '-';
    let scoreColor = 'var(--text-secondary)';

    if (metrics && metrics.length > 0) {
        const sum = metrics.reduce((acc, curr) => acc + (curr.score || 0), 0);
        averageScore = sum / metrics.length;
        scoreText = averageScore.toFixed(1) + '%';
        scoreColor = getScoreColor(averageScore / 100);
    }

    return `
        <div class="pillar-card">
            <div class="pillar-header">
                <span class="pillar-title">${title}</span>
                <span class="badge" style="background: var(--bg-secondary);">${metrics.length} métricas</span>
            </div>
            
            <div class="average-score" style="color: ${scoreColor}">
                ${scoreText}
            </div>
            
            <div class="metric-list">
                ${metrics.length > 0 ? metrics.map((metric, index) => renderMetricItem(metric, evalId)).join('') :
            '<p style="text-align:center; color:var(--text-secondary); font-size:0.9rem;">Sin métricas</p>'}
            </div>
        </div>
    `;
}

function renderMetricItem(metric, evalId) {
    const scoreVal = (metric.score || 0).toFixed(1) + '%';
    const color = getScoreColor((metric.score || 0) / 100);
    const bgColor = getScoreBgColor((metric.score || 0) / 100);

    // Encode data for click handler
    // Include evalId in the object for the modal
    const metricWithId = { ...metric, evalId: evalId };
    const metricData = encodeURIComponent(JSON.stringify(metricWithId));

    return `
        <div class="metric-item" onclick="openMetricModal('${metricData}')">
            <span style="font-weight: 500; font-size: 0.9rem;">${metric.name}</span>
            <span class="metric-score-badge" style="color: ${color}; background: ${bgColor};">
                ${scoreVal}
            </span>
        </div>
    `;
}

// Global function to open modal
window.openMetricModal = function (metricDataEncoded) {
    const metric = JSON.parse(decodeURIComponent(metricDataEncoded));
    const normalizedScore = (metric.score || 0) / 100;
    const color = getScoreColor(normalizedScore);
    const scoreVal = (metric.score || 0).toFixed(1) + '%';

    // Enhanced detail renderer
    const renderDetailValue = (key, value, isNested = false) => {
        if (value === null || value === undefined) return '<span style="color:#ccc;">null</span>';

        if (typeof value === 'object') {
            const entries = Object.entries(value);
            if (entries.length === 0) return Array.isArray(value) ? '[]' : '{}';

            return `
                <details class="detail-nested" ${isNested ? '' : 'open'}>
                    <summary class="detail-summary">
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
                        ${key} (${entries.length})
                    </summary>
                    <div style="margin-top: 0.5rem;">
                        ${entries.map(([k, v]) => `
                            <div class="detail-item">
                                ${renderDetailValue(k, v, true)}
                            </div>
                        `).join('')}
                    </div>
                </details>
            `;
        }

        return `
            <div class="detail-row">
                <span class="detail-key">${key}:</span>
                <span class="detail-value">${typeof value === 'number' ? value.toLocaleString(undefined, { maximumFractionDigits: 4 }) : value}</span>
            </div>
        `;
    };

    window.openFullImage = function (src) {
        const fullWin = window.open('', '_blank');
        fullWin.document.write(`
            <html>
                <head>
                    <title>Visualización - ${metric.name}</title>
                    <style>
                        body { margin: 0; background: #1a1a1a; display: flex; align-items: center; justify-content: center; height: 100vh; font-family: sans-serif; }
                        img { max-width: 95%; max-height: 95%; object-fit: contain; box-shadow: 0 10px 30px rgba(0,0,0,0.5); background: white; border-radius: 4px; }
                        .toolbar { position: fixed; top: 0; left: 0; right: 0; padding: 1rem; background: rgba(0,0,0,0.5); color: white; display: flex; justify-content: space-between; align-items: center; }
                        .btn-close { color: white; text-decoration: none; font-size: 1.5rem; font-weight: bold; }
                    </style>
                </head>
                <body>
                    <div class="toolbar">
                        <span>${metric.name} - Visualización Completa</span>
                        <a href="javascript:window.close()" class="btn-close">×</a>
                    </div>
                    <img src="${src}" alt="Visualización completa">
                </body>
            </html>
        `);
    };

    // Determine visualization source
    let vizSrc = '';
    if (metric.visualization) {
        if (metric.visualization.startsWith('data:') || metric.visualization.startsWith('http')) {
            vizSrc = metric.visualization;
        } else if (metric.visualization.startsWith('/')) {
            vizSrc = `http://localhost:5000${metric.visualization}`;
        } else {
            vizSrc = `data:image/png;base64,${metric.visualization}`;
        }
    }

    const modalHtml = `
        <div class="modal-overlay" onclick="window.closeMetricModal(event)">
            <div class="modal-content">
                <div class="modal-header">
                    <h3 style="margin:0;">${metric.name}</h3>
                    <button class="close-btn" onclick="window.closeMetricModal(event, true)">×</button>
                </div>
                
                <div style="text-align: center; margin-bottom: 2rem;">
                    <div style="font-size: 3rem; font-weight: 700; color: ${color};">
                        ${scoreVal}
                    </div>
                    <div style="color: var(--text-secondary);">Puntuación General</div>
                </div>
                
                ${metric.status === 'error' ? `
                    <div class="alert alert-error">
                        <strong>Error:</strong> ${metric.error}
                    </div>
                ` : ''}
                
                <div class="section" style="margin-bottom: 1.5rem;">
                    <h4 style="margin-bottom: 0.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.25rem;">📊 Visualización</h4>
                    
                     ${vizSrc ? `
                        <div style="text-align: center; padding: 1rem; background: #f9fafb; border-radius: 8px;">
                            <img src="${vizSrc}" class="clickable-viz" onclick="window.openFullImage('${vizSrc}')" style="max-width: 100%; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" title="Haz clic para ver en grande" alt="Visualización de métrica">
                            <div style="margin-top: 0.5rem; font-size: 0.75rem; color: var(--text-secondary);">🔍 Haz clic para ampliar</div>
                        </div>
                    ` : `
                        <div id="viz-container-${metric.name.replace(/\s+/g, '-')}" style="text-align: center; padding: 1rem; background: #f9fafb; border-radius: 8px;">
                            <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); toggleVisualization('${metric.name}', '${metric.evalId}')">
                                <span style="margin-right:0.5rem;">👁️</span> Generar Visualización
                            </button>
                            <div style="margin-top:0.5rem; font-size: 0.8rem; color: var(--text-secondary);">
                                Haz clic para generar la gráfica en tiempo real.
                            </div>
                        </div>
                    `}
                </div>
                
                <div style="display: grid; gap: 1.5rem;">
                    ${metric.details ? `
                        <div class="section">
                            <h4 style="margin-bottom: 0.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.25rem;">📝 Detalles Técnicos</h4>
                            <div style="background: #fcfcfc; border-radius: 8px; padding: 0.5rem; border: 1px solid #f0f0f0;">
                                ${Object.entries(metric.details).map(([key, value]) => `
                                    <div class="detail-item">
                                        ${renderDetailValue(key, value)}
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    ${metric.warnings && metric.warnings.length > 0 ? `
                        <div class="section">
                            <h4 style="margin-bottom: 0.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.25rem;">⚠️ Advertencias</h4>
                            <ul style="margin: 0; padding-left: 1.25rem; color: var(--warning-dark);">
                                ${metric.warnings.map(w => `<li>${w}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    ${metric.recommendations && metric.recommendations.length > 0 ? `
                        <div class="section">
                            <h4 style="margin-bottom: 0.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.25rem;">💡 Recomendaciones</h4>
                            <ul style="margin: 0; padding-left: 1.25rem; color: var(--text-primary);">
                                ${metric.recommendations.map(r => `<li>${r}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;

    const modalContainer = document.createElement('div');
    modalContainer.id = 'metric-modal-container';
    modalContainer.innerHTML = modalHtml;
    document.body.appendChild(modalContainer);
};

window.toggleVisualization = async function (metricName, evalId) {
    const containerId = `viz-container-${metricName.replace(/\s+/g, '-')}`;
    const container = document.getElementById(containerId);
    if (!container) return;

    // Check if already loaded
    if (container.querySelector('img')) return;

    container.innerHTML = '<div class="spinner" style="margin: 0 auto;"></div><div style="font-size:0.8rem; margin-top:0.5rem;">Generando visualización...</div>';

    try {
        const response = await fetch(`http://localhost:5000/api/evaluations/${evalId}/visualize/${metricName}`);
        const data = await response.json();

        if (response.status !== 200) {
            throw new Error(data.error || 'Error desconocido');
        }

        container.innerHTML = `
            <img src="data:image/png;base64,${data.image}" class="clickable-viz" onclick="window.openFullImage('data:image/png;base64,${data.image}')" style="max-width: 100%; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" title="Haz clic para ver en grande" alt="Visualización">
            <div style="margin-top: 0.5rem; font-size: 0.75rem; color: var(--text-secondary);">🔍 Haz clic para ampliar</div>
        `;
    } catch (e) {
        console.error(e);
        container.innerHTML = `
            <div class="alert alert-error" style="font-size: 0.8rem; text-align: left;">
                <strong>Error:</strong> ${e.message}
                <br>
                <button class="btn btn-secondary btn-sm" style="margin-top:0.5rem;" onclick="toggleVisualization('${metricName}', '${evalId}')">Reintentar</button>
            </div>`;
    }
}

window.closeMetricModal = function (event, force = false) {
    if (force || event.target.classList.contains('modal-overlay')) {
        const container = document.getElementById('metric-modal-container');
        if (container) {
            container.remove();
        }
    }
};

async function viewEvaluationDetails(evalId) {
    try {
        const results = await window.api.getEvaluationResults(evalId);

        const detailsWindow = window.open('', '_blank', 'width=800,height=600');
        detailsWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Detalles de Evaluación - ${evalId.substring(0, 8)}</title>
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        padding: 2rem;
                        background: #f5f5f5;
                    }
                    pre {
                        background: white;
                        padding: 1rem;
                        border-radius: 8px;
                        overflow-x: auto;
                        border: 1px solid #ddd;
                    }
                    h1 { color: #333; }
                </style>
            </head>
            <body>
                <h1>Detalles de Evaluación</h1>
                <pre>${JSON.stringify(results, null, 2)}</pre>
            </body>
            </html>
        `);
    } catch (error) {
        alert('Error al cargar detalles: ' + error.message);
    }
}
window.viewEvaluationDetails = viewEvaluationDetails;

async function downloadResults(evalId) {
    try {
        const results = await window.api.getEvaluationResults(evalId);

        const dataStr = JSON.stringify(results, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });

        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `evaluation_${evalId.substring(0, 8)}_${new Date().toISOString().split('T')[0]}.json`;
        link.click();

        URL.revokeObjectURL(url);
    } catch (error) {
        alert('Error al descargar resultados: ' + error.message);
    }
}
window.downloadResults = downloadResults;
