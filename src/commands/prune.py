# -*- coding: utf-8 -*-
"""Module for removing useless objects from an OpenAPI file."""
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
import src.utils.cleanup as clean
from src.utils.output import output_content as out


def prune(record: cfg.OpenAPI, outformat: cfg.Format = None) -> NoReturn:
    """Cleanup and print OpenAPI content of the provided OpenAPI file record.

    Arguments
    ---------
    record
        OpenAPI file record, which should be pruned. The record with
        valid OpenAPI file is assumed, usually dereferenced.
    outformat
        Enumeration member of an requested OpenAPI content format for output
        to the system console.

    """
    content = record.oas
    # Cleanup
    content, _, _ = clean.remove_unused_components(content)
    content = clean.remove_empty_objects(content)
    # Output
    out(content, outformat or record.oastype)
