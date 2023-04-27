import os
from crawler import Crawler
from concurrent.futures import ThreadPoolExecutor

from database.tumwrite import TUMWriteDatabase


class Worker:

    def __init__(self, crawler: Crawler, database: TUMWriteDatabase, module_id: str):
        self.crawler = crawler
        self.database = database
        self.module_id = module_id

    def run(self):
        print(f"Starting worker for module {self.module_id}")
        # insert english modules names
        for degree_id, mapping_info in self.crawler.module_degree_mappings(self.module_id):
            self.database.insert_mapping(degree_id,
                                         self.module_id,
                                         mapping_info["version"],
                                         mapping_info["ects"],
                                         mapping_info["weighting_factor"],
                                         mapping_info["valid_from"],
                                         mapping_info["valid_to"])


def run_crawler(database: TUMWriteDatabase, max_workers=1):
    crawler = Crawler()
    for degree_id, degree_info in crawler.degrees():
        database.insert_degree(degree_id,
                               degree_info["nr"],
                               degree_info["full_name_en"],
                               degree_info["full_name_de"],
                               degree_info["subtitle_en"],
                               degree_info["subtitle_de"],
                               degree_info["version"])

    executor = ThreadPoolExecutor(max_workers=max_workers)
    # get all module mappings in parallel
    for module_id, module_name_en, module_name_de in crawler.modules():
        print(f"Found module {module_id} ({module_name_en})")
        database.insert_module(module_id,
                               module_name_en,
                               module_name_de)
        worker = Worker(crawler, database, module_id)
        executor.submit(worker.run)

    executor.shutdown(wait=True)


if __name__ == '__main__':
    print('Connecting to database... ')
    database = TUMWriteDatabase()

    max_workers = int(os.getenv("MAX_WORKERS", 1))
    run_crawler(database, max_workers)
