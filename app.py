from pyexpat import model
from flask import Flask, render_template,request,jsonify,url_for
import sqlite3
import pandas as pd
import numpy as np

from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import pickle

import sqlite3
import requests
import json

app = Flask(__name__)


conn = sqlite3.connect('Realty_Listings.db')
conn.commit()


@app.route("/")
def home():
    return render_template('landingpage.html')

@app.route("/model",methods=["GET","POST"])
def model_training():

    key = 'password'

    if request.method == "POST":
        name = request.form.get("fname")

        if name == key:
            with sqlite3.connect("Realty_Listings.db") as conn:

                df = pd.read_sql_query("SELECT * from Housing_Price", conn)
                X = df.drop('Price_10000', axis=1)
                y = df['Price_10000']
                rf = RandomForestRegressor(n_estimators = 200, random_state = 42)
                X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.1,random_state=42)
                #rf.fit(X, y) 
                rf.fit(X_train,y_train)
                pred = rf.predict(X_test)
                mse = mean_squared_error(pred,y_test)
                prediction = rf.predict(np.array([[6.57,4.09]]))
                predicts = ' $ '+str(int(prediction)*10000)
                msee = str(int(mse))

                # save model
            with open('model.pkl','wb') as f:
                pickle.dump(rf,f)

            return 'Model has been trained.'

        else:
            return 'ACCESS DENIED'

    return render_template('model.html')


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


