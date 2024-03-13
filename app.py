import os
import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from scipy import stats
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
        
        # İstatistiksel özet hesaplama
        stats_summary = df.describe().loc[['mean', 'std', 'min', '25%', '50%', '75%', 'max']]
        stats_summary = stats_summary.rename(index={'50%': 'median', '25%': 'Q1', '75%': 'Q3'})
        stats_summary = stats_summary.rename(index=lambda x: x.capitalize())
        
        return render_template('select_column.html', columns=columns, filename=filename, stats=stats_summary.to_dict())
    else:
        return "Yalnızca CSV dosyaları kabul edilmektedir!"

@app.route('/visualize', methods=['POST'])
def visualize():
    filename = request.form.get('filename')
    selected_column = request.form['selected_column']
    df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    try:
        # Eksik değer kontrolü
        missing_values = df[selected_column].isnull().sum()
        missing_info = f"{selected_column} sütununda {missing_values} eksik değer bulunmaktadır." if missing_values > 0 else f"{selected_column} sütununda eksik değer bulunmamaktadır."

        # İstatistiksel özet hesaplama
        stats_summary = df[selected_column].describe().loc[['mean', 'std', 'min', '25%', '50%', '75%', 'max']]
        stats_summary = stats_summary.rename(index={'50%': 'median', '25%': 'Q1', '75%': 'Q3'})
        stats_summary = stats_summary.rename(index=lambda x: x.capitalize())

        # Histogram veya trend grafiği oluştur
        if pd.api.types.is_numeric_dtype(df[selected_column]):
            # Sayısal veriler için histogram
            plt.figure(figsize=(10, 6))
            n, bins, patches = plt.hist(df[selected_column], color=random.choice(['red', 'blue', 'green', 'yellow', 'orange', 'purple']), edgecolor='black', alpha=0.7, density=True)
            
            # Normalleştirilmiş histogramı kullanarak bir çizgi çiz
            bin_centers = 0.5 * (bins[:-1] + bins[1:])
            plt.plot(bin_centers, n, '-o', color='black')
            
            plt.title(f"{selected_column} Histogramı")
            plt.xlabel(selected_column)
            plt.ylabel("Yoğunluk")
            histogram_filename = f"{selected_column}_histogram.png"
            plt.savefig(os.path.join(app.config['STATIC_FOLDER'], histogram_filename))
            plt.close()
            
            return render_template('histograms.html', histogram=histogram_filename, stats=stats_summary.to_dict(), missing_info=missing_info)
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
            
            return render_template('trend.html', trend=trend_filename, stats=stats_summary.to_dict(), missing_info=missing_info)
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
