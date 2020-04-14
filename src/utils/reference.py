# -*- coding: utf-8 -*-
"""Module for resolving references."""
__version__ = '0.2.0'
__status__ = 'Beta'
__author__ = 'Libor Gabaj'
__copyright__ = 'Copyright 2020, ' + __author__
__credits__ = [__author__]
__license__ = 'MIT'
__maintainer__ = __author__
__email__ = 'libor.gabaj@gmail.com'

# Standard library modules
from typing import Tuple, List, Dict, Optional, NoReturn

# Third party modules

# Internal modules
import src.config as cfg
import src.utils.filesystem as fs


def dereference(content: Dict, source_file: str) -> Dict:
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
    - The function empties invalid references as marking them for deletion
      at post-processing.

    """
    if isinstance(content, list):
        for ref_idx, ref_item in enumerate(content):
            content[ref_idx] = dereference(ref_item, source_file)
    if isinstance(content, dict):
        for ref_key in list(content.keys()):
            if ref_key == '$ref':
                target_file, target_fragments = parse(content[ref_key])
                # Internal reference
                if not target_file:
                    target_file = source_file
                # External reference
                if target_file:
                    target_file = fs.resolve_filepath(target_file, source_file)
                    # Load target file from cache or file system
                    record_target = cfg.CACHE.get_record_by_file(target_file)
                    if not record_target:
                        record_target = fs.load_openapi_file(target_file)
                        cfg.CACHE.reg_record(record_target)
                    # Retrieve target (referenced) content
                    ref_content = get_ref_content(
                        record_target, target_fragments)
                    if ref_content is None:
                        continue
                    elif cfg.CACHE.dereference_internals:
                        content = ref_content
                    elif target_fragments[0] == 'paths':
                        content = ref_content
                    elif target_fragments[0] == 'components' \
                        and target_fragments[1] == 'securitySchemes':
                        content = ref_content
                    else:
                        content[ref_key] = concat(target_fragments)
                        if cfg.CACHE.dereference_import:
                            import_ref_content(ref_content, target_fragments)
            # No reference key
            else:
                ref_content = dereference(content[ref_key], source_file)
                if isinstance(ref_content, dict) and not ref_content:
                    del content[ref_key]
                else:
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


def find(content: Dict, reference: str, extern: bool = False) -> bool:
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


def find_security(content: Dict, scheme: str) -> bool:
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


def get_ref_content(record: cfg.OpenAPI, reference: List[Dict]) \
    -> Optional[Dict]:
    """Retrieve referenced content from source.

    Arguments
    ---------
    record
        Source OpenAPI file record.
    reference
        Local reference in form of list of fragments, i.e., keys of source
        content.

    Returns
    -------
    Target content of the reference or None. It is usually OpenAPI content,
    but might be a simple data type as well.

    """
    target = record.oas
    try:
        for fragment in reference:
            target = target[json_pointer(fragment)]
    except KeyError:
        return None
    target = dereference(target, record.oasfile)
    return target


def import_ref_content(content: Dict, reference: List[Dict]) -> NoReturn:
    """Import referenced content to the root OpenAPI document.

    Arguments
    ---------
    content
        OpenAPI document to be cleaned up.
    reference
        Local reference in form of list of fragments, i.e., keys of source
        content.

    """
    target = cfg.CACHE.get_record_first().oas
    for i, fragment in enumerate(reference):
        if i == len(reference) - 1:
            target.setdefault(fragment, content)
        else:
            target.setdefault(fragment, {})
            target = target[fragment]
