import logging
import os
from flask import Flask, render_template, request
from google.cloud import storage
app = Flask(__name__)
# import boundingbox
import numpy as np 
import cv2
import urllib


CLOUD_STORAGE_BUCKET = 'kchylee1'
# os.environ['CLOUD_STORAGE_BUCKET']

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Process the uploaded file and upload it to Google Cloud Storage."""
    uploaded_file = request.files.get('img')
    print type(uploaded_file)
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

    #Encodes image from url so it can be read by OpenCV
    resp = urllib.urlopen(blob.public_url)
    im = np.asarray(bytearray(resp.read()), dtype="uint8")
    im = cv2.imdecode(im, cv2.IMREAD_COLOR)
    im = cv2.resize(im, None, fx=32, fy=32)
    hsv_img = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

    #Red threshold
    red = np.uint8([[[0, 0, 255]]])
    red_hsv = cv2.cvtColor(red, cv2.COLOR_BGR2HSV)
    lower_red_hsv = np.array([[[np.subtract(red_hsv[0, 0, 0], 100), 100, 100]]])
    upper_red_hsv = np.array([[[np.add(red_hsv[0, 0, 0], 100), 255, 255]]])
    imgray_r = cv2.inRange(hsv_img, lower_red_hsv, upper_red_hsv)
    ret, thresh_r = cv2.threshold(imgray_r, 127, 255, cv2.THRESH_BINARY)

    #Green threshold
    green = np.uint8([[[0, 255, 0]]])
    green_hsv = cv2.cvtColor(green, cv2.COLOR_BGR2HSV)
    lower_green_hsv = np.array([[[np.subtract(green_hsv[0, 0, 0], 100), 100, 100]]])
    upper_green_hsv = np.array([[[np.add(green_hsv[0, 0, 0], 100), 255, 255]]])
    imgray_g = cv2.inRange(hsv_img, lower_green_hsv, upper_green_hsv)
    ret, thresh_g = cv2.threshold(imgray_g, 127, 255, cv2.THRESH_BINARY)

    #Blue threshold
    blue = np.uint8([[[255, 0, 0]]])
    blue_hsv = cv2.cvtColor(blue, cv2.COLOR_BGR2HSV)
    lower_blue_hsv = np.array([[[np.subtract(blue_hsv[0, 0, 0], 100), 100, 100]]])
    upper_blue_hsv = np.array([[[np.add(blue_hsv[0, 0, 0], 100), 255, 255]]])
    frame_threshed = cv2.inRange(hsv_img, lower_blue_hsv, upper_blue_hsv)
    imgray_b = frame_threshed
    ret, thresh_b = cv2.threshold(imgray_b, 127, 255, cv2.THRESH_BINARY)

    #Original threshold
    imgray_hsv = cv2.cvtColor(hsv_img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray_hsv, 127, 255, cv2.THRESH_BINARY)

    #Subtracting thresholds
    thresh_subtracted = cv2.subtract(thresh, thresh_b, thresh_r, thresh_g)

    #Adding thresholds
    thresh_added = cv2.add(thresh, thresh_b, thresh_r, thresh_g)

    #Defining contours and setting bounding box
    _, contours, hierarchy = cv2.findContours(thresh_added, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    areas = [cv2.contourArea(c) for c in contours]
    max_index = np.argmax(areas)
    cnt = contours[max_index]
    x, y, w, h = cv2.boundingRect(cnt)
    cv2.rectangle(im, (x, y), (x+w, y+h), (0, 255, 0), 2)

    #Upload image with bounding box
    
    bounded_im_name = uploaded_file.filename[:-4] + '_bound.png'
    bounded_im = cv2.imencode('.png', im)[1].tostring()
    print type(bounded_im)
    

    
    if not bounded_im:
        return 'bounded_im upload error.', 400

    # Create a Cloud Storage client.
    gcs = storage.Client()

    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket('kchylee1')

    # Create a new blob and upload the file's content.
    blob_bound = bucket.blob(bounded_im_name)
    
    blob_bound.upload_from_string(
        bounded_im
        # content_type=bounded_im.content_type
    )

    # The public URL can be used to directly access the uploaded file via HTTP
    return blob_bound.public_url