from typing import Callable, TypeVar

from pyresult.types import Result, Option

T = TypeVar('T')
E = TypeVar('E', bound=BaseException)


class lift:
    """An interface to lift a function into a Result or Option context."""

    @staticmethod
    def result(func: Callable[..., T]) -> Callable[..., Result[E, T]]:
        """Lift a function into a Result context."""
        return as_result(func)

    @staticmethod
    def option(func: Callable[..., T]) -> Callable[..., Option[T]]:
        """Lift a function into an Option context."""
        return as_option(func)


def as_result(func: Callable[..., T]) -> Callable[..., Result[E, T]]:
    """Decorator to convert a function that returns a value into a function that
    returns a Result. If the function raises an exception, it will return an
    Err containing the exception.

    Args:
        func: The function to convert.

    Returns:
        A new function that returns a Result.
    """

    def wrapper(*args, **kwargs) -> Result[E, T]:
        try:
            return Result.Ok(func(*args, **kwargs))
        except BaseException as e:
            return Result.Err(e)

    return wrapper


def as_option(func: Callable[..., T]) -> Callable[..., Option[T]]:
    """Decorator to convert a function that returns a value into a function that
    returns an Option. If the function raises an exception, it will return Nil.

    Args:
        func: The function to convert.

    Returns:
        A new function that returns an Option.
    """

    def wrapper(*args, **kwargs) -> Option[T]:
        try:
            return Option.Some(func(*args, **kwargs))
        except BaseException:
            return Option.Nil()

    return wrapper
