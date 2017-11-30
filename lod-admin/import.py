from rdflib import Graph
from rdflib import ConjunctiveGraph, Namespace, Literal
from rdflib.store import NO_STORE, VALID_STORE
import pprint

import logging

logging.basicConfig()
source = "drugbank"
triplestore_name = "triplestore_" + source
path = '../data/' + triplestore_name
graph = ConjunctiveGraph('Sleepycat')
rt = graph.open(path, create=False)

if rt == NO_STORE:
        # There is no underlying Sleepycat infrastructure, create it
    graph.open(path, create=True)
else:
    assert rt == VALID_STORE, 'The underlying store is corrupt'

for i in range(0, 1):
    g = ConjunctiveGraph()
    print i
    folder = "temp_" + source
    path = "../data/"+folder+"/file"+str(i)+".nq"
    # path = "../data/"+folder+"/file.nq"
    print path
    g.parse(path, format="nquads") 
    print "parse complete"
    
    for stmt in g:
        # pprint.pprint(stmt)
        graph.add(stmt)
        # graph.add((rdflib['pic:1'], rdflib.name, Literal('Jane & Bob')))
        
graph.close()
    