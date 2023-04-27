from database.database import Module, Degree, Mapping, init_db


class TUMReadDatabase():
    def __init__(self):
        init_db()

    def get_number_of_modules(self):
        return Module.select().count()

    def get_module_info(self, module_id):
        return Module.select().where(Module.module_id == module_id).dicts().first()

    def get_number_of_degrees(self):
        return Degree.select().count()

    def get_all_degrees(self):
        return Degree.select().dicts()

    def get_degree_info(self, degree_id: int):
        return Degree.select().where(Degree.degree_id == degree_id).dicts().first()

    def get_modules_of_degree(self, degree_id, valid_from=None, valid_to=None, degree_version=None):
        condition = Mapping.degree_id == degree_id

        if valid_from:
            condition &= Mapping.valid_from >= valid_from

        if valid_to:
            condition &= Mapping.valid_to <= valid_to

        if degree_version:
            condition &= Mapping.degree_version == degree_version

        return Module.select().join(Mapping).where(condition).dicts()

    def get_number_of_mappings(self):
        return Mapping.select().count()
