from flask import Flask, render_template, request
from bill_downloader import download_bill
import time

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ref = request.form['ref_number']
        download_bill(ref)
        time.sleep(1)
        print("File downloaded Sucessfully......")
        return render_template('index.html', message="File downloaded successfully.")
    return render_template('index.html')
