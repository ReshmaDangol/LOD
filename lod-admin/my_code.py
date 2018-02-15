# sudo fuser -k 9001/tcp


from flask import Flask, render_template
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import defaultdict
import rethinkdb as r

from rdflib import ConjunctiveGraph, Namespace, Literal
import rdflib
from rdflib import plugin
from common_functions import *

# properties = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
global_equivalent_class = []
global_proper_subset = []
tableprefix = ""

app = Flask(__name__)
endpoint = ""


def sparql_endpoint():
    global endpoint
    # url1 = "http://vocabulary.semantic-web.at/PoolParty/sparql/AustrianSkiTeam"
    # url2 = "http://datos.bcn.cl/sparql"
    # url3 = "http://services.data.gov.uk/statistics/sparql"
    # url4 = "http://ring.ciard.net/sparql1"
    # url5 = "http://www.linkedmdb.org/sparql"
    # url6 = "http://data.archiveshub.ac.uk/sparql"
    # url7 = "http://cultura.linkeddata.es/sparql"
    # url8 = "http://linkedgeodata.org/sparql/"
    # url9 = "http://canlink.library.ualberta.ca"
    # url = "http://localhost:3030/tdb1/"
    # url10 = "http://sparql.kupkb.org/sparql"

    # local Stardog triplestores
    # https://old.datahub.io/dataset/getty-aat
    url11 = "http://localhost:5820/aat/query"
    url12 = "http://localhost:5820/archiveshub/query"  # archives hub
    url13 = "http://localhost:5820/jamendo/query"
    url14 = "http://localhost:5820/linkedmdb/query"    

    url = "http://localhost:5820/" + database_name + "/query" #?reasoning=true&"

    endpoint = SPARQLWrapper(url)  # this should be user's input


sparql_endpoint()


def create_tables():
    r.connect("localhost", 28015).repl()
    r.db(database_name).table_create(
        tableprefix + "equivalentclass_group").run()
    r.db(database_name).table_create(tableprefix + "equivalentclass").run()
    r.db(database_name).table_create(tableprefix + "instance").run()
    r.db(database_name).table_create(tableprefix + "inverse_property").run()
    r.db(database_name).table_create(tableprefix + "property").run()
    r.db(database_name).table_create(tableprefix + "subclass").run()
    r.db(database_name).table_create(tableprefix + "class").run()
    r.db(database_name).table_create(tableprefix + "intersection").run()
    r.db(database_name).table_create(tableprefix + "graph_data").run()
    r.db(database_name).table_create(tableprefix + "graph_data_property").run()
    r.db(database_name).table_create(tableprefix + "property_datatype").run()    
    r.db(database_name).table_create(tableprefix + "property_type").run()    
    r.db(database_name).table_create(tableprefix + "error_log").run()    

    
    conn(tableprefix + "property").index_create('count').run()
    


def create_database():
    r.connect("localhost", 28015).repl()
    if (r.db_list().contains(database_name).run()):
        pass
    else:
        r.db_create(database_name).run()
        create_tables()


# create_database()


def get_graph():
    path = '../data/triplestore_drugbank'
    graph = ConjunctiveGraph('Sleepycat')
    graph.open(path, create=False)
    return graph


def execute_query_graph(graph):
    results = graph.query(query)
    return results

# create_tables()


@app.route('/')
def homepage():
    variable = "Test"
    return render_template("index.html")


@app.route('/about')
def aboutpage():
    variable = "About Page"
    return render_template("index.html", variable=variable)


def execute_query(query):
    endpoint.setQuery(query)
    endpoint.setReturnFormat(JSON)
   
    # print results
    # print len(results["results"]["bindings"])
    try:
        results = endpoint.query().convert()
        return results["results"]["bindings"]
  
    except:
        conn(tableprefix + "error_log").insert({"query":query}).run()
        return -1
# Fetch classes with max instances


