"""Biip interprets the data in barcodes."""

try:
    from importlib.metadata import version, PackageNotFoundError  # type: ignore
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError  # type: ignore

from biip._exceptions import BiipException, EncodeError, ParseError


__all__ = [
    "BiipException",
    "EncodeError",
    "ParseError",
]


try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
