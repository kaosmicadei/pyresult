# pyresult

A functional `Result` type for Python inspired by Rust's `Result<T, E>`. It
provides a alternative for error handling without crashing the
process.

## Example
```python
from pyresult import Result, lift


def parse_var(line: str) -> Result[ValueError, tuple[str, str]]:
    if "=" not in line:
        return Result.Err(ValueError(f"Missing '=' in line: {line!r}"))
    key, val = line.split("=")
    return Result.Ok((key, val))


# Convert any funtion into a Result-returning function  returning an
# `Ok(result)` on success or an `Err(exception)` on an exception.

@lift.result
def convert_var(kv: tuple[str, str]) -> tuple[str, object]:
    key, val = kv
    if val.lower() in ("true", "false"):
        return (key, val.lower() == "true")
    elif val.isdigit():
        return (key, int(val))
    else:
        return (key, val)  # keep it as string


def process_line(line: str) -> Result[Exception, tuple[str, object]]:
    return (
        parse_var(line)
        .and_then(convert_var)
    )


inputs = """HOST=localhost
PORT=8000
DEBUG=true
LOG_LEVEL=info
INVALID_LINE
"""

results = [process_line(line) for line in inputs.splitlines()]

for i, res in enumerate(results):
    res.map_or_else(
        lambda kv: print(f"[OK #{i}] {kv[0]} = {kv[1]!r}"),
        on_err=lambda err: print(f"[ERR #{i}] {type(err).__name__}: {err}")
    )

# Output:
# [OK #0] HOST = 'localhost'
# [OK #1] PORT = 8000
# [OK #2] DEBUG = True
# [OK #3] LOG_LEVEL = 'info'
# [ERR #4] ValueError: Missing '=' in line: 'INVALID_LINE'
```
