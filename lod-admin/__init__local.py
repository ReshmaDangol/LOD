#sudo fuser -k 9001/tcp


from flask import Flask, render_template
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import defaultdict
import rethinkdb as r

from rdflib import ConjunctiveGraph, Namespace, Literal
import rdflib
from rdflib import plugin

# properties = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
global_equivalent_class = []
global_proper_subset = []
tableprefix = ""
database_name = "linkedmdb"
database_name = "archiveshub"
database_name = "cultura"
database_name = "linkedgeodata"
database_name = "linkedmdb_local"
# tableprefix = "bcn_"

app = Flask(__name__)
endpoint = ""

def conn(table):
    r.connect( "localhost", 28015).repl()
    return r.db(database_name).table(table)

def sparql_endpoint(): 
    global endpoint    
    url1 = "http://vocabulary.semantic-web.at/PoolParty/sparql/AustrianSkiTeam"
    url2 = "http://datos.bcn.cl/sparql" 
    url3 = "http://services.data.gov.uk/statistics/sparql"
    url4 = "http://ring.ciard.net/sparql1"
    url5 = "http://www.linkedmdb.org/sparql"
    url6 = "http://data.archiveshub.ac.uk/sparql"
    url7 = "http://cultura.linkeddata.es/sparql"
    url8 = "http://linkedgeodata.org/sparql/"
    url9 = "http://canlink.library.ualberta.ca"
    endpoint = SPARQLWrapper(url8) #this should be user's input

# sparql_endpoint()

def create_tables():
    r.connect( "localhost", 28015).repl()
    r.db(database_name).table_create(tableprefix + "equivalentclass").run()
    r.db(database_name).table_create(tableprefix + "instance").run()
    r.db(database_name).table_create(tableprefix + "inverse_property").run()
    r.db(database_name).table_create(tableprefix + "property").run()
    r.db(database_name).table_create(tableprefix + "subclass").run()
    r.db(database_name).table_create(tableprefix + "class").run()

def create_database():
    r.connect( "localhost", 28015).repl()
    if (r.db_list().contains(database_name).run()):
        pass
    else:
        r.db_create(database_name).run()
        create_tables()

create_database()

def get_graph():
    path = '../data/triplestore_linkedmdb'
    graph = ConjunctiveGraph('Sleepycat')
    graph.open(path, create = False)
    return graph

def execute_query(query):
    graph = get_graph()
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
    return render_template("index.html", variable=variable )


def execute_query_endpoint(query):
    endpoint.setQuery(query)
    endpoint.setReturnFormat(JSON)
    results = endpoint.query().convert()   
    print results
    # print len(results["results"]["bindings"])
    return results["results"]["bindings"]

#Fetch classes with max instances
@app.route('/class')
def popular_class():
    count = 10
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
    classes = [] #[None] * count
    #classDetail = [None] * count
    # print results

    for result in results:
        # classes.append({"class" : result["class"]["value"]})
        classes.append({"class" : result["class"]})

    print conn(tableprefix + "class").insert(classes).run()
    return render_template("sparql.html", results=classes, page="class")

def return_array(*args):
    classes = args[0]
    len = args[1]
    class_arr = [None]*len
    index = 0
    for i,c in enumerate(classes):
        class_arr[index] = c["class"]
        index +=1
    return class_arr
    
@app.route('/property')
def fetch_property():
    classes = conn(tableprefix + "class").run()
    len = conn(tableprefix + "class").count().run()
    class_arr = return_array(classes,len)
    
    for i in range(0, len-1):
        for j in range(i+1, len):    
            print class_arr[i]
            print class_arr[j]
            poperty_between_class(class_arr[i], class_arr[j])
            poperty_between_class(class_arr[j], class_arr[i])
    return render_template("sparql.html")


@app.route('/subclass')
def fetch_sub_equivalent_class():
    global_equivalent_class = []
    global_proper_subset = []
    classes = conn(tableprefix + "class").run()
    len = conn(tableprefix + "class").count().run()
    class_arr = return_array(classes,len)
    for i in range(0, len-1):
        for j in range(i+1, len):          
            check_sub_equivalent_class(class_arr[i], class_arr[j])    
    
    # check_sub_equivalent_class("http://linkedgeodata.org/ontology/PowerTower", "http://linkedgeodata.org/ontology/PowerThing")    
    print global_proper_subset
    conn(tableprefix + "subclass").insert(global_proper_subset).run()
    conn(tableprefix + "equivalentclass").insert(global_equivalent_class).run()
    return render_template("sparql.html")

  
def poperty_between_class(*args):
    count = 10
    c1 = args[0]
    c2 = args[1]
    query = """
        SELECT (count(?instanceOfClassA) as ?count) ?prop 
            WHERE {
                ?instanceOfClassA a <"""+ c1 +"""> . 
                ?instanceOfClassB a <"""+ c2 +"""> . 
                ?instanceOfClassA ?prop ?instanceOfClassB .
            } 
        GROUP BY ?prop 
        ORDER BY DESC(?count) limit """ + str(count)
    # print query
    results = execute_query(query)
    # i = len(properties)
    #conn()
    data = []
    for result in results:
        #properties[c1][c2][i]= result["prop"]["value"]
        # p = result["prop"]["value"]
        p = result["prop"]
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
        print q
        q_result = execute_query(q)
        # max_cardinality = q_result[0]["count"]["value"] 
        max_cardinality = q_result[0]["count"]
        data.append( {
                "c1" : c1,
                "c2" : c2,
                "p" : p,
                "max_cardinality" :max_cardinality
            })
      
        # i + 1   
    conn(tableprefix + "property").insert(data).run()
    pass

