from typing import Dict

import requests


def _make_response(params: Dict, success: object = 200) -> object:
    response = requests.request(
        method='GET',
        url='https://api.etherscan.io/api',
        params=params,
    )

    status_code = response.status_code

    if status_code == success:
        return response

    return status_code


def _get_wallet_ecr20_data(wallet: str, apikey: str, func=_make_response):
    params_erc_20 = {'module': 'account',
                     'action': 'tokentx',
                     'address': wallet,
                     'sort': 'asc',
                     'apikey': apikey}

    response = func(params=params_erc_20)

    return response


def _get_wallet_normal_data(wallet: str, apikey: str, func=_make_response):
    params_normal = {'module': 'account',
                     'action': 'txlist',
                     'address': wallet,
                     'sort': 'asc',
                     'apikey': apikey}

    response = func(params=params_normal)

    return response


def _get_wallet_balance(wallet: str, apikey: str, func=_make_response):
    params_balance = {'module': 'account',
                      'action': 'balance',
                      'address': wallet,
                      'tag': 'latest',
                      'apikey': apikey}

    response = func(params=params_balance)

    return response


def _get_contract_data(contract: str, apikey: str, func=_make_response):
    params_contract = {'module': 'logs',
                       'action': 'getLogs',
                       'topic0': '0x2596d7dd6966c5673f9c06ddb0564c4f0e6d8d206ea075b83ad9ddd71a4fb927',
                       'address': contract,
                       'apikey': apikey}

    response = func(params=params_contract)

    return response


class EthScanApiInterface:

    @staticmethod
    def get_wallet_erc20_data():
        return _get_wallet_ecr20_data

    @staticmethod
    def get_wallet_normal_data():
        return _get_wallet_normal_data

    @staticmethod
    def get_wallet_balance():
        return _get_wallet_balance

    @staticmethod
    def get_contract_data():
        return _get_contract_data


if __name__ == '__main__':
    _make_response()
    _get_wallet_ecr20_data()
    _get_wallet_normal_data()
    _get_wallet_balance()
    _get_contract_data()

    EthScanApiInterface()
