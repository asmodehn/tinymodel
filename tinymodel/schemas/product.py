"""
Module to handle translation for categorical product of usable domain model language/concepts.
Should at least handle :
- tuples
- dicts
- classes (inc. slots)
- dataclasses


Note : These are mostly handled by the developer, traditionally
"""
from functools import singledispatch

from dataclasses import dataclass

import marshmallow
from marshmallow import fields


def product(**model):

    # delayed import
    from .schema import schema

    schema = type("", (marshmallow.Schema,), {
        k: schema(v) for k, v in model.items()
    })
    return schema


