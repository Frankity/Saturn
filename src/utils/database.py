from peewee import SqliteDatabase, Model, AutoField, IntegerField, CharField, BooleanField
from pydantic import BaseModel, Field, HttpUrl

database = SqliteDatabase("saturn.db")


class Requests(Model):
    id = AutoField(primary_key=True)
    name = CharField()
    url = CharField()
    method = IntegerField()
    folder = CharField()

    class Meta:
        database = database


class Folders(Model):
    id = AutoField(primary_key=True)
    name = CharField()
    environment = IntegerField()

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


class Headers(Model):
    id = AutoField(primary_key=True)
    key = CharField()
    value = CharField()
    request = IntegerField()

    class Meta:
        database = database


class Params(Model):
    id = AutoField(primary_key=True)
    key = CharField()
    value = CharField()
    request = IntegerField()
    enabled = BooleanField()

    class Meta:
        database = database


def create_needed_tables():
    with database as db:
        db.create_tables([Collection, Requests, Body, Headers, Params])