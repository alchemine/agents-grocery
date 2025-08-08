from time import sleep

from src.common.timer import Timer, T


def test_timer_context_runs_without_error():
    with Timer("Test Block") as t:
        assert t.name == "Test Block"
        sleep(0.01)


def test_timer_decorator_returns_function_result():
    @T
    def add(a, b):
        return a + b

    assert add(2, 3) == 5
