#sudo fuser -k 9001/tcp


from flask import Flask, render_template
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import defaultdict
import rethinkdb as r


properties = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
equivalentClass = []
properSubset = []
tableprefix = "bcn_"

app = Flask(__name__)
endpoint = ""

def conn():
    return  r.connect( "localhost", 28015).repl()

def sparqlEndpoint(): 
    global endpoint    
    url1 = "http://vocabulary.semantic-web.at/PoolParty/sparql/AustrianSkiTeam"
    url2 = "http://datos.bcn.cl/sparql" 
    endpoint = SPARQLWrapper(url2) #this should be user's input

sparqlEndpoint()

@app.route('/')
def homepage():
    variable = "Test"
    return render_template("index.html", variable=variable )

@app.route('/about')
def aboutpage():
    variable = "About Page"
    return render_template("index.html", variable=variable )


def executeQuery(query):
    endpoint.setQuery(query)
    endpoint.setReturnFormat(JSON)
    results = endpoint.query().convert()   
    # print len(results["results"]["bindings"])
    return results["results"]["bindings"]

#Fetch classes with max instances
@app.route('/class')
def popularClass():
    count = 10
    query = """ 
      SELECT DISTINCT ?class (count(?sub) AS ?instanceCount)
      WHERE {
        ?sub a ?class. 
      } 
      GROUP BY ?class 
      ORDER BY DESC(?instanceCount) 
      limit """ + str(count)
    results = executeQuery(query)
    i = 0
    classes = [None] * count
    #classDetail = [None] * count
    # print results

    for result in results:
        classes[i] = result["class"]["value"]
        #classDetail[i] = popularProperty(classes[i])
        #print classDetail[i]
        i +=1
    loopClasses(classes)
    #instanceCount(classes[0])
    #popertyBetweenClass(classes[0], classes[1])
    return render_template("sparql.html", results=classes, page="class")

def loopClasses(classes):
    for i,c in enumerate(classes):
        # print (i, c)
        for j in range(i+1, len(classes)-1):
            
            checkSubAndEquivalentClass(classes[i], classes[j])
            # popertyBetweenClass(classes[i], classes[j])
            # popertyBetweenClass(classes[j], classes[i])
    
    
    conn()
    r.db("LOD").table(tableprefix + "subclass").insert(properSubset).run()
    r.db("LOD").table(tableprefix + "equivalentclass").insert(equivalentClass).run()
    # getInstances()
  
def popertyBetweenClass(*args):
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
    results = executeQuery(query)
    i = len(properties)
    conn()
    data = []
    for result in results:
        #properties[c1][c2][i]= result["prop"]["value"]
        p = result["prop"]["value"]
        properties[i]= [c1, c2, p]
        q = """
            SELECT count(*) as ?count
            WHERE {
                ?s a <""" + c1 + """>.
                ?o a <""" + c2 + """>.
                ?s <""" + p + """> ?o
            }
            group by ?s
            order by desc(?count)
            limit 1
        """
        q_result = executeQuery(q)
        max_cardinality = q_result[0]["count"]["value"] 
        data.append( {
                "c1" : c1,
                "c2" : c2,
                "p" : p,
                "max_cardinality" :max_cardinality
            })
      
        i + 1   
    r.db("LOD").table(tableprefix + "class").insert(data).run()
    pass

def testquery():
    conn()
    # rows= r.db("LOD").table(tableprefix + "class").filter(
    #         (r.row["id"] == "10715377-6086-4010-927e-f4e90436f451") &
    #         (r.row["instance"]['s'] == "http://datos.bcn.cl/recurso/cl/dfl/ministerio-de-salud_subsecretaria-de-salud-publica/2006-04-24/1") &
    #         (r.row["instance"]['o'] == "http://datos.bcn.cl/recurso/cl/ley/ministerio-de-salud/1990-03-09/18933")
            
    #     ).run()

    r.db("LOD").table(tableprefix + "class").concat_map(
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
def getInstances():
    conn()
    rows = r.db("LOD").table(tableprefix + "class").run()
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
        results = executeQuery(query)
        for result in results:
            s = result["s"]["value"]
            o = result["o"]["value"]
            q = """
                SELECT count(*)
                WHERE {
                    ?o a <"""+c2+""">.
                    <"""+s+"""> <"""+p+"""> ?o
                }      
            """
            print q
            res = executeQuery(q)
            count = res[0]["callret-0"]["value"]
          
            data.append({
                    "s":s,
                    "count":count
                })
            # i+=1
        
        r.db("LOD").table(tableprefix + "class").get(id).update({"instance":data}).run()
    return render_template("dbtest.html", results=results, page="class")

  # print query

def countSharedInstance():
    conn()
    rows = r.db("LOD").table(tableprefix + "class").run()
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
            SELECT count(*) as count WHERE
            {
            ?s a <""" + s +""">.
            ?o a <""" + o +""">.
            ?s <"""+ p +"""> ?o

            }
            """
            result = executeQuery(query)
            count = result[0]["count"]["value"]

            r.db("LOD").table(tableprefix + "class").get(id).filter(
                # lambda instance: instance["instance"]["s"]==s & instance["instance"]["o"]==o
                (r.row["instance"]["s"] == s) & (r.row["instance"]["o"] == o)
            ).update({"instance":{"count":count}}).run()

        #    r.db("LOD").table(tableprefix + "class").get(id).update({"count":count}).run() 



def instanceCount(c1):
    query = """
        SELECT COUNT(?instance) as ?instanceCount
        WHERE {
            ?instance a <""" + c1 + """>
        }
    """
    results = executeQuery(query)
    return results[0]["instanceCount"]["value"]
    


def commonInstanceCount(*args):
    c1 = args[0]
    c2 = args[1]
    query ="""
    SELECT (COUNT(?instance) AS ?instanceCount)
      WHERE { 
        ?instance a <"""+ c1 +""">.
        ?instance a <"""+ c2 +"""> . 
      }
    """
    results = executeQuery(query)
    return results[0]["instanceCount"]["value"]
  

def checkSubAndEquivalentClass(*args):
    c1 = args[0]
    c2 = args[1]
    c1Count = instanceCount(c1)
    c2Count = instanceCount(c2)
    # i = len(properSubset)
    c1c2Count = commonInstanceCount(c1,c2)
    if (c1Count < c2Count): 
        if(c1c2Count == c1Count):
            properSubset.append({"subclass":c1, "class":c2})
    elif c2Count < c1Count:
        if(c1c2Count == c2Count):
            properSubset.append({"subclass":c2, "class":c1})
    elif c1c2Count == c1Count and c1c2Count == c2Count:
            equivalentClass.append({"c1":c1,"c2":c2})

# def checkEquivalentClass(*args):
#     c1 = args[0]
#     c2 = args[1]
#     c1Count = instanceCount(c1)
#     c2Count = instanceCount(c2)
#     c1c2Count = commonInstanceCount(c1,c2)
#     if(c1c2Count == c1Count and c1c2Count == c2Count):
#             equivalentClass.append({"c1":c1,"c2":c2})



@app.route('/sparql')
def sparqlTest():    
    sparqlEndpoint()
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
