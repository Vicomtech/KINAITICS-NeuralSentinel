// API Communication Layer
class API {
    constructor() {
        this.baseURL = 'http://localhost:5000/api';
        this.init();
    }

    async init() {
        try {
            const backendUrl = await window.electronAPI.getBackendUrl();
            this.baseURL = `${backendUrl}/api`;
        } catch (error) {
            console.warn('Using default backend URL');
        }
    }

    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || errorData.error || 'Request failed');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Models
    async getModels() {
        return this.request('/models');
    }

    async getModel(id) {
        return this.request(`/models/${id}`);
    }

    async uploadModel(formData) {
        const response = await fetch(`${this.baseURL}/models/upload`, {
            method: 'POST',
            body: formData,
        });
        return response.json();
    }

    async deleteModel(id) {
        return this.request(`/models/${id}`, { method: 'DELETE' });
    }

    async getModelArchitecture(id) {
        return this.request(`/models/${id}/architecture`);
    }

    // Datasets
    async getDatasets() {
        return this.request('/datasets');
    }

    async getDataset(id) {
        return this.request(`/datasets/${id}`);
    }

    async getDatasetPreview(id) {
        return this.request(`/datasets/${id}/preview`);
    }

    async uploadDataset(formData) {
        const response = await fetch(`${this.baseURL}/datasets/upload`, {
            method: 'POST',
            body: formData,
        });
        return response.json();
    }

    async deleteDataset(id) {
        return this.request(`/datasets/${id}`, { method: 'DELETE' });
    }

    // Metrics
    async getMetrics() {
        return this.request('/metrics');
    }

    async getMetricsByType(type) {
        return this.request(`/metrics/${type}`);
    }

    async getMetricInfo(name) {
        return this.request(`/metrics/${name}/info`);
    }

    // Evaluations
    async createEvaluation(data) {
        return this.request('/evaluations', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async startEvaluation(id) {
        return this.request(`/evaluations/${id}/start`, {
            method: 'POST',
        });
    }

    async cancelEvaluation(id) {
        return this.request(`/evaluations/${id}/cancel`, {
            method: 'POST',
        });
    }

    async getEvaluationStatus(id) {
        return this.request(`/evaluations/${id}/status`);
    }

    async getEvaluationResults(id) {
        return this.request(`/evaluations/${id}/results`);
    }

    async deleteEvaluation(id) {
        return this.request(`/evaluations/${id}`, { method: 'DELETE' });
    }

    async getEvaluationLogs(id, since = 0) {
        return this.request(`/evaluations/${id}/logs?since=${since}`);
    }

    async getEvaluationHistory() {
        return this.request('/evaluations/history');
    }

    // Plugins
    async getPlugins() {
        return this.request('/plugins');
    }

    async reloadPlugins() {
        return this.request('/plugins/reload', { method: 'POST' });
    }

    async getPlugin(name) {
        return this.request(`/plugins/${name}`);
    }

    async deletePlugin(name) {
        return this.request(`/plugins/${name}`, { method: 'DELETE' });
    }

    async uploadPlugin(formData) {
        const response = await fetch(`${this.baseURL}/plugins/upload`, {
            method: 'POST',
            body: formData,
        });
        return response.json();
    }
}

// Create global API instance
window.api = new API();
