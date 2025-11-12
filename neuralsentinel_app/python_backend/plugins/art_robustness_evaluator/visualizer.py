import sys
import os
import json
import importlib.util

# --------------------Visualizer for ART Robustness Evaluator--------------------
def safe_print(s: str):
    """Write UTF‑8 bytes directly to stdout (avoids locale issues)."""
    sys.stdout.buffer.write(s.encode("utf-8"))


# Debug initialization
print(f">>> [visualizer] ARGS: {sys.argv}", file=sys.stderr)

# Ensure we received the JSON payload
if len(sys.argv) < 2:
    safe_print("<div class='alert alert-danger'>Error: missing metrics argument</div>")
    sys.exit(0)

# Parse the JSON payload
try:
    payload = json.loads(sys.argv[1])
except Exception as e:
    safe_print(f"<div class='alert alert-danger'>Error parsing JSON: {e}</div>")
    sys.exit(0)

# Dynamically import BaseVisualizer from core/interfaces.py
core_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "core", "interfaces.py")
)
spec = importlib.util.spec_from_file_location("core.interfaces", core_path)
core = importlib.util.module_from_spec(spec)
sys.modules["core.interfaces"] = core
spec.loader.exec_module(core)
BaseVisualizer = core.BaseVisualizer


class ARTRobustnessVisualizer(BaseVisualizer):
    def __init__(self):
        # Visualizer name and ID
        self.name = "ART Robustness Evaluator"
        self.tab_id = "art_robustness_evaluator"

        # Short tooltips for each metric column
        self.tooltips = {
            "clean_accuracy": "Clean Accuracy: % correct on clean data.",
            "adv_accuracy": "Adversarial Accuracy: % correct under attack.",
            "accuracy_drop": "Absolute drop in accuracy due to attack.",
            "l2_dist_mean": "Avg L₂ norm of perturbation.",
            "l2_dist_max": "Max L₂ norm of perturbation.",
            "linf_dist_mean": "Avg L∞ norm of perturbation.",
            "linf_dist_max": "Max L∞ norm of perturbation.",
            "l0_dist_mean": "Avg L₀ norm (# changed features).",
            "l0_dist_max": "Max L₀ norm (# changed features).",
            "crossentropy_clean": "Avg cross‑entropy loss on clean data.",
            "crossentropy_adv": "Avg cross‑entropy loss on adversarial data.",
            "margin_clean": "Avg margin (true prob − runner‑up) on clean data.",
            "margin_adv": "Avg margin (true prob − runner‑up) on adversarial data.",
        }

    # Host‑framework API
    def get_tab_metadata(self):
        """Return tab metadata consumed by the host UI."""
        return {"id": self.tab_id, "name": self.name}

    # Main HTML generator
    def render_content(self, payload):
        base_file  = payload.get("__current_file", "")
        base_type  = payload.get("__current_type", "")
        other_file = payload.get("__other_file", "")
        data       = payload.get(self.tab_id, payload)

        html = []

        # Inline CSS styles
        html.append(
            """
<style>
.table th, .table td { padding: 0.75rem 1.5rem; }
.tooltipi {
  position: relative; display: inline-flex; align-items: center; justify-content: center;
  width: 1.2em; height: 1.2em; border-radius: 50%; background: #007bff;
  color: #fff; font-size: 0.8em; cursor: help; margin-left: 0.3em;
}
.tooltipi .tooltiptext {
  visibility: hidden; width: 180px; background: #333; color: #fff;
  text-align: center; border-radius: 4px; padding: 5px;
  position: absolute; z-index: 10; bottom: 125%; left: 50%;
  transform: translateX(-50%); opacity: 0; transition: opacity 0.3s;
}
.tooltipi:hover .tooltiptext { visibility: visible; opacity: 1; }

.flex-container { display: flex; justify-content: space-between; margin-top: 20px; }
.flex-item      { width: 48%; }
.bar-container  { text-align: center; margin-top: 20px; }
</style>
"""
        )

        # Title header
        html.append(f"<h2 style='text-align:center;margin-bottom:20px;'>{self.name}</h2>")

        # Dropdown selector
        sel_type  = "dataset" if base_type == "model" else "model"
        files_key = "datasets" if sel_type == "dataset" else "models"
        html.append(
            f"""
<div class="mb-3">
  <label>Select a <strong>{sel_type}</strong> to combine with <strong>{base_file}</strong>:</label>
  <select id="artr_sel" class="form-control">
    <option value="">-- select --</option>
  </select>
</div>
<div id="artr_loading_metrics" style="display:none; text-align:center; padding:20px; color:#666; font-style:italic;">
  Calculating metrics...
</div>
<div id="{self.tab_id}_metrics">
"""
        )

        # Initial metrics or placeholder
        if other_file and isinstance(data, dict) and not data.get("error"):
            html.append(self._render_metrics_content(data))
        elif isinstance(data, dict) and data.get("error"):
            html.append(f"<div class='alert alert-danger'>{data['error']}</div>")
        else:
            html.append("<div class='alert alert-warning'>No metrics to display. Select files above.</div>")
        html.append("</div>")  # Close _metrics div

        # Client‑side script
        html.append(
            f"""
<script>
(async () => {{
  const {{ getUploadedFiles, computeComboMetrics, getTabHtml }} = window.electronAPI;
  const sel        = document.getElementById('artr_sel');
  const loadingDiv = document.getElementById('artr_loading_metrics');
  const metricsDiv = document.getElementById('{self.tab_id}_metrics');

  // Populate dropdown with uploaded files
  const files = await getUploadedFiles();
  (files['{files_key}'] || []).forEach(f => sel.append(new Option(f, f)));
  if ('{other_file}') sel.value = '{other_file}';

  sel.onchange = async () => {{
    const other = sel.value;
    if (!other) return;

    // Show spinner and clear old results
    loadingDiv.style.display = 'block';
    metricsDiv.innerHTML = '';

    const args = {{
      modelFile:    '{base_type}' === 'model' ? '{base_file}' : other,
      datasetFile:  '{base_type}' === 'model' ? other        : '{base_file}',
      __current_file: '{base_file}',
      __current_type: '{base_type}',
      __other_file:   other,
      __other_type:   '{sel_type}'
    }};

    try {{
      const res = await computeComboMetrics(args);
      if (!res.success) {{
        metricsDiv.innerHTML = `<div class="alert alert-danger">Error: ${{res.error}}</div>`;
        return;
      }}

      // Build payload with new metrics
      const payload2 = Object.assign({{
        __current_file: args.__current_file,
        __current_type: args.__current_type,
        __other_file: args.__other_file,
        __other_type: args.__other_type
      }}, {{ '{self.tab_id}': res.metrics['{self.tab_id}'] }});

      // Get freshly rendered HTML
      const html2 = await getTabHtml('{self.tab_id}', payload2);

      // Insert only the metrics fragment to avoid duplicate UI
      const tmp  = document.createElement('div');
      tmp.innerHTML = html2;
      const inner = tmp.querySelector('#{self.tab_id}_metrics');
      metricsDiv.innerHTML = inner ? inner.innerHTML : html2;
    }} catch (e) {{
      metricsDiv.innerHTML = `<div class="alert alert-danger">Error: ${{e.message}}</div>`;
    }} finally {{
      loadingDiv.style.display = 'none';
    }}
  }};
}})();
</script>
"""
        )

        return "".join(html)

    # Metrics table and charts
    def _render_metrics_content(self, data):
        html = []
        first_metrics = next(iter(data.values())).get("metrics", {})
        keys = list(first_metrics.keys())

        # Table header
        header_cells = ["<th>Attack</th>"]
        for k in keys:
            label = k.replace("_", " ").title()
            tip   = self.tooltips.get(k, "")
            header_cells.append(
                f"<th>{label}"
                f"<span class='tooltipi'>i<span class='tooltiptext'>{tip}</span></span></th>"
            )

        # Table rows
        rows = []
        for atk, info in data.items():
            m     = info.get("metrics", {})
            cells = [f"<td><strong>{atk.upper()}</strong></td>"]
            for k in keys:
                v = m.get(k, 0.0)
                cells.append(f"<td>{v:.4f}</td>")
            rows.append(f"<tr>{''.join(cells)}</tr>")

        html.append(
            f"""
<div class="card">
  <div class="card-body">
    <h5>Robustness Metrics</h5>
    <table class="table table-bordered table-sm">
      <thead><tr>{''.join(header_cells)}</tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
"""
        )

        # Radar charts
        html.append("<div class='flex-container'>")
        if "fgsm" in data:
            html.append("<div class='flex-item'><h5>FGSM Attack</h5>")
            html.append(self._make_radar_svg(data, keys, 400, "fgsm"))
            html.append("</div>")
        if "pgd" in data:
            html.append("<div class='flex-item'><h5>PGD Attack</h5>")
            html.append(self._make_radar_svg(data, keys, 400, "pgd"))
            html.append("</div>")
        html.append("</div>")            # Close flex-container

        # Optional bar chart for PGD (now at the end and centered)
        if "pgd" in data and all(k in keys for k in ("clean_accuracy", "adv_accuracy", "accuracy_drop")):
            vals   = [data["pgd"]["metrics"][k] for k in ("clean_accuracy", "adv_accuracy", "accuracy_drop")]
            labels = ["Clean", "Adv", "Drop"]
            html.append("<div class='bar-container'>")
            html.append(self._make_bar_svg(labels, vals, 400, 200))
            html.append("</div>")

        html.append("</div></div>")      # Close card
        return "".join(html)

    # Bar chart SVG
    def _make_bar_svg(self, labels, values, width, height):
        maxv   = max(values) or 1.0
        bar_w  = width / len(values) * 0.6
        gap    = width / len(values) * 0.4
        svg = [
            f"<svg width='{width}' height='{height}' style='border:1px solid #ccc;'>",
            f"<line x1='20' y1='{height-30}' x2='{width-10}' y2='{height-30}' stroke='#333'/>",
        ]
        for i, v in enumerate(values):
            h = (v / maxv) * (height - 60)
            x = 20 + i * (bar_w + gap) + gap / 2
            y = height - 30 - h
            svg.append(f"<rect x='{x:.1f}' y='{y:.1f}' width='{bar_w:.1f}' height='{h:.1f}' fill='steelblue'/>")
            svg.append(f"<text x='{x + bar_w/2:.1f}' y='{y - 5:.1f}' text-anchor='middle'>{v:.4f}</text>")
            svg.append(f"<text x='{x + bar_w/2:.1f}' y='{height - 10}' text-anchor='middle'>{labels[i]}</text>")
        svg.append("</svg>")
        return "".join(svg)

    # Radar chart SVG
    def _make_radar_svg(self, data, metrics, size, attack):
        import math

        n       = len(metrics)
        angle   = 2 * math.pi / n
        cx = cy = size / 2
        r       = size / 2 - 50
        maxvals = {k: max(info["metrics"].get(k, 0) for info in data.values()) or 1.0 for k in metrics}

        svg = [f"<svg width='{size}' height='{size}' style='border:1px solid #ccc;margin-top:20px;'>"]

        # Guide circles
        for i in range(1, 5):
            radius = r * i / 4
            svg.append(f"<circle cx='{cx}' cy='{cy}' r='{radius:.1f}' fill='none' stroke='#ddd'/>")

        # Axes and labels
        for i, k in enumerate(metrics):
            a = angle * i - math.pi / 2
            x = cx + r * math.cos(a)
            y = cy + r * math.sin(a)
            svg.append(f"<line x1='{cx}' y1='{cy}' x2='{x:.1f}' y2='{y:.1f}' stroke='#aaa'/>")
            svg.append(
                f"<text x='{cx + (r + 20) * math.cos(a):.1f}' "
                f"y='{cy + (r + 20) * math.sin(a):.1f}' text-anchor='middle' font-size='10'>"
                f"{k.replace('_', ' ')}</text>"
            )

        # Polygon for selected attack
        color = "rgba(255, 0, 0, 0.2)" if attack == "fgsm" else "rgba(0, 0, 255, 0.2)"
        for atk, info in data.items():
            if atk != attack:
                continue
            pts = []
            for i, k in enumerate(metrics):
                val = info["metrics"].get(k, 0) / maxvals[k]
                a   = angle * i - math.pi / 2
                pts.append(f"{cx + r * val * math.cos(a):.1f},{cy + r * val * math.sin(a):.1f}")
            pts.append(pts[0])  # Close path
            svg.append(f"<polygon points='{','.join(pts)}' fill='{color}' stroke='{color}' stroke-width='2'/>")
        svg.append("</svg>")
        return "".join(svg)


# CLI entry‑point
if __name__ == "__main__":
    viz = ARTRobustnessVisualizer()
    safe_print(viz.render_content(payload))