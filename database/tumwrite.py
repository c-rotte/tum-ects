from database.database import Degree, Module, Mapping, init_db


class TUMWriteDatabase:
    def __init__(self):
        init_db()

    def insert_degree(self, degree_id, nr, full_name_en, full_name_de, subtitle_en, subtitle_de, version):
        Degree.insert(
            degree_id=degree_id,
            nr=nr,
            full_name_en=full_name_en,
            full_name_de=full_name_de,
            subtitle_en=subtitle_en,
            subtitle_de=subtitle_de,
            version=version
        ).on_conflict(
            conflict_target=Degree.degree_id,
            update={
                Degree.nr: nr,
                Degree.full_name_en: full_name_en,
                Degree.full_name_de: full_name_de,
                Degree.subtitle_en: subtitle_en,
                Degree.subtitle_de: subtitle_de,
                Degree.version: version
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
