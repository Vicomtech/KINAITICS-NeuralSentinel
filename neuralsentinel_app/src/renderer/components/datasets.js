// Datasets Management View
window.renderDatasets = function (container) {
    container.innerHTML = `
        <div class="card mb-2">
            <div class="card-header">
                <h3 class="card-title">Dataset Management</h3>
                <button class="btn btn-primary" onclick="showUploadDatasetDialog()">
                    <span>📤</span>
                    Upload Dataset
                </button>
            </div>
        </div>

        <div id="datasetsTable"></div>

        <!-- Upload Modal -->
        <div id="uploadDatasetModal" class="hidden" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 1000; display: flex; align-items: center; justify-content: center;">
            <div class="card" style="width: 600px; max-width: 90%;">
                <div class="card-header">
                    <h3 class="card-title">Upload Dataset</h3>
                    <button onclick="closeUploadDatasetDialog()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer;">×</button>
                </div>
                <div class="card-body">
                    <div class="form-group">
                        <label class="form-label">Dataset Name</label>
                        <input type="text" class="form-input" id="datasetName" placeholder="My validation dataset">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Data File (Features/X)</label>
                        <input type="file" class="form-input" id="datasetFile" accept=".npy,.npz">
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">
                            Primary input data file (examples: images, features)
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Labels File (Labels/y)</label>
                        <input type="file" class="form-input" id="datasetLabels" accept=".npy,.npz">
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">
                            File with corresponding labels (must have the same length as the data)
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Description (optional)</label>
                        <textarea class="form-textarea" id="datasetDescription" placeholder="Dataset description..."></textarea>
                    </div>
                    <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                        <button class="btn btn-secondary" onclick="closeUploadDatasetDialog()">Cancel</button>
                        <button class="btn btn-primary" onclick="uploadDataset()">Upload</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Dataset Preview Modal -->
        <div id="datasetViewModal" class="hidden" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 1000; display: flex; align-items: center; justify-content: center;">
            <div class="card" style="width: 900px; max-width: 95%; height: 85vh; display: flex; flex-direction: column;">
                <div class="card-header">
                    <h3 class="card-title">Dataset Preview</h3>
                    <button onclick="closeDatasetViewDialog()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer;">×</button>
                </div>
                <div class="card-body" style="flex: 1; overflow-y: auto; padding: 0; display: flex; flex-direction: column;">
                    <div id="datasetMetadata" style="padding: 1rem; border-bottom: 1px solid var(--border-color); background: #f8f9fa;"></div>
                    <div id="datasetPreviewContent" style="padding: 1.5rem; flex: 1; overflow-y: auto;">
                        <div class="spinner"></div>
                    </div>
                </div>
            </div>
        </div>
    `;

    loadDatasets();
};

