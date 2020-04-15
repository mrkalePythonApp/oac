# -*- coding: utf-8 -*-
"""Module for bundling OpenAPI files."""
__version__ = '0.3.0'
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
from src.utils.reference import dereference
import src.utils.cleanup as clean
from src.utils.output import output_content as out


def bundle(record: cfg.OpenAPI, outformat: cfg.Format = None) -> NoReturn:
    """Dereference and print content of the provided OpenAPI file record.

    Arguments
    ---------
    record
        OpenAPI file record, which dereference content should be printed.
        The record with valid OpenAPI document is assumed.
    outformat
        Enumeration member of an requested OpenAPI content format for output
        to the system console.

    """
    # Cleanup
    content = dereference(record.oas, record.oasfile)
    content, _, _ = clean.remove_unused_components(content)
    content = clean.remove_empty_objects(content)
    content = clean.reorder_components(content)
    # Output
    out(content, outformat or record.oastype)
