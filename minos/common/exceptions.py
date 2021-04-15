"""
Copyright (C) 2021 Clariteia SL

This file is part of minos framework.

Minos framework can not be copied and/or distributed without the express permission of Clariteia SL.
"""
from typing import Any


class MinosException(Exception):
    """Exception class for import packages or modules"""
    __slots__ = ('_message')

    def __init__(self, error_message: str):
        self._message = error_message

    def __repr__(self):
        return f"{type(self).__name__}(message={repr(self._message)})"

    def __str__(self) -> str:
        """represent in a string format the error message passed during the instantiation"""
        return self._message


class MinosImportException(MinosException): pass
class MinosProtocolException(MinosException): pass
class MinosMessageException(MinosException): pass
class MinosConfigException(MinosException): pass
class MinosModelException(MinosException): pass


class MinosModelAttributeException(MinosException):
    """Base model attributes exception."""
    pass


class MinosReqAttributeException(MinosModelAttributeException):
    """Exception to be raised when some required attributes are not provided."""
    pass


class MinosTypeAttributeException(MinosModelAttributeException):
    """Exception to be raised when there are any mismatching between the expected and observed attribute type."""
    pass


class MinosMalformedAttributeException(MinosModelAttributeException):
    """Exception to be raised when there are any kind of problems with the type definition."""
    pass


class MinosParseAttributeException(MinosModelAttributeException):
    """Exception to be raised when there are any kind of problems with the parsing logic."""

    def __init__(self, name: str, value: Any, exception: Exception):
        self.name = name
        self.value = value
        self.exception = exception
        super().__init__(f"{repr(exception)} was raised while parsing {repr(name)} field with {repr(value)} value.")

