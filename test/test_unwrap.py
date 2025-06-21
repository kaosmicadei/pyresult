from pyresult import Result


def test_unwrap_or():
    err = ValueError("broken")
    assert Result.Ok("valid").unwrap_or("fallback") == "valid"
    assert Result.Err(err).unwrap_or("fallback") == "fallback"


def test_unwrap_or_on_err():
    err = ValueError("broken")
    res = Result.Err(err).unwrap_or_else(str)
    assert res == "broken"
