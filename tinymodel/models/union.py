"""
Module to represent categorical sum of usable domain model language/concepts in python.
# Should at least provide:
- tagged unions
# Maybe via a meta class changing the semantics of attributes in a class : there can be only one...
# or a decorator, the co-dataclass semantics.
"""
from __future__ import annotations
import functools
import typing
from pprint import pformat

from marshmallow import Schema

from tinymodel.schemas.union import union as union_schema


class Union:
    """
    >>> prod = Union('the', 'answer', 'is', 42)
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

    def __init__(self, *args: typing.Union[bytes, int, str, Product, Union]):  # static type check for user code.
        self.value = args
        self.field = union_schema(*args)  # single dispatch based on value type to retrieve schema/field

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
def union(*args: typing.Any):
    return Union(*args)