@app.route('/setoperation')
def set_operation():
    classes = conn(tableprefix + "class")["class"].distinct().run()
    class_arr = list(classes)
    len_ = len(class_arr)
    # len_ = conn(tableprefix + "class")["class"].distinct().count().run()
    # class_arr = return_array(classes, len_)
    intersection = []
    for i in range(0, len_ - 1):
        for j in range(i + 1, len_):
            c1 = class_arr[i]
            c2 = class_arr[j]
            query1 = """
            SELECT (count(*) as ?count) ?s
            WHERE 
            {?s a <""" + c1 + """> .
            ?s a <""" + c2 + """> . 
            }
            GROUP BY ?s 
            Having (?count>0)
            """
            results = execute_query(query1)
            count_result = 0
            for r in results:
                count_result += 1
            #     if (len(r['count']['value'])>0):
            #         print(r['count']['value'])
            #         print(r['s']['value'])

            if(count_result > 0):

                query2 = """
                SELECT (count(distinct ?s) as ?count)
                WHERE 
                {?s a <""" + c1 + """> 
                }
                """
                result = execute_query(query2)
                count_c1 = result[0]["count"]["value"]
                query3 = """
                SELECT (count(distinct ?s) as ?count)
                WHERE 
                {?s a <""" + c2 + """> 
                }
                """
                result = execute_query(query3)
                count_c2 = result[0]["count"]["value"]

                if(count_result == int(count_c1) or count_result == int(count_c2)):
                    pass
                else:
                    print(query1)
                    print(count_result)
                    print(count_c1)
                    print(count_c2)
                    print('---')

                    intersection.append({
                        "c1": c1,
                        "c2": c2,
                        "count": count_result
                    })
    conn(tableprefix + "intersection").insert(intersection).run()
    return render_template("sparql.html")



@app.route('/property_type')
def inverse_functional_property():
    rows = conn(tableprefix + "property")["p"].distinct().run()
    property_type = []
    for row in rows:
        p = row
        #may be perform count to confirm?
        # SymmetricProperty
        query = """
            SELECT (COUNT(*) as ?instanceCount)
            WHERE {              
                ?s <""" + p + """> ?o.
                ?o <""" + p + """> ?s.
            }
        """
        print(query)
        result = execute_query(query)
        if result != -1:
            if(int(result[0]["instanceCount"]["value"])>0):
                property_type.append({
                    "p" : p,
                    "type" : "symmetric"
                })

        # Transitive Property exists in aat daraset
        query = """
            SELECT (COUNT(*) as ?instanceCount)
            WHERE {              
                ?a <""" + p + """> ?b.
                ?b <""" + p + """> ?c.
                ?a <""" + p + """> ?c.
            }
        """
        print(query)
        result = execute_query(query)
        if result != -1:
            if(int(result[0]["instanceCount"]["value"])>0):
                property_type.append({
                    "p" : p,
                    "type" : "transitive"
                })
        
        # inverse functional
        query = """
            SELECT (COUNT(*) as ?instanceCount)
            WHERE {              
                ?s1 <""" + p + """> ?o.
                ?s2 <""" + p + """> ?o.
            }
        """
        print(query)
        result = execute_query(query)
        if result != -1:
            if(int(result[0]["instanceCount"]["value"]) == 0):
                property_type.append({
                    "p" : p,
                    "type" : "inverse_functional"
                })

        # functional property
        # p = "http://purl.org/dc/terms/replaces"
        query = """
            SELECT (COUNT(*) as ?instanceCount)
            WHERE {              
                ?s <""" + p + """> ?o1.
                ?s <""" + p + """> ?o2 
            }
        """
        print(query)
        result = execute_query(query)
        if result != -1:
            if(int(result[0]["instanceCount"]["value"]) == 0):
                property_type.append({
                    "p" : p,
                    "type" : "functional"
                })



    conn(tableprefix + "property_type").insert(property_type).run()
        # if(int(rows[0]["instanceCount"]["value"]) > 0):
        #     # pass
        #     print rows[0]["instanceCount"]["value"]
        # else:
        #     print p

    return render_template("sparql.html")


@app.route('/class')
def popular_class():
    count = 20
    query = """ 
      SELECT DISTINCT ?class (count(?sub) AS ?instance_count)
      WHERE {
        ?sub a ?class. 
      } 
      GROUP BY ?class 
      ORDER BY DESC(?instance_count) 
      limit """ + str(count)

    results = execute_query(query)
    i = 0
    classes = []  # [None] * count
    #classDetail = [None] * count
    print(results)

    for result in results:
        class_uri = result["class"]["value"]
        if("http://" not in result["class"]["value"]) and ("https://" not in result["class"]["value"]) :
            class_uri = "_:" + result["class"]["value"] #if blank node
        classes.append({
            "class": class_uri,
            "count": int(result["instance_count"]["value"]),
            "name": get_class_name(result["class"]["value"])
        })
    print(conn(tableprefix + "class").insert(classes).run())
    conn(tableprefix + "class").index_create('count').run()
    return render_template("sparql.html", results=classes, page="class")


