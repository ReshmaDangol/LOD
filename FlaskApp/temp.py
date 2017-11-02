from rdflib import Graph

g = Graph()
g.parse("demo.nt", format="nt")

len(g) # prints 2

import pprint
for stmt in g:
    pprint.pprint(stmt)
