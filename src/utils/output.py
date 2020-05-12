# -*- coding: utf-8 -*-
"""Module for printing results to the standard console output."""
__version__ = '0.3.0'
__status__ = 'Beta'
__author__ = 'Libor Gabaj'
__copyright__ = 'Copyright 2020, ' + __author__
__credits__ = [__author__]
__license__ = 'MIT'
__maintainer__ = __author__
__email__ = 'libor.gabaj@gmail.com'

# Standard library modules
import json
from typing import List, Dict, NoReturn

# Third party modules
import yaml
import tabulate
import click

# Internal modules
from src.config import Format


def print_table(data: List, headers: List,
                showindex: bool = False) -> NoReturn:
    """Print input list of data in tabular form with headers.

    Arguments
    ---------
    data
        List of data to print
    headers
        List of table header titles
    showindex
        Flag about generating automatic index
    """
    click.echo(tabulate.tabulate(data, headers=headers, showindex=showindex))


def dump_yaml(data: List) -> NoReturn:
    """Print serialized YAML content."""

    class NoAliasDumper(yaml.Dumper):  # pylint: disable=too-many-ancestors
        """Custom dumper for ommiting anchors and aliases."""
        def ignore_aliases(self, data):
            return True

    result = yaml.dump(data, default_flow_style=False, sort_keys=False,
                       Dumper=NoAliasDumper, allow_unicode=True)
    click.echo(result)


def dump_json(data: List) -> NoReturn:
    """Print serialized JSON content."""
    result = json.dumps(data, indent=2, ensure_ascii=False)
    click.echo(result)


def output_content(content: Dict, outformat: Format) -> NoReturn:
    """Convert content to required format and print it to system console.

    Arguments
    ---------
    content
        OpenAPI content, which should be converted and printed.
    outformat
        Enumeration member of an requested OpenAPI content format for output
        to the system console.

    """
    if outformat is Format.YAML:
        dump_yaml(content)
    elif outformat is Format.JSON:
        dump_json(content)


def output_preamble(title: str, subtitle: str, color: bool = False) -> NoReturn:
    """Convert content to required format and print it to system console.

    Arguments
    ---------
    title
        The first line of the preamble.
    subtitle
        The second line of the preamble, usually the file path related
        to the preamble.
    color
        Flag about suppressing colorization of an output.

    """
    msg = title + ':'
    log = msg if color else click.style(msg, fg='yellow')
    click.echo(log)
    msg = subtitle
    log = msg if color else click.style(msg, fg='green')
    click.echo(log)
