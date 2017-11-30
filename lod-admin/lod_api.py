from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS, cross_origin

from . import common_functions as cf
import json
app = Flask(__name__)
CORS(app)  # allow cross domain access
api = Api(app)

userInputArr = []
parser = reqparse.RequestParser()
parser.add_argument('class')

def get_json(data):
    result = []
    for document in data:
        result.append(document)
    return result


def get_class():
    cursor_class = cf.conn("class").order_by(index=cf.get_r().desc(
        'count')).run()  # need to create index for count to use this
    nodes = get_json(cursor_class)
    return nodes

def get_class1():
    cursor_class = cf.conn('class').filter(lambda doc:
    cf.get_r().expr(["http://www.w3.org/2006/time#Interval","http://purl.org/NET/c4dm/event.owl#Event"])
        .contains(doc["class"])
    ) .run()
    nodes = get_json(cursor_class)
    return nodes
  


def get_class_group(userInputArr=''):
    if(userInputArr == ''):
        cursor = cf.conn("class").outer_join(
                        cf.conn("equivalentclass_group"),
                        lambda left, right:
                        left["class"] == right["class"]
                    ).zip().run()
    else:
        cursor = cf.conn("class").filter(lambda doc:
                cf.get_r().expr(userInputArr)
                    .contains(doc["class"])
                ).outer_join(
                    cf.conn("equivalentclass_group"),
                    lambda left, right:
                    left["class"] == right["class"]
                ).zip().run()

    result = []
    i = 0
    for document in cursor:
        print(document)
        try:
            x = document['group']
        except:
            document['group'] = "nogroup_" + str(i)
            i += 1
        result.append(document)
    return result


# def get_properties():
#     cursor = cf.conn("class").inner_join(
#             cf.conn("property"),
#             lambda left, right:
#                 left["class"] == right["c1"]
#         ).zip().run()
#     return get_json(cursor)

class ClassList(Resource):
    def get(self):
        return get_class()


class ClassWithDetail(Resource):
    def get(self):
        return {'nodes': get_class_group(), 'links': []}
    
    def post(self):
        args = parser.parse_args()
        args = json.loads(args['class']) 
        return {'nodes': get_class_group(args), 'links': []}

class AddNode(Resource):
    def get(self):
        return 1

    def post(self):
        args = parser.parse_args()
        args = json.loads(args['class']) 
        return  args, 201


api.add_resource(ClassList, '/classlist')
api.add_resource(ClassWithDetail, '/class')
api.add_resource(AddNode, '/addnode')
# api.add_resource(EquivalentClass,'/equivalentclass')

if __name__ == '__main__':
    app.run(debug=True)
