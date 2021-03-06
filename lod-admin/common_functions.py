import rethinkdb as r
import os
from SPARQLWrapper import SPARQLWrapper, JSON
from http import cookies
endpoint = ""
database_name =""
C = cookies.SimpleCookie()
# database_name = "cultura"
# database_name = "kupkb"
# database_name = "jamendo"
# database_name = "linkedmdb"
# database_name = "jamendo"

# database_name = "aat"
# database_name = "archiveshub"


db_url = os.environ['DB_URL']
query_prefix = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
"""

print(db_url)
def set_db(db):
    
    C["database_name"] = db
    global database_name
    database_name = db
    # print(database_name)

set_db("education")
def get_db():
    database_name = C["database_name"].value
    # print(database_name)

def sparql_endpoint():
    get_db()
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
    # url11 = "http://localhost:5820/aat/query"
    # url12 = "http://localhost:5820/archiveshub/query"  # archives hub
    # url13 = "http://localhost:5820/jamendo/query"
    # url14 = "http://localhost:5820/linkedmdb/query"    

    url = "http://localhost:5820/" + database_name + "/query"

    endpoint = SPARQLWrapper(url)  # this should be user's input


def execute_query(query):
    get_db()
    endpoint.setQuery(query)
    endpoint.setReturnFormat(JSON)
    results = endpoint.query().convert()
    # print results
    # print len(results["results"]["bindings"])
    return results["results"]["bindings"]

def conn_db():
    get_db()
    r.connect(db_url, 28015).repl()
    return r.db(database_name)


def conn(table):
    get_db()
    r.connect(db_url, 28015).repl()
    return r.db(database_name).table(table)


def get_r():
    return r


def get_class_name(url):
    temp = url.rsplit('/', 1)[-1]
    return temp.rsplit('#', 1)[-1]

# def return_array(*args):
#     classes = args[0]
#     len = args[1]
#     class_arr = [None] * len
#     index = 0
#     for i, c in enumerate(classes):
#         class_arr[index] = c  # ["class"]
#         index += 1
#     return class_arr
