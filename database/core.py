from database.utils.operations import OpInterface
from database.common.models import db, HashData, Wallets, WalletsHidden, WalletsUnderSanctions


db.connect()
db.create_tables([HashData, Wallets, WalletsHidden, WalletsUnderSanctions])

interface = OpInterface


if __name__ == '__main__':
    interface()
