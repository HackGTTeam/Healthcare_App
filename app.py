from email.headerregistry import AddressHeader
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
import bcrypt
import requests
import json


app = Flask(__name__)

from google.cloud import firestore
from google.cloud import bigquery

client = bigquery.Client()

db = firestore.Client() #for database


@app.route("/")
def home():
    return render_template('landingpage.html')

@app.route("/register",methods=["GET","POST"])
def create_profile():

    if request.method == "POST":
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        sex = request.form.get("sex")
        dob = request.form.get("DOB")
        other = request.form.get("other")
        street = request.form.get("street")
        
        doc_ref = db.collection('users').document(email)
        doc = doc_ref.get()
        if doc.exists:
            return render_template('register.html') + "<p align = 'center'>Email already exists</p>"
        else:
            if password == password2:
                hashed = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt()) #encrypts the password

                doc_ref = db.collection(u'users').document(email)
                doc_ref.set({
                    u'email' : email,
                    u'first': fname,
                    u'last': lname,
                    u'password' : hashed,
                    u'sex' : sex,
                    u'dob': dob,
                    u'other': other,
                    u'street': street
                })

                return render_template('enter_symptoms.html')
            else:
                return render_template('register.html') + "<p align = 'center'>Passwords don't match</p>"

    return render_template('register.html')

@app.route("/enter_symptoms",methods=["GET","POST"])
def add_symptoms():
    if request.method == "POST":
        temp = request.form.getlist("symptoms")
        response = requests.get("http://api.endlessmedical.com/v1/dx/InitSession")
        id = response.json()['SessionID']

        value = "1"

        response = requests.post("http://api.endlessmedical.com/v1/dx/AcceptTermsOfUse?SessionID=" + id + "&passphrase=" + "I have read, understood and I accept and agree to comply with the Terms of Use of EndlessMedicalAPI and Endless Medical services. The Terms of Use are available on endlessmedical.com")

        for name in temp:
            response = requests.post("http://api.endlessmedical.com/v1/dx/UpdateFeature?SessionID="+id+"&name=" + name + "&value=" + value)

        response = requests.get("http://api.endlessmedical.com/v1/dx/Analyze?SessionID=" + id)

        diseases = response.json()['Diseases']

        output = ""
        query = ""
        if diseases == []:
            output = "<p>Healthy</p>"
            query = 'SELECT Title, URL FROM hackathon-366314.hackathon.clinicals WHERE Upper(Conditions) LIKE Upper("Healthy") LIMIT 5'

        #STATUS = "Available" AND
        
        else:

            query = 'SELECT Title, URL FROM hackathon-366314.hackathon.clinicals WHERE STATUS = "Available" '  #used to access GCP BigQuery to search clinicals dataset

            output = "<p align = 'center'>Possible Diseases: <br>"
            for d in diseases:
                for i in d.keys():
                    output += i  #adds disease to print in html page
                    output += "   ;    "
                    query += 'AND Upper(Conditions) LIKE Upper("%' + i + '%") '
            output += "</p>"

            query += "LIMIT 5"
        
        results = client.query(query)
            
        clinicals = "<p>Clinical Trials: <br> "

        for row in results:
            title = row['Title']
            url = row['URL']
            clinicals += title + " : " + url
            clinicals += "<br>"

        clinicals += "</p>"

        return render_template('enter_symptoms.html') + output + clinicals


    return render_template('enter_symptoms.html')


app.run(debug=True)


