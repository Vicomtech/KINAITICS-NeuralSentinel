// Models Management View
window.renderModels = function (container) {
    container.innerHTML = `
        <div class="card mb-2">
            <div class="card-header">
                <h3 class="card-title">Model Management</h3>
                <button class="btn btn-primary" onclick="showUploadModelDialog()">
                    <span>📤</span>
                    Upload Model
                </button>
            </div>
        </div>

        <div id="modelsTable"></div>

        <!-- Upload Modal -->
        <div id="uploadModelModal" class="hidden" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 1000; display: flex; align-items: center; justify-content: center;">
            <div class="card" style="width: 500px; max-width: 90%;">
                <div class="card-header">
                    <h3 class="card-title">Upload Model</h3>
                    <button onclick="closeUploadModelDialog()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer;">×</button>
                </div>
                <div class="card-body">
                    <div class="form-group">
                        <label class="form-label">Model Name</label>
                        <input type="text" class="form-input" id="modelName" placeholder="My classification model">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Framework</label>
                        <select class="form-select" id="modelFramework">
                            <option value="tensorflow">TensorFlow</option>
                            <option value="pytorch">PyTorch</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Model File</label>
                        <input type="file" class="form-input" id="modelFile" accept=".pb,.h5,.tflite,.pt,.pth">
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">
                            Supported formats: .pb, .h5, .tflite (TensorFlow) | .pt, .pth (PyTorch)
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Description (optional)</label>
                        <textarea class="form-textarea" id="modelDescription" placeholder="Model description..."></textarea>
                    </div>
                    <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                        <button class="btn btn-secondary" onclick="closeUploadModelDialog()">Cancel</button>
                        <button class="btn btn-primary" onclick="uploadModel()">Upload</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Architecture View Modal -->
        <div id="modelViewModal" class="hidden" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 1000; display: flex; align-items: center; justify-content: center;">
            <div class="card" style="width: 800px; max-width: 90%; height: 80vh; display: flex; flex-direction: column;">
                <div class="card-header">
                    <h3 class="card-title">Model Architecture</h3>
                    <button onclick="closeModelViewDialog()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer;">×</button>
                </div>
                <div class="card-body" style="flex: 1; overflow-y: auto; padding: 0;">
                    <div id="modelArchitectureContent" style="padding: 1.5rem;">
                        <div class="spinner"></div>
                    </div>
                </div>
            </div>
        </div>
    `;

    loadModels();
};

async function loadModels() {
    const container = document.getElementById('modelsTable');
    container.innerHTML = '<div class="spinner" style="margin: 2rem auto;"></div>';

    try {
        const models = await window.api.getModels();

        if (models.length === 0) {
            container.innerHTML = `
                <div class="card">
                    <div class="empty-state">
                        <div class="empty-state-icon">🧠</div>
                        <div class="empty-state-title">No models loaded</div>
                        <div class="empty-state-text">
                            Upload your first TensorFlow or PyTorch model to get started
                        </div>
                        <button class="btn btn-primary" onclick="showUploadModelDialog()">
                            Upload Model
                        </button>
                    </div>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Framework</th>
                            <th>Formato</th>
                            <th>Size</th>
                            <th>Upload Date</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${models.map(model => `
                            <tr>
                                <td>
                                    <div style="font-weight: 600;">${model.name}</div>
                                    ${model.metadata?.description ? `<div style="font-size: 0.875rem; color: var(--text-secondary);">${model.metadata.description}</div>` : ''}
                                </td>
                                <td>
                                    <span class="badge badge-${model.framework === 'tensorflow' ? 'info' : 'purple'}">
                                        ${model.framework}
                                    </span>
                                </td>
                                <td>${model.format}</td>
                                <td>${(model.size / 1024 / 1024).toFixed(2)} MB</td>
                                <td>${new Date(model.upload_date).toLocaleDateString()}</td>
                                <td>
                                    <button class="btn btn-secondary btn-sm" onclick="viewModel('${model.id}')">View</button>
                                    <button class="btn btn-danger btn-sm" onclick="deleteModel('${model.id}')">Delete</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        container.innerHTML = `
            <div class="alert alert-danger">
                <span>⚠️</span>
                <div>Error loading models: ${error.message}</div>
            </div>
        `;
    }
}

function showUploadModelDialog() {
    document.getElementById('uploadModelModal').classList.remove('hidden');
}

function closeUploadModelDialog() {
    document.getElementById('uploadModelModal').classList.add('hidden');
    // Reset form
    document.getElementById('modelName').value = '';
    document.getElementById('modelDescription').value = '';
    document.getElementById('modelFile').value = '';
}

async function uploadModel() {
    const name = document.getElementById('modelName').value.trim();
    const framework = document.getElementById('modelFramework').value;
    const file = document.getElementById('modelFile').files[0];
    const description = document.getElementById('modelDescription').value.trim();

    if (!name || !file) {
        alert('Please complete the required fields');
        return;
    }

    const formData = new FormData();
    formData.append('name', name);
    formData.append('framework', framework);
    formData.append('file', file);
    if (description) formData.append('description', description);

    try {
        await window.api.uploadModel(formData);
        closeUploadModelDialog();
        loadModels();
    } catch (error) {
        alert('Error uploading model: ' + error.message);
    }
}

async function deleteModel(id) {
    if (!confirm('Are you sure you want to delete this model?')) return;

    try {
        await window.api.deleteModel(id);
        loadModels();
    } catch (error) {
        alert('Error deleting model: ' + error.message);
    }
}

async function viewModel(id) {
    const modal = document.getElementById('modelViewModal');
    const content = document.getElementById('modelArchitectureContent');

    modal.classList.remove('hidden');
    content.innerHTML = '<div class="spinner" style="margin: 2rem auto;"></div>';

    try {
        const architecture = await window.api.getModelArchitecture(id);

        let html = '';

        if (architecture.summary) {
            html += `
                <div style="background: #1e1e1e; color: #d4d4d4; padding: 1.5rem; border-radius: 8px; font-family: monospace; white-space: pre-wrap; font-size: 0.9rem; overflow-x: auto;">${architecture.summary}</div>
            `;
        }

        if (architecture.config) {
            html += `
                <div style="margin-top: 1.5rem;">
                    <h4 style="margin-bottom: 0.5rem;">JSON Configuration</h4>
                    <pre style="background: #f5f5f5; padding: 1rem; border-radius: 8px; overflow-x: auto; max-height: 300px;">${JSON.stringify(architecture.config, null, 2)}</pre>
                </div>
            `;
        }

        if (!architecture.summary && !architecture.config) {
            html = '<div class="alert alert-warning">Could not extract architecture information for this model.</div>';
        }

        content.innerHTML = html;

    } catch (error) {
        content.innerHTML = `
            <div class="alert alert-error">
                <strong>Error:</strong> Could not load architecture: ${error.message}
            </div>
        `;
    }
}

// Ensure global scope access
window.closeModelViewDialog = function () {
    document.getElementById('modelViewModal').classList.add('hidden');
};
