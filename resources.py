import json
import pdb
from flask import Flask, request, jsonify, make_response, g
from pymongo import MongoClient, ReturnDocument
from bson import Binary, Code
from bson.json_util import dumps
from flask_restful import Resource, Api
import random
import time



import bcrypt



app = Flask(__name__)
mongo = MongoClient('mongodb://motokosson:ghost@ds125906.mlab.com:25906/trip_planner_production')
app.db = mongo.trip_planner_production
api = Api(app)

app.bcrypt_rounds = 12




def validate_auth(user, password):
    users_collection = app.db.users
    database_user = users_collection.find_one({"username": user})

    if database_user is None:
        return False
    else:
        # check if the hash we generate based on auth matches stored hash
        encodedPassword = password.encode('utf-8')

        if bcrypt.checkpw(encodedPassword, database_user['password']):
            # g.setdefault('user', user)
            return True
        else:
            return False

def authenticated_request(func):
    def wrapper(*args, **kwargs):
        auth = request.authorization

        if not auth or not validate_auth(auth.username, auth.password):
            return ({'error': 'Basic Auth Required.'}, 401, None)

        return func(*args, **kwargs)

    return wrapper



class Users(Resource):

    def post(self):
        new_user = request.json

        username = new_user['username']
        password = new_user['password']

        # Convert password to utf-8 string
        encodedPassword = password.encode('utf-8')

        hashed = bcrypt.hashpw(
            encodedPassword, bcrypt.gensalt(app.bcrypt_rounds)
        )

        new_user['password'] = hashed

        users_collection = app.db.users
        users_collection.insert_one(new_user)

        user = users_collection.find_one({"username": username})
        return user

    @authenticated_request
    def get(self):
        users_collection = app.db.users
        user = request.authorization.username

        database_user = users_collection.find_one({'username': user})

        return (database_user, 200, None)


    def patch(self):
        name = request.args.get('name', type=str)
        favorite_food = request.args.get('favorite_food', type=str)
        new_favorite_food = request.args.get('new_favorite_food', type=str)
        users_collection = app.db.users

        user = users_collection.find_one_and_update(
            {"name": name},
             {"$set": {"favorite_food.0": new_favorite_food}},
             return_document=ReturnDocument.AFTER
        )
        print(user)
        if user is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            return user


@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(dumps(data), code)
    resp.headers.extend(headers or {})
    return resp


api.add_resource(Users, '/users')


class Trips(Resource):

    def post(self):
        new_trip = request.json
        new_trip_ar = new_trip['trips'][0]
        userID = new_trip_ar['trip_creator']
        did_attend = new_trip_ar['hasAttended']
        trip_id = new_trip_ar['trip_id']
        
        #variable that stores the trips collection
        trips_collection = app.db.trips

        #insert new trip document into the trip collection
        trips_collection.insert_one(new_trip)


        return (validate_user, 201, None)


    def get(self):

        #Attains specific query parameters from user needed to fetch desired information
        user = request.headers['trip_creator']
        get_past_trips = request.headers['hasAttended']

        #container for trips collection
        trips_collection = app.db.trips

        #Retrieve all trips that have the designated creator and has a specific Boolean value of attendance
        #that the user designates
        if get_past_trips == '':
            #results in the retrieval of all trips for a given user
            users_trips = trips_collection.find({"trip_creator": user})
        else:
            users_trips = trips_collection.find({"trip_creator": user, "hasAttended": {"$eq": get_past_trips.lower()}})

        return (users_trips, 200, None)

    def patch(self):
        #json
        body = request.json
        userID = body['trip_creator']
        trip_destination = body['trip_destination']
        trip_creator_has_attended = body['hasAttended']
        trip_id = body['trip_id']
        trip_attendees = body['trip_attendees']


        #container for trips collection
        trips_collection = app.db.trips

        #container for users collection
        users_collection = app.db.users

        trip = trips_collection.find_one({"trip_creator": userID, "trip_destination": trip_destination, "trip_id": trip_id})


        #condition to check if document exists within the trip collection; if so, update the hasAttended value
        #if not insert a new document
        if trip is None:
            return ({'error': 'Resource not found.'}, 404, None)
        else:
            trips_collection.update_one({"trip_id": trip_id}, {"$set": {"hasAttended": trip_creator_has_attended}})

            # time.sleep(1.0)
            # new_trip = trips_collection.find_one({"trip_creator": userID, "trip_destination": trip_destination, "trip_id": trip_id})

            return ({'Success': 'Trip Resource has been updated'}, 202, None)




api.add_resource(Trips, '/trips')


if __name__ == '__main__':
    # Turn this on in debug mode to get detailled information about request related exceptions: http://flask.pocoo.org/docs/0.10/config/
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)
