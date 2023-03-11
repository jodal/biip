"""Library's own exceptions."""

__all__ = ["BiipException", "EncodeError", "ParseError"]


class BiipException(Exception):  # noqa: N818
    """Base class for all custom exceptions raised by the library."""


class EncodeError(BiipException):
    """Error raised if encoding of a value fails."""


class ParseError(BiipException):
    """Error raised if parsing of barcode data fails."""
