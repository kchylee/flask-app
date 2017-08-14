import logging
import os
from flask import Flask, render_template, request
from google.cloud import storage
from google.appengine.api import images
app = Flask(__name__)
from cv2
import numpy as np

CLOUD_STORAGE_BUCKET = os.environ['CLOUD_STORAGE_BUCKET']

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/submitted', methods=['POST'])
def submitted_form():
    name = request.form['name']
    email = request.form['email']
    site = request.form['site_url']
    comments = request.form['comments']
    return render_template(
        'submitted_form.html',
        name=name,
        email=email,
        site=site,
        comments=comments
    )

@app.route('/upload', methods=['POST'])
def upload():
    """Process the uploaded file and upload it to Google Cloud Storage."""
    uploaded_file = request.files.get('img')

    if not uploaded_file:
        return 'No file uploaded.', 400

    # Create a Cloud Storage client.
    gcs = storage.Client()

    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket('kchylee1')

    # Create a new blob and upload the file's content.
    blob = bucket.blob(uploaded_file.filename)

    blob.upload_from_string(
        uploaded_file.read(),
        content_type=uploaded_file.content_type
    )

    img = self.request.get(blob.public_url)
    img = images.resize(img, 32, 32)
    

    # The public URL can be used to directly access the uploaded file via HTTP.
    return blob.public_url