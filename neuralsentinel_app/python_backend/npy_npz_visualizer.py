import numpy as np
from PIL import Image
from io import BytesIO
from base64 import b64encode
import sys
import json
import os

def array_to_img_tag(img_array, size=(128, 128)):
    """
    Convierte un array a una etiqueta <img> base64 usando pixelated rendering.
    """
    try:
        # float [0,1] -> uint8 [0,255], clip+cast para otros
        if np.issubdtype(img_array.dtype, np.floating):
            if img_array.max() <= 1.0:
                img_array = (img_array * 255).astype(np.uint8)
            else:
                img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        elif img_array.dtype != np.uint8:
            img_array = np.clip(img_array, 0, 255).astype(np.uint8)

        # Crear PIL Image
        if img_array.ndim == 2:
            img = Image.fromarray(img_array, mode='L')
        elif img_array.ndim == 3 and img_array.shape[2] == 3:
            img = Image.fromarray(img_array, mode='RGB')
        else:
            return "<p>Unsupported image shape.</p>"

        # Convertir a PNG base64
        buf = BytesIO()
        img.save(buf, format='PNG')
        b64 = b64encode(buf.getvalue()).decode('utf-8')

        w, h = size
        return (
            f'<img src="data:image/png;base64,{b64}" '
            f'width="{w}" height="{h}" '
            'style="image-rendering: pixelated; margin:5px;" />'
        )
    except Exception as e:
        return f"<p>Error rendering image: {e}</p>"

def render_preview(path):
    """
    Genera un HTML descriptivo de .npz o .npy, detectando
    si es tabular o de imágenes.
    """
    try:
        name = os.path.basename(path)
        html = f"<h2>Dataset Preview: {name}</h2>\n"

        # Cargar datos
        if path.endswith('.npz'):
            data = np.load(path, allow_pickle=True)
            x = data['x'] if 'x' in data.files else None
            y = data['y'] if 'y' in data.files else None
        else:
            arr = np.load(path, allow_pickle=True)
            if isinstance(arr, np.ndarray) and arr.dtype == object and arr.ndim == 0:
                obj = arr.item()
                x = obj.get('x', None)
                y = obj.get('y', None)
            else:
                # simple array sin dict
                x = arr
                y = None

        # Variables
        html += "<h3>Variables</h3><ul>"
        if x is not None:
            html += f"<li><strong>{'Features (x)' if x.ndim==2 else 'Images (x)'}</strong>: shape {x.shape}</li>"
        if y is not None:
            html += f"<li><strong>Labels (y)</strong>: shape {y.shape}</li>"
        html += "</ul>"

        # Determinar tipo
        is_img = (x is not None and x.ndim == 4 and x.shape[-1] == 3) \
                 or (x is not None and x.ndim==3 and x.shape[2]==3)
        is_tab = (x is not None and x.ndim == 2)

        # Mostrar imágenes
        if is_img:
            html += "<h3>Image Samples (x)</h3><div style='display:flex;'>"
            count = x.shape[0] if x.ndim==4 else 1
            for i in range(min(5, count)):
                img_arr = x[i] if x.ndim==4 else x
                html += array_to_img_tag(img_arr)
            html += "</div>"

        # Mostrar tabla de features
        if is_tab:
            html += "<h3>Feature Table (x)</h3>"
            html += "<table border='1' style='border-collapse:collapse;'>"
            html += "<thead><tr>" + "".join(f"<th>F{i}</th>" for i in range(min(10, x.shape[1]))) + "</tr></thead><tbody>"
            for row in x[:5]:
                html += "<tr>" + "".join(f"<td>{val:.3f}</td>" for val in row[:10]) + "</tr>"
            html += "</tbody></table>"

        # Mostrar labels
        if y is not None:
            if y.ndim == 2:
                html += "<h3>Label Samples (y)</h3>"
                html += "<table border='1' style='border-collapse:collapse;'>"
                # cabecera
                html += "<thead><tr>" + "".join(f"<th>C{i}</th>" for i in range(y.shape[1])) + "</tr></thead>"
                html += "<tbody>"
                for row in y[:5]:
                    html += "<tr>" + "".join(f"<td>{val:.1f}</td>" for val in row) + "</tr>"
                html += "</tbody></table>"
            else:
                html += f"<h3>Labels Array</h3><pre>{y.tolist()[:10]}</pre>"

        return {"html": html}

    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    file = sys.argv[1] if len(sys.argv)>1 else ''
    out = render_preview(file)
    print(json.dumps(out))
