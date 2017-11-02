from rdflib import Graph
from rdflib import ConjunctiveGraph, Namespace, Literal
from rdflib.store import NO_STORE, VALID_STORE
import pprint

import logging

logging.basicConfig()
source = "test"
triplestore_name = "triplestore_" + source
path = '../data/' + triplestore_name
graph = ConjunctiveGraph('Sleepycat')
rt = graph.open(path, create=False)

if rt == NO_STORE:
        # There is no underlying Sleepycat infrastructure, create it
    graph.open(path, create=True)
else:
    assert rt == VALID_STORE, 'The underlying store is corrupt'

# g.parse("lod_files/linkedmdb-latest-dump.nt", format="nt")
# g.parse("lod_files/ring-rdf-dump-datasets.xml")

# g.parse("lod_files/lod.b3kat.de.part0.ttl", format="ttl")
# g.parse("http://dbpedia.org/data3/Place.ntriples", format="nt")
# g.parse("lod_files/lwapis_v1.nt", format="nt") #529369 https://old.datahub.io/dataset/linked-web-apis



for i in range(0, 1):
    g = Graph()
    print i
    folder = "temp_" + source
    path = "../data/temp_linkedmdb/file"+str(i)+".nt"
    # path = "../data/lod_files/canlink-current.ttl"
    # path = "../data/"+folder+"/file.nt"
    print path
    g.parse(path, format="ttl") 
    print "parse complete"
    graph.add(g)        
        # close when done, otherwise sleepycat will leak lock entries.
        
graph.close()
    


# print len(g) # prints 2

# import pprint
# for stmt in g:
#     pprint.pprint(stmt)