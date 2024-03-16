# app.py

import os
import random

import matplotlib.pyplot as plt
import numpy as np
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

def calculate_stats(df):
    stats = {
        'Mean': df.mean(),
        'Median': df.median(),
        'Standard Deviation': df.std(),
        'Minimum': df.min(),
        'Maximum': df.max(),
        'Missing Values': df.isnull().sum(),  # Eksik değerlerin sayısını hesapla
        'Total Values': df.shape[0]  # Toplam değerlerin sayısını hesapla
    }
    stats['Missing Percentage'] = (stats['Missing Values'] / stats['Total Values']) * 100  # Eksik değerlerin yüzdesini hesapla
    return stats

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

@app.route('/select_graph_type', methods=['POST'])
def select_graph_type():
    filename = request.form.get('filename')
    selected_column = request.form['selected_column']
    
    # Seçilen sütunun veri tipini kontrol et
    df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    is_numeric = pd.api.types.is_numeric_dtype(df[selected_column])
    
    return render_template('select_graph_type.html', selected_column=selected_column, filename=filename, is_numeric=is_numeric)

@app.route('/visualize', methods=['POST'])
def visualize():
    filename = request.form.get('filename')
    selected_column = request.form['selected_column']
    graph_type = request.form.get('graph_type')  # Kullanıcının seçtiği grafik türü

    df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    try:
        if pd.api.types.is_numeric_dtype(df[selected_column]):
            if graph_type == 'histogram':
                plt.figure(figsize=(10, 6))
                n, bins, patches = plt.hist(df[selected_column], color=random.choice(['red', 'blue', 'green', 'yellow', 'orange', 'purple']), edgecolor='black', alpha=0.7, density=True)
                bin_centers = 0.5 * (bins[:-1] + bins[1:])
                plt.plot(bin_centers, n, '-o', color='black')
                plt.title(f"{selected_column} Histogramı")
                plt.xlabel(selected_column)
                plt.ylabel("Yoğunluk")
                graph_filename = f"{selected_column}_histogram.png"
            elif graph_type == 'boxplot':
                plt.figure(figsize=(10, 6))
                boxprops = dict(color='blue', linewidth=2)
                whiskerprops = dict(color='blue', linewidth=2)
                capprops = dict(color='blue', linewidth=2)
                medianprops = dict(color='red', linewidth=2)

                df.boxplot(column=selected_column, boxprops=boxprops, whiskerprops=whiskerprops, capprops=capprops, medianprops=medianprops, showmeans=True)
                plt.title(f"{selected_column} Kutu Grafiği")
                plt.ylabel(selected_column)
                plt.xticks(rotation=45)  # X eksenindeki sütun adlarını 45 derece döndürme
                plt.grid(True)  # Izgara ekleme
                plt.tight_layout()  # Grafiği düzenleme
                graph_filename = f"{selected_column}_boxplot.png"
            elif graph_type == 'scatter':
                # Örnek scatter plot oluşturmak için:
                plt.figure(figsize=(10, 6))
                plt.scatter(df.index, df[selected_column])
                plt.title(f"{selected_column} Dağılım Grafiği")
                plt.xlabel("Index")
                plt.ylabel(selected_column)
                graph_filename = f"{selected_column}_scatter.png"
            else:
                return "Geçersiz grafik türü!"

            plt.savefig(os.path.join(app.config['STATIC_FOLDER'], graph_filename))
            plt.close()

            # İstatistiksel özetleri ve eksik değerleri hesapla
            stats = calculate_stats(df[selected_column])
            missing_info = f"Toplam eksik değer sayısı: {stats['Missing Values']}, Eksik değer yüzdesi: {stats['Missing Percentage']:.2f}%"

            return render_template('histograms.html', graph_type=graph_type, histogram=graph_filename, selected_column=selected_column, stats=stats, missing_info=missing_info)
        elif pd.api.types.is_datetime64_any_dtype(df[selected_column]):
            # Zaman verileri için trend grafiği oluştur
            # (Burada grafik türü seçeneği verilmediği için varsayılan olarak trend grafiği kullanıldı)
            df[selected_column] = pd.to_datetime(df[selected_column])
            df.set_index(selected_column, inplace=True)
            plt.figure(figsize=(10, 6))
            df[selected_column].plot(color=random.choice(['red', 'blue', 'green', 'yellow', 'orange', 'purple']))
            plt.title(f"{selected_column} Trend Grafiği")
            plt.xlabel("Tarih")
            plt.ylabel(selected_column)
            graph_filename = f"{selected_column}_trend.png"
            plt.savefig(os.path.join(app.config['STATIC_FOLDER'], graph_filename))
            plt.close()

            # İstatistiksel özetleri hesapla
            stats = calculate_stats(df[selected_column])
            missing_info = f"Toplam eksik değer sayısı: {stats['Missing Values']}, Eksik değer yüzdesi: {stats['Missing Percentage']:.2f}%"

            return render_template('trend.html', graph_type=graph_type, trend=graph_filename, selected_column=selected_column, stats=stats, missing_info=missing_info)
        else:
            # Kategorik veri tipini kontrol et
            if df[selected_column].dtype == 'object':
                if graph_type == 'bar':
                    plt.figure(figsize=(10, 6))
                    df[selected_column].value_counts().plot(kind='bar', color=random.choice(['red', 'blue', 'green', 'yellow', 'orange', 'purple']))
                    plt.title(f"{selected_column} Bar Grafiği")
                    plt.xlabel(selected_column)
                    plt.ylabel("Frekans")
                    graph_filename = f"{selected_column}_bar.png"
                elif graph_type == 'pie':
                    plt.figure(figsize=(10, 6))
                    df[selected_column].value_counts().plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=random.choices(['red', 'blue', 'green', 'yellow', 'orange', 'purple'], k=len(df[selected_column].unique())))
                    plt.title(f"{selected_column} Pasta Grafiği")
                    plt.ylabel("")
                    graph_filename = f"{selected_column}_pie.png"
                else:
                    return "Geçersiz grafik türü!"
                
                plt.savefig(os.path.join(app.config['STATIC_FOLDER'], graph_filename))
                plt.close()

                # İstatistiksel özetleri hesapla
                stats = calculate_stats(df[selected_column])
                missing_info = f"Toplam eksik değer sayısı: {stats['Missing Values']}, Eksik değer yüzdesi: {stats['Missing Percentage']:.2f}%"

                return render_template('categorical.html', graph_type=graph_type, chart=graph_filename, selected_column=selected_column, stats=stats, missing_info=missing_info)
            else:
                return f"{selected_column} sütunu kategorik değil!"
    except KeyError:
        return f"{selected_column} sütunu mevcut değil!"

if __name__ == '__main__':
    app.run(debug=True)
