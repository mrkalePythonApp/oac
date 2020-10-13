# OpenAPI 3 CLI utilities
The Python command line interface application provides a utility `oac`
for manipulating documents written in
[OpenAPI Specification, Version 3.0.x](https://swagger.io/specification/),
while each of utility's commands is implemented as a standalone utility
at the same time.

## Requirements
Python 3.8+

## Installation
Clone the repository and execute the Python installation command.

```
git clone https://github.com/mrkalePythonApp/oac.git
cd oac
python setup.py install
```


<a id="commands"></a>
## Command and utililties

- [oac](#oac) - Main utility (OpenAPI CLI)
- [oac_bundle](#bundle) - Bundle OpenAPI file with its referenced ones
- [oac_convert](#convert) - Convert OpenAPI file
- [oac_orphans](#orphans) - List unreferenced components in OpenAPI file
- [oac_paths](#paths) - List HTTP methods from OpenAPI file
- [oac_prune](#prune) - Cleanup OpenAPI file

Each utility writes its result to the system console. If resulting file
is needed, the output from a utility should be redirected like

```
utility >outfile.ext
```

- The logical name and version of each utility can be obtained by the common
  option `--version`.
- The information text about each utility can be obtained by the common
  option `--help`.


<a id="oac"></a>
## oac

It is a main utility with several commands, each providing specific manipulation
function with provided input OpenAPI file.
Each command can be invoked as a standalone utility as described in the help
text.

```
Usage: oac [OPTIONS] COMMAND [ARGS]...

  Set of utilities for manipulating OpenAPI documents.

  Prefix each command with "oac_" to get a utility name, e.g., for "paths"
  the utility will be "oac_paths".

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  bundle   Bundle OpenAPI file with its referenced ones.
  convert  Convert OpenAPI file to opossite format or input one.
  orphans  List unreferenced components in OpenAPI file.
  paths    List HTTP methods from OpenAPI file.
  prune    Cleanup OpenAPI file.
```


<a id="bundle"></a>
## oac_bundle (OpenAPI Bundling)

The utility joins content of all referenced external OpenAPI files
into the resulting OpenAPI document.
The output OpenAPI document format is the same as the format of the input
OpenAPI file unless it is converted by an option for forced output format.

```
Usage: oac_bundle [OPTIONS] OPENAPI_FILE

  Bundle OpenAPI file with its referenced ones. Output result in input or
  forced format. At deep dereference all internal references are
  dereferenced too.

The output OpenAPI document format is the same as the format of the input
OpenAPI file unless it is converted by option for forced output format.
This option can be used for just converting OpenAPI document, even if
it does not have any unreferenced components.

Options:
  -d, --dereference         Deep dereference.
  -f, --format [yaml|json]  Forced output format.
  --version                 Show the version and exit.
  --help                    Show this message and exit.
```


<a id="convert"></a>
## oac_convert (OpenAPI Conversion)

The utility converts the content of an input file to output format.
If no output format is forced, the content is converted to the opposite
format between YAML and JSON.
No bundling or dereferencing is provided whatsoever.
```
Usage: oac_convert [OPTIONS] OPENAPI_FILE

  Convert OpenAPI file. Output result is in opposite format between YAML and
  JSON or in forced format.

Options:
  -f, --format [yaml|json]  Forced output format.
  --version                 Show the version and exit.
  --help                    Show this message and exit.
```


<a id="orphans"></a>
## oac_orphans (OpenAPI Orphans)

The utility lists all unreferenced components (in schemas, securitySchemes,
parameters, heades, requestBodies, responses, ...) from input OpenAPI file
in tabular form.
The output is implicitly colorized. Colorization is not appplied in redirection
to an output file.

```
Usage: oac_orphans [OPTIONS] OPENAPI_FILE

  List unreferenced components in OpenAPI file.

Options:
  -c         Suppress colorized output.
  --version  Show the version and exit.
  --help     Show this message and exit.
```


<a id="paths"></a>
## oac_paths (OpenAPI Paths)

The utility lists all HTTP methods and their paths from input OpenAPI file
in tabular form. If the input file references external OpenAPI files
with methods definitions, their relative paths to the input file are output
as well.
The output is implicitly colorized. Colorization is not appplied in redirection
to an output file.

```
Usage: oac_paths [OPTIONS] OPENAPI_FILE

  List HTTP methods from OpenAPI file. If there are no referenced files, the
  definition files are omitted in the output.

Options:
  -c         Suppress colorized output.
  --version  Show the version and exit.
  --help     Show this message and exit.
```


<a id="prune"></a>
## oac_prune (OpenAPI Pruning)

The utility removes all unreferenced components (in schemas, securitySchemes,
parameters, heades, requestBodies, responses, ...) from input OpenAPI file.
The utility does not executes dereferencing, so that it is useful to prune
just bundled OpenAPI file.
The output OpenAPI document format is the same as the format of the input
OpenAPI file unless it is converted by an option for forced output format.
This option can be used for just converting OpenAPI document, even if it does
not have any unreferenced components.

```
Usage: oac_prune [OPTIONS] OPENAPI_FILE

  Cleanup OpenAPI file. Output result in original or forced format.

  All unreferenced components (in schemas, securitySchemes, parameters,
  heades, requestBodies, responses, ...) are removed from the result.

Options:
  -f, --format [yaml|json]  Forced output format.
  --version                 Show the version and exit.
  --help                    Show this message and exit.
```