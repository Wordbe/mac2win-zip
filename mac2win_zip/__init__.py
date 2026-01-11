"""mac2win-zip: Create Windows-compatible ZIP files from macOS"""

__version__ = "1.0.1"
__author__ = "mac2win-zip contributors"
__license__ = "MIT"

from .cli import (
    create_windows_compatible_zip,
    sanitize_windows_filename,
)

__all__ = [
    "sanitize_windows_filename",
    "create_windows_compatible_zip",
]
