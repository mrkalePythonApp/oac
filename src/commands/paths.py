# -*- coding: utf-8 -*-
"""Module for listing HTTP methods of an OpenAPI file."""
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

# Internal modules
import src.config as cfg
from src.utils.reference import dereference
from src.utils.filesystem import get_relpath
from src.utils.output import print_table as table, output_preamble as preamble


def paths(record: cfg.OpenAPI, color: bool = False) -> NoReturn:
    """Print an output table with list of OpenAPI paths and methods.

    Arguments
    ---------
    record
        OpenAPI file record, which paths should be printed. The record with
        valid OpenAPI document is assumed.
    color
        Flag about suppressing colorization of an output.

    Notes
    -----
    Final table is sorted by Path and then by Method ascending alphabetically.

    """
    # Separate paths section and list them
    paths_list = []
    paths_key = 'paths'
    if paths_key in record.oas.keys() and record.oas[paths_key]:
        # List all endpoints
        for path_key, path_value in record.oas[paths_key].items():
            # Dereference a path specification
            path_value = dereference(path_value, record.oasfile)
            if not path_value:
                continue
            # List only HTTP methods
            for method_key, method_value in path_value.items():
                method_name = method_key.upper()
                # Exclude fixed fields not being HTTP methods
                if method_name not in cfg.Parameter.HTTP_METHODS.value:
                    continue
                # No method specification present
                if not isinstance(method_value, dict):
                    continue
                method_id = method_value.get('operationId',
                                             cfg.Parameter.NONE.value)
                oasfile = cfg.CACHE.get_record_last().oasfile
                oasfile = get_relpath(oasfile, record.oasfile)
                paths_list.append(cfg.Method(
                    name=method_name,
                    operid=method_id,
                    path=path_key,
                    oasfile=oasfile,
                    ).list)
    # Preamble
    preamble('HTTP methods from OpenAPI file',
             record.oasinput, color)
    # Sort data table
    paths_list.sort(key=lambda rec: rec[0])  # Sort by method
    paths_list.sort(key=lambda rec: rec[1])  # Sort by path
    # Output
    if paths_list:
        click.echo()
        headers = cfg.Method.headers
        _ = [rec.insert(0, idx + 1) for idx, rec in enumerate(paths_list)]
        # Remove last column from data table
        if cfg.CACHE.files == 1:
            headers = headers[:-1]
            paths_list = [rec[:-1] for rec in paths_list]
        table(paths_list, headers)
        paths_list.append(cfg.Method(oasfile=record.oasfile).list)
    else:
        msg = cfg.Parameter.NONE.value
        log = click.style(msg, fg='red') if color else msg
        click.echo(log)
