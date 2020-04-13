# -*- coding: utf-8 -*-
"""Module for configuration parameters and intermodule data exchange."""
__version__ = '0.1.0'
__status__ = 'Beta'
__author__ = 'Libor Gabaj'
__copyright__ = 'Copyright 2020, ' + __author__
__credits__ = [__author__]
__license__ = 'MIT'
__maintainer__ = __author__
__email__ = 'libor.gabaj@gmail.com'


# Standard library modules
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, ClassVar, NoReturn, Optional
from os import path
from copy import deepcopy


# Third party modules


class Parameter(Enum):
    """Enumeration of global static parameters."""
    EXT_YAML = ['yaml', 'yml']
    EXT_JSON = ['json']
    OAS_MARK3 = 'openapi'
    OAS_MARK2 = 'swagger'
    REF_DELIM = '#/'
    REF_SEPAR = '/'
    NONE = 'N/A'
    HTTP_METHODS = ['GET', 'PUT', 'POST', 'DELETE',
                    'OPTIONS', 'HEAD', 'PATCH', 'TRACE']
    COMPONENTS = ['securitySchemes', 'parameters', 'headers',
                  'requestBodies', 'responses', 'schemas', 'links',
                  'callbacks', 'examples', ]

class Format(Enum):
    """Enumeration of OpenAPI document format."""
    YAML = 'yaml'
    JSON = 'json'


@dataclass
class OpenAPI:
    """OpenAPI specification from an OpenAPI file"""
    # Originally provided OpenAPI file
    oasinput: str = None
    # Full file path of an OpenAPI document
    oasfile: str = None
    # Format of an OpenAPI document
    oastype: Format = None
    # Specification version of an OpenAPI document
    oasversion: str = None
    # OpenAPI document content
    oas: Dict = field(default_factory=dict)
    # Sequence order number of loading - index in cache list
    idx: int = None

    def reset(self) -> NoReturn:
        """Set default values to all fields."""
        self.oasinput = None
        self.oasfile = None
        self.oastype = None
        self.oasversion = None
        self.oas = {}
        self.idx = None


@dataclass
class Method:
    """HTTP method declaration"""

    # HTTP method name in uppercase
    name: str = Parameter.NONE.value
    # Path of an endpoint
    path: str = Parameter.NONE.value
    # OperationId for the method
    operid: str = Parameter.NONE.value
    # OpenAPI file with the method
    oasfile: str = Parameter.NONE.value
    # Headers for list of fields
    headers: ClassVar = ['No', 'Method', 'Path', 'OperationId',
                         'Definition file']

    @property
    def list(self) -> List:
        """Create list from fields."""
        return [self.name, self.path, self.operid, self.oasfile]

@dataclass
class FileCache:
    """Class with OpenAPI files data shared across modules."""
    records: List[OpenAPI] = field(default_factory=list)
    # Processing mode flags
    dereference_internals: bool = False
    dereference_once: bool = False
    dereference_import: bool = False

    @property
    def files(self):
        """Number of registered files."""
        return len(self.records)

    def reg_record(self, file_record: OpenAPI = OpenAPI()):
        """Register OpenAPI file record to the cache.

        Arguments
        ---------
        opeapi_file
            Absolute OpenAPI file path that should be retrieved.

        Notes
        -----
        - If file path in the file record is empty, the registration will be
          rejected.
        - If file is already registered, the registered record is updated by
          provided record, however, only for defined fields.
        """
        if file_record.oasfile is None:
            return
        record = self.get_record_by_file(file_record.oasfile)
        # Update record
        if record:
            if file_record.oastype:
                record.oastype = file_record.oastype
            if file_record.oas:
                record.oas = deepcopy(file_record.oas)
        # Create record
        else:
            record = file_record
            record.oasfile = path.abspath(record.oasfile)
            record.idx = self.files
            self.records.append(record)

    def get_record_by_file(self, openapi_file: str) -> Optional[OpenAPI]:
        """Retrieve OpenAPI file record by file path.

        Arguments
        ---------
        opeapi_file
            OpenAPI file path, usually absolute one, that should be retrieved.

        Returns
        -------
            Found OpenAPI file record or None

        """
        # Make absolute file path for sure
        openapi_file = path.abspath(openapi_file)
        # Find file and retrieve its record
        for record in self.records:
            if record.oasfile == openapi_file:
                return record
        return None

    def get_record_by_index(self, index: int) -> Optional[OpenAPI]:
        """Retrieve OpenAPI file record by index.

        Arguments
        ---------
        index
            Index of an OpenAPI file that should be retrieved.

        Returns
        -------
            Found OpenAPI file record or None

        """
        # Sanitize index
        index = abs(int(index))
        # Find file and retrieve its record
        for record in self.records:
            if record.idx == index:
                return record
        return None

    def get_record_first(self) -> Optional[OpenAPI]:
        """Retrieve first registered OpenAPI file record.

        Returns
        -------
            Found the very first registered OpenAPI file record or None, if
            no one has been registered yet.

        """
        return self.get_record_by_index(0)

    def get_record_last(self) -> Optional[OpenAPI]:
        """Retrieve last registered OpenAPI file record.

        Returns
        -------
            Found the very last registered OpenAPI file record or None, if
            no one has been registered yet.

        """
        return self.get_record_by_index(len(self.records) - 1)

# Instance of a file cache
CACHE = FileCache()
