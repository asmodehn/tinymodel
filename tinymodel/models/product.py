"""
Module to represent categorical product of usable domain model language/concepts in python.
# Should at least handle :
# - classes
# - dataclasses
# All composed python/json datastructure/types (dicts? schemas?)
"""

from __future__ import annotations

import decimal
import enum
import functools
import typing
from pprint import pformat

import hypothesis
import hypothesis.strategies as strats
from marshmallow import Schema

from tinymodel.schemas.product import product as product_schema


class Product:
    """
    >>> prod = Product(the_sentence='the answer is ', the_answer=42)
    42
    >>> repr(prod)
    42
    >>> str(prod)
    '42'
    """
    # TODO : put that in a small "invisible" data strucrture
    type: typing.Type[typing.Any]  #TODO : refine
    schema: Schema
    #strategy: strats.SearchStrategy  # TODO ...
    value: typing.Dict[typing.Any]  # TODO : refine

    def __init__(self, **kwargs: typing.Union[bytes, int, str, Product]):  # static type check for user code.
        self.value = kwargs
        self.field = product_schema(**kwargs)  # single dispatch based on value type to retrieve schema/field

    # NOTE : do not overload __call__ here, we should keep it available for user customization for his own behavior...

    # Note : This is the unambiguous interface. Safe, use for "external"/deterministic/automated communication
    def __repr__(self):
        return str(self.value)

    # Note: This is the pretty interface. Safe, use for "external/biased/contextual/human communication
    def __str__(self):
        return pformat(self.value)

    # Note : this is the pickle interface. unsafe, use only for "internal"/"known" communication.
    def __setstate__(self, state):
        raise NotImplementedError

    def __getstate__(self):
        raise NotImplementedError


@functools.lru_cache(maxsize=128, typed=True)   # enforcing purity, and ensuring type distinction...
def product(**kwargs: typing.Any):
    return Product(**kwargs)
