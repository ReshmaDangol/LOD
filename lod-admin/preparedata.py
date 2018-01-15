from common_functions import *


def assign_graph_id():
    cursor = conn("class").distinct().run()
    i = 0
    for document in cursor:
        id = document["id"]
        conn("class").filter({'id': id}).update({'graph_id': i}).run()
        i += 1


def prepare():
    # assign_graph_id()
    cursor = conn("class").distinct().run()
    # len_ = conn("class").distinct().count().run()
    # class_arr = return_array(cursor, len_)
    class_arr = list(cursor)
    len_ = len(class_arr)
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

            if(has_property12 > 0 or has_property21 > 0):
                if(has_property12 > 0 and has_property21 > 0):
                    s = c1
                    t = c2
                    bd = 1
                elif(has_property12 > 0):
                    s = c1
                    t = c2
                    bd = 0
                else:
                    s = c2
                    t = c1
                    bd = 0

                result = {
                    "source": s,
                    "target": t,
                    "bidirection": bd,
                    "intersect": 0,
                    "subclass": 0,
                    "linkid": str(i) + str(j) + "_property"
                }
                # print(result)
                conn("graph_data").insert(result).run()

        is_subclass = conn("subclass").filter(
            lambda class_:
            class_["subclass"].default('foo').eq(c1)
        ).run()

        for s in is_subclass:
            result = {
                "source": s["subclass"],
                "target": s["class"],
                "bidirection": 0,
                "intersect": 0,
                "subclass": 1,
                "linkid": str(i) + "_subclass"
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
                "source": s["c1"],
                "target": s["c1"] + "~~~" + s["c2"],
                "bidirection": 0,
                "intersect": 1,
                "subclass": 0,
                "linkid": str(i) + "_intersect"
            }

            if_exists = conn("graph_data").filter(
                get_r().row["linkid"].match("_intersect$")
            ).filter(
                lambda class_:
                (class_["source"].default('foo').eq(s["c1"]).and_(
                    class_["target"].default('foo').eq(s["c1"] + "~~~" + s["c2"])).or_(
                    class_["source"].default('foo').eq(s["c1"] + "~~~" + s["c2"]).and_(
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
                    "source": s["c1"] + "~~~" + s["c2"],
                    "target": s["c2"],
                    "bidirection": 0,
                    "intersect": 1,
                    "subclass": 0,
                    "linkid": str(i) + "_intersect_"
                }
                conn("graph_data").insert(result).run()

    for i, document in enumerate(cursor):
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

        conn("graph_data").filter({'id': id}).update(
            {'intersect': intersect, 'subclass': subclass, 'linkid': i}).run()


def prepare_propertydata():
    tempdata = list(conn("property").order_by(index=get_r().desc('count')).outer_join(
        conn("inverse_property"),
        lambda left, right:
            (left["p"].eq(right["p"])) #.and_(left["p"].ne(right["p2"]))
    ).zip().without('id').run())
    # pluck({'right': ['p', 'inverse']}, {'left': ['c1', 'c2', 'count', 'p']}).map(lambda doc: doc.merge({
    #     'c1': doc['left']['c1'],
    #     'c2': doc['left']['c2'],
    #     'count': doc['left']['count'],
    #     'p': doc['left']['p'],
    #     'p_i': doc['right']['inverse']})).run())#.without({'left', 'right'}).run())

    print(len(tempdata))
    conn("graph_data_property_temp").insert(tempdata).run()
    sparql_endpoint()
    for p in tempdata:
        try:
            for i in p["inverse"]:
                query = """
                SELECT (count(*) as ?count)
                WHERE{
                    ?s a <""" + p["c1"] + """>.
                    ?o a <""" + p["c2"]+ """>.
                    ?o <"""+i["p"]+"""> ?s
                } 
                """ 
                result = execute_query(query)
                count = result[0]["count"]["value"]
                i["count_"] = int(count)
        except:
            pass

    conn("graph_data_property_temp2").insert(tempdata).run()


    # tempdata2 = list(conn("property").order_by(index=get_r().desc('count')).inner_join(
    #     conn("inverse_property"),
    #     lambda left, right:
    #     (left["p"].eq(right["p2"])).and_(left["p"].ne(right["p1"]))
    # ).pluck({'right': ['p1', 'p2']}, {'left': ['c1', 'c2', 'count', 'p']}).map(lambda doc: doc.merge({
    #     'c1': doc['left']['c1'],
    #     'c2': doc['left']['c2'],
    #     'count': doc['left']['count'],
    #     'p': doc['left']['p'],
    #     'p_i': doc['right']['p1']})).without({'left', 'right'}).run())
    
    # print(len(tempdata2))
    # conn_db().table_create('graph_data_property_temp_').run()
    # conn("graph_data_property_temp_").insert(tempdata2).run()

    # conn_db().table_create('temp').run()
    # tempdata3 = list(conn("property").order_by(index=get_r().desc('count')).outer_join(
    #     conn("inverse_property"),
    #     lambda left, right:
    #     (left["p"].eq(right["p2"])).or_(left["p"].eq(right["p1"]))
    # ).zip().run())

    # conn("temp").insert(tempdata3).run()

    # tempdata4 = list(conn("temp").filter(
    #     lambda doc: (~doc.has_fields('p1'))
    # ).run())
    
    # print(len(tempdata4))
    # conn("graph_data_property_temp").insert(tempdata4).run()
    # conn_db().table_drop("temp").run()


def prepare_propertydata_part2():
    tempdata = conn("graph_data_property_temp").inner_join(
        conn("graph_data_property_temp").has_fields('p2'),
        lambda left, right:
        (left["c1"].eq(right["c2"])).and_(left["c2"].eq(
            right["c1"])).and_((left["p"].eq(right["p1"])).or_(left["p"].eq(right["p2"]))).and_(left["id"].ne(right["id"]))
    ).pluck({'right': ['c1', 'c2', 'count', 'p', 'p1', 'p2']}, {'left': ['c1', 'c2', 'count', 'p', 'p1', 'p2']}).map(
        lambda doc:
        doc.merge({
            # 'c1':doc['right']['c1'],
            # 'c2':doc['right']['c2'],
            # 'count':doc['right']['count'],
            # 'p':doc['right']['p'],
            # 'p1':doc['right']['p1'],
            # 'p2':doc['right']['p2'],
            # 'count2': doc['left']['count']
        })
    ).run()

    # print list(tempdata)

    conn("graph_data_property_temp2").insert(list(tempdata)).run()

    # conn("graph_data_property_temp").innerJoin(conn("graph_data_property_temp"), function(left, right){
    #     #  left("parent").eq(right("id"))
    #    return (left["c1"].eq(right["c1"])).and_(left["c2"].eq(right["c2"])).and_(left["p"].eq(right["p2"]))
    #     # .or( left("parent").eq("").and(left("id").eq(right("id"))))
    # }).merge(function(val) {
    # return {
    #     "left": {
    #     "parent": r.branch(
    #         val("left")("parent").eq(""),
    #         "",
    #         val("right")("label")
    #     )
    #     }
    # }
    # }).without({
    # "right": true
    # }).zip().orderBy("id")


# prepare()
# prepare_propertydata_part2()
prepare_propertydata()
