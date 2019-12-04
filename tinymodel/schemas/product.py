"""
Module to handle translation for categorical product of usable domain model language/concepts.
Should at least handle :
- tuples
- dicts
- classes (inc. slots)
- dataclasses
"""
from functools import singledispatch

from marshmallow import fields


@singledispatch
def product():
    pass


@product.register()
def _(model: tuple):  # or *args ???
    return fields.Tuple


