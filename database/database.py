import os

from peewee import (
    CharField,
    Model,
    DatabaseProxy,
    IntegerField,
    FloatField,
    CompositeKey,
    SQL,
    SqliteDatabase,
    PostgresqlDatabase,
)

db = DatabaseProxy()


class BaseDatabase:
    def __init__(self):
        if not isinstance(db, DatabaseProxy):
            return
        if os.getenv("DB_TYPE") == "sqlite":
            db_conn = SqliteDatabase(os.getenv("SQLITE_PATH"), pragmas={"foreign_keys": 1})
        else:
            db_conn = PostgresqlDatabase(
                database="tumgrades",
                host="database",
                user="tumgrades",
                password="tumgrades",
                port=int(os.getenv("DATABASE_PORT", 5432)),
            )
        db.initialize(db_conn)
        db.create_tables(BaseModel.__subclasses__())


class BaseModel(Model):
    class Meta:
        database = db


class Degree(BaseModel):
    degree_id = IntegerField(primary_key=True)
    full_text_en = CharField()
    short_text_en = CharField()
    full_text_de = CharField()
    short_text_de = CharField()


class Module(BaseModel):
    module_id = IntegerField(primary_key=True)
    name_en = CharField()
    name_de = CharField()


class Mapping(BaseModel):
    degree_id = IntegerField()
    module_id = IntegerField()
    degree_version = CharField()
    ects = FloatField()
    weighting_factor = FloatField()
    valid_from = CharField()
    valid_to = CharField()

    class Meta:
        primary_key = CompositeKey("degree_id", "module_id", "degree_version")
        constraints = [
            SQL("FOREIGN KEY(degree_id) REFERENCES degrees(degree_id) ON DELETE CASCADE"),
            SQL("FOREIGN KEY(module_id) REFERENCES modules(module_id) ON DELETE CASCADE"),
        ]


