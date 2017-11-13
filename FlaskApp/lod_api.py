from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS, cross_origin

import common_functions as cf
import json
app = Flask(__name__)
CORS(app) #allow cross domain access
api = Api(app)

def get_json(data):
    result = []
    i=0;
    for document in data:        
        result.append(document)
    return result

# def get_class():
#     cursor_class = cf.conn("class").order_by(index=cf.get_r().desc('count')).run() # need to create index for count to use this
#     nodes = get_json(cursor_class)
#     return nodes

def get_class_group():
    cursor = cf.conn("class").outer_join(
            cf.conn("equivalentclass_group"),
           lambda left, right: 
                left["class"] == right["class"] 
        ).zip().run()
    result = []
    i=0
    for document in cursor:
        print document
        try:
            x = document['group']
        except:        
            document['group']="nogroup_" + str(i)
            i+=1         
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
        temp = {'nodes':get_class_group(), 'links':[]}
        return temp

# class EquivalentClass(Resource):
#     def get(self):
#         return get_class_group()

api.add_resource(ClassList, '/class')
# api.add_resource(Subclass,'/subclass')
# api.add_resource(EquivalentClass,'/equivalentclass')

if __name__ == '__main__':
    app.run(debug=True)