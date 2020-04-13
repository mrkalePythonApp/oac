# -*- coding: utf-8 -*-
"""Module for listing unreferenced componensts of an OpenAPI file."""
__version__ = '0.1.0'
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
import click
from src.utils.output import print_table as table

# Internal modules
import src.config as cfg
from src.utils.cleanup import remove_unused_components
from src.utils.output import output_preamble as preamble


def orphans(record: cfg.OpenAPI, color: bool = False) -> NoReturn:
    """Print an output table with list of OpenAPI unreferenced components.

    Arguments
    ---------
    record
        OpenAPI file record, which paths should be printed. The record with
        valid and dereference OpenAPI document is assumed.
    color
        Flag about suppressing colorization of an output.

    Notes
    -----
    Final table is sorted ascendng alphabetically.

    """
    _, components, schemes = remove_unused_components(record.oas)
    preamble('Unreferenced components from OpenAPI file',
             record.oasinput, color)
    references = components + schemes
    if references:
        click.echo()
        data = [[idx + 1, ref] for idx, ref in enumerate(references)]
        table(data, ['No', 'Reference to component'])
    else:
        msg = cfg.Parameter.NONE.value
        log = click.style(msg, fg='red') if color else msg
        click.echo(log)
