// Define module-level variables or use session persistence
// Use a global object to persist state across view switches
if (!window.evaluationSession) {
    window.evaluationSession = {
        selectedMetrics: [],
        selectedMetricTypes: {},
        currentEvalId: null,
        isPolling: false,
        capturedLogs: [],
        logIndex: 0
    };
}

let availablePlugins = {};
let currentMetricTab = 'security';

// Map local variables to session object for backward compatibility/ease of use
// and define helpers to sync them
const getSession = () => window.evaluationSession;

// Icons configuration (Monochromatic / Outline style)
// We keep the icons black/monochrome as requested previously, but we will apply colors to the containers/bars
const metricTypeConfig = {
    security: {
        id: 'security',
        icon: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>`,
        label: 'Seguridad',
        colors: { bg: '#fee2e2', border: '#ef4444', text: '#991b1b', bar: '#ef4444' }
    },
    privacy: {
        id: 'privacy',
        icon: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>`,
        label: 'Privacidad',
        colors: { bg: '#dbeafe', border: '#3b82f6', text: '#1e40af', bar: '#3b82f6' }
    },
    fairness: {
        id: 'fairness',
        icon: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v19"/><path d="M5 8h14"/><path d="M2 13h4"/><path d="M18 13h4"/></svg>`,
        label: 'Equidad',
        colors: { bg: '#fef3c7', border: '#f59e0b', text: '#92400e', bar: '#f59e0b' }
    }
};

