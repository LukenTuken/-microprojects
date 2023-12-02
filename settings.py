import os


from dotenv import load_dotenv, find_dotenv
from pydantic_settings import BaseSettings
from pydantic import SecretStr

if not find_dotenv():
    exit('Environment variables are not loaded because the .env file is missing')
else:
    load_dotenv()


class EthScanSettings(BaseSettings):
    api_key: SecretStr = os.getenv('etherscan_api', None)
