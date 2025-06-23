"""
This module defines a Result and a Option types inspiredt on Rust's Result and
Option.

Their are desined to be used in a more functional programming style.

The Result type is used to represent the outcome of an operation, allowing
error handling without using exceptions.

The Option type is used to represent an optional value, allowing for the
handling of cases of missing, absent, or undefined values without using
`None`.

Both types allow short-circuiting a chain of operations. It means that if an
operation fails (in the case of Result) or if a value is not present (in the
case of Option), the next operations are skipped avoiding unnecessary
computations.

This is particularly useful, when dealing with batches of inputs where the
failure of one input should not prevent the processing of the others.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, NoReturn, TypeVar


T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E', bound=BaseException)
E1 = TypeVar('E1', bound=BaseException)


# Result Type
# ===========

class Result(ABC, Generic[E, T]):
    """A Result type that can either be Ok or Err.

    This is a generic class used to represent the outcome of an operation. It
    can hold a value of type T if the operation is successful (Ok), or an
    error of type E if the operation fails (Err).

    This class allows to propagate errors through a chain of operations
    without using exceptions and delay the decision on how to handle them.
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

    def _fold(self, on_ok: Callable[[T], U], on_err: Callable[[E], U]) -> U:
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

        return self._fold(
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

        return self._fold(func, lambda _: default)

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

        return self._fold(func, on_err)
    
    def map_err(self, func: Callable[[E], E1]) -> Result[E1, T]:
        """Applies a function to the contained error if the Result is Err.
        If the Result is Ok, it returns the Ok unchanged.

        It is intended to transform the error type of the Result, allowing
        for more specific error handling without changing the contained value.

        Args:
            func: Function to apply to the contained error if the Result is Err.

        Returns:
            A new Result containing the transformed error if Err, or the same
            Ok value if the Result is Ok.
        """

        return self._fold(
            on_ok=Result.Ok,
            on_err=lambda error: Result.Err(func(error))
        )

    def unwrap_or(self, default: T) -> T:
        """Returns the contained value if the Result is Ok, otherwise returns
        the provided default value.

        Args:
            default: The value to return if the Result is Err.

        Returns:
            The contained value if Ok, or the default value if Err.
        """

        return self._fold(lambda value: value, lambda _: default)

    def unwrap_or_else(self, func: Callable[[E], T]) -> T:
        """Returns the contained value if the Result is Ok, otherwise applies
        the provided function to the contained error and returns its result.

        Args:
            func: Function to apply to the contained error if the Result is Err.

        Returns:
            The contained value if Ok, or the result of applying the function
            to the error if Err.
        """

        return self._fold(lambda value: value, func)

    def and_then(self, func: Callable[[T], Result[E1, U]]) -> Result[E1, U]:
        """Applies a function that returns a Result to the contained value if
        the Result is Ok. If the Result is Err, it returns the Err unchanged.

        It is intended to chain operations that return Results, allowing
        to leave the chain safely and handle the error later.

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
    
    def inspect(self, func: Callable[[T], None]) -> Result[E, T]:
        """Applies a function to the contained value if the Result is Ok,
        allowing side effects without changing the Result.

        Useful for debugging or logging purposes.

        Args:
            func: Function to apply to the contained value if the Result is Ok.

        Returns:
            The Result unchanged.
        """
        if self.is_ok():
            func(self.unwrap())
        return self

    def as_option(self) -> Option[T]:
        """Converts the Result into an Option."""
        return self._fold(
            on_ok=Option.Some,
            on_err=lambda _: Option.Nil()
        )


class Ok(Result[E, T]):
    """
    A concrente Result implementation representing a successful operation
    containing a value of type T.
    """

    __slots__ = ('_value',)

    def __init__(self, value: T) -> None:
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
    A concrete Result implementation representing a failed operation containing
    an error of type E.
    """

    __slots__ = ('_error',)

    def __init__(self, error: E) -> None:
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
        return (
            isinstance(other, Err)
            and type(self._error) is type(other._error)
            and str(self._error) == str(other._error)
        )


# Option Type
# ===========

class Option(ABC, Generic[T]):
    """An Option type that can either be Some or Nil.

    This is a generic class used to represent an optional value. It can hold a
    value of type T if it exists (Some), or be empty (Nil) if the value does not
    exist.
    """

    @staticmethod
    def Some(value: T) -> Option[T]:
        """Creates an Option with a value."""
        return Some(value)

    @staticmethod
    def Nil() -> Option[T]:
        """Creates an Option without a value."""
        return Nil()

    @abstractmethod
    def unwrap(self) -> T:
        """Returns the value if it exists, otherwise raises an exception."""

    @abstractmethod
    def is_some(self) -> bool:
        """Checks if the Option contains a value."""

    def is_none(self) -> bool:
        """Checks if the Option does not contain a value."""
        return not self.is_some()

    def _fold(self, on_some: Callable[[T], U], on_none: Callable[[], U]) -> U:
        """
        Applies a function to the value if it exists, otherwise applies a
        function that returns a default value.

        Args:
            on_some: Function to apply if the Option is Some, taking the
                contained value.
            on_none: Function to apply if the Option is Nil.
        
        Returns:
            A value of type U resulting from applying the appropriate function.
        """

        return on_some(self.unwrap()) if self.is_some() else on_none()

    def map(self, func: Callable[[T], U]) -> Option[U]:
        """
        Applies a function to the value if it exists, returning a new Option.

        Args:
            func: Function to apply to the contained value if the Option is
                Some.
        
        Returns:
            A new Option containing the transformed value if Some, or Nil if the
            Option is Nil.
        """
        return self._fold(lambda v: Option.Some(func(v)), Option.Nil)

    def map_or(self, default: U, func: Callable[[T], U]) -> U:
        """
        Applies a function to the value if it exists, otherwise returns a
        default value.

        Args:
            default: The value to return if the Option is Nil.
            func: Function to apply to the contained value if the Option is
                Some.
        Returns:
            The result of applying the function if Some, or the default value if
            Nil.
        """
        return self._fold(func, lambda: default)

    def map_or_else(self, default_func: Callable[[], U], func: Callable[[T], U]) -> U:
        """
        Applies a function to the value if it exists, otherwise applies a
        default function.

        Args:
            default_func: Function to apply if the Option is Nil.
            func: Function to apply to the contained value if the Option is
                Some.
        
        Returns:
            The result of applying the function if Some, or the result of
            applying the default function if Nil.
        """
        return self._fold(func, default_func)

    def unwrap_or(self, default: T) -> T:
        """
        Returns the value if it exists, otherwise returns a default value.
        
        Args:
            default: The value to return if the Option is Nil.

        Returns:
            The contained value if Some, or the default value if Nil.
        """
        return self._fold(lambda v: v, lambda: default)

    def unwrap_or_else(self, default_func: Callable[[], T]) -> T:
        """
        Returns the value if it exists, otherwise applies a default function.

        Args:
            default_func: Function to apply if the Option is Nil.

        Returns:
            The contained value if Some, or the result of applying the default
            function if Nil.
        """
        return self._fold(lambda v: v, default_func)

    def and_then(self, func: Callable[[T], Option[U]]) -> Option[U]:
        """
        Applies a function that returns an Option to the value if it exists.

        Args:
            func: Function that takes the contained value and returns an Option.

        Returns:
            A new Option containing the transformed value if Some, or Nil if the
            Option is Nil.
        """
        return self._fold(func, Option.Nil)

    def expect(self, message: str) -> T:
        """
        Returns the value if it exists, otherwise raises an exception with a
        message.

        Args:
            message: The message to include in the exception if the Option is
                Nil.
        
        Returns:
            The contained value if Some.
        """
        if self.is_some():
            return self.unwrap()
        raise RuntimeError(f"{message}: Called expect on a Nil Option")

    def inspect(self, func: Callable[[T], None]) -> Option[T]:
        """
        Applies a function to the value if it exists, returning the Option
        itself.

        Useful for debugging or logging purposes.

        Args:
            func: Function to apply to the contained value if the Option is
                Some.
            
        Returns:
            The Option unchanged, allowing for side effects without modifying
            the Option.
        """
        if self.is_some():
            func(self.unwrap())
        return self
    
    def as_result(self, error: E) -> Result[E, T]:
        """
        Converts the Option into a Result, using the provided error if the
        Option is Nil.

        Args:
            error: The error to use if the Option is Nil.
        
        Returns:
            A Result containing the value if the Option is Some, or an Err with
            the provided error if the Option is Nil.
        """
        return self._fold(
            on_some=Result.Ok,
            on_none=lambda: Result.Err(error)
        )


class Some(Option[T]):
    """
    A concrete Option implementation representing a value of type T that exists.
    """

    __slots__ = ('_value',)

    def __init__(self, value: T):
        self._value = value

    def unwrap(self) -> T:
        return self._value

    def is_some(self) -> bool:
        return True

    def __repr__(self) -> str:
        return f"Some({self._value!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Some) and self._value == other._value


class Nil(Option[T]):
    """A concrete Option implementation representing the absence of a value."""

    def unwrap(self) -> T:
        raise RuntimeError("Called unwrap on a Nil Option")

    def is_some(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "Nil"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Nil)
