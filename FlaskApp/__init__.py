#sudo fuser -k 9001/tcp
from flask import Flask, render_template
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import defaultdict
properties = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
equivalentClass = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
properSubset = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))

app = Flask(__name__)
endpoint = ""

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
    # loopClasses(classes)
    instanceCount(classes[0])
    #popertyBetweenClass(classes[0], classes[1])
    return render_template("sparql.html", results=classes, page="class")

def loopClasses(classes):
    for i,c in enumerate(classes):
        # print (i, c)
        for j in range(i+1, len(classes)-1):
            popertyBetweenClass(classes[i], classes[j])
            popertyBetweenClass(classes[j], classes[i])
  
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
    i = 0
    for result in results:
        properties[c1][c2][i]= result["prop"]["value"]
        # print properties[c1][c2][i]
        # print "------"
        i += 1   
    pass

def instanceCount(c1):
    query = """
        SELECT COUNT(?instance) as ?instanceCount
        WHERE {
            ?instance a <""" + c1 + """>
        }
    """
    results = executeQuery(query)
    print results[0]["instanceCount"]["value"]
    pass


def commonInstanceCount(*args):
    c1 = args[0]
    c2 = args[1]
    query ="""
    SELECT (COUNT(?instance) AS ?instanceCount)
      WHERE { 
        ?instance a """+ c1 +""".
        ?instance a """+ c2 +""" . 
      }
    """
    results = executeQuery(query)
    print results[0]["instanceCount"]["value"]
    pass

def checkSubset(*args):
    c1 = args[0]
    c2 = args[1]
    c1Count = instanceCount(c1)
    c2Count = instanceCount(c2)
    i = len(properSubset)
    c1c2Count = commonInstanceCount(c1,c2)
    if (c1Count < c2Count):        
        if(c1c2Count == c1Count):
            properSubset[i] = [c1,c2]
    elif c2Count < c1Count:
        if(c1c2Count == c2Count):
            properSubset[i] = [c2,c1]
        
def checkEquivalentClass(*args):
    c1 = args[0]
    c2 = args[1]
    c1Count = instanceCount(c1)
    c2Count = instanceCount(c2)
    i = len(equivalentClass)
    c1c2Count = commonInstanceCount(c1,c2)
    if(c1c2Count == c1Count and c1c2Count == c2Count):
            equivalentClass[i] = [c1,c2]



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
