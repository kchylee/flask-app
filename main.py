import logging
import os
from flask import Flask, render_template, request
from google.cloud import storage
from google.appengine.api import images
app = Flask(__name__)
import cv2
import numpy as np
import urllib

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

    #Encodes image from url so it can be read by OpenCV
    resp = urllib.urlopen(blob.public_url)
    im = np.asarray(bytearray(resp.read()), dtype="uint8")
	im = cv2.imdecode(im, cv2.IMREAD_COLOR)

    im = images.resize(im, 32, 32)
    
    hsv_img = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

    #Red threshold
    red = np.uint8([[[0,0,255]]])
    red_hsv= cv2.cvtColor(red, cv2.COLOR_BGR2HSV)
    lower_red_hsv = np.array([[[np.subtract(red_hsv[0,0,0],100),100,100]]])
    upper_red_hsv = np.array([[[np.add(red_hsv[0,0,0],100),255,255]]])
    imgray_r = cv2.inRange(hsv_img, lower_red_hsv, upper_red_hsv)
    ret,thresh_r = cv2.threshold(imgray_r,127,255,cv2.THRESH_BINARY)

    #Green threshold
    green = np.uint8([[[0,255,0]]])
    green_hsv= cv2.cvtColor(green, cv2.COLOR_BGR2HSV)
    lower_green_hsv = np.array([[[np.subtract(green_hsv[0,0,0],100),100,100]]])
    upper_green_hsv = np.array([[[np.add(green_hsv[0,0,0],100),255,255]]])
    imgray_g = cv2.inRange(hsv_img, lower_green_hsv, upper_green_hsv)
    ret,thresh_g = cv2.threshold(imgray_g,127,255,cv2.THRESH_BINARY)

    #Blue threshold
    blue = np.uint8([[[255,0,0]]])
    blue_hsv= cv2.cvtColor(blue, cv2.COLOR_BGR2HSV)
    lower_blue_hsv = np.array([[[np.subtract(blue_hsv[0,0,0],100),100,100]]])
    upper_blue_hsv = np.array([[[np.add(blue_hsv[0,0,0],100),255,255]]])
    frame_threshed = cv2.inRange(hsv_img, lower_blue_hsv, upper_blue_hsv)
    imgray_b = frame_threshed
    ret,thresh_b = cv2.threshold(imgray_b,127,255,cv2.THRESH_BINARY)

    #Original threshold
    imgray_hsv = cv2.cvtColor(hsv_img, cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(imgray_hsv,127,255,cv2.THRESH_BINARY)

    #Subtracting thresholds
    thresh_subtracted = cv2.subtract(thresh,thresh_b, thresh_r, thresh_g)
    #thresh_subtracted = thresh - thresh_b - thresh_r - thresh_g

    #Adding thresholds
    thresh_added = cv2.add(thresh,thresh_b, thresh_r, thresh_g)
    #thresh_added = thresh + thresh_b + thresh_r + thresh_g

    #Defining contours and setting bounding box
    _, contours, hierarchy = cv2.findContours(thresh_added,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    areas = [cv2.contourArea(c) for c in contours]
    max_index = np.argmax(areas)
    cnt=contours[max_index]
    x,y,w,h = cv2.boundingRect(cnt)
    cv2.rectangle(im,(x,y),(x+w,y+h),(0,255,0),2)


    #Upload image with bounding box
    bounded_im = im

    if not bounded_im:
        return 'bounded_im upload error.', 400

    # Create a Cloud Storage client.
    gcs = storage.Client()

    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket('kchylee1')

    # Create a new blob and upload the file's content.
    blob_bound = bucket.blob(uploaded_file.filename + '_bound')

    blob_bound.upload_from_string(
        bounded_im.read(),
        content_type=bounded_im.content_type
    )

    # The public URL can be used to directly access the uploaded file via HTTP.
    return blob_bound.public_url