@app.route('/property')
def fetch_property():
    classes = conn(tableprefix + "class")["class"].distinct().run()
    class_arr = list(classes)
    len_ = len(class_arr)
    # len_ = conn(tableprefix + "class")["class"].distinct().count().run()
    # class_arr = return_array(classes, len_)

    for i in range(0, len_ - 1):
        for j in range(i, len_):
            print(class_arr[i])
            print(class_arr[j])
            poperty_between_class(class_arr[i], class_arr[j])
            poperty_between_class(class_arr[j], class_arr[i])
    return render_template("sparql.html")


@app.route('/subclass')
def fetch_sub_equivalent_class():
    # global_equivalent_class = []
    # global_proper_subset = []
    classes = conn(tableprefix + "class")["class"].distinct().run()
    class_arr = list(classes)
    len_ = len(class_arr)
    # len_ = conn(tableprefix + "class")["class"].distinct().count().run()
    # class_arr = return_array(classes, len_)
    for i in range(0, len_ - 1):
        for j in range(i + 1, len_):
            check_sub_equivalent_class(class_arr[i], class_arr[j])

    # check_sub_equivalent_class("http://linkedgeodata.org/ontology/PowerTower", "http://linkedgeodata.org/ontology/PowerThing")
    print("subclass->")
    print(global_proper_subset)
    print("equivalent->")
    print(global_equivalent_class)
    conn(tableprefix + "subclass").insert(global_proper_subset).run()
    conn(tableprefix + "equivalentclass").insert(global_equivalent_class).run()
    return render_template("sparql.html")


@app.route('/subclass_transitivity')
def subclass_check_transitivity():
    rows = conn(tableprefix + "subclass").run()
    for row in rows:
        c = row['class']
        sc =  row['subclass']
        result_1 = conn(tableprefix + "subclass").filter((r.row["class"] == c) & (r.row["subclass"] != sc)).run()
        for d in result_1:
            result_2 = conn(tableprefix + "subclass").filter((r.row["class"] == d["subclass"]) & (r.row["subclass"] == sc)).count().run()
            if(result_2>0):
                conn(tableprefix + "subclass").filter((r.row["class"] == c) & (r.row["subclass"] == sc)).update({"transitive_subclass": "true"}).run()
                print(get_class_name(c),get_class_name(sc),get_class_name(d["subclass"]) )


    rows =  conn(tableprefix + "subclass").filter({"transitive_subclass": "true"}).not_().run()
    for row in rows:    
        conn(tableprefix + "subclass_graph").insert({
                    "class": c,
                    "subclass":sc
                    }).count().run()
                
                # print(get_class_name(c),get_class_name(sc),get_class_name(d["subclass"]) )

    return render_template("sparql.html")           

def poperty_between_class(*args):
    count = 20
    c1 = args[0]
    c2 = args[1]
    query = """
        SELECT (count(?instanceOfClassA) as ?count) ?prop 
            WHERE {
                ?instanceOfClassA a <""" + c1 + """> . 
                ?instanceOfClassB a <""" + c2 + """> . 
                ?instanceOfClassA ?prop ?instanceOfClassB .
            } 
        GROUP BY ?prop 
        ORDER BY DESC(?count) limit """ + str(count)

    print(query)
    results = execute_query(query)
    # i = len(properties)
    # conn()
    data = []
    for result in results:
        print(result)
        print(result["count"]["value"])
        if(int(result["count"]["value"]) > 0):
            #properties[c1][c2][i]= result["prop"]["value"]
            p = result["prop"]["value"]
            # properties[i]= [c1, c2, p]
            q = """
                SELECT (count(*) as ?count)
                WHERE {
                    ?s a <""" + c1 + """>.
                    ?o a <""" + c2 + """>.
                    ?s <""" + p + """> ?o
                }
                group by ?s
                order by desc(?count)
                limit 1
            """

            # q = """
            #     SELECT (count(*) as ?count)
            #     WHERE {
            #         ?s <""" + p + """> ?o
            #         ?s <""" + p + """> ?o2
            #     }
            #     group by ?s
            #     order by desc(?count)
            #     limit 1
            # """

            print(q)
            q_result = execute_query(q)
            max_cardinality = q_result[0]["count"]["value"]
            data.append({
                "c1": c1,
                "c2": c2,
                "p": p,
                "max_cardinality": int(max_cardinality),
                "count": int(result["count"]["value"])
            })

        # i + 1
    conn(tableprefix + "property").insert(data).run()
   
    pass


