import os

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
        # Dosyayı güvenli bir şekilde kaydet
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # CSV dosyasını oku ve sütun isimlerini al
        df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        columns = df.columns.tolist()

        # Görselleştirmek için sütunları içeren bir form göster
        return render_template('select_column.html', columns=columns, filename=filename)
    else:
        return "Yalnızca CSV dosyaları kabul edilmektedir!"


@app.route('/visualize', methods=['POST'])
def visualize():
    filename = request.form.get('filename')
    selected_column = request.form['selected_column']
    df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    try:
        # Seçilen sütunu histogram olarak göster
        plt.hist(df[selected_column])
        plt.title(f"{selected_column} Histogramı")
        plt.xlabel(selected_column)
        plt.ylabel("Frekans")
        histogram_filename = f"{selected_column}_histogram.png"
        plt.savefig(os.path.join(app.config['STATIC_FOLDER'], histogram_filename))
        plt.close()
        return render_template('histograms.html', histogram=histogram_filename)
    except KeyError:
        return f"{selected_column} sütunu mevcut değil!"


@app.route('/histograms')
def histograms():
    return render_template('histograms.html')

if __name__ == '__main__':
    app.run(debug=True)
