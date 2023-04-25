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
        for mapping in self.crawler.module_degree_mappings(self.module_id):
            self.database.upsert_mapping(self.module_id, mapping)


def run_crawler(database: TUMDatabase, max_workers=1):
    crawler = Crawler()
    # we don't have to parallelize this because it's only one request
    for degree in crawler.degrees():
        database.upsert_degree(degree)

    executor = ThreadPoolExecutor(max_workers=max_workers)
    # get all module mappings in parallel
    for module_id, module_name in crawler.modules():
        database.upsert_module(module_id, module_name)
        worker = Worker(crawler, database, module_id)
        executor.submit(worker.run)

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
