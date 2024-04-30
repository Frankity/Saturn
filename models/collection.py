from peewee import SqliteDatabase, Model, CharField, AutoField

db = SqliteDatabase('saturn.db')


class Collection(Model):
    id = AutoField(primary_key=True)
    name = CharField()

    class Meta:
        database = db
