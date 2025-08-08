import pytest
from datetime import datetime

from src.common.utils import str2bool, str2dt, dt2str, vars_, SingletonBase


def test_str2bool_true_cases():
    for v in ["yes", "true", "t", "y", "1", True, "YeS", "TrUe"]:
        assert str2bool(v) is True


def test_str2bool_false_cases():
    for v in ["no", "false", "f", "n", "0", False, "FaLsE"]:
        assert str2bool(v) is False


def test_str2bool_invalid():
    with pytest.raises(ValueError):
        str2bool("maybe")


def test_dt_str_conversion():
    s = "2024-01-31"
    dt = str2dt(s)
    assert isinstance(dt, datetime)
    assert dt2str(dt) == s


def test_vars_filters_dunder():
    class Obj:
        def __init__(self):
            self.a = 1
            self.__hidden = 2

    v = vars_(Obj())
    # Current behavior keeps name-mangled privates (not starting with '__')
    assert v["a"] == 1
    assert v["_Obj__hidden"] == 2


def test_singleton_base_instance_key():
    class Dummy(SingletonBase):
        @classmethod
        def _generate_instance_key(cls, key: str) -> tuple:
            return (key,)

        def _init_once(self, key: str) -> None:
            self.key = key

    a1 = Dummy("x")
    a2 = Dummy("x")
    b = Dummy("y")

    assert a1 is a2
    assert a1 is not b
    assert a1.key == "x" and b.key == "y"
