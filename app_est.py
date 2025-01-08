from flask import Flask, request, render_template, redirect, url_for
import os
import pandas as pd
import plotly.express as px

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '../uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No se subió un archivo", 400

    file = request.files['file']
    if file.filename == '':
        return "No se seleccionó ningún archivo", 400

    if not file.filename.endswith('.csv'):
        return "Solo se permiten archivos CSV", 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    return redirect(url_for('dashboard', filename=file.filename))

@app.route('/dashboard/<filename>')
def dashboard(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return "Archivo no encontrado", 404

    try:
        df = pd.read_csv(filepath)
        table_html = df.to_html(classes='table table-striped', index=False)

        # Generar gráficos interactivos con Plotly
        histogram = px.histogram(df, x=df.columns[0]).to_html(full_html=False)
        scatter = px.scatter(df, x=df.columns[0], y=df.columns[1]).to_html(full_html=False)
        boxplot = px.box(df, y=df.columns[1]).to_html(full_html=False)
        heatmap = (
            px.imshow(df.corr(), text_auto=True).to_html(full_html=False)
            if not df.select_dtypes(include=['number']).empty else "<p>No hay suficientes datos numéricos para un heatmap.</p>"
        )

        return render_template(
            'dashboard.html',
            table_html=table_html,
            graphs={
                'histogram': histogram,
                'scatter': scatter,
                'boxplot': boxplot,
                'heatmap': heatmap,
            }
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)


