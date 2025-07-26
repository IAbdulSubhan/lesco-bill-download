from flask import Flask, render_template, request
from bill_downloader import download_bill
import time
import requests
import os
from dotenv import load_dotenv


load_dotenv()  # Load the .env file

app = Flask(__name__)

def notify_discord(message):
    webhook_url = os.getenv("DISCORD_WEBHOOK")
    if not webhook_url:
        print("Webhook URL is not set!")
        return
    payload = {"content": f"🚨 {message}"}
    requests.post(webhook_url, json=payload)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ref = request.form['ref_number']
        download_bill(ref)
        time.sleep(1)
        print("File downloaded Sucessfully......")
        return render_template('index.html', message="File downloaded successfully.")
    return render_template('index.html')
