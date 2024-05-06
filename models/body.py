from peewee import Model, AutoField, CharField, IntegerField, SqliteDatabase

db = SqliteDatabase('saturn.db')


class Body(Model):
    id = AutoField(primary_key=True)
    request = IntegerField()
    body = CharField()

    class Meta:
        database = db
