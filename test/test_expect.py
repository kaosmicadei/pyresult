import pytest
from pyresult import Result


def test_expect_on_ok():
    r = Result.Ok(42).expect("This should not fail")
    assert r == 42


def test_expect_raises_error_on_err():
    res = Result.Err(KeyError("key not found"))
    with pytest.raises(RuntimeError) as ctx:
        res.expect("a valid key")
    assert str(ctx.value) == "a valid key: 'key not found'"