window.renderEvaluation = function (container) {
    console.log('[Evaluation] Rendering view...');

    const session = getSession();

    // Reset state ONLY if not currently running
    if (!session.isPolling) {
        session.selectedMetrics = [];
        session.selectedMetricTypes = {};
        session.capturedLogs = [];
        session.logIndex = 0;
    }

    currentMetricTab = 'security';

    container.innerHTML = `
        <div class="card mb-2">
            <div class="card-header">
                <h3 class="card-title">Nueva Evaluación de Modelo</h3>
            </div>
            <div class="card-body">
                <div class="alert alert-info">
                    <span>ℹ️</span>
                    <div>Configura los parámetros de la auditoría seleccionando el modelo, dataset y métricas a evaluar.</div>
                </div>
            </div>
        </div>

        <!-- Three Column Layout for Selection -->
        <div class="grid grid-cols-3" style="gap: 1.5rem; align-items: start;">
            <!-- Column 1: Model & Dataset Selection -->
            <div class="card">
                <div class="card-header">
                    <h4 class="card-title">1️⃣ Seleccionar Datos</h4>
                </div>
                <div class="card-body">
                    <div class="form-group">
                        <label class="form-label">Modelo</label>
                        <select class="form-select" id="evalModel">
                            <option value="">Cargando modelo...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Dataset</label>
                        <select class="form-select" id="evalDataset">
                            <option value="">Cargando datasets...</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- Column 2: Metrics Selection -->
            <div class="card">
                <div class="card-header">
                    <h4 class="card-title">2️⃣ Seleccionar Métricas</h4>
                </div>
                <div class="card-body">
                    <div class="tabs">
                        <div class="tab active" data-tab="security" id="tab-security">
                            <span style="display: flex; align-items: center; gap: 0.5rem;">
                                ${metricTypeConfig.security.icon} Seguridad
                            </span>
                        </div>
                        <div class="tab" data-tab="privacy" id="tab-privacy">
                            <span style="display: flex; align-items: center; gap: 0.5rem;">
                                ${metricTypeConfig.privacy.icon} Privacidad
                            </span>
                        </div>
                        <div class="tab" data-tab="fairness" id="tab-fairness">
                            <span style="display: flex; align-items: center; gap: 0.5rem;">
                                ${metricTypeConfig.fairness.icon} Equidad
                            </span>
                        </div>
                    </div>
                    
                    <div id="metricsContainer" style="margin-top: 1rem; max-height: 400px; overflow-y: auto;">
                        <div class="spinner"></div>
                    </div>
                </div>
            </div>

            <!-- Column 3: Configuration Summary (Button only, progress moved down) -->
            <div class="card">
                <div class="card-header">
                    <h4 class="card-title">3️⃣ Configuración</h4>
                </div>
                <div class="card-body">
                    <div id="selectedMetrics" style="margin-bottom: 1rem;">
                        <div style="font-weight: 600; margin-bottom: 0.5rem;">Métricas Seleccionadas:</div>
                        <div id="selectedMetricsList" style="color: var(--text-secondary); font-size: 0.875rem;">
                            ${getSession().selectedMetrics.length > 0 ? getSession().selectedMetrics.join(', ') : 'Ninguna métrica seleccionada'}
                        </div>
                    </div>

                    <button class="btn btn-primary btn-lg" style="width: 100%; font-weight: 600;" id="startEvalBtn">
                        Iniciar Auditoría
                    </button>
                    <!-- Rocket icon removed from button as requested -->
                </div>
            </div>
        </div>

        <!-- Full Width Progress Section (Initially Hidden) -->
        <div id="evaluationProgress" class="hidden" style="margin-top: 2rem;">
            <div class="card">
                <div class="card-header" style="background: #f8fafc; border-bottom: 1px solid var(--border-color); padding: 1.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 1.5rem;">
                            <h4 class="card-title" style="margin: 0;">Estado de la Auditoría</h4>
                            <span id="evalStatusPercentage" style="font-size: 1.25rem; font-weight: 700; color: var(--primary-color);">0%</span>
                        </div>
                        <span id="evalStatus" style="font-size: 0.95rem; color: var(--text-secondary); background: white; padding: 0.25rem 0.75rem; border-radius: 1rem; border: 1px solid var(--border-color);">
                            Preparando...
                        </span>
                        <button id="cancelEvalBtn" class="btn btn-outline-danger btn-sm" style="display: none;">
                            Cancelar Evaluación
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <!-- Global Progress Bar -->
                    <div class="progress" style="height: 12px; background: #e5e7eb; border-radius: 6px; overflow: hidden; margin-bottom: 2rem;">
                        <div class="progress-bar" id="evalProgressBar" style="width: 0%; height: 100%; background-color: #2563eb !important; transition: width 0.3s ease;"></div>
                    </div>

                    <!-- Individual Metrics Grid -->
                    <div id="evalMetricsList" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
                        <!-- Metric cards will appear here -->
                    </div>

                    <!-- Log Monitor Section -->
                    <div id="logMonitorSection" style="margin-top: 2rem; border-top: 1px solid var(--border-color); padding-top: 1.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                            <h4 style="margin: 0; display: flex; align-items: center; gap: 0.5rem;">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>
                                Monitor de Consola (Python)
                            </h4>
                            <span style="font-size: 0.75rem; color: var(--text-secondary); background: #f3f4f6; padding: 0.2rem 0.6rem; border-radius: 4px;">Live Stream</span>
                        </div>
                        <div id="logTerminal" style="background: #1e1e1e; color: #d4d4d4; font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 0.8rem; padding: 1rem; border-radius: 8px; height: 300px; overflow-y: auto; line-height: 1.4; box-shadow: inset 0 2px 10px rgba(0,0,0,0.3); border: 1px solid #333;">
                            <div style="color: #6a9955;">[SISTEMA] Esperando inicio de logs...</div>
                        </div>
                        <div style="display: flex; justify-content: flex-end; margin-top: 0.5rem;">
                            <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.75rem; color: var(--text-secondary); cursor: pointer;">
                                <input type="checkbox" id="autoScrollLogs" checked style="cursor: pointer;"> Autoscroll
                            </label>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Attach Event Listeners
    setupEventListeners();

    // Load Data
    loadEvaluationData();

    // Check if we should resume a running evaluation
    checkAndResumeEvaluation();
};

function setupEventListeners() {
    // Tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.getAttribute('data-tab');
            switchMetricTab(tabName);
        });
    });

    // Start Button
    const startBtn = document.getElementById('startEvalBtn');
    if (startBtn) {
        startBtn.addEventListener('click', () => {
            console.log('[Evaluation] Start button clicked via EventListener');
            startEvaluation();
        });
    }

    // Selects
    const modelSelect = document.getElementById('evalModel');
    const datasetSelect = document.getElementById('evalDataset');

    if (modelSelect) modelSelect.addEventListener('change', updateEvaluationButton);
    if (datasetSelect) datasetSelect.addEventListener('change', updateEvaluationButton);

    // Cancel Button Listener
    const cancelBtn = document.getElementById('cancelEvalBtn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', async () => {
            const session = getSession();
            if (!session.currentEvalId) return;

            if (confirm('¿Estás seguro de que deseas cancelar la evaluación actual?')) {
                try {
                    cancelBtn.disabled = true;
                    cancelBtn.innerText = 'Chanceling...';
                    await window.api.cancelEvaluation(session.currentEvalId);
                    console.log('[Evaluation] Cancellation requested');
                } catch (error) {
                    console.error('[Evaluation] Error cancelling:', error);
                    alert('Error al cancelar la evaluación: ' + error.message);
                    cancelBtn.disabled = false;
                    cancelBtn.innerText = 'Cancelar Evaluación';
                }
            }
        });
    }
}

function switchMetricTab(tab) {
    currentMetricTab = tab;

    // Update tab UI
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`[data-tab="${tab}"]`).classList.add('active');

    // Show metrics
    showMetricsForTab(tab);
}

async function loadEvaluationData() {
    try {
        console.log('[Evaluation] Loading data...');
        const models = await window.api.getModels();
        const modelSelect = document.getElementById('evalModel');

        if (modelSelect) {
            modelSelect.innerHTML = (models.length === 0)
                ? '<option value="">No hay modelos cargados</option>'
                : '<option value="">Selecciona un modelo...</option>' + models.map(m => `<option value="${m.id}">${m.name} (${m.framework})</option>`).join('');
        }

        const datasets = await window.api.getDatasets();
        const datasetSelect = document.getElementById('evalDataset');

        if (datasetSelect) {
            datasetSelect.innerHTML = (datasets.length === 0)
                ? '<option value="">No hay datasets cargados</option>'
                : '<option value="">Selecciona un dataset...</option>' + datasets.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
        }

        const plugins = await window.api.getPlugins();
        availablePlugins = {
            security: plugins.filter(p => p.type === 'security'),
            privacy: plugins.filter(p => p.type === 'privacy'),
            fairness: plugins.filter(p => p.type === 'fairness')
        };
        console.log('[Evaluation] Plugins loaded:', availablePlugins);

        showMetricsForTab(currentMetricTab);

    } catch (error) {
        console.error('[Evaluation] Error loading data:', error);
    }
}

function showMetricsForTab(tab) {
    const container = document.getElementById('metricsContainer');
    const metrics = availablePlugins[tab] || [];

    if (metrics.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 1rem; color: var(--text-secondary);">
                No hay plugins de ${tab} disponibles
            </div>
        `;
        return;
    }

    container.innerHTML = metrics.map(metric => {
        const config = metricTypeConfig[metric.type] || metricTypeConfig.security;
        const session = getSession();
        const isChecked = session.selectedMetrics.includes(metric.name) ? 'checked' : '';

        // We restore colors to the container border/bg as requested
        return `
        <div style="margin-bottom: 0.75rem;">
            <label class="metric-option" style="display: flex; align-items: start; cursor: pointer; padding: 0.75rem; border-radius: var(--radius-md); background: ${config.colors.bg}; border: 1px solid ${config.colors.border}; transition: all 0.2s;">
                <input type="checkbox" class="metric-checkbox" value="${metric.name}" data-name="${metric.name}" data-type="${metric.type}"
                    ${isChecked}
                    style="margin-right: 0.75rem; margin-top: 0.25rem; cursor: pointer;">
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: ${config.colors.text}; display: flex; align-items: center; gap: 0.5rem;">
                        ${config.icon}
                        ${metric.name}
                    </div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem;">${metric.description}</div>
                </div>
            </label>
        </div>
    `;
    }).join('');

    // Re-attach event listeners
    container.querySelectorAll('.metric-checkbox').forEach(cb => {
        cb.addEventListener('change', (e) => {
            toggleMetric(e.target);
        });
    });
}

