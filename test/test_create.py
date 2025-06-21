import pytest
from pyresult import Result
from pyresult.result import Ok, Err


def test_ok_create_and_unwrap():
    r = Result.Ok(42)
    assert r.is_ok()
    assert r.unwrap() == 42


def test_err_create_and_unwrap():
    r = Result.Err(ValueError("error"))
    assert r.is_err()
    with pytest.raises(ValueError):
        r.unwrap()


def test_repr():
    assert repr(Result.Ok("test")) == "Ok('test')"
    assert repr(Result.Err(ValueError("x"))) == "Err(ValueError('x'))"


def test_eq():
    assert Result.Ok(1) == Ok(1)
    assert Result.Err(ValueError("x")) == Err(ValueError("x"))
