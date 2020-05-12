# -*- coding: utf-8 -*-
"""Module for converting format of an OpenAPI file."""
__version__ = '0.2.0'
__status__ = 'Beta'
__author__ = 'Libor Gabaj'
__copyright__ = 'Copyright 2020, ' + __author__
__credits__ = [__author__]
__license__ = 'MIT'
__maintainer__ = __author__
__email__ = 'libor.gabaj@gmail.com'

# Standard library modules
from typing import NoReturn

# Third party modules

# Internal modules
import src.config as cfg
from src.utils.output import output_content as out


def convert(record: cfg.OpenAPI, outformat: cfg.Format = None) -> NoReturn:
    """Print OpenAPI content of the provided OpenAPI file record.

    Arguments
    ---------
    record
        OpenAPI file record, which should be converted. The record with
        valid OpenAPI file is assumed. It can contain external references too.
    outformat
        Enumeration member of an requested OpenAPI content format for output
        to the system console.

    """
    content = record.oas
    # Output
    out(content, outformat \
        or cfg.Format.JSON if record.oastype == cfg.Format.YAML \
        else cfg.Format.YAML)
