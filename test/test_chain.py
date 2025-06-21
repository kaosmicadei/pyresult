from pyresult import Result


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
