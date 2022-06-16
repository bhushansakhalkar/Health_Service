from array import array
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import redis
import pymongo
from bson.objectid import ObjectId
import time
# Create your views here.
def index(request):
    try:
        mongoClient = pymongo.MongoClient("mongodb+srv://teamblue:teamblue@cluster0.ezeqtyg.mongodb.net/?retryWrites=true&w=majority")
        mydb = mongoClient["Hosp_management"]
        mycol = mydb["patients"]
        mycol1 = mydb['ambulances']
        dat = []
        data = {}
        for x in mycol.find({ "ambulanceId": {"$ne": "none"}}):
            
            data = {"name":x['Fname']+" "+x['Lname'],"lat":x['Latitude'],"lng":x['Longitude'],"ambulanceId":x['ambulanceId']}
            objInstance = ObjectId(x['ambulanceId'])
            for y in mycol1.find({'_id':objInstance}):
                data1 = {"ambulanceLat":y['lat'],"ambulanceLon":y['lon']}
                data.update(data1)
            dat.append(data)
    except Exception as e:
        print(e)
    return render(request,"maps.html",{"data":"Yes","patients":dat})

def redisConnection(request):
    client = redis.Redis(host='localhost',port=6379,db=0)
    if request.method == "GET":
        name = request.GET['name']
        print(name)
        if name == 'ambulance':
            ambu1 = client.geodist("ambulance1","ambulance","patient","km")
        else:
            ambu1 = client.geodist("ambulance1","ambulance","hospital","km")
        return HttpResponse(ambu1)
    else:
        lat = request.POST['lat']
        lng = request.POST['lng']
        dat = lat,lng,"ambulance"
        try:
            client.geoadd("ambulance1",dat)
            data="Done"
        except Exception as e:
            data = e
        return HttpResponse(data)

def AddPatient(request):
    client = redis.Redis(host='localhost',port=6379,db=0)
    try:
        lat = request.POST['lat']
        lng = request.POST['lng']
        dat = lat,lng,"patient"
        client.geoadd("ambulance1",dat)
        data="Done"
    except Exception as e:
            data = e
    return HttpResponse(data)


def findHospitals(request):
    client = redis.Redis(host="localhost",port=6379,db=0)
    try:
        lat = request.POST['lat']
        lng = request.POST['lng']
        data = ""
        no = 0
        res = client.georadius("hospitals",lng,lat,5,"km",withdist=True,withcoord=True)
        for x in res:
            for y in x:
                 data = data + str(y)+"\n"
                
        return HttpResponse(data)
    except Exception as e:
        print(e)


def addHospitals(request):
    client = redis.Redis(host='localhost',port=6379,db=0)
    try:
        lat = request.POST['lat']
        lng = request.POST['lng']
        dat = lat,lng,"hospital"
        client.geoadd("ambulance1",dat)
        data="Done"
    except Exception as e:
            data = e
    return HttpResponse(data)

def updatePatient(request):
    try:
        fname = request.POST['patientFName']
        lname = request.POST['patientLName']
        ambulanceId = request.POST['ambulanceId']
        lat = request.POST['lat']
        lng = request.POST['lng']
        mongoClient = pymongo.MongoClient("mongodb+srv://teamblue:teamblue@cluster0.ezeqtyg.mongodb.net/?retryWrites=true&w=majority")
        mydb = mongoClient["Hosp_management"]
        mycol = mydb["patients"]
        mycol1 = mydb['ambulances']
        myquery = { "_id": ObjectId(ambulanceId) }
        newvalues = { "$set": { "Status": "True","lat":lat,"lon":lng } }
        myquery1 = { "Fname": fname }
        newvalues1 = { "$set": { "ambulanceId": "None","Latitude":lat,"Longitude":lng } }
        try:
            x = mycol1.update_one(myquery, newvalues)
            y = mycol.update_one(myquery1,newvalues1)
            print(x)
            print(y)
        except Exception as e:
            print(e)
        return HttpResponse("Done")
    except Exception as e:
        print(e)
        return HttpResponse("Not DOne")