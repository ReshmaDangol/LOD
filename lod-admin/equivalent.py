import common_functions as cf


def modify_equiv_class():
    cursor = cf.conn("equivalentclass").run()
    result = []
    for row in cursor:
        groupname = cf.get_class_name(row["c1"]) + "-" + cf.get_class_name(row["c2"])
        result.append({
            "class": row["c1"],
            "group": groupname
        })
        result.append({
            "class": row["c2"],
            "group": groupname
        })

    cf.conn("equivalentclass_group").insert(result).run()

modify_equiv_class()