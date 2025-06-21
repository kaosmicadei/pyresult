"""
This module defines a Result type that emulates the behavior of Rust's Result
type. It allows error handling through a chain of operations without using
exceptions allowinf failures without crashing the whole process.

It is particularly useful when dealing with batches of inputs where the failure
of one input should not prevent the processing of the others.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, NoReturn, TypeVar


T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E', bound=BaseException)


class Result(ABC, Generic[E, T]):
    """A Result type that can either be Ok or Err.

    This is a generic class that can be used to represent the outcome of an
    operation. It can hold a value of type T if the operation is successful
    (Ok), or an error of type E if the operation fails (Err).

    This class allows to propagate errors through a chain of operations
    without using exceptions allowing later decision on how to handle them.
    """

    @staticmethod
    def Ok(value: T) -> Result[E, T]:
        """Creates an Ok Result containing the given value."""
        return Ok(value)

    @staticmethod
    def Err(error: E) -> Result[E, T]:
        """Creates an Error Result containing the given error."""
        return Err(error)

    @abstractmethod
    def is_ok(self) -> bool: ...

    def is_err(self) -> bool:
        return not self.is_ok()

    @abstractmethod
    def unwrap(self) -> T:
        """
        Returns the value contained in an Ok result, otherwise raises the
        contained error.
        """

    @abstractmethod
    def _get_error(self) -> E:
        # Returns the error if this is an Err result, otherwise raises the
        # contained error.
        # It is used internally to avoid exposing the error directly.
        ...

    def fold(self, on_ok: Callable[[T], U], on_err: Callable[[E], U]) -> U:
        """Reduces the Result to a single value by applying the appropriate
        function based on whether the Result is Ok or Err.

        Args:
            on_ok: Function to apply if the Result is Ok, taking the contained
                value.
            on_err: Function to apply if the Result is Err, taking the contained
                error.
        Returns:
            A value of type U resulting from applying the appropriate function.
        """

        if self.is_ok():
            return on_ok(self.unwrap())
        return on_err(self._get_error())

    def map(self, func: Callable[[T], U]) -> Result[E, U]:
        """Applies a function to the contained value if the Result is Ok.
        If the Result is Err, it returns the Err unchanged.

        Args:
            func: Function to apply to the contained value if the Result is Ok.

        Returns:
            A new Result containing the transformed value if Ok, or the same Err
            if the Result is Err.
        """

        return self.fold(
            on_ok=lambda value: Result.Ok(func(value)),
            on_err=Result.Err
        )

    def map_or(self, default: U, func: Callable[[T], U]) -> U:
        """Applies a function to the contained value if the Result is Ok.
        If the Result is Err, it returns the provided default value.

        Args:
            default: The value to return if the Result is Err.
            func: Function to apply to the contained value if the Result is Ok.

        Returns:
            The result of applying the function if Ok, or the default value if
            Err.
        """

        return self.fold(func, lambda _: default)

    def map_or_else(
        self, func: Callable[[T], U], on_err: Callable[[E], U]
    ) -> U:
        """Applies a function to the contained value if the Result is Ok.
        If the Result is Err, it applies the provided error handler function.

        Args:
            func: Function to apply to the contained value if the Result is Ok.
            on_err: Function to apply to the contained error if the Result is
                Err.

        Returns:
            The result of applying the function if Ok, or the result of applying
            the error handler if Err.
        """

        return self.fold(func, on_err)

    def unwrap_or(self, default: T) -> T:
        """Returns the contained value if the Result is Ok, otherwise returns
        the provided default value.

        Args:
            default: The value to return if the Result is Err.

        Returns:
            The contained value if Ok, or the default value if Err.
        """

        return self.fold(lambda value: value, lambda _: default)

    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        """Returns the contained value if the Result is Ok, otherwise applies
        the provided function to the contained error and returns its result.

        Args:
            func: Function to apply to the contained error if the Result is Err.

        Returns:
            The contained value if Ok, or the result of applying the function
            to the error if Err.
        """

        return self.fold(lambda value: value, func)

    def and_then(self, func: Callable[[T], Result[E, U]]) -> Result[E, U]:
        """Applies a function that returns a Result to the contained value if
        the Result is Ok. If the Result is Err, it returns the Err unchanged.

        It is intended to chain operations that return Results, allowing
        for error propagation without using exceptions. This allows to leave the
        chain safely and handle the error later.

        Args:
            func: Function that takes the contained value and returns a Result.
        Returns:
            A new Result containing the transformed value if Ok, or the same Err
            if the Result is Err.
        """

        if self.is_ok():
            return func(self.unwrap())
        return Result.Err(self._get_error())

    def expect(self, message: str) -> T:
        """Returns the contained value if the Result is Ok, otherwise raises an
        exception with the provided message.

        Args:
            message: The message to include in the exception if the Result is
            Err.

        Returns:
            The contained value if Ok.

        Raises:
            RuntimeError: If the Result is Err, containing the provided message
                and the error.
        """

        if self.is_ok():
            return self.unwrap()
        raise RuntimeError(f"{message}: {self._get_error()}")
    
    def ok_or_none(self) -> T | None:
        """Returns the contained value if the Result is Ok, otherwise returns
        None.

        Returns:
            The contained value if Ok, or None if Err.
        """

        return self.unwrap_or(None)
    
    def inspect(self, func: Callable[[T], None]) -> Result[E, T]:
        """Applies a function to the contained value if the Result is Ok,
        allowing side effects without changing the Result.

        Args:
            func: Function to apply to the contained value if the Result is Ok.

        Returns:
            The Result unchanged.
        """
        if self.is_ok():
            func(self.unwrap())
        return self


class Ok(Result[E, T]):
    """
    A Result representing a successful operation containing a value of type T.
    """

    __slots__ = ('_value',)

    def __init__(self, value: T):
        self._value = value

    def is_ok(self) -> bool:
        return True

    def unwrap(self) -> T:
        return self._value

    def _get_error(self) -> NoReturn:
        raise RuntimeError("Tried to get an error from an Ok result")

    def __repr__(self) -> str:
        return f"Ok({self._value!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Ok) and self._value == other._value


class Err(Result[E, T]):
    """
    A Result representing a failed operation containing an error of type E.
    """

    __slots__ = ('_error',)

    def __init__(self, error: E):
        self._error = error

    def is_ok(self) -> bool:
        return False

    def unwrap(self) -> Any:
        raise self._get_error()

    def _get_error(self) -> E:
        return self._error

    def __repr__(self) -> str:
        return f"Err({self._error!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Err) and self._error == other._error


def match_result(
    result: Result[E, T], on_ok: Callable[[T], U], on_err: Callable[[E], U]
) -> U:
    """Matches a Result and applies the appropriate function based on whether
    the Result is Ok or Err.

    Args:
        result: The Result to match.
        on_ok: Function to apply if the Result is Ok, taking the contained
            value.
        on_err: Function to apply if the Result is Err, taking the contained
            error.

    Returns:
        A value of type U resulting from applying the appropriate function.
    """

    return result.fold(on_ok, on_err)
