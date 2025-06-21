from pyresult import Result


def parse_var(line: str) -> Result[ValueError, tuple[str, str]]:
    if "=" not in line:
        return Result.Err(ValueError(f"Missing '=' in line: {line!r}"))
    key, val = line.split("=")
    return Result.Ok((key, val))


def coerce_value(key: str, val: str) -> Result[ValueError, tuple[str, object]]:
    try:
        if val.lower() in ("true", "false"):
            return Result.Ok((key, val.lower() == "true"))
        elif val.isdigit():
            return Result.Ok((key, int(val)))
        else:
            return Result.Ok((key, val))  # fallback to string
    except _ as e:
        return Result.Err(ValueError(f"Failed to convert {val!r}: {e}"))


def process_line(line: str) -> Result[ValueError, tuple[str, object]]:
    return (
        parse_var(line)
        .and_then(lambda kv: coerce_value(*kv))
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
