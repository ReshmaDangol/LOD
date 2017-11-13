import rethinkdb as r

database_name = "archiveshub"

def conn(table):
    r.connect( "localhost", 28015).repl()
    return r.db(database_name).table(table)

def get_r():
    return r

def get_class_name(url):
    temp = url.rsplit('/', 1)[-1]
    return temp.rsplit('#',1)[-1]