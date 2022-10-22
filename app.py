from pyexpat import model
from flask import Flask, render_template,request,jsonify,url_for
import pandas as pd
import numpy as np

from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import pickle

import requests
import json

app = Flask(__name__)

# from google.cloud import firestore
# from google.cloud import bigquery

#client = bigquery.Client()

#db = firestore.Client() #for database


@app.route("/")
def home():
    return render_template('landingpage.html')

@app.route("/register",methods=["GET","POST"])
def model_training():

    # if request.method == "POST":
    #     fname = request.form.get("fname")
    #     lname = request.form.get("lname")
    #     uname = request.form.get("uname")

    #     doc_ref = db.collection(u'users').document(uname)
    #     doc_ref.set({
    #         u'uname' : uname,
    #         u'first': fname,
    #         u'last': lname
    #     })

    return render_template('register.html')


@app.route("/predict",methods=["GET","POST"])
def predict_entries():

    if request.method == "POST":
       
        RM =  request.form.get("rm")
        DIS = request.form.get("dis")
        
        # load model
        with open('model.pkl', 'rb') as f:
            model = pickle.load(f)

        prediction = model.predict(np.array([[RM,DIS]]))
        #predicts = ' $ '+str(int(prediction)*10000)
        predicts = ' $ '+ str(int((round(float(prediction),5))*10000))
        prediction = float(prediction)
        
        with sqlite3.connect("Realty_Listings.db") as conn:
            c = conn.cursor()
            sql = ("INSERT INTO Housing_Price (RM, DIS, Price_10000)" "VALUES (?, ?, ?)")
            val = (RM, DIS, prediction)
            c.execute(sql, val)
            
        #return predicts
        return render_template("output.html",RM=RM,DIS=DIS,predicts=predicts)
    
    return render_template('predict.html')


app.run(debug=True)


