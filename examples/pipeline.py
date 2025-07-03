from pathlib import Path
import logging
from typing import TypeVar

from pyresult import Result, Iter, lift

logger = logging.getLogger(__name__)


def benchmark(
    input_files: list[Path], output_file: Path
) -> Result[Exception, None]:
    return (
        Iter(input_files)
        .for_each(run_task)  # Generates an Iter[Result[E, T]]
        .flatten_result()  # Extract successful results only: Result[E, Iter[T]]
        .and_then(aggregate_results)
        .and_then(summarize)
        .and_then(lambda r: save(r, output_file))
        .on_err(logger.error)
    )


# Opaque functions to represent the steps in the pipeline
T = TypeVar("T")  # Input type for the algorithm
U = TypeVar("U")  # Output type for the algorithm
E = TypeVar("E", bound=BaseException)  # Error type for the algorithm


def run_task(file: Path) -> Result[E, T]:
    return (
        load(file)
        .and_then(execute_algorithm)
        .on_err(logger.error)
    )


@lift.result
def load(file: Path) -> T: ...


@lift.result
def aggregate_results(data: Iter[T]) -> U: ...


@lift.result
def summarize(data: T) -> U: ...


@lift.result
def save(data: T, file: Path) -> None: ...


# === Example!
def execute_algorithm(data: T) -> Result[E, U]:
    return (
        embed(data)
        .and_then(optimize_loop)
        .and_then(decode)
    )


@lift.result
def embed(data: T) -> U: ...


@lift.result
def optimize_loop(data: T) -> U: ...


@lift.result
def decode(data: T) -> U: ...
