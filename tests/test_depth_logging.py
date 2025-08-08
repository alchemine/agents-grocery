from src.common.depth_logging import D


def test_depth_decorator_nested_calls():
    calls = []

    @D
    def inner(x):
        calls.append(f"inner-{x}")
        return x + 1

    @D
    def outer(y):
        z = inner(y)
        calls.append(f"outer-{z}")
        return z * 2

    result = outer(3)
    assert result == 8
    assert calls == ["inner-3", "outer-4"]
