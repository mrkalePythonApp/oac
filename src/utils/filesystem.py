# -*- coding: utf-8 -*-
"""Module for processing files and folders."""
__version__ = '0.1.0'
__status__ = 'Beta'
__author__ = 'Libor Gabaj'
__copyright__ = 'Copyright 2020, ' + __author__
__credits__ = [__author__]
__license__ = 'MIT'
__maintainer__ = __author__
__email__ = 'libor.gabaj@gmail.com'

# Standard library modules
import os
import json

# Third party modules
import yaml

# Internal modules
import src.config as cfg


def load_openapi_file(openapi_file: str) -> cfg.OpenAPI:
    """Load correct OpenAPI file.

    Arguments
    ---------
    openapi_file
        Full path determination of an OpenAPI file to be validate.

    Returns
    -------
    OpenAPI file record.

    Raises
    ------
    ValueError
        Incorrect file extension detected.
    FileNotFoundError
        Referenced OpenAPi file does not exist.
    EOFError
        OpenAPI file is empty.
    SyntaxError
        OpenAPI file is not the expected OpenAPI Specification, version 3.0.x.

    Notes
    -----
    - Validate on expected file extension and determine OpenAPI file format.
    - Validate on expected OpenAPI specification and load file content.

    """
    record = cfg.OpenAPI(
        oasinput=os.path.normpath(openapi_file),
        oasfile=os.path.abspath(openapi_file),
        )
    extension = \
        os.path.splitext(record.oasfile)[1].replace(os.extsep, '').lower()
    # Test on YAML file
    if extension in cfg.Parameter.EXT_YAML.value:
        record.oastype = cfg.Format.YAML
    # Test on JSON file
    elif extension in cfg.Parameter.EXT_JSON.value:
        record.oastype = cfg.Format.JSON
    # Extension validation failed
    else:
        extensions_list = ', '.join(
            cfg.Parameter.EXT_YAML.value + cfg.Parameter.EXT_JSON.value)
        errmsg = \
            f'Extension of "{record.oasfile}" is not from "{extensions_list}"!'
        raise ValueError(errmsg)
    # Read content
    try:
        with open(record.oasfile) as input_file:
            content = input_file.read()
    except FileNotFoundError as err:
        errmsg = f'Referenced OpenAPI file "{record.oasfile}" does not exist!'
        raise type(err)(errmsg).with_traceback(err.__traceback__)
    if not content:
        errmsg = f'OpenAPI file "{record.oasfile}" is empty!'
        raise EOFError(errmsg)
    # Choose loading function for corresponding OpenAPI format
    if record.oastype is cfg.Format.YAML:
        fnc_load = yaml.safe_load
    if record.oastype is cfg.Format.JSON:
        fnc_load = json.loads
    record.oas = fnc_load(content)
    if record.oas:
        if check_openapi3(record):
            record.oasversion = record.oas[cfg.Parameter.OAS_MARK3.value]
        # elif check_openapi2(record):
        #     record.oasversion = record.oas[cfg.Parameter.OAS_MARK2.value]
        else:
            errmsg = \
                f'OpenAPI file "{record.oasfile} is not marked as "' \
                f'OpenAPI 3 Specification!'
                # f'expected OpenAPI Specification!'
            raise SyntaxError(errmsg)
    return record


def check_openapi3(record: cfg.OpenAPI) -> bool:
    """Check if OpenAPI file i OpenAPI Specification 3.0.x.

    Arguments
    ---------
    record
        OpenAPI file record to be checked.

    Returns
    -------
    Flag about conformity to expected OpenAPI specification.

    """
    oas_key = cfg.Parameter.OAS_MARK3.value
    if oas_key in record.oas.keys():
        version = record.oas[oas_key].split('.', 3)
        # Should be 3.0.* version
        if len(version) == 3 \
            and version[0] == '3' and version[1] == '0' \
            and version[2][:1].isdigit():
            return True
    return False


def check_openapi2(record: cfg.OpenAPI) -> bool:
    """Check if OpenAPI file i OpenAPI Specification 2.0.

    Arguments
    ---------
    record
        OpenAPI file record to be checked.

    Returns
    -------
    Flag about conformity to expected OpenAPI specification.

    """
    oas_key = cfg.Parameter.OAS_MARK3.value
    if oas_key in record.oas.keys():
        if record.oas[oas_key] == '2.0':
            return True
    return False


def resolve_filepath(file_target, file_source):
    """Compose absolute file path of a given target file provided
       relatively to a source file.

    Arguments
    ---------
    file_target
        Target file path usually in relative form to the source file.
    file_source
        Source file path usually in absolute form.

    Returns
    -------
    Absolute path of the target file.

    Notes
    -----
    - If the target filepath is already absolute, it is returned without
        relation to the source file.
    """
    # Absolute target file path
    if os.path.isabs(file_target):
        return file_target
    # Relative target file provided
    dir_source = os.path.dirname(os.path.abspath(file_source))
    file_target = os.path.join(dir_source, file_target)
    file_target = os.path.abspath(os.path.normpath(file_target))
    return file_target

def get_relpath(cur_file: str, ref_file: str) ->str:
    """Compose relative file path to reference file.

    Arguments
    ---------
    cur_file
        Absolute path of a target file.
    ref_file
        Absolute path of a reference file, which a relative path is composing
        to.

    Returns
    -------
        Relative path of the current file.

    """
    ref_dir = os.path.dirname(ref_file)
    cur_dir = os.path.dirname(cur_file)
    cur_base = os.path.basename(cur_file)
    # Composition
    rel_path = os.path.relpath(cur_dir, ref_dir)
    rel_file = os.path.join(rel_path, cur_base)
    # rel_file = os.path.normpath(rel_file)
    return rel_file
