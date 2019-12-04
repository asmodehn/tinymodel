"""
Module to represent categorical product of usable domain model language/concepts in python.
# Should at least handle :
# - classes
# - dataclasses
# All composed python/json datastructure/types (dicts? schemas?)
"""


import decimal
import enum
import typing

import hypothesis
import hypothesis.strategies as strats
from marshmallow import Schema


from tinymodel import schemas


class Product:
    """
    >>> prod = Product('the', 'answer', 'is', 42)
    42
    >>> repr(prod)
    42
    >>> str(prod)
    '42'
    """
    type: typing.Type[typing.Any]  #TODO : refine
    schema: Schema
    #strategy: strats.SearchStrategy  # TODO ...
    value: typing.Any  # TODO : refine

    def __init__(self, *args: typing.Union[bytes, int, str]):  # static type check for user code.
        self.args = args
        from ..schemas.product import product
        self.field = product(args)  # single dispatch based on value type to retrieve schema/field

    # NOTE : do not overload __call__ here, we should keep it available for user customization for his own behavior...

    # Note : This is the unambiguous interface. Safe, use for "external"/deterministic/automated communication
    def __repr__(self):
        pass

    # Note: This is the pretty interface. Safe, use for "external/biased/contextual/human communication
    def __str__(self):
        pass

    # Note : this is the pickle interface. unsafe, use only for "internal"/"known" communication.
    def __setstate__(self, state):
        pass

    def __getstate__(self):
        pass