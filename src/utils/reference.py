# -*- coding: utf-8 -*-
"""Module for resolving references."""
__version__ = '0.1.0'
__status__ = 'Beta'
__author__ = 'Libor Gabaj'
__copyright__ = 'Copyright 2020, ' + __author__
__credits__ = [__author__]
__license__ = 'MIT'
__maintainer__ = __author__
__email__ = 'libor.gabaj@gmail.com'

# Standard library modules
from typing import Tuple, List

# Third party modules

# Internal modules
import src.config as cfg
import src.utils.filesystem as fs


def dereference(content: dict, source_file: str) -> dict:
    """Resolve references in provided content dictionary.

    Arguments
    ---------
    content
        OpenAPI document to be cleaned up.
    source_file
        OpenAPI file with dereferenced content and used for resolving relative
        file paths.

    Returns
    -------
    Dereference OpenAPI content without external references, but either with
    local ones or entirely without them.

    Notes
    -----
    - The function is called recursively for nested dictionaries.

    """
    if isinstance(content, list):
        for ref_idx, ref_item in enumerate(content):
            content[ref_idx] = dereference(ref_item, source_file)
    if isinstance(content, dict):
        # Retrieve root (master) OpenAPI file
        record_root = cfg.CACHE.get_record_first()
        # Process all objects
        # for ref_key, ref_value in content.items():
        for ref_key in list(content.keys()):
            ref_value = content[ref_key]
            if ref_key == '$ref':
                target_file, target_fragments = parse(ref_value)
                # External reference
                if target_file:
                    target_file = fs.resolve_filepath(target_file, source_file)
                    # Load target file from cache or file system
                    record_target = cfg.CACHE.get_record_by_file(target_file)
                    if not record_target:
                        record_target = fs.load_openapi_file(target_file)
                        cfg.CACHE.reg_record(record_target)
                    # Retrieve target (referenced) content
                    ref_content = record_target.oas
                    try:
                        for fragment in target_fragments:
                            fragment = json_pointer(fragment)
                            ref_content = ref_content[fragment]
                    # Target content already imported
                    except KeyError:
                        pass
                    if cfg.CACHE.dereference_once:
                        content = ref_content
                        break
                    # Make internal reference from external one
                    # by importing target leaf referenced content to the
                    # root document if required.
                    # Make deep dereference (without import) for
                    # 'paths', 'components/securitySchemes'.
                    if cfg.CACHE.dereference_import \
                        and target_fragments[0] != 'paths' \
                        and (target_fragments[0] != 'components' \
                            or target_fragments[1] != 'securitySchemes'):
                        # Reset reference to oneself
                        if (len(target_fragments) == 2 \
                                and target_fragments[0] == 'components') \
                                or len(target_fragments) == 1:
                            content[ref_key] = ''
                            continue
                        target = dereference(ref_content, target_file)
                        if cfg.CACHE.dereference_internals:
                            content = target
                            continue
                        # Inject dereferenced content to root OpenAPI file
                        ref_content = record_root.oas
                        for i, fragment in enumerate(target_fragments):
                            if i == len(target_fragments) - 1:
                                ref_content.setdefault(fragment, target)
                            else:
                                ref_content.setdefault(fragment, {})
                                ref_content = ref_content[fragment]
                        # Set internal reference
                        content[ref_key] = concat(target_fragments)
                    # Deep dereference
                    else:
                        content = dereference(ref_content, target_file)
                # Import internal reference from referenced file
                elif cfg.CACHE.dereference_import \
                    and source_file != record_root.oasfile:
                    # Retrieve local target (locally referenced) content
                    record_source = cfg.CACHE.get_record_by_file(source_file)
                    target = record_source.oas
                    try:
                        for fragment in target_fragments:
                            fragment = json_pointer(fragment)
                            target = target[fragment]
                    # Target content already imported
                    except KeyError:
                        pass
                    else:
                        target = dereference(target, source_file)
                        if cfg.CACHE.dereference_internals:
                            content = target
                            continue
                        # Inject dereferenced content to root OpenAPI file
                        ref_content = record_root.oas
                        for i, fragment in enumerate(target_fragments):
                            if i == len(target_fragments) - 1:
                                ref_content.setdefault(fragment, target)
                            else:
                                ref_content.setdefault(fragment, {})
                                ref_content = ref_content[fragment]
            # No reference key
            else:
                if cfg.CACHE.dereference_once:
                    content[ref_key] = ref_value
                else:
                    ref_content = dereference(ref_value, source_file)
                    content[ref_key] = ref_content
    return content


def parse(ref_value: str) -> Tuple[str, List[str]]:
    """Extract referenced file and list of target reference fragments.

    Arguments
    ---------
    ref_value
        Reference value string that should be parsed.

    Returns
    -------
    Tuple with referenced file (can be None) and list of target fragments.

    Notes
    -----
    '/home/my/file.yaml#/components/schemas/custom'
    => '/home/my/file.yaml', ['components', 'schemas', 'custom']

    """
    ref_file, ref_target = ref_value.split(cfg.Parameter.REF_DELIM.value)
    ref_fragments = ref_target.split(cfg.Parameter.REF_SEPAR.value)
    return ref_file, ref_fragments


def concat(ref_fragments: List[str], ref_file: str = None) -> str:
    """Concatenate reference fragments and prefix them with file if needed.

    Arguments
    ---------
    ref_fragments
        List of reference fragments.
    ref_file
        Referenced target file.

    Returns
    -------
    Reference value string that should be parsed.

    Notes
    -----
    ['components', 'schemas', 'custom'], '/home/my/file.yaml'
    => '/home/my/file.yaml#/components/schemas/custom'

    """
    ref_target = ref_file or ''
    ref_target += cfg.Parameter.REF_DELIM.value \
        + cfg.Parameter.REF_SEPAR.value.join(ref_fragments)
    return ref_target


def json_pointer(jsonpointer: str) -> str:
    """Replace escape characters in JSON pointer."""
    return jsonpointer.replace("~0", "~").replace("~1", "/")


def find(content: dict, reference: str, extern: bool = False) -> bool:
    """Check if reference is used in the provided content.

    Arguments
    ---------
    content
        OpenAPI document to be cleaned up.
    reference
        Internal reference to be searched.
    extern
        Flag about searching in external references too.

    Returns
    -------
    Flag determining presence of the reference in the content.

    """
    if isinstance(content, list):
        for item in content:
            if find(item, reference, extern):
                return True
    if isinstance(content, dict):
        for key, value in content.items():
            if key == '$ref':
                if value.endswith(reference) if extern \
                    else value == reference:
                    return True
            if find(value, reference, extern):
                return True
    return False


def find_security(content: dict, scheme: str) -> bool:
    """Check if security scheme is used in the provided content.

    Arguments
    ---------
    content
        OpenAPI document to be cleaned up.
    scheme
        Security scheme to be searched.

    Returns
    -------
    Flag determining presence of the security scheme in the content.

    """
    if isinstance(content, list):
        for item in content:
            if find_security(item, scheme):
                return True
    if isinstance(content, dict):
        for key, value in content.items():
            if key == 'security':
                for security in value:
                    if isinstance(security, dict) and scheme in security:
                        return True
            if find_security(value, scheme):
                return True
    return False
