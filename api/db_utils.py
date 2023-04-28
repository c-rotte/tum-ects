from database.database import Mapping, Module


def get_modules_of_degree(self, degree_id, valid_from=None, valid_to=None, degree_version=None):
    condition = Mapping.degree_id == degree_id
    if valid_from:
        condition &= Mapping.valid_from >= valid_from

    if valid_to:
        condition &= Mapping.valid_to <= valid_to

    if degree_version:
        condition &= Mapping.degree_version == degree_version

    return Module.select().join(Mapping).where(condition).dicts()