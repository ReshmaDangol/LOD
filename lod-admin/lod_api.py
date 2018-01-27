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
parser.add_argument('s')  # subject
parser.add_argument('t')  # target, object
parser.add_argument('b')  # bidirection
parser.add_argument('p')  # property
parser.add_argument('limit')  # result limit
parser.add_argument('link_subclass')
parser.add_argument('link_intersection')
parser.add_argument('link_property')
parser.add_argument('p_filter')  # selected property
parser.add_argument('i')  # an instance of a class
parser.add_argument('database_name')

query_prefix = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
"""

ignore_properties = ["http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                     "http://www.w3.org/1999/02/22-rdf-syntax-ns#first",
                     "http://www.w3.org/1999/02/22-rdf-syntax-ns#rest",
                     "http://www.w3.org/1999/02/22-rdf-syntax-ns#value",
                     "http://www.w3.org/1999/02/22-rdf-syntax-ns#subject",
                     "http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate",
                     "http://www.w3.org/1999/02/22-rdf-syntax-ns#object",

                     "http://www.w3.org/2000/01/rdf-schema#domain",
                     "http://www.w3.org/2000/01/rdf-schema#range",
                     "http://www.w3.org/2000/01/rdf-schema#label",
                     "http://www.w3.org/2000/01/rdf-schema#member",
                     ]

#"http://www.w3.org/2000/01/rdf-schema#seeAlso",
#"http://www.w3.org/2000/01/rdf-schema#comment",
#"http://www.w3.org/2000/01/rdf-schema#isDefinedBy"
#"http://www.w3.org/2000/01/rdf-schema#subClassOf",
#"http://www.w3.org/2000/01/rdf-schema#subPropertyOf",

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


def get_class_group(args):
    print(args)
    userInputArr = json.loads(args['class'])
    link_property = args['link_property']
    link_intersection = args['link_intersection']
    link_subclass = args['link_subclass']

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

    startTime = datetime.now()
    intersection_arr = ''
    for document in cursor:
        c = document["class"]
        document["id"] = index
        index += 1

        is_subclass = conn("subclass").filter(
            lambda class_: class_["subclass"] == c).count().run()
        document['subclass'] = 1 if is_subclass > 0 else 0

        is_equivalent = conn("equivalentclass").filter(
            lambda class_:
            class_["c1"].default('foo').eq(c).or_(
                class_["c2"].default('foo').eq(c)
            )
        ).run()
        document['equivalent'] = 0
        for r in is_equivalent:
            if(document['equivalent'] == 1):
                pass
            else:
                document['equivalent'] = 1 if(
                    r["c1"] in userInputArr and r["c2"] in userInputArr) else 0
        intersection_arr = userInputArr

        if(link_intersection == 'true'):
            does_intersect = conn("intersection").filter(
                lambda class_:
                class_["c1"].default('foo').eq(c)
            ).run()
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
                            "group":	"nogroup_" + str(i) + "_intersect",
                            "id":	str(index) + "_intersect",
                            "name":	"",
                            "subclass":	0,
                            "intersect": 1
                        }
                    )

        try:
            x = document['group']
        except:
            document['group'] = "nogroup_" + str(i)
            i += 1
        result.append(document)
    timeElapsed = datetime.now() - startTime
    print('Nodes Time elpased (hh:mm:ss.ms) {}'.format(timeElapsed))

    if(userInputArr == ''):
        links = conn("graph_data").run()  # remove redundancy
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
        filter_ = {}
        if(link_intersection == 'false') and (link_subclass == 'false'):
            filter_ = {'subclass': 0, 'intersect': 0}
        elif(link_intersection == 'false'):
            filter_ = {'intersect': 0}
        elif(link_subclass == 'false'):
            filter_ = {'subclass': 0}
            print("--")

        print(filter_)

        startTime = datetime.now()

        links = conn("graph_data").filter(
            lambda doc:
                get_r().expr(filter_arr)
                .contains(doc["source"]).and_(
                    get_r().expr(filter_arr)
                    .contains(doc["target"])
                )
        ).filter(filter_).run()

        timeElapsed = datetime.now() - startTime
        print('Links list Time elpased (hh:mm:ss.ms) {}'.format(timeElapsed))

    link_arr = list(links)
    len_ = len(link_arr)
    print(len_)

    startTime = datetime.now()
    i = 0
    # link_arr = return_array(links, len_)
    for node in result:
        for j in range(0, len_):
            link = link_arr[j]
            # print(node["class"])
            if(link["source"] == node["class"]):
                link["source"] = i
            if(link["target"] == node["class"]):
                link["target"] = i
        i += 1

    timeElapsed = datetime.now() - startTime
    print('Links list Time elpased (hh:mm:ss.ms) {}'.format(timeElapsed))

    json_data = {"nodes": result, "links": np.array(link_arr).tolist()}

    return json_data


# def get_properties():
#     cursor = conn("class").inner_join(
#             conn("property"),
#             lambda left, right:
#                 left["class"] == right["c1"]
#         ).zip().run()
#     return list(cursor)

def get_property(s, t, b, l):

    # cursor1 = list(conn("property").order_by(index=get_r().desc('count')).filter({"c1":s, "c2": t}).outer_join(
    #     conn("inverse_property"),
    #     lambda left, right:
    #         (left["p"].eq(right["p"])) #.and_(left["p"].ne(right["p2"]))
    # ).zip().limit(int(l)).run())

    cursor1 = list(conn("graph_data_property").order_by(index=get_r().desc('count')).filter(
        {"c1": s, "c2": t}
    ).limit(int(l)).without('id').run())

    print(s)
    print(t)
    print(cursor1)
    if(int(b) == 1):
        cursor2 = list(conn("graph_data_property").order_by(index=get_r().desc('count')).filter(
            {"c1": t, "c2": s}
        ).limit(int(l)).without('id').run())
        # cursor2 = list(conn("property").order_by(index=get_r().desc('count')).filter({"c1":t, "c2": s}).outer_join(
        # conn("inverse_property"),
        # lambda left, right:
        #     (left["p"].eq(right["p"])) #.and_(left["p"].ne(right["p2"]))
        # ).zip().limit(int(l)).run())

        property_list = cursor1 + cursor2
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


def _get_property(s, t, b, l):

    cursor1 = conn("property").order_by(index=get_r().desc('count')).filter({"c1": s, "c2": t}).outer_join(
        conn("inverse_property"),
        lambda left, right:
        (left["p"].eq(right["p1"])).or_(left["p"].eq(right["p2"]))
    ).zip().limit(int(l)).run()
    # return list(cursor)

    # cursor1 = conn("property").order_by(index=get_r().desc('count')).filter({"c1":s, "c2": t}).limit(int(l)).run()
    # print(int(b))
    if(int(b) == 1):
        cursor2 = conn("property").order_by(index=get_r().desc('count')).filter({"c1": t, "c2": s}).outer_join(
            conn("inverse_property"),
            lambda left, right:
            (left["p"].eq(right["p1"])).or_(left["p"].eq(right["p2"]))
        ).zip().limit(int(l)).run()
        # cursor2 = conn("property").order_by(index=get_r().desc('count')).filter({"c1":t, "c2": s}).limit(int(l)).run()
        return list(cursor1) + list(cursor2)
    else:
        return list(cursor1)


def query_subject(s, p_filter):
    # query subjects based of the popular properties
    # rows = conn("property").filter({"c1": s})["p"].distinct().run()
    p = "1"
    for row in p_filter:
        p += """ || ?p =<""" + row + """>"""

    query = query_prefix + """
        SELECT * 
        WHERE {
            ?s a <""" + s + """> .
            ?s ?p ?o .
            OPTIONAL{?s rdfs:label ?s_label .
            FILTER (langMatches(lang(?s_label),"en"))
            }
            OPTIONAL{?o rdfs:label ?o_label .
            FILTER (langMatches(lang(?o_label),"en"))
            }
            OPTIONAL{?p rdfs:label ?p_label.
            FILTER (langMatches(lang(?p_label),"en"))
            }   
            OPTIONAL{?s foaf:name ?s_name .
            }
            OPTIONAL{?o foaf:name ?o_name .
            }
            OPTIONAL{?p foaf:name ?p_name .
            }                        
            FILTER (""" + p + """) .
            FILTER (?o != <""" + s + """>)
        }
        limit 200
    """
    print(query)
    result = execute_query(query)
    return result


def query_property(s, p, o):
    query = query_prefix + """
        SELECT * 
        WHERE {
            ?s a <""" + s + """> .
            ?o a <""" + o + """> .
            ?s <""" + p + """> ?o .
            OPTIONAL{?s rdfs:label ?s_label.
            FILTER (langMatches(lang(?s_label),"en"))
            }
            OPTIONAL{?o rdfs:label ?o_label .
            FILTER (langMatches(lang(?o_label),"en"))
            }
            OPTIONAL{?s foaf:name ?s_name.
            }
            OPTIONAL{?o foaf:name ?o_name .
            }
            
        }
        limit 200
    """
    print(query)
    result = execute_query(query)
    return result


def query_property_list(s):
    return conn("property").filter({"c1": s})["p"].distinct().run()


def query_intersect(s, o):
    rows = query_property_list(s)
    p = "1"
    for row in rows:
        p += """ || ?p =<""" + row + """>"""

    query = query_prefix + """
        SELECT * 
        WHERE {
            ?s a <""" + s + """> .
            ?s a <""" + o + """> .
            OPTIONAL{?s rdfs:label ?s_label .
            FILTER (langMatches(lang(?s_label),"en"))
            }
            OPTIONAL{?s foaf:name ?s_name .
            }
        }
        limit 200
    """
    print(query)
    result = execute_query(query)
    return result


def sparql_query(s, p, o, p_filter):
    sparql_endpoint()
    if(p == '') and (o == ''):
        result = query_subject(s, p_filter)
    elif p == '':
        result = query_intersect(s, o)
    else:
        result = query_property(s, p, o)
    return result


def query_class_detail(c):
    cursor = conn("property_datatype").filter({"class":c}).run()  # need to create index for count to use this
    nodes = list(cursor)
    return nodes["property_datatype"]

# def query_class_detail(s):
#     sparql_endpoint()
#     query = query_prefix + """
#         SELECT DISTINCT ?p ?datatype
#         WHERE {
#             ?s a <""" + s + """>.
#             ?s ?p ?o.
#         BIND (datatype(?o) AS ?datatype) . 
#             Filter (?datatype !='') . 
#         }
#         ORDER BY ?p
#     """
#     results = execute_query(query)
#     json = []
#     p_prev = ''
#     json_datatype = []
#     for index,result in enumerate(results):        
#         p = result["p"]["value"]
#         type_value = get_class_name(result["datatype"]["value"])
#         if(p == p_prev or p_prev == ''):
#             p_prev = result["p"]["value"]
#             json_datatype.append(type_value)
#         else:            
#             json.append({
#                 "p" : p_prev,
#                 "datatype" : json_datatype
#             })
#             p_prev = result["p"]["value"]
#             json_datatype = []
#             json_datatype.append(type_value)
        
