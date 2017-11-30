
from flask import Flask, render_template
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import defaultdict
import rethinkdb as r
from flask import jsonify

from rdflib import ConjunctiveGraph, Namespace, Literal
import rdflib
from rdflib import plugin
from urllib2 import Request, urlopen, URLError
import json

import common_functions as cf
app = Flask(__name__)

url="http://localhost:5000/"

def on_page_load():
    request = Request(url + 'classlist')
    try:
        response = urlopen(request)
        nodes =  json.loads(response.read())
        
        return nodes
    except URLError, e:
        print 'error', e

@app.route("/")
def load_page():    
    return render_template("index.html", nodes=on_page_load(), page="index")    

on_page_load()
if __name__ == "__main__":
    app.run(debug=True,port=9000)
