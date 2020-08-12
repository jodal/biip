"""Library's own exceptions."""

__all__ = ["BiipException", "EncodeError", "ParseError"]


class BiipException(Exception):
    """Base class for all custom exceptions raised by the library."""

    pass


class EncodeError(BiipException):
    """Error raised if encoding of a value fails."""

    pass


class ParseError(BiipException):
    """Error raised if parsing of barcode data fails."""

    pass
