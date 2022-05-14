from peewee import *
from myapp.report import *

DATABASE = "full_report.db"

db = SqliteDatabase(DATABASE)


class BaseModel(Model):
    class Meta:
        database = db


class Driver(BaseModel):
    id = CharField(primary_key=True)
    name = CharField(unique=True)
    car = CharField()
    start_time = CharField()
    end_time = CharField()
    delta_time = CharField()

    class Meta:
        db_table = "Drivers_Results"


def create_tables():
    with db:
        db.create_tables([Driver])


def insert_into_driver_table():
    all_rows = ordering(order="asc", driver_id="")

    Driver.insert_many(all_rows).execute()


if __name__ == "__main__":
    create_tables()
    insert_into_driver_table()


