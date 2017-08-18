import logging
import os
from flask import Flask, request, current_app
from google.cloud import storage
app = Flask(__name__)
import boundingbox

CLOUD_STORAGE_BUCKET = 'kchylee1'
# os.environ['CLOUD_STORAGE_BUCKET']

@app.route('/')
def index():
    return current_app.send_static_file('index.html')

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

    return boundingbox.box(blob.public_url, uploaded_file)
