from peewee import Model, AutoField, CharField, IntegerField, SqliteDatabase

db = SqliteDatabase('saturn.db')


class Requests(Model):
    id = AutoField(primary_key=True)
    name = CharField()
    url = CharField()
    type = IntegerField()

    class Meta:
        database = db