def testquery():
    # conn()
    # rows= conn(tableprefix + "property").filter(
    #         (r.row["id"] == "10715377-6086-4010-927e-f4e90436f451") &
    #         (r.row["instance"]['s'] == "http://datos.bcn.cl/recurso/cl/dfl/ministerio-de-salud_subsecretaria-de-salud-publica/2006-04-24/1") &
    #         (r.row["instance"]['o'] == "http://datos.bcn.cl/recurso/cl/ley/ministerio-de-salud/1990-03-09/18933")

    #     ).run()

    conn(tableprefix + "property").concat_map(
        lambda doc: doc['instance']
        .concat_map(lambda data: [{"id": doc["id"], 'instance':data}]
                    )).filter(
        lambda doc:
            (doc["instance"]["o"] == "http://datos.bcn.cl/recurso/cl/dfl/ministerio-de-salud_subsecretaria-de-salud-publica/2006-04-24/1") &
            (doc["instance"]["s"] == "http://datos.bcn.cl/recurso/cl/ley/ministerio-de-salud/1990-03-09/18933") &
            (doc["id"] == "10715377-6086-4010-927e-f4e90436f451")
    ).update(
        {"aa": "ww"}
    ).run()

    return render_template("dbtest.html")


@app.route('/getinstance')
def get_instances():
    rows = conn(tableprefix + "property").run()
    for row in rows:
        c1 = row["c1"]
        c2 = row["c2"]
        p = row["p"]
        id = row["id"]
        query = """
        SELECT distinct * WHERE
        {
            ?s a <""" + c1 + """>.
            ?o a <""" + c2 + """>.
            ?s <""" + p + """> ?o
        }
        LIMIT 10
        """
        # i=0
        data = []
        results = execute_query(query)
        for result in results:
            s = result["s"]["value"]
            o = result["o"]["value"]
            q = """
                SELECT (count(*) as ?count)
                WHERE {
                    ?o a <""" + c2 + """>.
                    <""" + s + """> <""" + p + """> ?o
                }      
            """
            print(q)
            res = execute_query(q)
            count = res[0]["count"]["value"]
            data.append({
                "s": s,
                "count": count
            })
            # i+=1

        conn(tableprefix + "property").get(id).update({"instance": data}).run()
    return render_template("dbtest.html", results=results, page="class")

  # print query


def count_shared_instance():
    rows = conn(tableprefix + "property").run()
    for row in rows:
        c1 = row["c1"]
        c2 = row["c2"]
        p = row["p"]
        instance = row["instance"]
        id = row["id"]
        for i in instance:
            s = i["s"]
            o = i["o"]

            query = """
            SELECT (count(*) as ?count) WHERE
            {
            ?s a <""" + s + """>.
            ?o a <""" + o + """>.
            ?s <""" + p + """> ?o

            }
            """
            result = execute_query(query)
            count = result[0]["count"]["value"]

            conn(tableprefix + "property").get(id).filter(
                # lambda instance: instance["instance"]["s"]==s & instance["instance"]["o"]==o
                (r.row["instance"]["s"] == s) & (r.row["instance"]["o"] == o)
            ).update({"instance": {"count": count}}).run()

        #    conn(tableprefix + "property").get(id).update({"count":count}).run()


def instance_count(c1):
    query = """
        SELECT (COUNT(?instance) as ?instance_count)
        WHERE {
            ?instance a <""" + c1 + """>
        }
    """
    results = execute_query(query)
    # print(c1)
    # print(results[0]["instance_count"]["value"])
    return int(results[0]["instance_count"]["value"])


def common_instance_count(*args):
    c1 = args[0]
    c2 = args[1]
    query = """
    SELECT (COUNT(?instance) AS ?instance_count)
      WHERE { 
        ?instance a <""" + c1 + """>.
        ?instance a <""" + c2 + """> . 
      }
    """
    # print(query)
    results = execute_query(query)
    try:
        count = int(results[0]["instance_count"]["value"])
    except:
        count = 0
    # print(query)
    return count


def check_sub_equivalent_class(*args):

    c1 = args[0]
    c2 = args[1]
    c1Count = instance_count(c1)
    c2Count = instance_count(c2)
    c1c2Count = common_instance_count(c1, c2)
    if (c1Count < c2Count):
        if(c1c2Count == c1Count) and c1Count!=0:            
            global_proper_subset.append({"subclass": c1, "class": c2})
    elif c2Count < c1Count:
        if(c1c2Count == c2Count) and c2Count!=0:
            global_proper_subset.append({"subclass": c2, "class": c1})
    elif c1c2Count == c1Count and c1c2Count == c2Count and c1Count!=0:
        global_equivalent_class.append({"c1": c1, "c2": c2})


