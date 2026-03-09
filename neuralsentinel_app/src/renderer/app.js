// Application Main Controller
class App {
    constructor() {
        this.currentView = 'dashboard';
        this.views = {};
        this.init();
    }

    init() {
        this.setupNavigation();
        this.loadView('dashboard');
        this.checkBackendConnection();
    }

    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');

        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const view = item.dataset.view;
                this.switchView(view);
            });
        });
    }

    switchView(viewName) {
        // Update active nav item
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.view === viewName) {
                item.classList.add('active');
            }
        });

        // Update page title
        const titles = {
            dashboard: 'Dashboard',
            models: 'Gestión de Modelos',
            datasets: 'Gestión de Datasets',
            evaluation: 'Evaluación',
            results: 'Resultados',
            plugins: 'Plugins',
            settings: 'Configuración'
        };
        document.querySelector('.page-title').textContent = titles[viewName];

        // Load view
        this.loadView(viewName);
        this.currentView = viewName;
    }

    loadView(viewName) {
        const container = document.getElementById('app-content');

        // Call view-specific render function
        switch (viewName) {
            case 'dashboard':
                if (window.renderDashboard) window.renderDashboard(container);
                break;
            case 'models':
                if (window.renderModels) window.renderModels(container);
                break;
            case 'datasets':
                if (window.renderDatasets) window.renderDatasets(container);
                break;
            case 'evaluation':
                if (window.renderEvaluation) window.renderEvaluation(container);
                else console.error('renderEvaluation not found');
                break;
            case 'results':
                console.log('Switching to Results view...');
                if (window.renderResults) {
                    window.renderResults(container);
                } else {
                    console.error('renderResults function not found in window scope!');
                    container.innerHTML = '<div class="alert alert-danger">Error: No se pudo cargar la vista de Resultados. Verifica la consola.</div>';
                }
                break;
            case 'plugins':
                if (window.renderPlugins) window.renderPlugins(container);
                break;
            case 'settings':
                if (window.renderSettings) window.renderSettings(container);
                break;
            default:
                container.innerHTML = '<div class="empty-state"><h2>Vista no encontrada</h2></div>';
        }
    }

    async checkBackendConnection() {
        try {
            await window.api.getModels();
            console.log('Backend connected successfully');
        } catch (error) {
            console.error('Backend connection failed:', error);
            this.showConnectionError();
        }
    }

    showConnectionError() {
        const container = document.getElementById('app-content');
        container.innerHTML = `
            <div class="alert alert-danger">
                <span>⚠️</span>
                <div>
                    <strong>Error de conexión</strong><br>
                    No se pudo conectar con el backend de Python. Asegúrate de que esté ejecutándose.
                    <br><br>
                    <code>cd backend && python app.py</code>
                </div>
            </div>
        `;
    }

    showLoading(container) {
        container.innerHTML = `
            <div style="display: flex; justify-content: center; align-items: center; height: 400px;">
                <div class="spinner"></div>
            </div>
        `;
    }

    showError(container, message) {
        container.innerHTML = `
            <div class="alert alert-danger">
                <span>⚠️</span>
                <div><strong>Error:</strong> ${message}</div>
            </div>
        `;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});
