"""Utility module.

Commonly used functions and classes are here.
"""

import json
from hashlib import md5
from datetime import datetime
from abc import ABCMeta, abstractmethod


vars_ = lambda obj: {k: v for k, v in vars(obj).items() if not k.startswith("__")}
str2dt = lambda s, format="%Y-%m-%d": datetime.datetime.strptime(s, format)
dt2str = lambda dt, format="%Y-%m-%d": dt.strftime(format)


def tprint(dic: dict) -> None:
    """Print dictionary with fancy 'psql' format."""
    from tabulate import tabulate

    print(tabulate(dic, headers="keys", tablefmt="psql"))


def str2bool(s: str | bool) -> bool:
    """String to boolean."""
    if isinstance(s, bool):
        return s
    if s.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif s.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise ValueError(f"Invalid input: {s} (type: {type(s)})")


def get_hash_id(*seeds) -> str:
    """Get hash ID from seeds"""
    seed = "-".join([str(s) for s in seeds])
    return md5(seed.encode()).hexdigest()


def dump_json(obj: dict, indent: int = 2, ensure_ascii: bool = False) -> str:
    """Dump dictionary to JSON string."""
    return json.dumps(obj, indent=indent, ensure_ascii=ensure_ascii)


##################################################
# Singleton
##################################################
class SingletonBase(metaclass=ABCMeta):
    """Singleton base class.

    Example:
        class LLMManager(SingletonBase):
            @classmethod
            def _generate_instance_key(cls, model_name: str, provider: str) -> tuple:
                return (model_name, provider)

            def _init_once(self, model_name: str, provider: str) -> None:
                self.model_name = model_name
                self.provider = provider
    """

    _init = set()
    _instances = {}

    def __new__(cls, *args, **kwargs):
        instance_key = cls._generate_instance_key(*args, **kwargs)
        if instance_key not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[instance_key] = instance
            instance._init_once(*args, **kwargs)
            cls._init.add(instance_key)
        return cls._instances[instance_key]

    @classmethod
    @abstractmethod
    def _generate_instance_key(cls, *args, **kwargs) -> tuple: ...

    @abstractmethod
    def _init_once(self, *args, **kwargs): ...
