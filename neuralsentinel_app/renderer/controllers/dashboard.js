const {
  log,
  getUploadedFiles,
  getPluginMeta,
  computeComboMetrics,
  getTabHtml,
  showSaveDialog,
  readFileContent,
  getH5Visualizer,
  getCsvPreview,
  getNpyNpzVisualizer,
  getDatasetColumns,
  deleteFile,
  XLSX
} = window.electronAPI;

// --------------------Plugin manager Class--------------------
/**
 * Main class for managing plugins, file visualization, and metrics
 */
class PluginManager {
  constructor() {
    this.plugins = {};           // Registered plugins metadata and containers
    this.currentMetrics = {};    // Currently displayed metrics
    this.selectedFile = null;    // Currently selected file
    this.selectedType = null;    // Type of selected file (dataset/model)
    this.utils = {};             // Utility methods
  }

  // --------------------Initialization methods--------------------
  /**
   * Initializes the plugin manager and UI components
   */
  async init() {
    this.registerUtils();
    await this.loadPlugins();     // Load and register plugin tabs
    await this.initFileLists();   // Initialize file lists
    this.setupTabButtons();       // Setup tab navigation
    this.setupExportButtons();    // Setup export functionality
    this.showTab('visualization'); // Start with visualization tab
  }

  /**
   * Registers utility methods used throughout the class
   */
  registerUtils() {
    this.utils = {
      logEvent: (msg) => log(msg),
      escapeHtml: (s) => s.replace(/&/g, "&amp;")
                         .replace(/</g, "&lt;")
                         .replace(/>/g, "&gt;"),
      flattenObject: this.flattenObject.bind(this),
      convertCsvToTable: this.convertCsvToTable.bind(this),
      convertExcelToTable: this.convertExcelToTable.bind(this)
    };
  }

  // --------------------Plugin management--------------------
  /**
   * Loads and registers all active plugins
   */
  async loadPlugins() {
    const tabBar = document.querySelector('.tab-bar');
    const pluginContents = document.getElementById('pluginContents');

    // Clear existing plugin buttons and contents
    tabBar.querySelectorAll('button.plugin-tab-button').forEach(b => b.remove());
    pluginContents.innerHTML = '';
    this.plugins = {};

    // Get active plugins from backend
    const active = await getPluginMeta();
    this.utils.logEvent(`[PLUGINS] Active: ${active.map(p => p.displayName).join(', ')}`);

    // Create UI elements for each plugin
    for (const p of active) {
      const id = p.name.toLowerCase().replace(/\s+/g, '_');
      const label = p.displayName;

      // Create plugin tab button
      const btn = document.createElement('button');
      btn.id = `tab_${id}`;
      btn.className = 'tab-button plugin-tab-button';
      btn.textContent = label;
      btn.addEventListener('click', () => this.showPluginTab(id));
      tabBar.appendChild(btn);

      // Create plugin content container
      const div = document.createElement('div');
      div.id = `${id}_tab`;
      div.className = 'plugin-content';
      div.style.display = 'none';
      pluginContents.appendChild(div);

      // Store plugin metadata
      this.plugins[id] = { meta: p, container: div };
    }
  }

  // --------------------File management--------------------
  /**
   * Initializes file lists for datasets and models
   */
  async initFileLists() {
    const { datasets, models } = await getUploadedFiles();

    // 1) Poblar ambas listas
    this.populateFileList('datasetList', datasets, 'dataset');
    this.populateFileList('modelList',   models,   'model');

    // 2) Recuperar última selección guardada
    this.selectedFile = localStorage.getItem('lastUploadedFile');
    this.selectedType = localStorage.getItem('lastUploadedType');

    if (this.selectedFile && this.selectedType) {
      // Mostrar texto arriba
      document.getElementById('fileInfo').textContent =
        `Selected: ${this.selectedFile} (${this.selectedType})`;

      // ** MARCAR EL ÍTEM CORRECTO EN EL SIDEBAR **
      const listId = this.selectedType === 'dataset'
                    ? 'datasetList'
                    : 'modelList';
      const ul = document.getElementById(listId);
      ul.querySelectorAll('.file-item').forEach(li => {
        const name = li.querySelector('.file-name').textContent;
        if (name === this.selectedFile) {
          li.classList.add('selected');
        }
      });

      // 3) Cargar visualización
      await this.loadVisualization(this.selectedFile, this.selectedType);
    }
  }


