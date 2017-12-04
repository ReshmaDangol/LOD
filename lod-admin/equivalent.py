from common_functions import *


def modify_equiv_class():
    cursor = conn("equivalentclass").run()
    result = []
    for row in cursor:
        groupname = get_class_name(row["c1"]) + "-" + get_class_name(row["c2"])
        result.append({
            "class": row["c1"],
            "group": groupname
        })
        result.append({
            "class": row["c2"],
            "group": groupname
        })

    conn("equivalentclass_group").insert(result).run()

modify_equiv_class()