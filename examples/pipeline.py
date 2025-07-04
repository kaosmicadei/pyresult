from pathlib import Path
import logging
from typing import TypeVar

from pyresult import Result, Iter, lift

logger = logging.getLogger(__name__)


# An example of benchmark pipeline that processes multiple input files,
# runs a task on each file, aggregates the results, summarizes them,
# and saves the final report to an output file.
def benchmark(
    input_files: list[Path], output_file: Path
) -> Result[Exception, None]:
    return (
        Iter(input_files)
        .for_each(run_task)  # Generates an Iter[Result[E, T]]
        .flatten_result()  # Extract successful results only: Result[E, Iter[T]]
        .and_then(aggregate_results)
        .and_then(summarize)
        .and_then(lambda report: save(report, output_file))
        .on_err(logger.error)
    )


# Opaque functions to represent the steps in the pipeline.
T = TypeVar("T")  # Input type
U = TypeVar("U")  # Output type
E = TypeVar("E", bound=BaseException)  # Error type


def run_task(file: Path) -> Result[E, T]:
    return (
        load(file)
        .and_then(execute_algorithm)
        .on_err(logger.error)
    )


@lift.result
def load(file: Path) -> T: ...


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


@lift.result
def aggregate_results(data: Iter[T]) -> U: ...


@lift.result
def summarize(data: T) -> U: ...


@lift.result
def save(data: T, file: Path) -> None: ...
