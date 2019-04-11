# PyCyRest

## Introduction

Simple python library to connect to [cyREST](http://apps.cytoscape.org/apps/cyrest).

## Usage

```python
import pycyrest

client = pycyrest.CyRest()

print(client.operations)  # get a list of all possible operations

client.getStylesNames()  # Call operation as attribute.

help(client.getStylesNames)  # See description and arguments for an operation
```

To get more information about each operation use the python `help` function.

## Installation

```bash
pip install pycyrest
```

## License

MIT
