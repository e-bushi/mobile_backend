import json
import pdb
from flask import Flask, request
from pymongo import MongoClient
from bson import Binary, Code
from bson.json_util import dumps

app = Flask(__name__)
mongo = MongoClient('localhost', 27017)
app.db = mongo.local

@app.route('/')
def hello_world():
    return 'Hello Earth!'

@app.route('/person')
def person_route():
    person = {"name": "Chris", 'age': 26}
    json_person = json.dumps(person)
#    pdb.set_trace()

    return (json_person, 200, None)

@app.route('/my_page')
def text():
    return "This is my page you should actually appreciate this"

#@app.route('/pets')
#def favorite_pets():
#    pets = [{'name': 'Mango', 'color':'Mango'},{'name': 'mizu', 'color':'indigo'}]
#    json_pets = json.dumps(pets)
#
#    return (json_pets, 200, None)

@app.route('/users',methods = ['POST', 'GET'])
def get_or_add_users():
    if request.method == 'POST':
        users_dict = request.json
        users_collection = app.db.users
        
        result = users_collection.insert_one(users_dict)
        
        json_result = dumps(users_dict)
        
        return (json_result, 201, None)
    elif request.method == 'GET':
        name_ = request.args.get('name')

        users_collection = app.db.users
        collection = [users_collection.find()]
        
#        result_array = []
#        result_array.append(collection)

        json_result = dumps(collection)
    
    return (json_result, 200, None)


@app.route('/courses', methods = ['POST', 'GET'])
def get_or_add_courses():
    if request.method == 'POST':
        courses_dict = request.json
        print(courses_dict)
        courses_collection = app.db.courses

        result = courses_collection.insert_one(courses_dict)

    elif request.method == 'GET':
        courses_collection = app.db.courses
        collection = courses_collection.find()

        json_result = dumps(collection)

        return (json_result, 200, None)

@app.route('/courses', methods = 'GET')
def count_courses():


@app.route('/carts', methods = ['POST'])
def create_cart():
    carts_dict = request.json
    carts_collection = app.db.carts

    result = carts_collection.insert_one(carts_dict)

    json_result = dumps(carts_dict)

    return (json_result, 201, None)




@app.route('/carts', methods = ['PATCH'])
def update_cart():
    cart_dict = request.json


    cart_collection = app.db.carts
    result = cart_collection.update_one({'quantity': 4}, {'$inc': {'quantity': 10}})

    json_result = dumps(cart_dict)

    return (json_result, 202, None)


if __name__ == '__main__':
    app.run(debug = True)
