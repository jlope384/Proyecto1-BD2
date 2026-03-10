from bson import ObjectId
from fastapi import Response

from bson import ObjectId

def serialize_doc(doc):
    if not doc:
        return doc

    if "_id" in doc:
        doc["_id"] = str(doc["_id"])

    for key, value in doc.items():

        if isinstance(value, ObjectId):
            doc[key] = str(value)

        elif isinstance(value, dict):
            doc[key] = serialize_doc(value)

        elif isinstance(value, list):
            new_list = []
            for item in value:
                if isinstance(item, dict):
                    new_list.append(serialize_doc(item))
                else:
                    new_list.append(item)
            doc[key] = new_list

    return doc


def allow_all_cors(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"