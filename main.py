from database.common.models import db, HashData, Wallets, WalletsHidden, WalletsUnderSanctions
from database.core import interface
from ethscan_api.core import EthScanApiInterface, api_key

"""Initializing the interface for working with the database.
Create a database and tables"""

db_write = interface.create()
db_read = interface.retrieve()

"""Input data for the program: Base hacker wallet, base victim wallet,
contract address from where we will get the data.
In this program we obtain data from logs."""

hacker_wallet = '0x0a5984f86200415894821bfefc1c1de036dbf9e7'
victim_wallet = '0xa910f92acdaf488fa6ef02174fb86208ad7722ba'
contract = '0x40C57923924B5c5c5455c48D93317139ADDaC8fb'
exception_contracts = ('0x0000', '0x1111', '0x2222', '0x3333', '0x4444',
                       '0x5555', '0x6666', '0x7777', '0x8888', '0x9999')

"""Connecting interface for interaction with Etherscan"""
wallet_erc20_data = EthScanApiInterface.get_wallet_erc20_data()
wallet_normal_data = EthScanApiInterface.get_wallet_normal_data()
wallet_balance = EthScanApiInterface.get_wallet_balance()
contract_data = EthScanApiInterface.get_contract_data()


def recursive_search(wallet: str) -> str:
    """
    Recursive function to find the final wallet.
    In normal transactions, we check whether there was a transfer to another wallet;
    if there was, we go to it and repeat the procedure. If not, returns the last wallet.
    """
    response_normal_data = wallet_normal_data(wallet.lower(), api_key).json()
    data_result = response_normal_data.get('result')

    if data_result[-1]['from'] == wallet and data_result[-1]['functionName'] == '':
        print('Go to the wallet', data_result[-1]['to'])
        result = recursive_search(data_result[-1]['to'])
    else:
        print('=' * 60)
        print('I return the final wallet', wallet)
        result = data_result[-1]['to']
        return result

    return result


"""A program block in which we search and record attack hashes,
 which tokens and in what quantity were stolen.
 We also conduct an initial search for wallets where tokens were sent.
 We mark them as the one we are looking for, or as a spacer, and write them into the database."""

response_wallet = wallet_erc20_data(hacker_wallet, api_key)
response_wallet = response_wallet.json()

for element in response_wallet.get('result'):
    if element['from'] == victim_wallet:
        token_value = float(int(element.get('value')) / (10 ** int(element.get('tokenDecimal'))))

        data = [{'hash': element.get('hash'),
                 'from_wallet': element.get('from'),
                 'to_wallet': element.get('to'),
                 'token_name': element.get('tokenName'),
                 'token_value': token_value}]

        print('Recorded token:', data[0].get('token_name'))
        db_write(db, HashData, data)

    if element['from'] == hacker_wallet:

        balance = wallet_balance(element.get('to'), api_key)
        balance = balance.json()
        balance = float(balance.get('result')) / 10 ** 18

        data_wallet = [{'wallet': element.get('to'),
                        'balance': balance,
                        'note': 'None'}]

        if balance == 0:
            continue
        elif balance >= 0.1 and not data_wallet[0]['wallet'].startswith(exception_contracts):
            data_wallet[0]['note'] = 'money is here'
            db_write(db, Wallets, data_wallet)
            print('Wrote down the wallet {0} balance: {1}'.format(data_wallet[0]['wallet'], data_wallet[0]['balance']))
        else:
            data_wallet[0]['note'] = 'gasket'
            db_write(db, Wallets, data_wallet)
            print('Wrote down the wallet {0} balance: {1}'.format(data_wallet[0]['wallet'], data_wallet[0]['balance']))

"""A block for recursively searching for wallets and balances and recording them in the database.
We read the gasket wallets and look for the final wallet with money."""

print('Starting a deep search')
gasket = db_read(db, Wallets, Wallets.wallet, Wallets.note == 'gasket')
for element in gasket:
    print('='*60)
    print('Wallet', element.wallet)
    ultimate_wallet = recursive_search(element.wallet)
    if not ultimate_wallet.startswith(exception_contracts):
        balance = wallet_balance(ultimate_wallet.lower(), api_key)
        balance = balance.json()
        balance = float(balance.get('result')) / 10 ** 18
        if balance >= 0.1:
            data_wallet = {'wallet': ultimate_wallet,
                           'balance': balance,
                           'note': 'money is here'}
            db_write(db, WalletsHidden, data_wallet)

"""Block for combining two tables with wallets into one"""
primary_wallets = db_read(db, Wallets, Wallets.wallet, Wallets.balance, Wallets.note)
for primary_wallet in primary_wallets:
    if primary_wallet.note == 'money is here':
        print('money is here')
        if WalletsHidden.get_or_none(primary_wallet.wallet) is None:

            recorded_data = {'wallet': primary_wallet.wallet,
                             'balance': primary_wallet.balance,
                             'note': primary_wallet.note}

            db_write(db, WalletsHidden, recorded_data)

"""Contract data request block, with hex decoding to the wallet address."""
response_contract = contract_data(contract, api_key)
response_contract = response_contract.json()
for element in response_contract.get('result'):

    contract_data = element.get('data')
    contract_data = ''.join(contract_data[130:])

    wallets = [{'wallet': contract_data[i:i + 64]} for i in range(0, len(contract_data), 64)]
    for wallet in wallets:
        wallet['wallet'] = ''.join(['0x', wallet['wallet'][24:]])
        if WalletsUnderSanctions.get_or_none(WalletsUnderSanctions.wallet == wallet['wallet']) is None:
            db_write(db, WalletsUnderSanctions, wallet)