def get_uri(uri):
    temp = uri.rsplit('#', 1)
    if(len(temp)>1):
        return temp[0]
    else:
        return uri.rsplit('/', 1)[0]

@app.route("/inverse")
def inverse_property():

    # properties = conn(tableprefix + "property")['p'].distinct().limit(5).run()
    # print(properties)
    rows = conn(tableprefix + "property").run()
    checked_property = []
    inverse_property = []
    for row in rows:
        c1 = row["c1"]
        c2 = row["c2"]
        p = row["p"]

        if p in checked_property:
            print("found")
        else:
            checked_property.append(p)
            # q = """
            # SELECT  (count(?p) as ?count) ?p
            # WHERE {
            # ?s a <""" + c1 + """>.
            # ?o a <""" + c2 + """>.
            # ?s <""" + p + """> ?o.
            # ?o ?p ?s
            # }
            # group by ?p
            # order by desc(?count)  
            # """

            #FILTER regex(str(?p), '"""+ get_uri(p) +"""') #filter by vocab

            q = """
            SELECT  (count(?p) as ?count) ?p
            WHERE {
            ?s <""" + p + """> ?o.
            ?o ?p ?s .
            
            }
            group by ?p
            order by desc(?count)  
            """
            # 
            # print(q)
            print("--")
            q_results = execute_query(q)
            print(q_results)
            i_properties = []
            for r in q_results:
                if(int(r["count"]["value"])>0):
                    inverse = r["p"]["value"]
                    # i_properties.append(inverse)
                    i_properties.append({"p":inverse,"count": r["count"]["value"]})
            
            if i_properties:
                inverse_property.append({"p": p, "inverse": i_properties})
                
            # if(len(q_results) > 0):
            #     print(q_results[0]["count"]["value"])
            #     if(int(q_results[0]["count"]["value"]) > 0):
            #         inverse = q_results[0]["p"]["value"]
            #         checked_property.append(inverse)
            #         inverse_property.append({"p1": p, "p2": inverse})

    print("---")
    conn(tableprefix + "inverse_property").insert(inverse_property).run()
    return render_template("sparql.html")


@app.route('/sparql')
def sparqlTest():
    sparql_endpoint()
    query = """ select * where {?s ?p ?o} limit 2 """
    endpoint.setQuery(query)
    endpoint.setReturnFormat(JSON)
    results = endpoint.query().convert()
    print(len(results))

    # for result in results:
    #   print(result)#["x"]["value"])#+" -- "+result["o"]["value"])

    return render_template("sparql.html", results=results)





@app.route('/datatype')
@app.route('/datatype')
def get_datatye():
    classes = conn(tableprefix + "class")["class"].distinct().run()
    class_arr = list(classes)
    len_ = len(class_arr)
    json_result = []
    for i in range(0, len_ - 1):
        query = """
            SELECT DISTINCT ?p ?datatype
            WHERE {
                ?s a <""" + class_arr[i] + """>.
                ?s ?p ?o.
            BIND (datatype(?o) AS ?datatype) . 
                Filter (?datatype !='') . 
            }
            ORDER BY ?p
        """
        results = execute_query(query)
        json = []
        p_prev = ''
        json_datatype = []
        for index,result in enumerate(results):        
            p = result["p"]["value"]
            type_value = get_class_name(result["datatype"]["value"])
            count_query = """
                SELECT (count(*) as ?count)
                WHERE
                {
                    ?s a <""" + class_arr[i] + """>.
                    ?s <"""+ p +"""> ?o.
                }
            """
            res = execute_query(count_query)
            instance_count = res[0]["count"]["value"]
            
            if(p == p_prev or p_prev == ''):
                p_prev = result["p"]["value"]
                json_datatype.append(type_value)
            else:            
                json.append({
                    "p" : p_prev,
                    "count" : instance_count,
                    "datatype" : json_datatype
                })
                p_prev = result["p"]["value"]
                json_datatype = []
                json_datatype.append(type_value)
            
            if(index == len(results)-1):
                json.append({
                    "p" : p_prev,
                    "count" : instance_count,
                    "datatype" : json_datatype
                })
        
        json_result.append({
            "class" : class_arr[i],
            "property_datatype":json
        })
        
    conn(tableprefix + "property_datatype").insert(json_result).run()
    return render_template("sparql.html")



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
