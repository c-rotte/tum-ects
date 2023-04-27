from database.database import Degree, Module, Mapping, init_db


class TUMWriteDatabase:
    def __init__(self):
        init_db()

    def insert_degree(self, degree_id, full_text_en, short_text_en, full_text_de, short_text_de):
        Degree.insert(
            degree_id=degree_id,
            full_text_en=full_text_en,
            short_text_en=short_text_en,
            full_text_de=full_text_de,
            short_text_de=short_text_de,
        ).on_conflict(
            conflict_target=Degree.degree_id,
            update={
                Degree.full_text_en: full_text_en,
                Degree.short_text_en: short_text_en,
                Degree.full_text_de: full_text_de,
                Degree.short_text_de: short_text_de,
            },
        ).execute()

    def insert_module(self, module_id, name_en, name_de):
        Module.insert(module_id=module_id, name_en=name_en, name_de=name_de).on_conflict(
            conflict_target=(Module.module_id),
            update={Module.name_en: name_en, Module.name_de: name_de},
        ).execute()

    def insert_mapping(
        self, degree_id, module_id, degree_version, ects, weighting_factor, valid_from, valid_to
    ):
        Mapping.insert(
            degree_id=degree_id,
            module_id=module_id,
            degree_version=degree_version,
            ects=ects,
            weighting_factor=weighting_factor,
            valid_from=valid_from,
            valid_to=valid_to,
        ).on_conflict(
            conflict_target=(Mapping.degree_id, Mapping.module_id),
            update={
                Mapping.degree_version: degree_version,
                Mapping.ects: ects,
                Mapping.weighting_factor: weighting_factor,
                Mapping.valid_from: valid_from,
                Mapping.valid_to: valid_to,
            },
        ).execute()
