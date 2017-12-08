import rethinkdb as r
import os
database_name = "cultura"
database_name = "kupkb"
database_name = "jamendo"
database_name = "linkedmdb"
database_name = "jamendo"


database_name = "archiveshub"
database_name = "aat"

print(os.environ['DB_URL'])
def conn(table):    
    r.connect(os.environ['DB_URL'], 28015).repl()
    return r.db(database_name).table(table)

def get_r():
    return r

def get_class_name(url):
    temp = url.rsplit('/', 1)[-1]
    return temp.rsplit('#',1)[-1]

def return_array(*args):
    classes = args[0]
    len = args[1]
    class_arr = [None] * len
    index = 0
    for i, c in enumerate(classes):
        class_arr[index] = c  # ["class"]
        index += 1
    return class_arr