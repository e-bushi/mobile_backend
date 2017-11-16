import json
import pdb
from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient, ReturnDocument
from bson import Binary, Code
from bson.json_util import dumps
from flask_restful import Resource, Api

app = Flask(__name__)
mongo = MongoClient('localhost', 27017)
app.db = mongo.test_database
api = Api(app)


class Users(Resource):

    def post(self):
        new_user = request.json
        users_collection = app.db.users
        result = users_collection.insert_one(new_user)
        user = users_collection.find_one({"_id": result.inserted_id})
        return user

    def get(self):
        name = request.args.get('name', type=str)
        users_collection = app.db.users
        user = users_collection.find_one({"name": name})

        if user is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            return user

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
