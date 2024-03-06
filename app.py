import os
import random

import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "Dosya Bulunamadı!"
    
    file = request.files['file']

    if file.filename == '':
        return "Dosya Seçilmedi!"
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        columns = df.columns.tolist()

        return render_template('select_column.html', columns=columns, filename=filename)
    else:
        return "Yalnızca CSV dosyaları kabul edilmektedir!"

@app.route('/visualize', methods=['POST'])
def visualize():
    filename = request.form.get('filename')
    selected_column = request.form['selected_column']
    df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    try:
        # Histogram veya trend grafiği oluştur
        if pd.api.types.is_numeric_dtype(df[selected_column]):
            # Sayısal veriler için histogram
            plt.figure(figsize=(10, 6))
            plt.hist(df[selected_column], color=random.choice(['red', 'blue', 'green', 'yellow', 'orange', 'purple']), edgecolor='black', alpha=0.7)
            plt.title(f"{selected_column} Histogramı")
            plt.xlabel(selected_column)
            plt.ylabel("Frekans")
            histogram_filename = f"{selected_column}_histogram.png"
            plt.savefig(os.path.join(app.config['STATIC_FOLDER'], histogram_filename))
            plt.close()
            
            return render_template('histograms.html', histogram=histogram_filename)
        elif pd.api.types.is_datetime64_any_dtype(df[selected_column]):
            # Zaman verileri için trend grafiği
            df[selected_column] = pd.to_datetime(df[selected_column])
            df.set_index(selected_column, inplace=True)
            
            plt.figure(figsize=(10, 6))
            df[selected_column].plot(color=random.choice(['red', 'blue', 'green', 'yellow', 'orange', 'purple']))
            plt.title(f"{selected_column} Trend Grafiği")
            plt.xlabel("Tarih")
            plt.ylabel(selected_column)
            trend_filename = f"{selected_column}_trend.png"
            plt.savefig(os.path.join(app.config['STATIC_FOLDER'], trend_filename))
            plt.close()
            
            return render_template('trend.html', trend=trend_filename)
        else:
            return f"{selected_column} sütunu sayısal veya tarih verileri içermemektedir!"
    except KeyError:
        return f"{selected_column} sütunu mevcut değil!"

@app.route('/histograms')
def histograms():
    return render_template('histograms.html')

@app.route('/trend')
def trend():
    return render_template('trend.html')

if __name__ == '__main__':
    app.run(debug=True)
