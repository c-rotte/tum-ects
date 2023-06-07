import os
import time
from crawler import Crawler
from concurrent.futures import ThreadPoolExecutor

from database.database import Module, Degree, Mapping, init_db


class Worker:
    def __init__(self, crawler: Crawler, module_id: str):
        self.crawler = crawler
        self.module_id = module_id

    def run(self):
        # insert mapping
        try:
            for degree_id, mapping_info in self.crawler.module_degree_mappings(self.module_id):
                degree_exists = Degree.select().where(Degree.degree_id == degree_id).exists()
                module_exists = Module.select().where(Module.module_id == self.module_id).exists()
                if not degree_exists or not module_exists:
                    # skip mapping if degree or module does not exist
                    # (the module should exist, but we check it anyway)
                    continue
                Mapping.insert(
                    degree_id=degree_id,
                    module_id=self.module_id,
                    degree_version=mapping_info["version"],
                    ects=mapping_info["ects"],
                    valid_from=mapping_info["valid_from"],
                    valid_to=mapping_info["valid_to"],
                    weighting_factor=mapping_info["weighting_factor"]
                ).on_conflict_replace().execute()
        except Exception as e:
            print(f"Error inserting mapping: {e}")


def run_crawler(max_workers=1):
    crawler = Crawler()
    for degree_id, degree_info in crawler.degrees():
        Degree.insert(
            degree_id=degree_id, **degree_info
        ).on_conflict_replace().execute()

    executor = ThreadPoolExecutor(max_workers=max_workers)
    for module_id, module_info in crawler.modules():
        Module.insert(
            module_id=module_id,
            module_name_en=module_info["name_en"],
            module_name_de=module_info["name_de"],
            module_nr=module_info["nr"]
        ).on_conflict_replace().execute()
        # get all module mappings in parallel
        worker = Worker(crawler, module_id)
        executor.submit(worker.run)

    executor.shutdown(wait=True)


if __name__ == "__main__":
    print("Connecting to database... ")
    init_db()
    max_workers = int(os.getenv("MAX_WORKERS", 1))
    print(f"Running crawler with {max_workers} workers")
    start_time = time.time()
    run_crawler(max_workers)
    print(f"Finished crawling in {time.time() - start_time} seconds")