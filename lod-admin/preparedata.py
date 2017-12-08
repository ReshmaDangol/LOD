from common_functions import *


def assign_graph_id():
    cursor = conn("class").distinct().run()
    i=0
    for document in cursor:
        id = document["id"]
        conn("class").filter({'id':id}).update({'graph_id':i}).run()
        i+=1
    
def prepare():
    # assign_graph_id()
    cursor = conn("class").distinct().run()
    len_ = conn("class").distinct().count().run()
    class_arr = return_array(cursor, len_)
    print(len_)
    for i in range(0, len_ - 1):
        for j in range(i + 1, len_):
            c1 = class_arr[i]["class"]
            c2 = class_arr[j]["class"]
            # graph_id1 = class_arr[i]["graph_id"]
            # graph_id2 = class_arr[j]["graph_id"]
            
            has_property12 = conn("property").filter(
                lambda class_:
                    class_["c1"].default('foo').eq(c1).and_(
                    class_["c2"].default('foo').eq(c2)
                )
            ).count().run()
            has_property21 = conn("property").filter(
                lambda class_:
                    class_["c1"].default('foo').eq(c2).and_(
                    class_["c2"].default('foo').eq(c1)
                )
            ).count().run()
            
            if(has_property12>0 or has_property21>0):
                if(has_property12>0 and has_property21>0):
                    s = c1 
                    t = c2
                    bd = 1
                elif(has_property12>0):
                    s = c1 
                    t = c2
                    bd = 0
                else:
                    s = c2 
                    t = c1
                    bd = 0
                
                result = {
                            "source" : s, 
                            "target" : t,
                            "bidirection" : bd,
                            "intersect" : 0,
                            "subclass" : 0,
                            "linkid" : str(i)+"_property"
                        }
                # print(result)
                conn("graph_data").insert(result).run()

            
        is_subclass = conn("subclass").filter(
                 lambda class_:
                    class_["subclass"].default('foo').eq(c1)
        ).run()

        for s in is_subclass:
            result = {
                            "source" : s["subclass"], 
                            "target" : s["class"],
                            "bidirection" : 0,
                            "intersect" : 0,
                            "subclass" : 1,
                            "linkid" : str(i)+"_subclass"
                        }            
            conn("graph_data").insert(result).run()

        is_intersect = conn("intersection").filter(
                 lambda class_:
                    class_["c1"].default('foo').eq(c1).or_(
                    class_["c2"].default('foo').eq(c1)
                    )
            ).run()

        for s in is_intersect:      
            result = {
                            "source" : s["c1"], 
                            "target" : s["c1"] + "~~~" + s["c2"],
                            "bidirection" : 0,
                            "intersect" : 1,
                            "subclass" : 0,
                            "linkid" : str(i)+"_intersect"
                        }    

            if_exists = conn("graph_data").filter(
                get_r().row["linkid"].match("_intersect$")
            ).filter(
                    lambda class_:
                        (class_["source"].default('foo').eq(s["c1"]).and_(
                        class_["target"].default('foo').eq(s["c1"]+"~~~"+s["c2"])).or_(
                        class_["source"].default('foo').eq(s["c1"]+"~~~"+s["c2"]).and_(
                        class_["target"].default('foo').eq(s["c2"])
                        )
                        )
                    )
                ).count().run()

            if if_exists == 0:
                print(s["c1"])
                print(s["c2"])
                print("---")
                conn("graph_data").insert(result).run()
                result = {
                            "source" : s["c1"] + "~~~" + s["c2"], 
                            "target" : s["c2"],
                            "bidirection" : 0,
                            "intersect" : 1,
                            "subclass" : 0,
                            "linkid" : str(i)+"_intersect_"
                        }  
                conn("graph_data").insert(result).run()




    for i,document in enumerate(cursor):
        c = document["class"]
        id = document["id"]
        is_subclass = conn("subclass").filter(
            lambda class_: class_["subclass"] == c).count().run()
        subclass = 1 if is_subclass > 0 else 0

        does_intersect = conn("intersection").filter(
            lambda class_:
                class_["c1"].default('foo').eq(c).or_(
                class_["c2"].default('foo').eq(c)
            )
        ).count().run()
        intersect = 1 if does_intersect > 0 else 0

        conn("graph_data").filter({'id':id}).update({'intersect':intersect,'subclass':subclass,'linkid':i}).run()
   

prepare()