  /**
   * Populates a file list with clickable items
   * @param {string} listId - ID of the list element
   * @param {Array} files - Array of filenames
   * @param {string} fileType - Type of files ('dataset' or 'model')
   */
  populateFileList(listId, files, fileType) {
    const ul = document.getElementById(listId);
    ul.innerHTML = '';
    
    for (const name of files) {
      const li = document.createElement('li');
      li.className = 'file-item';

      // Create clickable filename span
      const span = document.createElement('span');
      span.className = 'file-name';
      span.textContent = name;
      span.addEventListener('click', async () => {
        // Update selection UI
        this.utils.logEvent(`[USER] selected file: ${name} (${fileType})`);
        document.querySelectorAll('.file-item').forEach(item => {
          item.classList.remove('selected');
        });
        li.classList.add('selected');

        // Store selection and update UI
        //this.utils.logEvent(`Selected file: ${name}`);
        localStorage.setItem('lastUploadedFile', name);
        localStorage.setItem('lastUploadedType', fileType);
        this.selectedFile = name;
        this.selectedType = fileType;
        document.getElementById('fileInfo').textContent =
          `Selected: ${name} (${fileType})`;

        // Load visualization for selected file
        await this.loadVisualization(name, fileType);
        this.showTab('visualization');
      });

      // Create delete button
      const del = document.createElement('button');
      del.className = 'delete-btn';
      del.innerText = '🗑️';
      del.title = 'Eliminate';
      del.addEventListener('click', async e => {
        e.stopPropagation();
        if (!confirm(`Delete "${name}"?`)) return;
        
        await window.electronAPI.deleteFile({ fileName: name, fileType });
        li.remove();
        
        // Clear view if deleted file was selected
        if (this.selectedFile === name) {
          document.getElementById('visualArea').textContent = 'No file selected.';
          this.selectedFile = null;
        }
      });

      li.append(span, del);
      ul.appendChild(li);
    }
  }

  // --------------------Visualization--------------------
  /**
   * Loads and displays visualization for the selected file
   * @param {string} fileName - Name of the file to visualize
   * @param {string} fileType - Type of file ('dataset' or 'model')
   */
  async loadVisualization(fileName, fileType) {
    const labelEl = document.getElementById('visualLabel');
    const area = document.getElementById('visualArea');
    area.innerHTML = '<div style="text-align:center; padding:20px; color:#666; font-style:italic;">Loading visualization...</div>';

    // Update label based on file type
    if (fileName && fileType === 'dataset') {
      labelEl.textContent = `Dataset: ${fileName}`;
    } else if (fileName && fileType === 'model') {
      labelEl.textContent = `Model: ${fileName}`;
    } else {
      labelEl.textContent = '';
    }

    try {
      const { success, filePath } = await window.electronAPI.getFilePath(fileName, fileType);
      if (!success) throw new Error('File not found');

      // Handle model files
      if (fileType === 'model') {
        const { success: ok, summary, error } = await getH5Visualizer(filePath);
        if (!ok) throw new Error(error);
        area.innerHTML = `<pre>${this.utils.escapeHtml(summary)}</pre>`;
        return;
      }

      // Handle dataset files based on extension
      const ext = filePath.split('.').pop().toLowerCase();

      if (ext === 'csv') {
        const { success: ok, preview, error } = await getCsvPreview(filePath);
        if (!ok) throw new Error(error);
        area.innerHTML = this.utils.convertCsvToTable(preview);
      } else if (ext === 'xls' || ext === 'xlsx') {
        const html = this.utils.convertExcelToTable(filePath);
        area.innerHTML = html;
      } else if (ext === 'npy' || ext === 'npz') {
        const { success: ok, htmlPreview, error } = await getNpyNpzVisualizer(filePath);
        if (!ok) throw new Error(error);
        area.innerHTML = htmlPreview;
      } else {
        throw new Error('Unsupported file type');
      }
    } catch (e) {
      area.textContent = `Error: ${e.message}`;
    }
  }

  // --------------------Tab management--------------------
  /**
   * Sets up event listeners for tab buttons
   */
  setupTabButtons() {
    document.getElementById('tabVisualization')
            .addEventListener('click', () => this.showTab('visualization'));
            his.utils.logEvent(`[USER] entered visualization tab`);
  }

  /**
   * Shows the specified tab and hides others
   * @param {string} name - Name of the tab to show
   */
  showTab(name) {
    // Hide all content areas
    document.querySelectorAll('.tab-content, .plugin-content').forEach(el => {
      el.style.display = 'none';
      if (el.classList.contains('plugin-content')) {
        el.innerHTML = '';
      }
    });
  
    // Deactivate all buttons
    document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
  
    // Activate requested tab
    const btnId = `tab${name.charAt(0).toUpperCase() + name.slice(1)}`;
    const contId = `${name}Content`;
    document.getElementById(btnId).classList.add('active');
    document.getElementById(contId).style.display = 'block';
  }

  // --------------------Export functionality--------------------
  /**
   * Sets up event listeners for export buttons
   */
  setupExportButtons() {
    document.getElementById('exportExcelBtn')
            ?.addEventListener('click', () => this.exportToExcel());
            this.utils.logEvent('[USER] clicked export to Excel');
    document.getElementById('exportCsvBtn')
            ?.addEventListener('click', () => this.exportToCSV());
            this.utils.logEvent('[USER] clicked export to CSV');
  }

