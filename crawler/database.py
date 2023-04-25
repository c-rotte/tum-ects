import pymongo


class TUMDatabase:

    def __init__(self, mongo_conn):
        try:
            self.client = pymongo.MongoClient(mongo_conn)
            self.client.server_info()
            self.connection_error = None
        except Exception as e:
            self.connection_error = e
            return
        self.database = self.client['tum']

    def upsert_degree(self, degree_id: str, name_en: str = None, name_de: str = None):
        """Upsert a degree into the database."""
        update_data = {}
        if name_en is not None:
            update_data['name_en'] = name_en
        if name_de is not None:
            update_data['name_de'] = name_de

        self.database.degrees.update_one(
            {'_id': degree_id},
            {'$set': update_data},
            upsert=True
        )

    def upsert_module(self, module_id: str, name_en: str = None, name_de: str = None):
        """Upsert a module into the database."""
        update_data = {}
        if name_en is not None:
            update_data['name_en'] = name_en
        if name_de is not None:
            update_data['name_de'] = name_de

        self.database.modules.update_one(
            {'_id': module_id},
            {'$set': update_data},
            upsert=True
        )

    def upsert_mapping(self, module_id: str, degree_id: str, mapping_data: dict):
        """Upsert a module degree mapping into the database."""
        self.database.mappings.update_one(
            {'module_id': module_id, 'degree_id': degree_id},
            {'$set': mapping_data},
            upsert=True
        )
