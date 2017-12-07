import json
import pdb
from flask import Flask, request, jsonify, make_response, g
from pymongo import MongoClient, ReturnDocument
from bson import Binary, Code
from bson.json_util import dumps
from flask_restful import Resource, Api


import bcrypt



app = Flask(__name__)
mongo = MongoClient('mongodb://motokosson:ghost@ds125906.mlab.com:25906/trip_planner_production')
app.db = mongo.trip_planner_production
api = Api(app)

app.bcrypt_rounds = 12




def validate_auth(user, password):
    # auth_info = request.authorization
    #
    # #username
    # username = auth_info.username
    # # pdb.set_trace()
    # #password
    # password = auth_info.password

    user_collection = app.db.users
    user = user_collection.find_one({'username': user})

    # pdb.set_trace()
    if user is None:
        return False
    else:
        # check if the hash we generate based on auth matches stored hash
        encodedPassword = password.encode('utf-8')
        if bcrypt.hashpw(encodedPassword, user['password']) == user['password']:
            g.setdefault('user', user)
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

        # hashed = hashed.decode()
        new_user['password'] = hashed
        # json_body['password'] = hashed
        users_collection = app.db.users
        users_collection.insert_one(new_user)


        # # Find user by email
        # database_user = users_collection.find_one({'email': username})

        # # # Encode password
        # jsonEncodedPassword = request.json['password'].encode('utf-8')


        # result = users_collection.insert_one(username)
        user = users_collection.find_one({"username": username})
        return user

    @authenticated_request
    def get(self):
        users_collection = app.db.users
        auth_info = request.authorization.username

        database_user = users_collection.find_one({'username': username})
        #username
        return database_user

        #password
        # password = auth_info.password
        #
        # users_collection = app.db.users
        # # Find user by email
        # database_user = users_collection.find_one({'username': username})
        #
        # # Encode password
        # jsonEncodedPassword = password.encode('utf-8')
        #
        # ## Check if client password from login matches database password
        # # Method 1: Use hashpw to compare passwords
        # if bcrypt.hashpw(jsonEncodedPassword, database_user['password']) == database_user['password']:
        #     ## Let them in
        #     return ("You have access {}".format(database_user['username']))
        # else:
        #     ## Tell user they have invalid credentials
        #     return ("Sorry, your credentials are incorrect")

        # Method 2: Use checkpw
        # if bcrypt.checkpw(jsonEncodedPassword, bcrypt.gensalt(app.bcrypt_rounds)) == True:
        #     ## Let them in
        #     return ("Access granted")
        # else:
        #     ## Send 401 - Unauthorized
        #     return ("Sorry, Unauthorized access")



        ## Check if client password from login matches database password
        # Method 1: Use hashpw to compare passwords

        # if bcrypt.hashpw(jsonEncodedPassword, database_user['password']) == database_user['password']:
        #     ## Let them in
        #     print("in 1")
        # else:
        #     ## Tell user they have invalid credentials
        #     print("failed 1")
        #
        # # Method 2: Use checkpw
        # if bcrypt.checkpw(jsonEncodedPassword, bcrypt.gensalt(app.bcrypt_rounds)) == True:
        #     ## Let them in
        #     print("in 2")
        # else:
        #     ## Send 401 - Unauthorized
        #     print("failed 2")

    # def post(self):
    #     new_user = request.json
    #     users_collection = app.db.users
    #     result = users_collection.insert_one(new_user)
    #     user = users_collection.find_one({"_id": result.inserted_id})
    #     return user

    # def get(self):
    #     name = request.args.get('name', type=str)
    #     users_collection = app.db.users
    #     user = users_collection.find_one({"name": name})
    #
    #     if user is None:
    #         response = jsonify(data=[])
    #         response.status_code = 404
    #         return response
    #     else:
    #         return user

    def patch(self):
        name = request.args.get('name', type=str)
        favorite_food = request.args.get('favorite_food', type=str)
        new_favorite_food = request.args.get('new_favorite_food', type=str)
        users_collection = app.db.users
        # dic = users_collection.aggregate(
        #     [
        #         {
        #             '$project':
        #                 {
        #                     "number": {'$indexOfArray': ['$favorite_food', favorite_food]}
        #                 }
        #         }
        #     ])
        # pdb.set_trace()
        # user = users_collection.find_one_and_update(
        #     {"name": name},
        #     {"$set": {"favorite_food.{}".format(int(dic["number"])): new_favorite_food}},
        #     return_document=ReturnDocument.AFTER
        # )

        # foods = users_collection.find_one(favorite_food)
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
        userID = request.args.get('name')
        users_collection = app.db.users
        get_user = users_collection.find_one({"name": userID})
#        pdb.set_trace()
#        get_user['trips'] = new_trip
#        get_user.save()
        result = users_collection.update_one({"name": userID}, {"$push": {"trips": new_trip}})
        pdb.set_trace()
        return (result, 201, None)


    def get(self):
        # user = request.args.get('name')
        trip = request.args.get('destination')
        users_collection = app.db.users
        # trip_ = users_collection[trip]
        result = users_collection.find({"trips.destination": trip}, {"trips.$":1})
#        destination = users_collection.aggregate({"$match": {"trips.destination": trip}})

#        if trip in result:
#            destination = trip_[trip]
#            return destination

        return (result, 200, None)

    # def patch(self):
    #     user = request.args.get('name')


api.add_resource(Trips, '/trips')


if __name__ == '__main__':
    # Turn this on in debug mode to get detailled information about request related exceptions: http://flask.pocoo.org/docs/0.10/config/
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)
