import pymongo


class Database:

    def __init__(self, mongo_conn):
        try:
            self.client = pymongo.MongoClient(mongo_conn)
            self.client.server_info()
            self.connection_error = None
        except Exception as e:
            self.connection_error = e
            return
        self.database = self.client["ects"]

    def get_module(self, degree_id, module_id):
        result = self.database["degrees"].aggregate([
            {
                "$match": {
                    "info.degree_id": degree_id,
                    "info.courses.module_id": module_id
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "module": {
                        "$first": {
                            "$filter": {
                                "input": "$info.courses",
                                "cond": {
                                    "$eq": [
                                        "$$this.module_id", module_id
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        ])
        result_list = list(result)
        if not result_list:
            return None
        return result_list[0]["module"]

    def status(self):
        return {
            "degrees": self.database["degrees"].count_documents({})
        }

