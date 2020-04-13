# -*- coding: utf-8 -*-
"""Utilities for manipulating OpenAPI 3 documents."""
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
from src.utils.filesystem import load_openapi_file
import src.config as cfg
import src.commands.paths as paths
import src.commands.bundle as bundle
import src.commands.prune as prune
import src.commands.orphans as orphans


# def get_file(ctx, param, value):
#     """Callback for piping CLI commands."""
#     if value or click.get_text_stream('stdin').isatty():
#         return value
#     return click.get_text_stream('stdin').read().strip()

@click.group()
@click.version_option(__version__, prog_name='OpenAPI CLI')
def oac():
    """Set of utilities for manipulating OpenAPI documents.

    Prefix each command with "oac_" to get a utility name, e.g., for "paths"
    the utility will be "oac_paths".
    """


@oac.command('bundle')
@click.argument('openapi_file', required=True,
                type=click.Path(exists=True),
                )
@click.option('-d', '--dereference', 'deref',
              is_flag=True, default=False,
              help='Deep dereference.')
@click.option('-f', '--format', 'outformat',
              type=click.Choice(['yaml', 'json']), required=False,
              help='Forced output format.')
@click.version_option(bundle.__version__, prog_name='OpenAPI Bundling')
def oac_bundle(openapi_file: str, deref: bool, outformat: str) -> NoReturn:
    """Bundle OpenAPI file with its referenced ones.
       Output result in input or forced format.
       At deep dereference all internal references are dereferenced too.
    """
    try:
        record = load_openapi_file(openapi_file)
        cfg.CACHE.reg_record(record)
        cfg.CACHE.dereference_import = True
        cfg.CACHE.dereference_internals = deref
        if outformat:
            outformat = cfg.Format.JSON if outformat == 'json' \
                else cfg.Format.YAML
        bundle.bundle(record, outformat)
    except (ValueError, FileNotFoundError, EOFError, SyntaxError) as err:
        raise click.BadParameter(err)


@oac.command('orphans')
@click.argument('openapi_file', required=True,
                type=click.Path(exists=True),
                )
@click.option('-c', 'color',
              is_flag=True, default=False,
              help='Suppress colorized output.')
@click.version_option(orphans.__version__, prog_name='OpenAPI Orphans')
def oac_orphans(openapi_file: str, color: bool) -> NoReturn:
    """List unreferenced components in OpenAPI file."""
    try:
        record = load_openapi_file(openapi_file)
        cfg.CACHE.reg_record(record)
        orphans.orphans(record, color)
    except (ValueError, FileNotFoundError, EOFError, SyntaxError) as err:
        raise click.BadParameter(err)


@oac.command('paths')
@click.argument('openapi_file', required=True,
                type=click.Path(exists=True),
                )
@click.option('-c', 'color',
              is_flag=True, default=False,
              help='Suppress colorized output.')
@click.version_option(paths.__version__, prog_name='OpenAPI Paths')
def oac_paths(openapi_file: str, color: bool) -> NoReturn:
    """List HTTP methods from OpenAPI file.
       If there are no referenced files, the definition files are omitted
       in the output.
    """
    try:
        record = load_openapi_file(openapi_file)
        cfg.CACHE.reg_record(record)
        cfg.CACHE.dereference_once = True
        paths.paths(record, color)
    except (ValueError, FileNotFoundError, EOFError, SyntaxError) as err:
        raise click.BadParameter(err)


@oac.command('prune')
@click.argument('openapi_file', required=True,
                type=click.Path(exists=True),
                )
@click.option('-f', '--format', 'outformat',
              type=click.Choice(['yaml', 'json']), required=False,
              help='Forced output format.')
@click.version_option(prune.__version__, prog_name='OpenAPI Pruning')
def oac_prune(openapi_file: str, outformat: str) -> NoReturn:
    """Cleanup OpenAPI file.
       Output result in original or forced format.

       All unreferenced components (in schemas, securitySchemes, parameters,
       heades, requestBodies, responses, ...) are removed from the result.
    """
    try:
        record = load_openapi_file(openapi_file)
        cfg.CACHE.reg_record(record)
        if outformat:
            outformat = cfg.Format.JSON if outformat == 'json' \
                else cfg.Format.YAML
        prune.prune(record, outformat)
    except (ValueError, FileNotFoundError, EOFError, SyntaxError) as err:
        raise click.BadParameter(err)


if __name__ == '__main__':
    oac()
