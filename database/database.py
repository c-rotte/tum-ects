import os

from peewee import (
    Model,
    DatabaseProxy,
    IntegerField,
    FloatField,
    TextField,
    ForeignKeyField,
    CompositeKey,
    SqliteDatabase,
    PostgresqlDatabase,
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
    nr = TextField()
    full_name_en = TextField()
    full_name_de = TextField()
    subtitle_en = TextField()
    subtitle_de = TextField()
    version = TextField()


class Module(BaseModel):
    module_id = IntegerField(primary_key=True)
    name_en = TextField(null=True)
    name_de = TextField(null=True)


class Mapping(BaseModel):
    degree_id = ForeignKeyField(Degree, backref='mappings', on_delete='CASCADE')
    module_id = ForeignKeyField(Module, backref='mappings', on_delete='CASCADE')
    degree_version = TextField()
    ects = FloatField(null=True)
    weighting_factor = FloatField(null=True)
    valid_from = TextField(null=True)
    valid_to = TextField(null=True)

    class Meta:
        primary_key = CompositeKey("degree_id", "module_id")
