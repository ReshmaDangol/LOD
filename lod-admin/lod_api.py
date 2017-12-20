from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS, cross_origin

from common_functions import *
import numpy as np

from datetime import datetime 


import json
app = Flask(__name__)
CORS(app)  # allow cross domain access
api = Api(app)

userInputArr = []
parser = reqparse.RequestParser()
parser.add_argument('class')
parser.add_argument('s')
parser.add_argument('t')
parser.add_argument('b')
parser.add_argument('p')
parser.add_argument('limit')


# def list(data):
#     # result = []
#     # for document in data:
#     #     result.append(document)
#     # return result
#     return list(data)

def get_class():
    cursor_class = conn("class").order_by(index=get_r().desc(
        'count')).run()  # need to create index for count to use this
    nodes = list(cursor_class)
    return nodes

def get_class_group(userInputArr=''):  
    
    if(userInputArr == ''):
        cursor = conn("class").outer_join(
            conn("equivalentclass_group"),
            lambda left, right:
            left["class"] == right["class"]
        ).zip().run()
    else:
        cursor = conn("class").filter(lambda doc:
                                      get_r().expr(userInputArr)
                                      .contains(doc["class"])
                                      ).outer_join(
            conn("equivalentclass_group"),
            lambda left, right:
            left["class"] == right["class"]
        ).zip().run()

    result = []
    i = 0
    index = 0

    startTime= datetime.now() 
    for document in cursor:
        c = document["class"]
        document["id"] = index
        index +=1
        
        is_subclass = conn("subclass").filter(
            lambda class_: class_["subclass"] == c).count().run()
        document['subclass'] = 1 if is_subclass > 0 else 0

        is_equivalent = conn("equivalentclass").filter(
            lambda class_:
            class_["c1"].default('foo').eq(c).or_(
                class_["c2"].default('foo').eq(c)
            )
        ).run()

        for r in is_equivalent:
            document['equivalent'] = 1 if(r["c1"] in userInputArr and r["c2"] in userInputArr) else 0
             

        does_intersect = conn("intersection").filter(
            lambda class_:
            class_["c1"].default('foo').eq(c)
        ).run()
    
    
        intersection_arr = userInputArr
        for r in does_intersect:            
            if(r["c1"] in userInputArr and r["c2"] in userInputArr):   
                intersection_arr.append(r["c1"] + "~~~" + r["c2"])
                intersection_arr.append(r["c2"] + "~~~" + r["c1"])
                # intersection_arr.append(r["c2"])             
                # print(r)
                result.append(
                    {
                        "class": r["c1"] + "~~~" + r["c2"],
                        "count":	0,
                        "equivalent":	0,
                        "group":	"nogroup_"+ str(i)+"_intersect",
                        "id":	str(index)+"_intersect",
                        "name":	"",
                        "subclass":	0,
                        "intersect" :1
                    }
                )
 
        try:
            x = document['group']
        except:
            document['group'] = "nogroup_" + str(i)
            i += 1
        # print(document['group'])
        result.append(document)
    timeElapsed=datetime.now()-startTime 
    print('Nodes Time elpased (hh:mm:ss.ms) {}'.format(timeElapsed))  
    

    
    if(userInputArr == ''):
        links = conn("graph_data").run() #remove redundancy
        len_ = conn("graph_data").count().run()
    else:
        filter_arr = intersection_arr
        # output = set()
        # for x in intersection_arr:
        #     output.add(x)
        # new_arr = list(output)
        # filter_arr = userInputArr
        # for i in range(-1, len(new_arr) - 2):            
        #     # print(i)
        #     for j in range(i+1, len(new_arr)-1):
        #         i+=1
        #         i+=1
        #         # print(j)
        #         filter_arr.append(new_arr[i]+"~~~"+new_arr[j])
        #         filter_arr.append(new_arr[j]+"~~~"+new_arr[i])
        
        count__ = len(filter_arr)
        print(count__)
        startTime= datetime.now() 
        links = conn("graph_data").filter(
            lambda doc:
                get_r().expr(filter_arr)
                .contains(doc["source"]).and_( 
                get_r().expr(filter_arr)
                .contains(doc["target"])
                )
        ).run()

        timeElapsed=datetime.now()-startTime 
        print('Links list Time elpased (hh:mm:ss.ms) {}'.format(timeElapsed))  
    
  
    link_arr = list(links)
    len_ = len(link_arr)
    print(len_)
    
    startTime= datetime.now() 
    i=0
    # link_arr = return_array(links, len_)
    for node in result:
        for j in range(0, len_):
            link = link_arr[j]   
            # print(node["class"])  
            if(link["source"] == node["class"]):
                link["source"] = i
            if(link["target"] == node["class"]):
                link["target"] = i
        i+=1

    timeElapsed=datetime.now()-startTime 
    print('Links list Time elpased (hh:mm:ss.ms) {}'.format(timeElapsed))  
    
    json_data = {"nodes":result,"links":np.array(link_arr).tolist()}

    return json_data