function toggleMetric(checkbox) {
    const name = checkbox.getAttribute('data-name');
    const type = checkbox.getAttribute('data-type');
    const session = getSession();

    console.log(`[Evaluation] Toggling metric: ${name} (${type})`);

    if (checkbox.checked) {
        if (!session.selectedMetrics.includes(name)) {
            session.selectedMetrics.push(name);
            session.selectedMetricTypes[name] = type;
        }
    } else {
        session.selectedMetrics = session.selectedMetrics.filter(m => m !== name);
        delete session.selectedMetricTypes[name];
    }

    updateSelectedMetricsUI();
    updateEvaluationButton(); // Ensure button state is updated
}

function updateSelectedMetricsUI() {
    const container = document.getElementById('selectedMetricsList');
    if (!container) return;

    const session = getSession();

    if (session.selectedMetrics.length === 0) {
        container.innerHTML = '<span style="color: var(--text-secondary);">Ninguna métrica seleccionada</span>';
    } else {
        container.innerHTML = session.selectedMetrics.map(m => {
            const type = session.selectedMetricTypes[m] || 'security';
            const config = metricTypeConfig[type];
            // Restore colors to badges
            return `<span class="badge" style="background: ${config.colors.bg}; color: ${config.colors.text}; border: 1px solid ${config.colors.border}; margin-right: 0.5rem; margin-bottom: 0.25rem; display: inline-flex; align-items: center; gap: 0.25rem;">${config.icon} ${m}</span>`;
        }).join('');
    }
}

