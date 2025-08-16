"""Configuration constants for the project."""

import json
import logging
from os import getenv
from pathlib import Path
from os.path import exists
from dotenv import load_dotenv
from socket import gethostname

import psycopg
from easydict import EasyDict

from src.common.loader import load_yaml


logger = logging.getLogger(__name__)


load_dotenv()


##################################################
# Environments
##################################################
ENV = getenv("ENV", "dev")
SERVICE_NAME = gethostname()


##################################################
# Database connection
##################################################
ELASTICSEARCH_URL = getenv("ELASTICSEARCH_URL")
ELASTICSEARCH_USER = getenv("ELASTICSEARCH_USER")
ELASTICSEARCH_PASSWORD = getenv("ELASTICSEARCH_PASSWORD")


##################################################
# PATH
##################################################
ROOT_DIR = Path(__file__).parent.parent


##################################################
# Configurations
##################################################
class FallbackConfig(EasyDict):
    """Config with automatic fallback to secondary config."""

    def __init__(self, primary: dict, fallback: dict):
        super().__init__(primary)
        self._fallback = fallback
        self._merge_configs(self, self._fallback)

    def _merge_configs(self, primary_dict: dict, fallback_dict: dict):
        for key, value in fallback_dict.items():
            if key in primary_dict:
                if isinstance(primary_dict[key], dict) and isinstance(value, dict):
                    self._merge_configs(primary_dict[key], value)
            else:
                primary_dict[key] = value


def get_global_config(env: str) -> EasyDict:
    """Get config from the server."""
    try:
        conninfo = f"postgresql://{getenv('POSTGRES_USER')}:{getenv('POSTGRES_PASSWORD')}@{getenv('POSTGRES_HOST')}:{getenv('POSTGRES_PORT')}/{getenv('POSTGRES_DB')}"
        table = getenv("POSTGRES_CONFIG_TABLE")

        with psycopg.connect(conninfo) as conn:
            with conn.cursor() as cur:
                sql = f"SELECT key, value FROM {table} WHERE env = '{env}'"
                cur.execute(sql)
                result = {e[0]: e[1] for e in cur}
        result = EasyDict(result)
        if not result:
            message = f"No config found in {conninfo} / {table} / {env}"
            logger.error(message)
            raise ValueError(message)

        pretty_result = json.dumps(result, indent=2, ensure_ascii=False)
        logger.info(f"Config loaded:\n{pretty_result}")
    except Exception as e:
        logger.warning(f"No config found in the server: {e}")
        result = {}

    return result


def get_local_config(env: str) -> EasyDict:
    """Get config from the local file."""
    config_path = ROOT_DIR / "config" / "config.yaml"
    if not exists(config_path):
        config_path = ROOT_DIR / "config" / f"config.{env}.yaml"
    return load_yaml(config_path)


CFG = FallbackConfig(
    primary=get_local_config(ENV),
    fallback=get_global_config(ENV),
)


if __name__ == "__main__":
    print(
        f"""
ENV: {ENV}
SERVICE_NAME: {SERVICE_NAME}
ELASTICSEARCH_URL: {ELASTICSEARCH_URL}
ELASTICSEARCH_USER: {ELASTICSEARCH_USER}
ELASTICSEARCH_PASSWORD: {ELASTICSEARCH_PASSWORD}
ROOT_DIR: {ROOT_DIR}
CFG: {CFG}
"""
    )
