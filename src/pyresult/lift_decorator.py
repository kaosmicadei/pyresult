from typing import Callable, Generic, TypeVar

from pyresult.result import Result
from pyresult.option import Option

T = TypeVar('T')
E = TypeVar('E', bound=BaseException)


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
    returns an Option. If the function raises an exception, it will return None.

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