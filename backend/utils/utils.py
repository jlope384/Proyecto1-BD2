from bson import ObjectId

def serialize_doc(doc):
    if not doc:
        return doc

    doc["_id"] = str(doc["_id"])

    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)

        if isinstance(value, list):
            new_list = []
            for item in value:
                if isinstance(item, dict):
                    new_list.append(serialize_doc(item))
                else:
                    new_list.append(item)
            doc[key] = new_list

    return doc