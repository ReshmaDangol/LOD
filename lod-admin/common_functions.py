import rethinkdb as r
import os
database_name = "cultura"
database_name = "kupkb"
database_name = "jamendo"
database_name = "linkedmdb"
database_name = "jamendo"


database_name = "archiveshub"
database_name = "aat"


def conn(table):
    print(os.environ)
    r.connect(os.environ['DB_URL'], 28015).repl()
    return r.db(database_name).table(table)

def get_r():
    return r

def get_class_name(url):
    temp = url.rsplit('/', 1)[-1]
    return temp.rsplit('#',1)[-1]