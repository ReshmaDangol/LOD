from common_functions import *

classlist = []
def modify_equiv_class():
    cursor = conn("equivalentclass").run()
    result = []
    for row in cursor:
        c1 = row["c1"]
        c2 = row["c2"]
        id = row["id"]
        classlist = []

        search = conn("equivalentclass").filter(
            (r.row["c1"] == c1) | (r.row["c1"] == c2) | (r.row["c2"] == c1) | (r.row["c2"] == c2)
        ).filter(r.row["id"] != id).run()

        for s in search:
            classlist.append(s["c1"])
            classlist.append(s["c2"])                    
        
        classlist = sorted(list(set(classlist)), key=str.lower)
        groupname = "_".join(get_class_name(str(x)) for x in classlist)

        # groupname = get_class_name(row["c1"]) + "-" + get_class_name(row["c2"])
        result.append({
            "class": row["c1"],
            "group": groupname
        })
        result.append({
            "class": row["c2"],
            "group": groupname
        })

    print(result)
    # conn("equivalentclass_group").insert(result).run()


modify_equiv_class()
