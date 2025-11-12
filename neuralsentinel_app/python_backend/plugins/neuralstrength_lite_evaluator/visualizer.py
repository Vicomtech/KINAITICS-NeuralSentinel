import sys
import os
import json
import importlib.util

# --------------------Visualizer for Neuralstrength Lite Evaluator--------------------
def safe_print(s: str):
    sys.stdout.buffer.write(s.encode("utf-8"))

# Debug initialization
print(f">>> [visualizer] ARGS: {sys.argv}", file=sys.stderr)
if len(sys.argv) < 2:
    safe_print("<div class='alert alert-danger'>Error: missing metrics argument</div>")
    sys.exit(0)

# Parse the JSON payload
try:
    payload = json.loads(sys.argv[1])
except Exception as e:
    safe_print(f"<div class='alert alert-danger'>Error parsing JSON: {e}</div>")
    sys.exit(0)

# Load BaseVisualizer from core/interfaces.py
core_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir, "core", "interfaces.py"
))
spec = importlib.util.spec_from_file_location("core.interfaces", core_path)
core = importlib.util.module_from_spec(spec)
sys.modules["core.interfaces"] = core
spec.loader.exec_module(core)
BaseVisualizer = core.BaseVisualizer

class NeuralstrengthLiteVisualizer(BaseVisualizer):
    def __init__(self):
        # Initialize visualizer with the name and tooltips
        self.name = "Neuralstrength Lite Evaluator"
        self.tab_id = "neuralstrength_lite_evaluator"
        self.details = {
            "fgsm": ("FGSM: Fast Gradient Sign Method", "Single-step attack that perturbs input along the sign of the gradient."),
            "pgd": ("PGD: Projected Gradient Descent", "Iterative attack that projects perturbed samples back onto the ε-ball."),
            "bim": ("BIM: Basic Iterative Method", "Multiple small FGSM steps to craft adversarial examples."),
            "trojaning": ("Trojaning Attack", "Modifies inputs to implant a hidden trigger for backdoor behavior.")
        }

    def get_tab_metadata(self):
        """
        Returns metadata for the visualizer tab.
        """
        return {"id": self.tab_id, "name": self.name}

    def render_content(self, data):
        """
        Renders the visual content for the evaluator's results.
        """
        import sys, json

        # Debugging
        print(f">>> [visualizer] payload keys: {list(data.keys())}", file=sys.stderr)

        # Extract file info
        base_file = data.pop("__current_file", "")
        base_type = data.pop("__current_type", "")
        other_file = data.pop("__other_file", "")
        other_type = data.pop("__other_type", "")
        print(f">>> [visualizer] base={base_file}/{base_type} other={other_file}/{other_type}", file=sys.stderr)

        # Determine model & dataset for export
        model_for_export = base_file if base_type == "model" else other_file
        dataset_for_export = base_file if base_type == "dataset" else other_file

        # Check if any metrics are present
        has_metrics = any(k in self.details for k in data)

        if has_metrics:
            html = []

            # Global error
            if data.get("error"):
                html.append(f"<div class='alert alert-danger'>{data['error']}</div>")
            else:
                # Joint header
                if base_file and other_file:
                    html.append(f"<h3>Joint metrics of <em>{base_file}</em> + <em>{other_file}</em></h3>")

                # One card per engine
                for eng, out in data.items():
                    if eng not in self.details or not isinstance(out, dict):
                        continue
                    title, tip = self.details[eng]
                    icon = (
                        "<span title='{tip}' "
                        "style='display:inline-block;width:1.2em;height:1.2em;line-height:1.2em;"
                        "border:2px solid #007bff;border-radius:50%;"
                        "text-align:center;color:#007bff;cursor:help;"
                        "font-weight:bold;font-size:0.9em;margin-left:8px;'>i</span>"
                    ).format(tip=tip)

                    html.append(
                        "<div class='card mb-4'>"
                        "  <div class='card-header bg-info text-white'>"
                        f"    <h4 style='display:inline'>{title}</h4>{icon}"
                        "  </div>"
                        "  <div class='card-body'>"
                    )

                    # Engine-specific error
                    if out.get("error"):
                        html.append(f"<div class='alert alert-danger'>{out['error']}</div></div></div>")
                        continue

                    m, imp = out.get("metrics", {}), out.get("impact", {})

                    # Metrics list
                    if m:
                        html.append("<ul class='list-group mb-3'>")
                        for k, v in m.items():
                            disp = (
                                f"{v:.4f}" if isinstance(v, (int, float)) else
                                json.dumps(v) if isinstance(v, (list, dict)) else
                                str(v)
                            )
                            lbl2 = k.replace("_", " ").title()
                            html.append(f"<li class='list-group-item'><strong>{lbl2}:</strong> {disp}</li>")
                        html.append("</ul>")

                    # Accuracy chart
                    if all(key in m for key in ("original_accuracy", "adversarial_accuracy", "difference_accuracy")):
                        html.append("<h5>Accuracy Chart</h5>")
                        html.append(self._make_bar_svg(
                            ["Orig Acc", "Adv Acc", "Diff Acc"],
                            [m["original_accuracy"], m["adversarial_accuracy"], m["difference_accuracy"]],
                            600, 200
                        ))

                    # Similarity chart
                    if all(key in m for key in ("avg_similarity", "max_similarity", "min_similarity")):
                        html.append("<h5>Similarity Chart</h5>")
                        html.append(self._make_bar_svg(
                            ["Avg Sim", "Max Sim", "Min Sim"],
                            [m["avg_similarity"], m["max_similarity"], m["min_similarity"]],
                            600, 200
                        ))

                    # Impact heatmap
                    block = imp.get("input_0", imp)
                    if isinstance(block, dict) and "values" in block and "neurons" in block:
                        vals, neurons = block["values"], block["neurons"]
                        # Table
                        html.append("<h5>Impact Heatmap (Table)</h5>"
                                    "<table class='table table-sm table-bordered'><thead><tr><th></th>")
                        for n in neurons:
                            html.append(f"<th>N{n}</th>")
                        html.append("</tr></thead><tbody>")
                        for i, row in enumerate(vals):
                            html.append(f"<tr><th>Row {i}</th>")
                            for v in row:
                                html.append(f"<td>{v:.4f}</td>")
                            html.append("</tr>")
                        html.append("</tbody></table>")
                        # SVG
                        html.append("<h5>Impact Heatmap (SVG)</h5>")
                        html.append(self._make_heatmap_svg(vals, neurons, 600))

                    html.append("</div></div>")

                # Export buttons (pass modelFile & datasetFile)
                html.append(
                    """
                    <div class='d-flex justify-content-center mt-4 mb-4'>
                        <button class='btn btn-primary' style='margin-right: 0.75rem' onclick=\"(async()=>{
                            const r=await window.electronAPI.exportMetrics({modelFile:'%s',datasetFile:'%s'});
                            if(!r.success)alert('Export failed: '+(r.error||'Unknown'));
                        })()\">
                            <i class='fas fa-file-excel'></i> Export to Excel
                        </button>
                        <button class='btn btn-success' style='margin-left: 0.75rem' onclick=\"(async()=>{
                            const r=await window.electronAPI.exportCsv({modelFile:'%s',datasetFile:'%s'});
                            if(!r.success)alert('Export failed: '+(r.error||'Unknown'));
                        })()\">
                            <i class='fas fa-file-csv'></i> Export to CSV
                        </button>
                    </div>
                    """ % (model_for_export, dataset_for_export, model_for_export, dataset_for_export)
                )
            return "".join(html)

        # If no metrics: show selector + loading + placeholder
        html = []
        sel_type = "model" if base_type == "dataset" else "dataset"
        files_key = "models" if sel_type == "model" else "datasets"
        html.append(f"<h2 style='text-align:center'>{self.name}</h2>")
        html.append(f"""
        <div id="{self.tab_id}_dropdown" class="mb-3">
          <label>Select a <strong>{sel_type}</strong> to combine with <strong>{base_file}</strong>:</label>
          <select id="ns_other_select" class="form-control">
            <option value="">-- select --</option>
          </select>
        </div>
        """)
        html.append("""
        <div id="ns_loading_metrics"
             style="display:none; text-align:center; padding:20px; color:#666; font-style:italic;">
          Calculating metrics...
        </div>
        """)
        html.append(f"<div id='{self.tab_id}_metrics'>"
                    "<div class='alert alert-warning'>No metrics to display. Select files above.</div>"
                    "</div>")

        html.append(f"""
        <script>
        (async () => {{
          const {{ getUploadedFiles, computeComboMetrics, getTabHtml }} = window.electronAPI;
          const sel = document.getElementById('ns_other_select');
          const loadingDiv = document.getElementById('ns_loading_metrics');
          const metricsDiv = document.getElementById('{self.tab_id}_metrics');

          const files = await getUploadedFiles();
          (files['{files_key}']||[]).forEach(f => sel.append(new Option(f,f)));

          sel.addEventListener('change', async () => {{
            const other = sel.value; if(!other) return;
            loadingDiv.style.display = 'block';
            metricsDiv.innerHTML = '';

            try {{
              const args = {{
                modelFile: '{base_file}',
                datasetFile: '{base_file}',
                __current_file: '{base_file}',
                __current_type: '{base_type}',
                __other_file: other,
                __other_type: '{sel_type}'
              }};
              if ('{base_type}' === 'model') args.datasetFile = other;
              else args.modelFile = other;

              const res = await computeComboMetrics(args);
              if (!res.success) {{
                metricsDiv.innerHTML = `<div class="alert alert-danger">Error: ${{res.error}}</div>`;
                return;
              }}

              const payload2 = {{
                __current_file: args.__current_file,
                __current_type: args.__current_type,
                __other_file: args.__other_file,
                __other_type: args.__other_type,
                ...(res.metrics['{self.tab_id}']||res.metrics)
              }};
              const html2 = await getTabHtml('{self.tab_id}', payload2);
              metricsDiv.innerHTML = html2;
            }} catch(e) {{
              metricsDiv.innerHTML = `<div class="alert alert-danger">Error: ${{e.message}}</div>`;
            }} finally {{
              loadingDiv.style.display = 'none';
            }}
          }});
        }})();
        </script>
        """)

        return "".join(html)

    def _make_bar_svg(self, labels, values, w, h):
        """
        Create a bar chart in SVG format for the given labels and values.
        """
        maxv = max(values) or 1.0
        bw = w / len(values) * 0.6
        gap = w / len(values) * 0.4
        svg = [f"<svg width='{w}' height='{h}' style='border:1px solid #ccc;'>"]
        for i, v in enumerate(values):
            hh = (v / maxv) * (h - 40)
            x = i * (bw + gap) + gap / 2
            y = h - hh - 10
            svg.append(f"<rect x='{x:.1f}' y='{y:.1f}' width='{bw:.1f}' height='{hh:.1f}' fill='steelblue'/>")
            svg.append(f"<text x='{x + bw / 2:.1f}' y='{y - 2:.1f}' text-anchor='middle'>{v:.4f}</text>")
            svg.append(f"<text x='{x + bw / 2:.1f}' y='{h - 2}' text-anchor='middle'>{labels[i]}</text>")
        svg.append("</svg>")
        return "".join(svg)

    def _make_heatmap_svg(self, values, neurons, w):
        """
        Create a heatmap in SVG format for the given values and neurons.
        """
        rows, cols = len(values), len(neurons)
        cell = w / cols
        top = 30
        h = top + rows * cell + 20
        flat = [v for row in values for v in row] or [0]
        mn, mx = min(flat), max(flat)
        rng = mx - mn or 1.0

        svg = [
            f"<svg width='{w}' height='{h}' style='border:1px solid #ccc;'>",
            f"<text x='{w/2}' y='20' text-anchor='middle' font-size='14'>Impact Heatmap</text>"
        ]
        for i, row in enumerate(values):
            for j, v in enumerate(row):
                norm = (v - mn) / rng
                g = int(180 * (1 - norm))
                svg.append(
                    f"<rect x='{j * cell:.1f}' y='{top + i * cell:.1f}' width='{cell:.1f}' "
                    f"height='{cell:.1f}' fill='rgb(255,{g},0)'/>"
                )
        for j, n in enumerate(neurons):
            x = j * cell + cell / 2
            svg.append(f"<text x='{x:.1f}' y='{h - 5}' text-anchor='middle' font-size='10'>N{n}</text>")
        svg.append("</svg>")
        return "".join(svg)

if __name__ == "__main__":
    viz = NeuralstrengthLiteVisualizer()
    html = viz.render_content(payload)
    safe_print(html)
