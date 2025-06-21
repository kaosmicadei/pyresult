from pyresult import Result


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