#         if(index == len(results)-1):
#             json.append({
#                 "p" : p_prev,
#                 "datatype" : json_datatype
#             })
    
#     return json

    # SELECT distinct ?datatype
    #     WHERE {
    #         ?s a <"""+ s +""">.
    #         ?s ?p ?o.
    #         BIND (datatype(?o) AS ?datatype) .
    #     }

    # """


def query_instance_property_object(s, p):
    sparql_endpoint()
    query = query_prefix + """
        SELECT *
        WHERE{            
            <""" + s + """> <""" + p + """> ?o.
            OPTIONAL{ ?o rdfs:label ?o_label .
            FILTER (langMatches(lang(?o_label),"en"))
            }
            OPTIONAL{ ?o  foaf:name ?o_name .}
        }
        
    """
    print(query)
    result = execute_query(query)
    return result


def query_instance_property(i):
    sparql_endpoint()
    p = ''
    for row in ignore_properties:
        p += """ ?p !=<""" + row + """> &&"""
    p = p[:-2]
    query = query_prefix + """
        SELECT *
        WHERE{            
            OPTIONAL{ <""" + i + """>  rdfs:label ?s_label .
            FILTER (langMatches(lang(?s_label),"en"))
            }
            OPTIONAL{ <""" + i + """>  foaf:name ?s_name .}
        }
        
    """
    result = execute_query(query)
    try:
        node_name = result[0]["s_name"]["value"]
    except:
        try:
            node_name = result[0]["s_label"]["value"]
        except:
            node_name = i

    query = """
        SELECT DISTINCT ?p  (COUNT(?p) as ?count)
        WHERE {
            <""" + i + """> ?p ?o.
            FILTER(""" + p + """)      
            }
        GROUP BY ?p
        ORDER BY DESC(?count)  
         
    """
    print(query)
    results = execute_query(query)

    nodes = []
    nodes.append({
        "id": 0,
        "name": node_name,
        "node": i,
        "subject": i
    })
    links = []
    index = 1
    for result in results:
        try:
            p = result["p"]["value"]
            print(p)
            count = result["count"]["value"]
            nodes.append({
                "id": index,
                "node": p,
                "name": count,
                "subject": i
            })
            links.append(
                {
                    "linkid": "property_" + str(index),
                    "source": 0,
                    "target": index,
                    "name": p
                }
            )
            index += 1
        except:
            pass

    json_data = {"nodes": nodes, "links": links}
    print(json_data)
    return json_data


