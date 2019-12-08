"""
Module to handle translation for atomic components of usable domain model language/concepts.
Should at least handle :
- bytes
- decimal (int and float are optimisations - careful with that)
- str

Note : These are mostly handled by the language implementer, traditionally
"""
import decimal
import enum
import typing
from functools import singledispatch

import marshmallow.fields as fields
import marshmallow.base as base


@singledispatch
def atom(model):
    raise NotImplementedError


@atom.register
def _(model_int: int):
    return fields.Integer


@atom.register
def _(model: str):
    return fields.String

