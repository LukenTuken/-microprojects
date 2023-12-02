import peewee as pw


db = pw.SqliteDatabase('hash_wallets.db')


class BaseModel(pw.Model):
    class Meta:
        database = db


class HashData(BaseModel):
    hash = pw.TextField()
    from_wallet = pw.TextField()
    to_wallet = pw.TextField()
    token_name = pw.TextField()
    token_value = pw.FloatField()


class Wallets(BaseModel):
    wallet = pw.TextField()
    balance = pw.FloatField()
    note = pw.TextField()


class WalletsHidden(BaseModel):
    wallet = pw.TextField()
    balance = pw.FloatField()
    note = pw.TextField()


class WalletsUnderSanctions(BaseModel):
    wallet = pw.TextField()
