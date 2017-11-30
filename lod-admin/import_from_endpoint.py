from rdflib import Graph
from rdflib import ConjunctiveGraph, Namespace, Literal, RDF, URIRef
from rdflib.store import NO_STORE, VALID_STORE
import pprint
from SPARQLWrapper import SPARQLWrapper, JSON, XML
import logging
from xml.dom.minidom import parse, parseString

logging.basicConfig()
path = '../data/triplestore_ring'
graph = ConjunctiveGraph('Sleepycat')
rt = graph.open(path, create=False)

if rt == NO_STORE:
        # There is no underlying Sleepycat infrastructure, create it
    graph.open(path, create=True)
else:
    assert rt == VALID_STORE, 'The underlying store is corrupt'



url = "http://ring.ciard.net/sparql1"
endpoint = SPARQLWrapper(url)

offset = 12803 #12770
resultcount = 1
resultlimit = resultcount
while (resultcount == resultlimit):
# i=0
# while (i == 0):
#     i = 1
    query = """select * where
            {
            ?s ?p ?o .
            }
        Limit """+ str(resultlimit) +""" offset """ + str(offset)
    
    print query
    offset += resultlimit
    endpoint.setQuery(query)
    endpoint.setReturnFormat(XML)
    results = endpoint.query().convert()  
    # results = endpoint.query()
    # pp = pprint.PrettyPrinter(depth=6)
    # pp.pprint(results) 
    # print results["results"]
    # qres = results["results"]["bindings"]
    print parseString(results)
    
    resultcount = 0
    # for row in qres:
    #     # print row
    #     resultcount += 1
    #     # print row['s']['value'] +" - "+ row['p']['value'] +" - "+ row['o']['value'] +" - "+ row['label']['value']
    #     if (row['s']['value'].startswith('http://')):
    #         s = URIRef(row['s']['value'])
    #     else:
    #         s = Literal(row['s']['value'])
        
    #     if (row['p']['value'].startswith('http://')):
    #         p = URIRef(row['p']['value'])
    #     else:
    #         p = Literal(row['p']['value'])

    #     if (row['o']['value'].startswith('http://')):
    #         o = URIRef(row['o']['value'])
    #     else:
    #         o = Literal(row['o']['value'])
          
        # graph.add((s,p,o))
        # graph.add((URIRef(row['s']['value']), URIRef(row['p']['value']), URIRef(row['o']['value'])))
    print "---"  
graph.close()
    


# print len(g) # prints 2

# import pprint
# for stmt in g:
#     pprint.pprint(stmt)