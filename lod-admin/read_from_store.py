    
#sudo easy_install rdfextras 
# from flask import Flask, render_template

from rdflib import ConjunctiveGraph, Namespace, Literal
# from rdflib.store import NO_STORE, VALID_STORE    

import rdflib
from rdflib import plugin
# import logging
# logging.basicConfig()
# plugin.register(
#     'sparql', rdflib.query.Processor,
#     'rdfextras.sparql.processor', 'Processor')
# plugin.register(
#     'sparql', rdflib.query.Result,
#     'rdfextras.sparql.query', 'SPARQLQueryResult')


path = '../data/triplestore_linkedmdb'
graph = ConjunctiveGraph('Sleepycat')
graph.open(path, create = False)

# print('Triples still in graph: ', len(graph))
# graph.serialize(format='turtle')


query = """SELECT (count(?o) AS ?count)
       WHERE {
         <http://lod.b3kat.de/title/BV000053857> ?p ?o.
       }
       Limit 10"""
query = """SELECT distinct ?valType
       WHERE {
         ?s ?p ?o.
 BIND (datatype(?o) AS ?valType) . 
       }
       Limit 10"""

query = """SELECT (count(*) as ?count)
       WHERE {
         ?s ?p ?o.       }limit 10
      """

query= """SELECT DISTINCT ?class (count(?sub) AS ?instance_count)
      WHERE {
        ?sub a ?class. 
      } 
      GROUP BY ?class 
      ORDER BY DESC(?instance_count) Limit 10
      """
queryq= """
      select * where {?s ?p ?o} limit 10
"""

query = """
        SELECT (count(?instanceOfClassA) as ?count) ?prop 
            WHERE {
                ?instanceOfClassA a <http://xmlns.com/foaf/0.1/Document> . 
                ?instanceOfClassB a <http://www.w3.org/ns/dcat#Dataset> . 
                ?instanceOfClassA ?prop ?instanceOfClassB .
            } 
        GROUP BY ?prop 
        ORDER BY DESC(?count) limit 2
"""

query = """
        SELECT (count(?instanceOfClassA) as ?count) ?prop 
            WHERE {
                ?instanceOfClassA a <http://data.linkedmdb.org/resource/movie/actor> . 
                ?instanceOfClassB a <http://data.linkedmdb.org/resource/movie/writer> . 
                ?instanceOfClassA ?prop ?instanceOfClassB .
            } 
        GROUP BY ?prop 
        ORDER BY DESC(?count) limit 2
"""

SELECT (count(?instanceOfClassA) as ?count) ?prop 
            WHERE {
                ?instanceOfClassA a <http://purl.org/NET/c4dm/event.owl#Event> . 
                ?instanceOfClassB a <http://purl.org/ontology/bibo/Document> . 
                ?instanceOfClassA ?prop ?instanceOfClassB .
            } 
        GROUP BY ?prop 
        ORDER BY DESC(?count) limit 2


print query
qres = graph.query(query)
print "query executed"

print qres
print len(graph)
# for count in graph.query(query):
#     print "--"
#     print count


graph.close()