function updateEvaluationButton() {
    const model = document.getElementById('evalModel').value;
    const dataset = document.getElementById('evalDataset').value;
    const btn = document.getElementById('startEvalBtn');
    const session = getSession();

    btn.disabled = false;

    // Visual feedback only
    const isValid = (model && dataset && session.selectedMetrics.length > 0);
    btn.style.opacity = isValid ? '1' : '0.6';
    btn.style.cursor = isValid ? 'pointer' : 'not-allowed';
}

async function startEvaluation() {
    console.log('[Evaluation] Starting evaluation...');
    const session = getSession();
    const modelId = document.getElementById('evalModel').value;
    const datasetId = document.getElementById('evalDataset').value;
    const btn = document.getElementById('startEvalBtn');
    const progressDiv = document.getElementById('evaluationProgress');

    if (!modelId || !datasetId || session.selectedMetrics.length === 0) {
        alert('Por favor completa todos los campos (modelo, dataset y al menos una métrica).');
        return;
    }

    btn.disabled = true;
    btn.style.opacity = '0.7';
    btn.innerText = 'Iniciando...';

    // Show full width progress section
    progressDiv.classList.remove('hidden');
    progressDiv.scrollIntoView({ behavior: 'smooth' });

    // Initialize metric status grid IMMEDIATELY
    initializeMetricStatusDisplay();

    document.getElementById('evalStatus').textContent = 'Iniciando evaluación...';
    document.getElementById('evalProgressBar').style.width = '5%';

    try {
        // Create evaluation
        const evaluation = await window.api.createEvaluation({
            model_id: modelId,
            dataset_id: datasetId,
            metrics: session.selectedMetrics
        });

        session.currentEvalId = evaluation.id;
        console.log('[Evaluation] Evaluation created:', evaluation);

        // Start evaluation
        await window.api.startEvaluation(evaluation.id);
        console.log('[Evaluation] Evaluation started');

        btn.innerText = 'Evaluando...';
        document.getElementById('cancelEvalBtn').style.display = 'block';

        // Poll for results and logs
        const results = await pollEvaluationStatus(evaluation.id);

        document.getElementById('evalProgressBar').style.width = '100%';
        document.getElementById('evalStatusPercentage').innerText = '100%';
        document.getElementById('evalStatus').textContent = '¡Evaluación completada!';

        btn.innerText = '¡Completado!';
        btn.classList.add('btn-success');

        setTimeout(() => {
            alert('Evaluación completada exitosamente.');
            window.app.switchView('results');
        }, 1500);

    } catch (error) {
        console.error('[Evaluation] Error:', error);
        alert('Error en la evaluación: ' + error.message);
        btn.disabled = false;
        btn.style.opacity = '1';
        btn.innerText = 'Iniciar Auditoría';
    }
}

