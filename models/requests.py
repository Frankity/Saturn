from peewee import Model, AutoField, CharField, IntegerField, SqliteDatabase
from pydantic import BaseModel, HttpUrl, Field

db = SqliteDatabase('saturn.db')


class Requests(Model):
    id = AutoField(primary_key=True)
    name = CharField()
    url = CharField()
    type = IntegerField()

    class Meta:
        database = db

class RequestModel(BaseModel):
    name: str = Field(..., min_length=3)
    url: HttpUrl
    type: int