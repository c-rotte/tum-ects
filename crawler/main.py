import os
from crawler import Crawler
from concurrent.futures import ThreadPoolExecutor

from database.database import Module, Degree, Mapping, init_db


class Worker:
    def __init__(self, crawler: Crawler, module_id: str):
        self.crawler = crawler
        self.module_id = module_id

    def run(self):
        print(f"Starting worker for module {self.module_id}")
        # insert english modules names
        for degree_id, mapping_info in self.crawler.module_degree_mappings(
            self.module_id
        ):
            Mapping.insert(
                degree_id=degree_id, module_id=self.module_id, **mapping_info
            ).on_conflict_replace().execute()


def run_crawler(max_workers=1):
    crawler = Crawler()
    for degree_id, degree_info in crawler.degrees():
        Degree.insert(
            degree_id=degree_id, **degree_info
        ).on_conflict_replace().execute()

    executor = ThreadPoolExecutor(max_workers=max_workers)
    # get all module mappings in parallel
    for module_id, module_name_en, module_name_de in crawler.modules():
        print(f"Found module {module_id} ({module_name_en})")
        Module.insert(
            module_id=module_id,
            module_name_en=module_name_en,
            module_name_de=module_name_de,
        ).on_conflict_replace().execute()
        worker = Worker(crawler, module_id)
        executor.submit(worker.run)

    executor.shutdown(wait=True)


if __name__ == "__main__":
    print("Connecting to database... ")
    init_db()
    max_workers = int(os.getenv("MAX_WORKERS", 1))
    run_crawler(max_workers)