function initializeMetricStatusDisplay() {
    const container = document.getElementById('evalMetricsList');
    if (!container) return;

    const session = getSession();

    container.innerHTML = session.selectedMetrics.map(name => {
        const type = session.selectedMetricTypes[name] || 'security';
        const config = metricTypeConfig[type];

        // Large Card Style for each metric
        return `
            <div id="metric-progress-${name}" style="background: white; border: 1px solid var(--border-color); border-radius: 8px; padding: 1.25rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); position: relative; overflow: hidden;">
                <!-- Type colored stripe on left -->
                <div style="position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: ${config.colors.bar};"></div>
                
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-left: 0.5rem;">
                    <div style="font-weight: 600; font-size: 1rem; display: flex; align-items: center; gap: 0.75rem; color: var(--text-primary);">
                        <span style="display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: 6px; background: ${config.colors.bg}; color: ${config.colors.text}; border: 1px solid ${config.colors.border};">
                            ${config.icon}
                        </span>
                        ${name}
                    </div>
                </div>
                
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.5rem; color: var(--text-secondary); padding-left: 0.5rem;">
                    <span class="metric-status-text">Pendiente</span>
                    <span class="metric-progress-text">0%</span>
                </div>

                <div class="progress" style="height: 10px; background: #f3f4f6; border-radius: 5px; overflow: hidden; margin-left: 0.5rem;">
                    <div class="progress-bar metric-bar" style="width: 0%; background-color: ${config.colors.bar}; transition: width 0.3s ease;"></div>
                </div>
            </div>
        `;
    }).join('');
}

async function checkAndResumeEvaluation() {
    const session = getSession();

    // If we have a currentEvalId, ensure the UI reflects the running state
    if (session.currentEvalId) {
        console.log('[Evaluation] Resuming/Syncing view for evaluation:', session.currentEvalId);

        const progressDiv = document.getElementById('evaluationProgress');
        const startBtn = document.getElementById('startEvalBtn');

        if (progressDiv) progressDiv.classList.remove('hidden');
        if (startBtn) {
            startBtn.disabled = true;
            startBtn.innerText = 'Auditoría en curso...';
        }

        // Repopulate Logs immediately from session
        const terminal = document.getElementById('logTerminal');
        if (terminal && session.capturedLogs.length > 0) {
            terminal.innerHTML = ''; // Clear "waiting" message
            session.capturedLogs.forEach(logHtml => {
                const div = document.createElement('div');
                div.style.marginBottom = '2px';
                div.innerHTML = logHtml;
                terminal.appendChild(div);
            });
            terminal.scrollTop = terminal.scrollHeight;
        }

        // Ensure metrics are displayed
        const listContainer = document.getElementById('evalMetricsList');
        if (listContainer && listContainer.children.length === 0) {
            try {
                const status = await window.api.getEvaluationStatus(session.currentEvalId);
                session.selectedMetrics = status.metrics || [];
                initializeMetricStatusDisplay();

                // If it was already completed/errored, update UI final state
                if (status.status === 'completed' || status.status === 'error' || status.status === 'cancelled') {
                    session.isPolling = false;
                    session.currentEvalId = null;
                }
            } catch (e) {
                console.error('[Evaluation] Error polling status:', e);
                // Don't alert here to avoid spamming the user, just log
            }
        }

        document.getElementById('cancelEvalBtn').style.display = 'block';

        // Start polling ONLY if not already polling
        if (!session.isPolling) {
            pollEvaluationStatus(session.currentEvalId);
        } else {
            console.log('[Evaluation] Polling is already active in background.');
        }
    }
}

