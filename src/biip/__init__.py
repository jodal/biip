"""Biip interprets the data in barcodes."""

try:
    from importlib.metadata import version, PackageNotFoundError  # type: ignore
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError  # type: ignore


try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"


class ParseError(Exception):
    """Error raised if parsing of barcode data fails."""

    pass


class EncodeError(Exception):
    """Error raised if encoding of a value fails."""

    pass
