import logging
import os
from flask import Flask, request, current_app
from google.cloud import storage
app = Flask(__name__)
import boundingbox
import pylibmc

# Environment variables are defined in app.yaml.
MEMCACHE_SERVER = os.environ.get('MEMCACHE_SERVER', 'localhost:11211')
MEMCACHE_USERNAME = os.environ.get('MEMCACHE_USERNAME')
MEMCACHE_PASSWORD = os.environ.get('MEMCACHE_PASSWORD')
memcache_client = pylibmc.Client(
    [MEMCACHE_SERVER], binary=True,
    username=MEMCACHE_USERNAME, password=MEMCACHE_PASSWORD)
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

    #Caching bounded image URL
    image_with_box = boundingbox.box(blob.public_url, uploaded_file)
    if memcache_client.get("bound_image") == None:
        memcache_client.set("bound_image", image_with_box)
    else:
        memcache_client.prepend("bound_image", image_with_box + ",")    
    return image_with_box

@app.route('/getcache', methods=['GET'])
def getcache():
    return memcache_client.get("bound_image")