import os
from crawler import Crawler
from database import TUMDatabase
from concurrent.futures import ThreadPoolExecutor


class Worker:

    def __init__(self, crawler: Crawler, database: TUMDatabase, module_id: str):
        self.crawler = crawler
        self.database = database
        self.module_id = module_id

    def run(self):
        # insert english modules names
        for mapping in self.crawler.module_degree_mappings(self.module_id, english=True):
            self.database.upsert_mapping(self.module_id, mapping)
        # insert german module names
        for mapping in self.crawler.module_degree_mappings(self.module_id, english=False):
            self.database.upsert_mapping(self.module_id, mapping)


def run_crawler(database: TUMDatabase, max_workers=1):
    crawler = Crawler()
    # we don't have to parallelize this because it's only one request
    # insert english degree names
    for degree in crawler.degrees(english=True):
        database.upsert_degree(degree["id"], name_en=degree["text"], name_de=None)

    # insert german degree names
    for degree in crawler.degrees(english=False):
        database.upsert_degree(degree["id"], name_en=None, name_de=degree["text"])

    executor = ThreadPoolExecutor(max_workers=max_workers)
    # get all module mappings in parallel
    # insert english module names
    for module_id, module_name in crawler.modules(english=True):
        database.upsert_module(module_id, name_en=module_name, name_de=None)
        worker = Worker(crawler, database, module_id)
        executor.submit(worker.run)

    # insert german module names
    for module_id, module_name in crawler.modules(english=False):
        database.upsert_module(module_id, name_en=None, name_de=module_name)

    executor.shutdown(wait=True)


if __name__ == '__main__':

    mongodb_connection = os.getenv('MONGODB', 'mongodb://localhost:27017')
    print('Connecting to MongoDB... ')
    database = TUMDatabase(mongodb_connection)
    if database.connection_error:
        print(f'Could not connect to <{mongodb_connection}>.')
        print(database.connection_error)
        exit(-1)

    max_workers = int(os.getenv("MAX_WORKERS", 1))
    run_crawler(database, max_workers)
