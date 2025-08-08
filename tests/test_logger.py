import logging

import pytest

from src.common import logger as logger_module
from src.common.logger import build_general_logger, pretty_dict, STYLES


@pytest.fixture()
def silent_logger():
    lg = build_general_logger(
        logger_name="test_logger", log_to_console=False, log_to_file=False
    )
    return lg


def test_build_general_logger_basic():
    lg = build_general_logger(
        logger_name="test_logger_basic", log_to_console=False, log_to_file=False
    )
    assert isinstance(lg, logging.Logger)


def test_pretty_dict_formats_dict():
    d = {"a": 1, "b": {"c": 2}}
    s = pretty_dict(d)
    assert "\n" in s and '"a"' in s and '"c"' in s


def test_slog_and_log_helpers(monkeypatch, silent_logger):
    # Redirect module-level logger to silent logger to avoid I/O
    monkeypatch.setattr(logger_module, "logger", silent_logger, raising=True)

    msg = {"msg": "hello"}
    out = logger_module.slog(msg, style="OKGREEN")
    assert STYLES["BOLD"] in out and "hello" in out

    info_out = logger_module.log_info("test", prefix="TAG")
    assert "[TAG]" in info_out

    warn_out = logger_module.log_warning("warn")
    assert "warn" in warn_out

    err_out = logger_module.log_error("err")
    assert "err" in err_out