class ClassList(Resource):
    def post(self):
        args = parser.parse_args()
        set_db(args['database_name'])
        return get_class()


class ClassWithDetail(Resource):
    def get(self):
        # return {'nodes': get_class_group(), 'links': get_class_links()}
        return get_class_group()

    def post(self):
        args = parser.parse_args()
        set_db(args['database_name'])
        # args = json.loads(args['class'])
        # return {'nodes': get_class_group(args), 'links': get_class_links(args)}
        return get_class_group(args)


class AddNode(Resource):
    def get(self):
        return 1

    def post(self):
        args = parser.parse_args()
        set_db(args['database_name'])
        args = json.loads(args['class'])
        return args, 201


class Property(Resource):
    def post(self):
        args = parser.parse_args()
        set_db(args['database_name'])
        return get_property(args['s'].strip(), args['t'].strip(), args['b'].strip(), args['limit'].strip())


class SPARQLQuery(Resource):
    def post(self):
        args = parser.parse_args()
        set_db(args['database_name'])
        return {"data": sparql_query(args['s'], args['p'], args['t'], json.loads(args['p_filter'].strip()))}


class PropertyList(Resource):
    def post(self):
        args = parser.parse_args()
        set_db(args['database_name'])
        return query_property_list(args['s'].strip())


class InstancePropertyList(Resource):
    def post(self):
        args = parser.parse_args()
        set_db(args['database_name'])
        return query_instance_property(args['i'])


class InstancePropertyObject(Resource):
    def post(self):
        args = parser.parse_args()
        set_db(args['database_name'])
        return query_instance_property_object(args['s'], args['p'])


class ClassAllDetail(Resource):
    def post(self):
        args = parser.parse_args()
        set_db(args['database_name'])
        return query_class_detail(args['s'])


api.add_resource(ClassList, '/classlist')
api.add_resource(ClassWithDetail, '/class')
api.add_resource(AddNode, '/addnode')
api.add_resource(Property, '/property')
api.add_resource(SPARQLQuery, '/query')
api.add_resource(PropertyList, '/query/propertylist')
api.add_resource(InstancePropertyList, '/query/instance/propertylist')
api.add_resource(InstancePropertyObject, '/query/instance/property/object')
api.add_resource(ClassAllDetail, '/query/class/detail')


# api.add_resource(EquivalentClass,'/equivalentclass')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
