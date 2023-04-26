import os
from crawler import Crawler
from database import TUMWriteDatabase
from concurrent.futures import ThreadPoolExecutor


class Worker:

    def __init__(self, crawler: Crawler, database: TUMWriteDatabase, module_id: str):
        self.crawler = crawler
        self.database = database
        self.module_id = module_id

    def run(self):
        # insert english modules names
        for degree_id, mapping_info in self.crawler.module_degree_mappings(self.module_id):
            self.database.insert_mapping(self.module_id,
                                         degree_id,
                                         mapping_info["version"],
                                         mapping_info["ects"],
                                         mapping_info["weighting_factor"],
                                         mapping_info["valid_from"],
                                         mapping_info["valid_to"])


def run_crawler(database: TUMWriteDatabase, max_workers=1):
    crawler = Crawler()
    # we don't have to parallelize this because it's only one request
    degrees = crawler.degrees()
    for degree_id in degrees:
        database.insert_degree(degree_id,
                               degrees[degree_id]["full_text_en"],
                               degrees[degree_id]["short_text_en"],
                               degrees[degree_id]["full_text_de"],
                               degrees[degree_id]["short_text_de"])

    executor = ThreadPoolExecutor(max_workers=max_workers)
    # get all module mappings in parallel
    for module_id, module_name_en, module_name_de in crawler.modules():
        database.insert_module(module_id,
                               module_name_en,
                               module_name_de)
        worker = Worker(crawler, database, module_id)
        executor.submit(worker.run)

    executor.shutdown(wait=True)


if __name__ == '__main__':

    mongodb_connection = os.getenv('MONGODB', 'mongodb://localhost:27017')
    print('Connecting to MongoDB... ')
    database = TUMWriteDatabase(name="tum-ects",
                                host="127.0.0.1",
                                user="postgres",
                                password="postgres",
                                port=int(os.getenv("DATABASE_PORT", 5432)))
    if database.connection_error:
        print(f'Could not connect to <{mongodb_connection}>.')
        print(database.connection_error)
        exit(-1)

    max_workers = int(os.getenv("MAX_WORKERS", 1))
    run_crawler(database, max_workers)
