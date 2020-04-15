# -*- coding: utf-8 -*-
"""Module for cleaning OpenAPI content."""
__version__ = '0.3.0'
__status__ = 'Beta'
__author__ = 'Libor Gabaj'
__copyright__ = 'Copyright 2020, ' + __author__
__credits__ = [__author__]
__license__ = 'MIT'
__maintainer__ = __author__
__email__ = 'libor.gabaj@gmail.com'

# Standard library modules
from typing import Tuple, List, Dict

# Third party modules

# Internal modules
from src.config import Parameter
import src.utils.reference as ref


def remove_empty_objects(content: Dict) -> Dict:
    """Remove dictionary keys with empty values.

    Arguments
    ---------
    content
        OpenAPI document to be cleaned up.

    Returns
    -------
    OpenAPI document without empty properties.

    """
    if isinstance(content, list):
        for key, value in enumerate(content):
            ref_content = remove_empty_objects(value)
            if isinstance(ref_content, list) and not ref_content:
                del content[key]
            else:
                content[key] = ref_content
    if isinstance(content, dict):
        for key in list(content.keys()):
            if isinstance(content[key], dict) and not content[key]:
                del content[key]
            elif isinstance(content[key], list) and not content[key]:
                del content[key]
            # Security basic authorization should be empty naturally
            elif key == 'security':
                continue
            else:
                content[key] = remove_empty_objects(content[key])
    return content


def remove_unused_components(content: Dict) -> Tuple[Dict,
                                                     List[str], List[str]]:
    """Remove unreferenced properties in content's components' properties,
    i.e., at the second level.

    Arguments
    ---------
    content
        OpenAPI content to be cleaned up.

    Returns
    -------
    Tuple with OpenAPI content without orphan objects in components object
    and lists of removed references and secury schemes.

    """
    removed_references = []
    key_section = 'components'
    # Provided content has components object
    if key_section in content and isinstance(content[key_section], dict):
        # Iteratively cleanup components' properties
        while True:
            removed_count = len(removed_references)
            for comps_prop in list(content[key_section].keys()):
                if comps_prop == 'securitySchemes':
                    continue
                # Remove not referenced subproperties
                target = content[key_section][comps_prop]
                for key in list(target.keys()):
                    reference = ref.concat([key_section, comps_prop, key])
                    if not ref.find(content, reference):
                        del target[key]
                        removed_references.append(reference)
                # Remove empty property (with all unreferenced subproperties)
                if not target:
                    del content[key_section][comps_prop]
                    removed_references.append(ref.concat([key_section,
                                                          comps_prop]))
            # Stop iteration if nothing has been removed
            if removed_count == len(removed_references):
                break
    removed_references.sort()
    content, removed_schemes = remove_unused_securities(content)
    return content, removed_references, removed_schemes


def remove_unused_securities(content: Dict) -> Tuple[Dict, List[str]]:
    """Remove unreferenced properties in content's components' property
    `securitySchemes`.

    Arguments
    ---------
    content
        OpenAPI content to be cleaned up.

    Returns
    -------
    Tuple with OpenAPI content without orphan security schemes in components
    object and list of removed schemes.

    Notes
    -----
    - Only "components/securitySchemes" is cleaned up.

    """
    removed_schemes = []
    key_components = 'components'
    key_schemes = 'securitySchemes'
    # Provided content has security schemes object
    if key_components in content and key_schemes in content[key_components] \
        and isinstance(content[key_components][key_schemes], dict):
        target = content[key_components][key_schemes]
        for scheme in list(target.keys()):
            # Remove not referenced schemes
            if not ref.find_security(content, scheme):
                del target[scheme]
                removed_schemes.append(ref.concat(
                    [key_components, key_schemes, scheme]))
            # Remove empty property (with all unreferenced subproperties)
            if not target:
                del content[key_components][key_schemes]
                removed_schemes.append(ref.concat(
                    [key_components, key_schemes]))
    removed_schemes.sort()
    return content, removed_schemes


def reorder_components(content: Dict) -> Dict:
    """Sort components properties in required order.

    Arguments
    ---------
    content
        OpenAPI content to be cleaned up.

    Returns
    -------
    Sorted OpenAPI content's components.

    """
    key_section = 'components'
    if key_section in content and isinstance(content[key_section], dict):
        target = {}
        for comp_prop in sorted(content[key_section].keys()):
            target.setdefault(comp_prop, {})
            # Sort components' subproperties
            for key in sorted(content[key_section][comp_prop].keys()):
                target[comp_prop].setdefault(
                    key, content[key_section][comp_prop][key])
        content[key_section] = target
    return content