async function loadDatasets() {
    const container = document.getElementById('datasetsTable');
    container.innerHTML = '<div class="spinner" style="margin: 2rem auto;"></div>';

    try {
        const datasets = await window.api.getDatasets();

        if (datasets.length === 0) {
            container.innerHTML = `
                <div class="card">
                    <div class="empty-state">
                        <div class="empty-state-icon">📁</div>
                        <div class="empty-state-title">No datasets loaded</div>
                        <div class="empty-state-text">
                            Upload your first NumPy dataset (.npy, .npz) to get started
                        </div>
                        <button class="btn btn-primary" onclick="showUploadDatasetDialog()">
                            Upload Dataset
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
                            <th>Format</th>
                            <th>Size</th>
                            <th>Labels</th>
                            <th>Upload Date</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${datasets.map(dataset => `
                            <tr>
                                <td>
                                    <div style="font-weight: 600;">${dataset.name}</div>
                                    ${dataset.description ? `<div style="font-size: 0.875rem; color: var(--text-secondary);">${dataset.description}</div>` : ''}
                                </td>
                                <td><span class="badge badge-info">${dataset.format || '.npy'}</span></td>
                                <td>${(dataset.size / 1024 / 1024).toFixed(2)} MB</td>
                                <td>
                                    ${dataset.has_labels ? '<span class="badge badge-success">✓ Included</span>' : '<span class="badge badge-warning">No labels</span>'}
                                </td>
                                <td>${new Date(dataset.upload_date).toLocaleDateString()}</td>
                                <td>
                                    <button class="btn btn-secondary btn-sm" onclick="viewDataset('${dataset.id}')">View</button>
                                    <button class="btn btn-danger btn-sm" onclick="deleteDataset('${dataset.id}')">Delete</button>
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
                <div>Error loading datasets: ${error.message}</div>
            </div>
        `;
    }
}

function showUploadDatasetDialog() {
    document.getElementById('uploadDatasetModal').classList.remove('hidden');
}

function closeUploadDatasetDialog() {
    document.getElementById('uploadDatasetModal').classList.add('hidden');
    document.getElementById('datasetName').value = '';
    document.getElementById('datasetDescription').value = '';
    document.getElementById('datasetFile').value = '';
    document.getElementById('datasetLabels').value = '';
}

async function uploadDataset() {
    const name = document.getElementById('datasetName').value.trim();
    const dataFile = document.getElementById('datasetFile').files[0];
    const labelsFile = document.getElementById('datasetLabels').files[0];
    const description = document.getElementById('datasetDescription').value.trim();

    if (!name || !dataFile) {
        alert('Please enter a name and select a data file');
        return;
    }

    const formData = new FormData();
    formData.append('name', name);
    formData.append('data_file', dataFile);

    if (labelsFile) {
        formData.append('labels_file', labelsFile);
    }

    if (description) {
        formData.append('description', description);
    }

    try {
        await window.api.uploadDataset(formData);
        closeUploadDatasetDialog();
        loadDatasets();

        if (labelsFile) {
            alert('Dataset uploaded successfully with data and labels');
        } else {
            alert('Dataset uploaded successfully (without labels)');
        }
    } catch (error) {
        alert('Error uploading dataset: ' + error.message);
    }
}

async function deleteDataset(id) {
    if (!confirm('Are you sure you want to delete this dataset?')) return;

    try {
        await window.api.deleteDataset(id);
        loadDatasets();
    } catch (error) {
        alert('Error deleting dataset: ' + error.message);
    }
}

window.closeDatasetViewDialog = function () {
    document.getElementById('datasetViewModal').classList.add('hidden');
};

window.viewDataset = async function (id) {
    const modal = document.getElementById('datasetViewModal');
    const metadataEl = document.getElementById('datasetMetadata');
    const contentEl = document.getElementById('datasetPreviewContent');

    modal.classList.remove('hidden');

    metadataEl.innerHTML = 'Loading metadata...';
    contentEl.innerHTML = '<div class="spinner" style="margin: 2rem auto;"></div>';

    try {
        // Get Preview Data
        const preview = await window.api.getDatasetPreview(id);

        // Render Metadata
        metadataEl.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; font-size: 0.9rem;">
                <div><strong>Forma (Shape):</strong> ${preview.shape}</div>
                <div><strong>Data Type (DType):</strong> ${preview.dtype}</div>
                <div><strong>View Type:</strong> <span class="badge badge-info">${preview.type === 'images' ? 'Images' : 'Table'}</span></div>
            </div>
        `;

        // Render Content
        if (preview.type === 'images') {
            contentEl.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 1rem;">
                    ${preview.data.map(imgBase64 => `
                        <div style="border: 1px solid #ddd; padding: 0.5rem; border-radius: 4px; text-align: center; background: white;">
                            <img src="data:image/png;base64,${imgBase64}" style="max-width: 100%; height: auto; display: block; margin: 0 auto;">
                        </div>
                    `).join('')}
                </div>
                <p style="text-align: center; color: var(--text-secondary); margin-top: 1rem;">Showing first ${preview.data.length} items</p>
            `;
        } else {
            // Tabular View
            const rows = preview.data;
            if (!rows || rows.length === 0) {
                contentEl.innerHTML = '<p>Empty dataset</p>';
                return;
            }

            // Generate table headers (Index, Col 0, Col 1...)
            // Limit columns if too many
            const colCount = Array.isArray(rows[0]) ? rows[0].length : 1;
            const displayCols = Math.min(colCount, 20); // Max 20 columns

            let tableHtml = '<table class="table table-striped" style="font-size: 0.85rem;"><thead><tr><th>#</th>';
            for (let i = 0; i < displayCols; i++) {
                tableHtml += `<th>Col ${i}</th>`;
            }
            if (colCount > displayCols) tableHtml += '<th>...</th>';
            tableHtml += '</tr></thead><tbody>';

            rows.forEach((row, idx) => {
                tableHtml += `<tr><td>${idx}</td>`;
                const rowData = Array.isArray(row) ? row : [row];

                for (let i = 0; i < displayCols; i++) {
                    let val = rowData[i];
                    if (typeof val === 'number') val = val.toFixed(4);
                    tableHtml += `<td>${val}</td>`;
                }
                if (colCount > displayCols) tableHtml += '<td>...</td>';
                tableHtml += '</tr>';
            });

            tableHtml += '</tbody></table>';
            contentEl.innerHTML = `
                <div style="overflow-x: auto;">${tableHtml}</div>
                <p style="text-align: center; color: var(--text-secondary); margin-top: 1rem;">Showing first ${rows.length} items</p>
            `;
        }

    } catch (error) {
        contentEl.innerHTML = `
            <div class="alert alert-error">
                <strong>Error:</strong> Could not load preview: ${error.message}
            </div>
        `;
    }
};
