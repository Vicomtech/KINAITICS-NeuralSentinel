// Dashboard View
window.renderDashboard = function (container) {
    container.innerHTML = `
        <div class="grid grid-cols-4 mb-3">
            <!-- Metric Cards -->
            <div class="metric-card">
                <div class="metric-info">
                    <div class="metric-label">Loaded Models</div>
                    <div class="metric-value" id="totalModels">0</div>
                    <div class="metric-trend positive">
                        ↑ Ready to evaluate
                    </div>
                </div>
                <div class="metric-icon yellow">🧠</div>
            </div>

            <div class="metric-card">
                <div class="metric-info">
                    <div class="metric-label">Datasets</div>
                    <div class="metric-value" id="totalDatasets">0</div>
                    <div class="metric-trend positive">
                        ↑ Available
                    </div>
                </div>
                <div class="metric-icon cyan">📁</div>
            </div>

            <div class="metric-card">
                <div class="metric-info">
                    <div class="metric-label">Evaluations</div>
                    <div class="metric-value" id="totalEvaluations">0</div>
                    <div class="metric-trend">
                        Completed
                    </div>
                </div>
                <div class="metric-icon green">📊</div>
            </div>

            <div class="metric-card">
                <div class="metric-info">
                    <div class="metric-label">Plugins</div>
                    <div class="metric-value" id="totalPlugins">0</div>
                    <div class="metric-trend">
                        Active
                    </div>
                </div>
                <div class="metric-icon purple">🔌</div>
            </div>
        </div>

        <!-- Recent Activity -->
        <div class="grid grid-cols-2">
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Recent Models</h3>
                    <button class="btn btn-outline btn-sm" onclick="app.switchView('models')">
                        View all
                    </button>
                </div>
                <div class="card-body" id="recentModels">
                    <div class="empty-state">
                        <div class="empty-state-icon">🧠</div>
                        <div class="empty-state-title">No models loaded</div>
                        <div class="empty-state-text">
                            Upload your first TensorFlow or PyTorch model
                        </div>
                        <button class="btn btn-primary" onclick="app.switchView('models')">
                            Upload Model
                        </button>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Evaluations Recientes</h3>
                    <button class="btn btn-outline btn-sm" onclick="window.app.switchView('results')">
                        View all
                    </button>
                </div>
                <div class="card-body" id="recentEvaluations">
                    <div class="empty-state">
                        <div class="empty-state-icon">📈</div>
                        <div class="empty-state-title">No evaluations yet</div>
                        <div class="empty-state-text">
                            Create your first model audit
                        </div>
                        <button class="btn btn-primary" onclick="app.switchView('evaluation')">
                            New Evaluation
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Quick Actions -->
        <div class="card mt-2">
            <div class="card-header">
                <h3 class="card-title">Quick Actions</h3>
            </div>
            <div class="card-body">
                <div class="grid grid-cols-3">
                    <button class="btn btn-outline btn-lg" onclick="app.switchView('models')">
                        <span>📤</span>
                        Upload Model
                    </button>
                    <button class="btn btn-outline btn-lg" onclick="app.switchView('datasets')">
                        <span>📥</span>
                        Upload Dataset
                    </button>
                    <button class="btn btn-primary btn-lg" onclick="app.switchView('evaluation')">
                        <span>🚀</span>
                        New Evaluation
                    </button>
                </div>
            </div>
        </div>
    `;

    // Load dashboard data
    loadDashboardData();
};

async function loadDashboardData() {
    try {
        // Load metrics
        const [models, datasets, evaluations, plugins] = await Promise.all([
            window.api.getModels(),
            window.api.getDatasets(),
            window.api.getEvaluationHistory(),
            window.api.getPlugins()
        ]);

        // Update metric cards
        document.getElementById('totalModels').textContent = models.length;
        document.getElementById('totalDatasets').textContent = datasets.length;
        document.getElementById('totalEvaluations').textContent = evaluations.length;
        document.getElementById('totalPlugins').textContent = plugins.length;

        // Show recent models
        if (models.length > 0) {
            const recentModels = models.slice(0, 3);
            document.getElementById('recentModels').innerHTML = `
                <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                    ${recentModels.map(model => `
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; background: var(--bg-light); border-radius: var(--radius-md);">
                            <div>
                                <div style="font-weight: 600;">${model.name}</div>
                                <div style="font-size: 0.875rem; color: var(--text-secondary);">
                                    ${model.framework} • ${(model.size / 1024 / 1024).toFixed(2)} MB
                                </div>
                            </div>
                            <span class="badge badge-${model.framework === 'tensorflow' ? 'info' : 'purple'}">
                                ${model.framework}
                            </span>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        // Show recent evaluations
        if (evaluations.length > 0) {
            const recentEvals = evaluations.slice(0, 3);
            document.getElementById('recentEvaluations').innerHTML = `
                <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                    ${recentEvals.map(evaluationItem => `
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; background: var(--bg-light); border-radius: var(--radius-md);">
                            <div>
                                <div style="font-weight: 600;">${evaluationItem.model_name || 'Evaluation'}</div>
                                <div style="font-size: 0.875rem; color: var(--text-secondary);">
                                    ${new Date(evaluationItem.start_time).toLocaleDateString()} • ${evaluationItem.metrics.length} metrics
                                </div>
                            </div>
                            <span class="badge badge-${evaluationItem.status === 'completed' ? 'success' : 'warning'}">
                                ${evaluationItem.status}
                            </span>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}
