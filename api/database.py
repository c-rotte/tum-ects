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
        self.database = self.client["tum"]

    def get_all_pStpStpNrs(self, language="english"):
        if language not in ["english", "german"]:
            raise ValueError(f"invalid curriculum language: {language}")
        result = self.database[f"curricula-{language}"].aggregate([
            {"$group": {
                "_id": "null",
                "pStpStpNrs": {
                    "$push": "$pStpStpNr"
                }
            }},
            {"$project": {"_id": 0}}
        ])
        result_list = list(result)
        if not result_list:
            return None
        return result_list[0]

    def get_curriculum(self, pStpStpNr, language="english"):
        if language not in ["english", "german"]:
            raise ValueError(f"invalid curriculum language: {language}")
        result = self.database[f"curricula-{language}"].find_one(
            {"pStpStpNr": pStpStpNr},
            {"_id": 0, "curriculum": 1}
        )
        return result

    def get_modules(self, pStpStpNr, language="english"):
        if language not in ["english", "german"]:
            raise ValueError(f"invalid curriculum language: {language}")
        result = self.database[f"curricula-{language}"].find_one(
            {"pStpStpNr": pStpStpNr},
            {"_id": 0, "modules": 1}
        )
        return result

    def get_module(self, pStpStpNr, module_id, language="english"):
        if language not in ["english", "german"]:
            raise ValueError(f"invalid curriculum language: {language}")
        result = self.database[f"curricula-{language}"].aggregate([
            {"$match": {
                "pStpStpNr": pStpStpNr,
                "modules.module_id": module_id
            }},
            {"$project": {"_id": 0,
                          "module": {"$first": {"$filter": {
                              "input": "$modules",
                              "cond": {"$eq": ["$$this.module_id", module_id]}}}}}
             }
        ])
        result_list = list(result)
        if not result_list:
            return None
        return result_list[0]["module"]

    def get_pStpStpNrs_with_module(self, module_id, language="english"):
        if language not in ["english", "german"]:
            raise ValueError(f"invalid curriculum language: {language}")
        result = self.database[f"curricula-{language}"].aggregate([
            {"$match": {
                "modules.module_id": module_id
            }},
            {"$group": {
                "_id": "null",
                "pStpStpNrs": {
                    "$push": "$pStpStpNr"
                }
            }},
            {"$project": {"_id": 0}}
        ])
        result_list = list(result)
        if not result_list:
            return None
        return result_list[0]

    def get_pStpStpNrs_with_degree(self, degree_id, language="english"):
        if language not in ["english", "german"]:
            raise ValueError(f"invalid curriculum language: {language}")
        result = self.database[f"curricula-{language}"].aggregate([
            {"$match": {
                "degree_id": degree_id
            }},
            {"$group": {
                "_id": "null",
                "pStpStpNrs": {
                    "$push": "$pStpStpNr"
                }
            }},
            {"$project": {"_id": 0}}
        ])
        result_list = list(result)
        if not result_list:
            return None
        return result_list[0]

    def status(self):
        crawled_degrees_de = self.database["curricula-german"].count_documents({})
        crawled_degrees_en = self.database["curricula-english"].count_documents({})
        return {
            "crawled_degrees": {
                "german": crawled_degrees_de,
                "english": crawled_degrees_en
            }
        }
