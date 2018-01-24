from common_functions import *


def modify_equiv_class():
    cursor = conn("equivalentclass").run()
    result = []
    classlist = []
    for row in cursor:
        c1 = row["c1"]
        c2 = row["c2"]
        id = row["id"]
        group_classlist = []

        search = conn("equivalentclass").filter(
            (r.row["c1"] == c1) | (r.row["c1"] == c2) | (
                r.row["c2"] == c1) | (r.row["c2"] == c2)
        ).filter(r.row["id"] != id).run()

        for s in search:
            group_classlist.append(s["c1"])
            group_classlist.append(s["c2"])

        group_classlist = sorted(list(set(group_classlist)), key=str.lower)
        groupname = "_".join(get_class_name(str(x)) for x in group_classlist)

        # groupname = get_class_name(row["c1"]) + "-" + get_class_name(row["c2"])
        if(c1 not in classlist):
            classlist.append(c1)
            result.append({
                "class": c1,
                "group": groupname
            })
        if(c2 not in classlist):
            classlist.append(c2)
            result.append({
                "class": c2,
                "group": groupname
            })
    conn("equivalentclass_group").insert(result).run()


modify_equiv_class()
