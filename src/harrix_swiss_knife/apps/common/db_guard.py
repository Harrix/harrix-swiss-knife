"""Database guard helpers shared across apps."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Concatenate, ParamSpec, Protocol, TypeVar, cast, runtime_checkable

from harrix_swiss_knife.apps.common import message_box

P = ParamSpec("P")
R = TypeVar("R")
SelfT = TypeVar("SelfT")


@runtime_checkable
class _SupportsDbValidation(Protocol):
    def _validate_database_connection(self) -> bool: ...


@runtime_checkable
class _SupportsShowError(Protocol):
    def _show_error(self, title: str, message: str) -> None: ...


def requires_database(
    *, is_show_warning: bool = True
) -> Callable[[Callable[Concatenate[SelfT, P], R]], Callable[Concatenate[SelfT, P], R | None]]:
    """Ensure database connection is available before executing method."""

    def decorator(
        func: Callable[Concatenate[SelfT, P], R],
    ) -> Callable[Concatenate[SelfT, P], R | None]:
        @wraps(func)
        def wrapper(self: SelfT, *args: P.args, **kwargs: P.kwargs) -> R | None:
            validator = cast("_SupportsDbValidation", self)
            if not validator._validate_database_connection():
                if is_show_warning:
                    if isinstance(self, _SupportsShowError):
                        self._show_error("❌ Database Error", "❌ Database connection not available")
                    else:
                        message_box.warning(None, "❌ Database Error", "❌ Database connection not available")
                return None

            return func(self, *args, **kwargs)

        return wrapper

    return decorator

