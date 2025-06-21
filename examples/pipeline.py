from pyresult import Result


def parse_config(raw: str) -> Result[ValueError, dict]:
    if "=" not in raw:
        return Result.Err(ValueError("Missing '=' in config"))
    key, val = raw.split("=")
    return Result.Ok({key.strip(): val.strip()})


def run_test(config: dict) -> Result[RuntimeError, str]:
    if config.get("mode") == "dangerous":
        return Result.Err(RuntimeError("Refused to run dangerous mode"))
    return Result.Ok(f"Test run with config: {config}")


def safe_pipeline(raw_inputs: list[str]) -> list[Result[BaseException, str]]:
    results = []

    for raw in raw_inputs:
        result = (
            parse_config(raw)
            .and_then(run_test)
        )
        results.append(result)

    return results


def log_results(results: list[Result[BaseException, str]]):
    for i, res in enumerate(results):
        res.map_or_else(
            lambda output: print(f"[OK #{i}] {output}"),
            lambda err: print(f"[ERR #{i}] {type(err).__name__}: {err}")
        )


inputs = [
    "mode=safe",
    "threshold=10",
    "mode=dangerous",
    "incompleteconfig"
]

results = safe_pipeline(inputs)
log_results(results)
# Output:
# [OK #0] Test run with config: {'mode': 'safe'}
# [OK #1] Test run with config: {'threshold': '10'}
# [ERR #2] RuntimeError: Refused to run dangerous mode
# [ERR #3] ValueError: Missing '=' in config