# def get_properties():
#     cursor = conn("class").inner_join(
#             conn("property"),
#             lambda left, right:
#                 left["class"] == right["c1"]
#         ).zip().run()
#     return list(cursor)

def get_property(s,t,b,l):
    
    # cursor1 = list(conn("property").order_by(index=get_r().desc('count')).filter({"c1":s, "c2": t}).outer_join(
    #     conn("inverse_property"),
    #     lambda left, right:
    #         (left["p"].eq(right["p"])) #.and_(left["p"].ne(right["p2"]))
    # ).zip().limit(int(l)).run())

    cursor1 = list(conn("graph_data_property_temp2").order_by(index=get_r().desc('count')).filter(
        {"c1":s, "c2": t}
        ).limit(int(l)).without('id').run())
    
    print(s)
    print(t)
    print(cursor1)
    if(int(b) == 1):
        cursor2 = list(conn("graph_data_property_temp2").order_by(index=get_r().desc('count')).filter(
        {"c1":t, "c2": s}
        ).limit(int(l)).without('id').run())
        # cursor2 = list(conn("property").order_by(index=get_r().desc('count')).filter({"c1":t, "c2": s}).outer_join(
        # conn("inverse_property"),
        # lambda left, right:
        #     (left["p"].eq(right["p"])) #.and_(left["p"].ne(right["p2"]))
        # ).zip().limit(int(l)).run())

        property_list = cursor1+cursor2
    else:
        property_list = cursor1  
    
    print(property_list)
          
    x = []
    for p in property_list:
        x.append(p["p"])
    
    for p in property_list:
        try:        
            for i in p["inverse"]:
                if(i["p"] in x):
                    print(i["p"])
                    i["show"] = 1
                    # i.append({"show":1})
        except:
            pass
    return property_list

def _get_property(s,t,b,l):
    
    cursor1 = conn("property").order_by(index=get_r().desc('count')).filter({"c1":s, "c2": t}).outer_join(
            conn("inverse_property"),
            lambda left, right:
            (left["p"].eq(right["p1"])).or_(left["p"].eq(right["p2"]))
        ).zip().limit(int(l)).run()
    # return list(cursor)

    # cursor1 = conn("property").order_by(index=get_r().desc('count')).filter({"c1":s, "c2": t}).limit(int(l)).run()
    # print(int(b))
    if(int(b) == 1):
        cursor2 = conn("property").order_by(index=get_r().desc('count')).filter({"c1":t, "c2": s}).outer_join(
            conn("inverse_property"),
            lambda left, right:
            (left["p"].eq(right["p1"])).or_(left["p"].eq(right["p2"]))
        ).zip().limit(int(l)).run()
        # cursor2 = conn("property").order_by(index=get_r().desc('count')).filter({"c1":t, "c2": s}).limit(int(l)).run()
        return list(cursor1)+list(cursor2)
    else:
        return list(cursor1)

def query_subject(s):
    rows = conn("property").filter({"c1":s})["p"].distinct().run()
    p = "1"
    for row in rows:
        p += """ || ?p =<"""+ row +""">"""

    query = """
        SELECT * 
        WHERE {
            ?s a <"""+ s +"""> .
            ?s ?p ?o .
            FILTER ("""+ p +""")
        }
        limit 200
    """
    result = execute_query(query)
    return result


def sparql_query(s,p,o):
    sparql_endpoint()
    if(p == '') and (o == ''):
        result = query_subject(s)
    return result

class ClassList(Resource):
    def get(self):
        return get_class()


class ClassWithDetail(Resource):
    def get(self):
        # return {'nodes': get_class_group(), 'links': get_class_links()}
        return get_class_group()
    def post(self):
        args = parser.parse_args()
        args = json.loads(args['class'])
        # return {'nodes': get_class_group(args), 'links': get_class_links(args)}
        return get_class_group(args)

class AddNode(Resource):
    def get(self):
        return 1

    def post(self):
        args = parser.parse_args()
        args = json.loads(args['class'])
        return args, 201

class Property(Resource):
    def post(self):
        args = parser.parse_args()
        return get_property(args['s'].strip(), args['t'].strip(), args['b'].strip(), args['limit'].strip())

class SPARQLQuery(Resource):
    def post(self):
        args = parser.parse_args()
        return {"data":sparql_query(args['s'], args['p'], args['t'])}



api.add_resource(ClassList, '/classlist')
api.add_resource(ClassWithDetail, '/class')
api.add_resource(AddNode, '/addnode')
api.add_resource(Property, '/property')
api.add_resource(SPARQLQuery, '/query')
# api.add_resource(EquivalentClass,'/equivalentclass')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
