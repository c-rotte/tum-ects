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

    def add_degree(self, pStpStpNr, obj):
        self.database["degrees"].insert_one({"pStpStpNr": pStpStpNr, "info": obj})

    def remove_degree(self, pStpStpNr):
        self.database["degrees"].delete_many(filter={"pStpStpNr": pStpStpNr})
