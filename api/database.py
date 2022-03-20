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

    def get_all_degree_ids(self):
        result = self.database["degrees"].aggregate([
            {"$group": {
                "_id": "null",
                "degree_ids": {
                    "$addToSet": "$info.degree_id"
                }
            }},
            {"$project": {"_id": 0}}
        ])
        result_list = list(result)
        if not result_list:
            return None
        return result_list[0]

    def get_degree(self, degree_id, list_modules):
        result = self.database["degrees"].find_one(
            {"info.degree_id": degree_id},
            {"_id": 0} if list_modules else {"_id": 0, "info.courses": 0}
        )
        return result

    def get_module(self, degree_id, module_id):
        result = self.database["degrees"].aggregate([
            {"$match": {
                "info.degree_id": degree_id,
                "info.courses.module_id": module_id
            }},
            {"$project": {"_id": 0,
                          "module": {"$first": {"$filter": {
                              "input": "$info.courses",
                              "cond": {"$eq": ["$$this.module_id", module_id]}}}}}
             }
        ])
        result_list = list(result)
        if not result_list:
            return None
        return result_list[0]["module"]

    def get_degrees_with_module(self, module_id):
        result = self.database["degrees"].aggregate([
            {"$match": {
                "info.courses.module_id": module_id
            }},
            {"$group": {
                "_id": "null",
                "degree_ids": {
                    "$addToSet": "$info.degree_id"
                }
            }},
            {"$project": {"_id": 0}}
        ])
        result_list = list(result)
        if not result_list:
            return None
        return result_list[0]

    def status(self):
        crawled_degrees = self.database["degrees"].count_documents({})
        return {
            "crawled_degrees": crawled_degrees
        }
