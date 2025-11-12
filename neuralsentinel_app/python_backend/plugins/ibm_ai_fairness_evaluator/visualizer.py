import sys, os, json, importlib.util

# --------------------Visualizer for IBM AI Fairness Evaluator--------------------
def safe_print(s: str):
    sys.stdout.buffer.write(s.encode('utf-8'))

# DEBUG: what args arrived
print(">>> [visualizer] ARGS:", sys.argv, file=sys.stderr)

# Parse JSON payload of metrics (or empty)
try:
    m = json.loads(sys.argv[1])
except Exception as e:
    safe_print(f"<div class='alert alert-danger'>Error parsing JSON: {e}</div>")
    sys.exit(0)

# Load BaseVisualizer from the core library
core_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', 'core', 'interfaces.py'
))
spec = importlib.util.spec_from_file_location("core.interfaces", core_path)
core = importlib.util.module_from_spec(spec)
sys.modules["core.interfaces"] = core
spec.loader.exec_module(core)
BaseVisualizer = core.BaseVisualizer

class IBMFairnessVisualizer(BaseVisualizer):
    def __init__(self):
        # Initialize the visualizer with the name and tooltips
        self.name   = "IBM AI Fairness Evaluator"
        self.tab_id = "ibm_ai_fairness_evaluator"
        self.tooltips = {
            "disparate_impact": "Ratio of favorable outcomes for unprivileged vs privileged.",
            "statistical_parity_difference": "Difference in selection rates between groups.",
            "mean_difference": "Difference in mean predicted outcomes."
        }

    def get_tab_metadata(self):
        """
        Metadata for the tab shown in the UI.
        """
        return {"id": self.tab_id, "name": "Fairness"}

    def render_content(self, m, _dataset_name=None):
        """
        Render the content of the fairness evaluation, including a table of results and charts.
        """
        # Centered title
        title_html = f"<h2 style='text-align:center; margin-bottom:20px;'>{self.name}</h2>"

        # If missing parameters, show selection form
        if not m or "label_column" not in m or "protected_column" not in m:
            return title_html + self.render_input_form()

        # If we have metrics but they're being calculated
        if m.get("calculating", False):
            return title_html + """
<div class="card">
  <div class="card-body" style="text-align:center; padding:20px; color:#666; font-style:italic;">
    Calculating metrics...
  </div>
</div>
"""

        # Helper to render a colored badge based on the value of the metric
        def badge(v, mn, mx):
            cls = "badge-success" if mn <= v <= mx else "badge-danger"
            return f"<span class='badge {cls}'>{v:.4f}</span>"

        # Tooltip icon for each metric
        def tooltip(key):
            tip = self.tooltips.get(key, "")
            return (f"<span title=\"{tip}\" style=\"cursor:help;"
                    "background:#fff;border:1px solid #ccc;border-radius:50%;"
                    "display:inline-block;width:18px;height:18px;text-align:center;"
                    "line-height:18px;margin-left:6px;color:#007bff;\">?</span>")

        # Main card with table and chart for the fairness metrics
        html = [f"""
<div class="card">
  <div class="card-body" style="padding-left: 30px;">
    <div style="display: flex; justify-content: space-between;">
      <div style="width: 100%;">
        <h5>Configuration</h5>
        <table class="table table-sm mb-3">
          <tr><th>Label Column:</th><td>{m['label_column']}</td></tr>
          <tr><th>Protected Column:</th><td>{m['protected_column']}</td></tr>
          <tr><th>Instances:</th><td>{m['num_instances']}</td></tr>
        </table>
        <div style="margin-top: 80px;">
        <h5>Fairness Metrics</h5>
        <table class="table table-bordered table-sm mb-4">
          <thead>
            <tr>
              <th>Metric</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Disparate Impact {tooltip('disparate_impact')}</td>
              <td>{badge(m['disparate_impact'], 0.8, 1.2)}</td>
            </tr>
            <tr>
              <td>Stat. Parity Difference {tooltip('statistical_parity_difference')}</td>
              <td>{badge(m['statistical_parity_difference'], -0.1, 0.1)}</td>
            </tr>
            <tr>
              <td>Mean Difference {tooltip('mean_difference')}</td>
              <td>{badge(m['mean_difference'], -0.1, 0.1)}</td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>
      <div style="width: 100%;">
        <h5>Fairness Overview</h5>
        {self._make_bar_svg(
            ["Disparate Impact", "Stat. Parity Diff", "Mean Difference"],
            [m['disparate_impact'],
             m['statistical_parity_difference'],
             m['mean_difference']],
            width=500, height=300
        )}
      </div>
    </div>
  </div>
</div>
"""]
        return title_html + "".join(html)

    def render_input_form(self):
        """
        Form to select label and protected columns.
        """
        return """
<div class="card">
  <div class="card-body">
    <div class="form-group">
      <label for="labelColumnSelect">Label Column</label>
      <select id="labelColumnSelect" class="form-control">
        <option value="" selected disabled>Select a column</option>
      </select>
    </div>
    <div class="form-group">
      <label for="protectedColumnSelect">Protected Column</label>
      <select id="protectedColumnSelect" class="form-control">
        <option value="" selected disabled>Select a column</option>
      </select>
    </div>
    <div id="metricsLoading" style="display:none; text-align:center; padding:20px; color:#666; font-style:italic;">
      Calculating metrics...
    </div>
  </div>
</div>
<script>
(async () => {
  // use the context-isolated API bridge
  const { getDatasetColumns, computeComboMetrics, getTabHtml } = window.electronAPI;
  const dataset = localStorage.getItem('lastUploadedFile');
  const labelSelect = document.getElementById('labelColumnSelect');
  const protSelect = document.getElementById('protectedColumnSelect');
  const loadingDiv = document.getElementById('metricsLoading');

  // populate dropdowns
  const res = await getDatasetColumns(dataset);
  if (res.success) {
    res.columns.forEach(col => {
      labelSelect.add(new Option(col, col));
      protSelect.add(new Option(col, col));
    });
  }

  // Function to calculate and display metrics
  async function calculateMetrics() {
    const lbl = labelSelect.value;
    const prot = protSelect.value;
    
    if (!lbl || !prot) return;
    
    // Show loading indicator
    loadingDiv.style.display = 'block';
    
    // Update UI with calculating state
    const calculatingMetrics = { 
      label_column: lbl, 
      protected_column: prot, 
      calculating: true 
    };
    const calculatingHtml = await getTabHtml('ibm_ai_fairness_evaluator', calculatingMetrics);
    document.getElementById('ibm_ai_fairness_evaluator_tab').innerHTML = calculatingHtml;

    // Calculate actual metrics
    const result = await computeComboMetrics({
      modelFile: '__DUMMY__',
      datasetFile: dataset,
      labelColumn: lbl,
      protectedColumn: prot
    });
    
    // Hide loading indicator
    loadingDiv.style.display = 'none';
    
    const metrics = result.success
      ? result.metrics['ibm_ai_fairness_evaluator']
      : { error: result.error || 'Unknown error' };
    const html = await getTabHtml('ibm_ai_fairness_evaluator', metrics);
    document.getElementById('ibm_ai_fairness_evaluator_tab').innerHTML = html;
  }

  // Add event listeners for both selects
  labelSelect.addEventListener('change', calculateMetrics);
  protSelect.addEventListener('change', calculateMetrics);
})();
</script>
"""
    
    def _make_bar_svg(self, labels, values, width, height):
        """
        Create a bar chart in SVG format for the given labels and values.
        """
        maxv = max(abs(v) for v in values) or 1.0
        bar_w = width / len(values) * 0.6
        gap = width / len(values) * 0.4
        svg = [f"<svg width='{width}' height='{height}' style='border:1px solid #ccc;'>"]
        # X-axis line
        svg.append(f"<line x1='40' y1='{height-30}' x2='{width-10}' y2='{height-30}' stroke='#333'/>")
        for i, v in enumerate(values):
            h = (v / maxv) * (height-80)
            x = 40 + i*(bar_w+gap)+gap/2
            y = height - 30 - (h if h>0 else 0)
            color = 'steelblue' if v>=0 else 'tomato'
            svg.append(f"<rect x='{x:.1f}' y='{y:.1f}' width='{bar_w:.1f}' height='{abs(h):.1f}' fill='{color}'/>")
            svg.append(f"<text x='{x+bar_w/2:.1f}' y='{y-5:.1f}' text-anchor='middle' font-size='10'>{v:.4f}</text>")
            svg.append(f"<text x='{x+bar_w/2:.1f}' y='{height-15}' text-anchor='middle' font-size='10'>{labels[i]}</text>")
        svg.append("</svg>")
        return "".join(svg)


if __name__ == "__main__":
    viz = IBMFairnessVisualizer()
    safe_print(viz.render_content(m))