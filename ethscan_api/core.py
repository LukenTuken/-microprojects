from settings import EthScanSettings
from ethscan_api.utils.ethscan_api_handler import EthScanApiInterface

site = EthScanSettings()

api_key = site.api_key.get_secret_value()

site_api = EthScanApiInterface()

if __name__ == '__main__':
    site_api()