async function pollEvaluationStatus(evalId, maxAttempts = 600) {
    const session = getSession();
    if (session.isPolling) return;
    session.isPolling = true;
    session.currentEvalId = evalId;

    for (let i = 0; i < maxAttempts; i++) {
        // If the view was destroyed but polling continues, we just keep updating the session
        // If the view exists, we update the DOM

        await new Promise(resolve => setTimeout(resolve, 1000));

        try {
            // Fetch status and logs in parallel
            const [status, logData] = await Promise.all([
                window.api.getEvaluationStatus(evalId),
                window.api.getEvaluationLogs(evalId, session.logIndex)
            ]);

            // Update Logs
            if (logData && logData.logs && logData.logs.length > 0) {
                const terminal = document.getElementById('logTerminal');

                logData.logs.forEach(log => {
                    let logHtml = '';
                    // Basic syntax highlighting for logs
                    let color = 'inherit';
                    if (log.includes('ERROR') || log.includes('Exception')) {
                        color = '#f14c4c';
                    } else if (log.includes('WARNING')) {
                        color = '#cca700';
                    } else if (log.includes('successfully') || log.includes('Completado')) {
                        color = '#89d185';
                    }

                    if (log.startsWith('[')) {
                        const endBracket = log.indexOf(']');
                        const timestamp = log.substring(0, endBracket + 1);
                        const message = log.substring(endBracket + 1);
                        logHtml = `<span style="color: #808080;">${timestamp}</span><span style="color: ${color};">${message}</span>`;
                    } else {
                        logHtml = `<span style="color: ${color};">${log}</span>`;
                    }

                    // Store in session
                    session.capturedLogs.push(logHtml);

                    // Update DOM if available
                    if (terminal) {
                        const div = document.createElement('div');
                        div.style.marginBottom = '2px';
                        div.innerHTML = logHtml;
                        terminal.appendChild(div);
                    }
                });

                session.logIndex = logData.next_index;

                // Autoscroll
                if (terminal) {
                    const autoScroll = document.getElementById('autoScrollLogs');
                    if (autoScroll && autoScroll.checked) {
                        terminal.scrollTop = terminal.scrollHeight;
                    }
                }
            }

            // Update individual metric progress
            if (status.metric_statuses) {
                Object.entries(status.metric_statuses).map(([name, stateData]) => {
                    const el = document.getElementById(`metric-progress-${name}`);
                    if (!el) return;

                    const statusText = el.querySelector('.metric-status-text');
                    const progressText = el.querySelector('.metric-progress-text');
                    const bar = el.querySelector('.metric-bar');

                    let stateString = typeof stateData === 'string' ? stateData : stateData.status;
                    let progress = typeof stateData === 'object' ? (stateData.progress || 0) : 0;

                    progressText.innerText = `${progress}%`;
                    bar.style.width = `${progress}%`;

                    if (stateString === 'running') {
                        statusText.innerText = 'Ejecutando análisis...';
                        statusText.style.color = 'var(--primary-color)';
                        bar.classList.add('progress-bar-striped'); // Assuming we have or can add this CSS
                        bar.classList.add('progress-bar-animated');
                    } else if (stateString === 'completed') {
                        statusText.innerText = '✅ Completado';
                        statusText.style.color = '#059669';
                        bar.style.backgroundColor = '#059669';
                    } else if (stateString === 'error') {
                        statusText.innerText = '❌ Error';
                        statusText.style.color = '#ef4444';
                        bar.style.backgroundColor = '#ef4444';
                    }
                });
            }

            // Update main status
            if (status.status === 'completed') {
                session.isPolling = false;
                session.currentEvalId = null;
                return await window.api.getEvaluationResults(evalId);
            } else if (status.status === 'error' || status.status === 'cancelled') {
                session.isPolling = false;
                if (status.status === 'cancelled') {
                    document.getElementById('evalStatus').textContent = '⚠️ Evaluación cancelada';
                    document.getElementById('evalProgressBar').style.backgroundColor = '#f59e0b';
                }
                throw new Error(status.error || `Evaluation ${status.status}`);
            }

            // Update main progress bar
            if (status.progress !== undefined && status.progress !== null) {
                const nb = document.getElementById('evalProgressBar');
                const st = document.getElementById('evalStatus');
                const pc = document.getElementById('evalStatusPercentage');
                const cb = document.getElementById('cancelEvalBtn');

                if (nb) nb.style.width = `${status.progress}%`;
                if (pc) pc.innerText = `${status.progress}%`;

                if (st && status.status === 'running') {
                    st.textContent = `Analizando vulnerabilidades y métricas...`;
                }

                // Show cancel button if running
                if (cb && status.status === 'running') {
                    cb.style.display = 'block';
                }
            }

        } catch (e) {
            console.error('Polling error:', e);
        }
    }

    throw new Error('Evaluation timeout');
}

// Global hook for results page to resume
window.resumeEvaluation = function (evalId) {
    if (!window.evaluationSession) {
        window.evaluationSession = {
            selectedMetrics: [],
            selectedMetricTypes: {},
            currentEvalId: evalId,
            isPolling: false,
            capturedLogs: [],
            logIndex: 0
        };
    } else {
        window.evaluationSession.currentEvalId = evalId;
    }
    window.app.switchView('evaluation');
};
