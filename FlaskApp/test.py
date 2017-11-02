from rdflib import ConjunctiveGraph, Namespace, Literal 
path = './mytriplestore'
graph = ConjunctiveGraph('Sleepycat')
graph.open(path, create = False)
query = """SELECT count(?o)
   WHERE {
     <http://lod.b3kat.de/title/BV000524797#item-DE-824> ?p ?o.
   }
   Limit 10"""

qres = graph.query(query)
for row in qres:
   print row