def testquery():
    #conn()
    # rows= conn(tableprefix + "property").filter(
    #         (r.row["id"] == "10715377-6086-4010-927e-f4e90436f451") &
    #         (r.row["instance"]['s'] == "http://datos.bcn.cl/recurso/cl/dfl/ministerio-de-salud_subsecretaria-de-salud-publica/2006-04-24/1") &
    #         (r.row["instance"]['o'] == "http://datos.bcn.cl/recurso/cl/ley/ministerio-de-salud/1990-03-09/18933")
            
    #     ).run()

    conn(tableprefix + "property").concat_map(
        lambda doc: doc['instance']           
                .concat_map(lambda data: [{"id":doc["id"],'instance':data}]
    )).filter(
        lambda doc:
            (doc["instance"]["o"]=="http://datos.bcn.cl/recurso/cl/dfl/ministerio-de-salud_subsecretaria-de-salud-publica/2006-04-24/1") &
            (doc["instance"]["s"]=="http://datos.bcn.cl/recurso/cl/ley/ministerio-de-salud/1990-03-09/18933") &
            (doc["id"]=="10715377-6086-4010-927e-f4e90436f451")
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
            ?s a <""" + c1 +""">.
            ?o a <""" + c2 +""">.
            ?s <"""+ p +"""> ?o
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
                    ?o a <"""+c2+""">.
                    <"""+s+"""> <"""+p+"""> ?o
                }      
            """
            print q
            res = execute_query(q)
            count = res[0]["count"]["value"]          
            data.append({
                    "s":s,
                    "count":count
                })
            # i+=1
        
        conn(tableprefix + "property").get(id).update({"instance":data}).run()
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
            ?s a <""" + s +""">.
            ?o a <""" + o +""">.
            ?s <"""+ p +"""> ?o

            }
            """
            result = execute_query(query)
            count = result[0]["count"]["value"]

            conn(tableprefix + "property").get(id).filter(
                # lambda instance: instance["instance"]["s"]==s & instance["instance"]["o"]==o
                (r.row["instance"]["s"] == s) & (r.row["instance"]["o"] == o)
            ).update({"instance":{"count":count}}).run()

        #    conn(tableprefix + "property").get(id).update({"count":count}).run() 



def instance_count(c1):
    query = """
        SELECT (COUNT(?instance) as ?instance_count)
        WHERE {
            ?instance a <""" + c1 + """>
        }
    """
    print query
    results = execute_query(query)
    print c1
    print results[0]["instance_count"]["value"]
    return int(results[0]["instance_count"]["value"])
    
def common_instance_count(*args):
    c1 = args[0]
    c2 = args[1]
    query ="""
    SELECT (COUNT(?instance) AS ?instance_count)
      WHERE { 
        ?instance a <"""+ c1 +""">.
        ?instance a <"""+ c2 +"""> . 
      }
    """

    print query
    results = execute_query(query)
    try:
        count = int(results[0]["instance_count"]["value"])
    except:
        count = 0
    print query
    return count
  

def check_sub_equivalent_class(*args):
    
    c1 = args[0]
    c2 = args[1]
    c1Count = instance_count(c1)
    c2Count = instance_count(c2)
    c1c2Count = common_instance_count(c1,c2)
    if (c1Count < c2Count): 
        if(c1c2Count == c1Count):
            global_proper_subset.append({"subclass":c1, "class":c2})
    elif c2Count < c1Count:
        if(c1c2Count == c2Count):
            global_proper_subset.append({"subclass":c2, "class":c1})
    elif c1c2Count == c1Count and c1c2Count == c2Count:
            global_equivalent_class.append({"c1":c1,"c2":c2})

@app.route("/inverse")
def inverse_property():   
    
    properties = conn(tableprefix + "property")['p'].distinct().run()
    print properties
    rows = conn(tableprefix + "property").run()
    checked_property = []
    inverse_property = []
    for row in rows:
        c1 = row["c1"]
        c2 = row["c2"]
        p = row["p"]      
        
        if p in checked_property:
            print "found"         
        else:
            checked_property.append(p)
            q = """
            SELECT  (count(?p) as ?count) ?p
            WHERE {
            ?s a <"""+ c1 +""">.
            ?o a <"""+ c2 +""">.
            ?s <"""+ p +"""> ?o.
            ?o ?p ?s
            }
            group by ?p
            order by desc(?count)
            limit 1
            """
            print q
            q_results = execute_query(q)
            if(len(q_results)>0):
                inverse = q_results[0]["p"]["value"]
                checked_property.append(inverse)
                inverse_property.append({"p1":p, "p2": inverse})
            
       
    print "---"
    conn(tableprefix+ "inverse_property").insert(inverse_property).run()
    return render_template("sparql.html")
    

@app.route('/sparql')
def sparqlTest():    
    sparql_endpoint()
    query = """ select * where {?s ?p ?o} limit 2 """
    endpoint.setQuery(query)
    endpoint.setReturnFormat(JSON)
    results = endpoint.query().convert()   
    print len(results)

    #for result in results:
    #   print(result)#["x"]["value"])#+" -- "+result["o"]["value"])


    return render_template("sparql.html", results=results)






if __name__ == "__main__":
    app.run(debug=True)
