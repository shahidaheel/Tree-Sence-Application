from collections import OrderedDict
import pickle
from datetime import datetime
import requests
from flask import Flask, jsonify, request, redirect,render_template,url_for
from flask import session
import cv2
from random import seed
from random import randint
import numpy as np
import datetime
from dbconnect import *
import tensorflow as tf
from keras.models import load_model
density_constant=0.011931675
IMG_SIZE = (256,256)

model = load_model('treesense.h5')
model.summary()
seed(101)
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
@app.route('/')
def home():
	return render_template('./index.html')
@app.route('/index')
def index():
	return render_template('./index.html')
@app.route('/login')
def login():
	return render_template('./login.html')

@app.route('/accountcreation')
def accountcreation():
	return render_template('./accountcreation.html')

@app.route('/newaccount', methods=["GET", "POST"])
def newaccount():
    username = request.form["name"]
    contact = request.form["email"]
    password = request.form["password"]
  
    sql='SELECT * FROM user WHERE email = "%s" ' % \
     (contact)
    print(sql)
    user=recoredselect(sql)
    print(user)
    if len(user)>0:
        return render_template('index.html', mess='User already exists with that Mobile number')
    inserquery('INSERT INTO user (name,  email,password) VALUES ("%s", "%s", "%s")'% \
     (username,  contact,password))
          
    return render_template("index.html")



@app.route('/loginverification', methods=["GET", "POST"])
def loginverification():
    uname = request.form["email"]
    password = request.form["password"]
    sql='SELECT * FROM user WHERE email = "%s" AND password = "%s"'  % \
         (uname, password)
    print(sql)
    user=recoredselect(sql)
    if len(user)>0:
        session['id']=user[0][0]
        session['name'] = user[0][1]
        session['uname'] = user[0][2]
        sessionName=user[0][1]
        return render_template("dashboard.html", key=sessionName)               
    else:
        return render_template("index.html", mess="Invalid Email Id and password")
    

@app.route('/predict')
def predict():
	return render_template('./predict.html')

@app.route('/res')
def res():
	return render_template('./result.html')

def show_detected_treecount(img_path):
    img = tf.io.read_file(img_path)
    img = tf.io.decode_jpeg(img)
    img = tf.image.convert_image_dtype(img, tf.float32)
    img = tf.image.resize(img, IMG_SIZE)
    input_array = tf.keras.preprocessing.image.img_to_array(img)
    input_array = tf.expand_dims(input_array, 0) 
    imgs_pred_single = model.predict(input_array)
    total_dens_pred_single = tf.reduce_sum(imgs_pred_single, axis=[1,2,3]).numpy()
    predicted_treecount_single=[int(count) for count in total_dens_pred_single*density_constant]
    return [predicted_treecount_single]


@app.route('/fileupload', methods=["GET", "POST"])
def fileupload():
    
    imageurl = request.files['fileurl']
    imageurl.save("TestingData/image/1.jpg")
    value = str(randint(0,90))+".jpg"
    img = cv2.imread("TestingData/image/1.jpg")

    cv2.imwrite("static/images/"+str(value), img)
    
    impath="static/images/"+str(value)
    
    result= show_detected_treecount(impath)
    return render_template('./result.html',val=value,res=result)
  
        
if __name__ == '__main__':
       
       app.run(debug=False)
