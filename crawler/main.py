import os
from crawler import Crawler
from database import Database
from concurrent.futures import ThreadPoolExecutor


class Worker:

    def __init__(self, crawler: Crawler, database: Database, module_id: str):
        self.crawler = crawler
        self.database = database
        self.module_id = module_id

    def run(self):
        for mapping in self.crawler.module_degree_mappings(self.module_id, english=True):
            # TODO: add mapping to database
            pass


def run_crawler(self, max_workers=1):
    for degree in self.crawler.degrees():
        # TODO: add degree to database
        pass
    executor = ThreadPoolExecutor(max_workers=max_workers)
    # check all numbers
    for module_id, module_name in self.crawler.modules():
        # TODO: add module to database
        worker = Worker(self.crawler, self.database, module_id)
        executor.submit(worker.run)
    executor.shutdown(wait=True)


if __name__ == '__main__':

    mongodb_connection = os.getenv('MONGODB', 'mongodb://localhost:27017')
    print('Connecting to MongoDB... ')
    database = Database(mongodb_connection)
    if database.connection_error:
        print(f'Could not connect to <{mongodb_connection}>.')
        print(database.connection_error)
        exit(-1)

    max_workers = int(os.getenv("MAX_WORKERS", 1))
    run_crawler(max_workers)
