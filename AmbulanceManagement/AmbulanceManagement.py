import sys
from bson import ObjectId
from pymongo import MongoClient
import pymongo;
from bson.json_util import dumps
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import redis

redis = redis.Redis(
host= 'localhost',
port= '6379')
redis.flushdb() #Use this to flush all data.


try:
    client = pymongo.MongoClient("mongodb+srv://teamblue:teamblue@cluster0.ezeqtyg.mongodb.net/?retryWrites=true&w=majority", connect=False)
    db = client["Hosp_management"]
    patient_coll = db["patients"]
    ambulace_coll = db["ambulances"]

    patients = patient_coll.find({"PhoneNumber":"17965983265"})

    for patient in patients:
        patient_id = patient["_id"]
        ambulance_data=ambulace_coll.find({"Status" : "True"})

        for ambulance in ambulance_data:
            redis.geoadd("Ambulance",[(float)(ambulance["lon"]),(float)(ambulance["lat"]),(str)(ambulance["_id"])])
            print(ambulance["AmbulanceNumber"] + " " + "Ambulace added")

        #Finding the nearest ambulance to the patient
        Ambulace_list = redis.georadius("Ambulance",(float)(patient["Longitude"]),(float)(patient["Latitude"]),5,"km","WITHDIST","ASC")
        ambulance_id = (str)(Ambulace_list[0][0])
        ambulance_id = ambulance_id[2:-1]
        print(ambulance_id)
        for ambulancelist in ambulance_data:
            print(ambulancelist["_id"])
            if ambulancelist["_id"] == ambulance_id:
                ambulance_number = ambulancelist["AmbulanceNumber"]
                print(ambulance_number + " is assigned to patient with phone number " + patient["Fname"] + " " + patient["Lname"] + "with phone number " + patient["PhoneNumber"] )

        #updating document in ambulance collection. Avaliabilty status from true to false 
        ambulance_query = { "_id": ObjectId(ambulance_id) }
        newvalues = { "$set": { "Status": "False" } }
        ambulace_coll.update_one(ambulance_query, newvalues)
        updated_ambulance = ambulace_coll.find_one({"_id": ObjectId(ambulance_id)})
        print("Updated ambulance data")
        print(updated_ambulance)

        #Ambulance co-ordinates updated in the patient collection
        patient_query = { "_id": ObjectId(patient_id) }
        newvalues = { "$set": { "ambulanceId": ambulance_id } }
        patient_coll.update_one(patient_query, newvalues)
        updated_patient = patient_coll.find_one({"_id": patient_id})
        print("Ambulance assigned to Patient")
        print(updated_patient)

       
except Exception as e:
    print(e)
