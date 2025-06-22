from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar

T = TypeVar('T')
U = TypeVar('U')


class Option(ABC, Generic[T]):

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
        Applies a function to the value if it exists, otherwise applies
        another function.
        """

        return on_some(self.unwrap()) if self.is_some() else on_none()

    def map(self, func: Callable[[T], U]) -> Option[U]:
        """
        Applies a function to the value if it exists, returning a new Option.
        """
        return self._fold(lambda v: Option.Some(func(v)), lambda: Option.Nil())

    def map_or(self, default: U, func: Callable[[T], U]) -> U:
        """
        Applies a function to the value if it exists, otherwise returns a
        default value.
        """
        return self._fold(lambda v: func(v), lambda: default)

    def map_or_else(self, default_func: Callable[[], U], func: Callable[[T], U]) -> U:
        """
        Applies a function to the value if it exists, otherwise applies a
        default function.
        """
        return self._fold(lambda v: func(v), default_func)

    def unwrap_or(self, default: T) -> T:
        """Returns the value if it exists, otherwise returns a default value."""
        return self._fold(lambda v: v, lambda: default)

    def unwrap_or_else(self, default_func: Callable[[], T]) -> T:
        """
        Returns the value if it exists, otherwise applies a default function.
        """
        return self._fold(lambda v: v, default_func)

    def and_then(self, func: Callable[[T], Option[U]]) -> Option[U]:
        """
        Applies a function that returns an Option to the value if it exists.
        """
        return self._fold(func, lambda: Option.Nil())

    def expect(self, message: str) -> T:
        """
        Returns the value if it exists, otherwise raises an exception with a
        message.
        """
        if self.is_some():
            return self.unwrap()
        raise RuntimeError(f"{message}: Called expect on a Nil Option")

    def inspect(self, func: Callable[[T], None]) -> Option[T]:
        """
        Applies a function to the value if it exists, returning the Option
        itself.
        """
        if self.is_some():
            func(self.unwrap())
        return self


class Some(Option[T]):

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

    def unwrap(self) -> T:
        raise RuntimeError("Called unwrap on a Nil Option")

    def is_some(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "Nil"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Nil)
