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
    PostgresqlDatabase, TextField,
)

db = DatabaseProxy()


def init_db():
    if not isinstance(db, DatabaseProxy):
        return
    if os.getenv("DB_TYPE") == "sqlite":
        db_conn = SqliteDatabase(os.getenv("SQLITE_PATH", "tumgrades.sqlite"), pragmas={"foreign_keys": 1})
    else:
        db_conn = PostgresqlDatabase(
            database=os.getenv("DATABASE", "postgres"),
            host=os.getenv("DATABASE_HOST", "database"),
            user=os.getenv("DATABASE_USER", "postgres"),
            password=os.getenv("DATABASE_PASSWORD", "postgres"),
            port=int(os.getenv("DATABASE_PORT", 5432)),
        )
    db.initialize(db_conn)
    db.create_tables([Degree, Module])
    # Mapping has foreign key constraints on Degree and Module, so we need to create it after the other tables
    db.create_tables([Mapping])


class BaseModel(Model):
    class Meta:
        database = db


class Degree(BaseModel):
    degree_id = IntegerField(primary_key=True)
    full_text_en = TextField(null=True)
    short_text_en = TextField(null=True)
    full_text_de = TextField(null=True)
    short_text_de = TextField(null=True)


class Module(BaseModel):
    module_id = IntegerField(primary_key=True)
    name_en = TextField(null=True)
    name_de = TextField(null=True)


class Mapping(BaseModel):
    degree_id = IntegerField()
    module_id = IntegerField()
    degree_version = TextField()
    ects = FloatField()
    weighting_factor = FloatField()
    valid_from = TextField(null=True)
    valid_to = TextField(null=True)

    class Meta:
        primary_key = CompositeKey("degree_id", "module_id", "degree_version")
        constraints = [
            SQL("FOREIGN KEY(degree_id) REFERENCES degree(degree_id) ON DELETE CASCADE"),
            SQL("FOREIGN KEY(module_id) REFERENCES module(module_id) ON DELETE CASCADE"),
        ]
