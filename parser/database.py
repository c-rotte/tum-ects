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
        self.database = self.client['tum']

    def add_degree(self, pStpStpNr, obj):
        self.database['degrees'].insert_one({'pStpStpNr': pStpStpNr, 'info': obj})

    def remove_degree(self, pStpStpNr):
        self.database['degrees'].delete_many(filter={'pStpStpNr': pStpStpNr})

    # curriculum collections: 'curricula-german' and 'curricula-english'
    def add_curriculum(self, degree_info,  language='english'):
        if language not in ['english', 'german']:
            raise ValueError(f'invalid curriculum language: {language}')
        self.database[f'curricula-{language}'].insert_one(degree_info)

    def remove_curriculum(self, pStpStpNr, language='english'):
        if language not in ['english', 'german']:
            raise ValueError(f'invalid curriculum language: {language}')
        self.database[f'curricula-{language}'].delete_many(filter={'pStpStpNr': pStpStpNr})
