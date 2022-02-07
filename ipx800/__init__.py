"""Module to control the IPX800 V4 device from GCE Electronics."""

import importlib.metadata

from ipx800.ipx800 import ApiError, IPX800 as ipx800  # noqa


__version__ = importlib.metadata.version("gandi-2-terraform")
