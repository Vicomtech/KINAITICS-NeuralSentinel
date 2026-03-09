// Settings View (moved from datasets.js)
window.renderSettings = function (container) {
    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Configuración</h3>
            </div>
            <div class="card-body">
                <div class="form-group">
                    <label class="form-label">Tema</label>
                    <select class="form-select">
                        <option>Claro</option>
                        <option selected>Sistema</option>
                        <option>Oscuro</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Puerto del Backend</label>
                    <input type="number" class="form-input" value="5000" readonly>
                </div>
            </div>
        </div>
    `;
};
