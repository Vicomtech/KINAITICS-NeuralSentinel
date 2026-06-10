// Settings View (moved from datasets.js)
window.renderSettings = function (container) {
    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Settings</h3>
            </div>
            <div class="card-body">
                <div class="form-group">
                    <label class="form-label">Theme</label>
                    <select class="form-select">
                        <option>Light</option>
                        <option selected>System</option>
                        <option>Dark</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Backend Port</label>
                    <input type="number" class="form-input" value="5000" readonly>
                </div>
            </div>
        </div>
    `;
};
