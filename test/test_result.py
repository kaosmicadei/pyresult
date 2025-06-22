import pytest
from pyresult import Result
from pyresult.result import Ok, Err


# Testing Creation and Unwrapping
# ===============================

def test_ok_create_and_unwrap():
    r = Result.Ok(42)
    assert r.is_ok()
    assert r.unwrap() == 42


def test_err_create_and_unwrap():
    r = Result.Err(ValueError("error"))
    assert r.is_err()
    with pytest.raises(ValueError):
        r.unwrap()


def test_unwrap_or():
    err = ValueError("broken")
    assert Result.Ok("valid").unwrap_or("fallback") == "valid"
    assert Result.Err(err).unwrap_or("fallback") == "fallback"


def test_unwrap_or_else():
    err = ValueError("broken")
    assert Result.Ok("valid").unwrap_or_else(lambda _: "fallback") == "valid"
    assert Result.Err(err).unwrap_or_else(lambda _: "fallback") == "fallback"


# Testing Mapping
# ===============

def test_map_on_ok():
    r = Result.Ok(42).map(lambda x: x + 1)
    assert r.unwrap() == 43


def test_map_on_err_shortcut():
    err = ValueError("error")
    r = Result.Err(err).map(lambda x: x + 1)
    assert r == Result.Err(err)


def test_map_or_on_ok():
    r = Result.Ok(42).map_or(100, lambda x: x + 1)
    assert r == 43


def test_map_or_on_err():
    r = Result.Err(ValueError("oops")).map_or("fallback", lambda x: x + 1)
    assert r == "fallback"


# Testing Chaining
# ================

def test_and_then_on_ok():
    def doulbe(x):
        return Result.Ok(x * 2)

    r = Result.Ok(21).and_then(doulbe)
    assert r.unwrap() == 42


def test_and_then_on_err_shortcut():
    def fail(_):
        return Result.Err(ValueError("This should not be called."))

    err = ValueError("bad sequence")
    r = Result.Err(err).and_then(fail)
    assert r == Result.Err(err)


# Testing Expectation
# ===================

def test_expect_on_ok():
    r = Result.Ok(42).expect("This should not fail")
    assert r == 42


def test_expect_raises_error_on_err():
    res = Result.Err(KeyError("key not found"))
    with pytest.raises(RuntimeError) as ctx:
        res.expect("a valid key")
    assert str(ctx.value) == "a valid key: 'key not found'"


# Testing String Representation and Equality
# ==========================================

def test_repr():
    assert repr(Result.Ok("test")) == "Ok('test')"
    assert repr(Result.Err(ValueError("x"))) == "Err(ValueError('x'))"


def test_eq():
    assert Result.Ok(1) == Ok(1)
    assert Result.Err(ValueError("x")) == Err(ValueError("x"))
