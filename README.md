# PyCyRest

## Introduction

Simple python library to connect to [cyREST](http://apps.cytoscape.org/apps/cyrest).

## Usage

```python
import pycyrest

client = pycyrest.CyRest()

print(client.operations)  # get a list of all possible operations

client.getStylesNames()  # Get a list of currently available styles

```

## Installation

```bash
pip install pycyrest
```

## License

MIT