  /**
   * Exports current metrics to Excel format
   */
  async exportToExcel() {
    if (!this.currentMetrics) {
      alert('No metrics to export.');
      return;
    }
    
    const workbook = XLSX.utils.book_new();
    for (const [plugin, data] of Object.entries(this.currentMetrics)) {
      const flat = this.utils.flattenObject(data);
      const arr = Object.entries(flat).map(([k,v]) => ({ Metric:k, Value:v }));
      const ws = XLSX.utils.json_to_sheet(arr);
      XLSX.utils.book_append_sheet(workbook, ws, plugin.slice(0,31));
    }
    
    const { filePath } = await showSaveDialog({
      title: 'Save Metrics as Excel',
      defaultPath: `metrics_${this.selectedFile}.xlsx`,
      filters: [{ name:'Excel', extensions:['xlsx'] }]
    });
    
    if (filePath) XLSX.writeFile(workbook, filePath);
  }

  /**
   * Exports current metrics to CSV format
   */
  async exportToCSV() {
    if (!this.currentMetrics) {
      alert('No metrics to export.');
      return;
    }
    
    let csv = 'Plugin,Metric,Value\n';
    for (const [plugin,data] of Object.entries(this.currentMetrics)) {
      const flat = this.utils.flattenObject(data);
      for (const [k,v] of Object.entries(flat)) {
        csv += `"${plugin}","${k}","${v}"\n`;
      }
    }
    
    const { filePath } = await showSaveDialog({
      title: 'Save CSV',
      defaultPath: `metrics_${this.selectedFile}.csv`,
      filters: [{ name:'CSV', extensions:['csv'] }]
    });
    
    if (filePath) window.electronAPI.writeFile(filePath, csv);
  }

  // --------------------Utility methods--------------------
  /**
   * Converts CSV content to HTML table
   * @param {string} csvContent - CSV content to convert
   * @returns {string} HTML table representation
   */
  convertCsvToTable(csvContent) {
    const lines = csvContent.split('\n').filter(l => l.trim());
    if (!lines.length) return '<div class="error">CSV vacío.</div>';
    
    const headers = lines.shift().split(',');
    let html = '<table class="csv-table"><thead><tr>';
    headers.forEach(h => html += `<th>${this.utils.escapeHtml(h)}</th>`);
    html += '</tr></thead><tbody>';
    
    for (const line of lines) {
      const cells = line.split(',');
      html += '<tr>';
      cells.forEach(c => html += `<td>${this.utils.escapeHtml(c)}</td>`);
      html += '</tr>';
    }
    
    return html + '</tbody></table>';
  }

  /**
   * Converts Excel file to HTML table
   * @param {string} filePath - Path to Excel file
   * @returns {string} HTML table representation
   */
  convertExcelToTable(filePath) {
    const wb = XLSX.readFile(filePath);
    const ws = wb.Sheets[wb.SheetNames[0]];
    return XLSX.utils.sheet_to_html(ws);
  }

  /**
   * Flattens a nested object into single-level properties
   * @param {Object} obj - Object to flatten
   * @param {string} prefix - Current prefix for nested properties
   * @returns {Object} Flattened object
   */
  flattenObject(obj, prefix = '') {
    const out = {};
    for (const [k,v] of Object.entries(obj)) {
      const key = prefix ? `${prefix}.${k}` : k;
      if (v !== null && typeof v === 'object' && !Array.isArray(v)) {
        Object.assign(out, this.flattenObject(v, key));
      } else {
        out[key] = v;
      }
    }
    return out;
  }

  // --------------------Plugin tab handling--------------------
  /**
   * Shows and loads content for a specific plugin tab
   * @param {string} pluginName - Name of the plugin to show
   */
  async showPluginTab(pluginName) {
    this.utils.logEvent(`[USER] entered plugin tab: ${pluginName}`);
    // Hide all content areas
    document.querySelectorAll('.tab-content, .plugin-content')
            .forEach(el => el.style.display = 'none');

    // Deactivate all buttons
    document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));

    // Activate requested plugin button
    document.getElementById(`tab_${pluginName}`).classList.add('active');

    // Prepare plugin container
    const container = this.plugins[pluginName].container;
    container.innerHTML = `<div class="spinner">Loading…</div>`;
    container.style.display = 'block';

    try {
      // Prepare payload for plugin
      const payload = {
        __current_file: this.selectedFile,
        __current_type: this.selectedType
      };

      // Get plugin HTML from backend
      const html = await getTabHtml(pluginName, payload);
      container.innerHTML = html;

      // Re-inject and execute any scripts
      container.querySelectorAll('script').forEach(old => {
        const s = document.createElement('script');
        if (old.src) s.src = old.src;
        else s.textContent = old.textContent;
        document.head.appendChild(s);
        old.remove();
      });
    } catch (err) {
      container.innerHTML = `
        <div class="alert alert-danger">
          Error loading plugin: ${this.utils.escapeHtml(err.message)}
        </div>`;
      this.utils.logEvent(`showPluginTab error: ${err.message}`);
    }
  }
}

// --------------------Initialization--------------------
window.addEventListener('DOMContentLoaded', () => {
  // Setup sidebar toggle
  const sidebar = document.querySelector('.sidebar');
  const toggleBtn = document.getElementById('toggleSidebarBtn');
  if (sidebar && toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
    });
  }

  // Initialize plugin manager
  const mgr = new PluginManager();
  mgr.init();
});