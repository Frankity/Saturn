
from peewee import SqliteDatabase, Model, AutoField, IntegerField, CharField
from pydantic import BaseModel, Field, HttpUrl


database = SqliteDatabase("saturn.db")


class Requests(Model):
    id = AutoField(primary_key=True)
    name = CharField()
    url = CharField()
    type = IntegerField()

    class Meta:
        database = database


class RequestModel(BaseModel):
    name: str = Field(..., min_length=3)
    url: HttpUrl
    type: int


class Collection(Model):
    id = AutoField(primary_key=True)
    name = CharField()

    class Meta:
        database = database


class Body(Model):
    id = AutoField(primary_key=True)
    request = IntegerField()
    body = CharField()

    class Meta:
        database = database


def create_needed_tables():
    with database as db:
        db.create_tables([Collection, Requests, Body])