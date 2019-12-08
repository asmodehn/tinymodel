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
from tinymodel.schemas.schema import schema

# class Product:
#     """
#     >>> prod = Product(the_sentence='the answer is ', the_answer=42)
#     42
#     >>> repr(prod)
#     42
#     >>> str(prod)
#     '42'
#     """
#     # TODO : put that in a small "invisible" data strucrture
#     type: typing.Type[typing.Any]  #TODO : refine
#     schema: Schema
#     #strategy: strats.SearchStrategy  # TODO ...
#     value: typing.Dict[typing.Any]  # TODO : refine
#
#     def __init__(self, value: typing.Any):  # static type check for user code.
#         self.type = type(value)
#         self.value = value
#         self.schema = product_schema(value)  # single dispatch based on value type to retrieve schema/field



# TODO : factor in with model...
class Product:

    value: typing.Any

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


def product(*args):  # TODO : args ?

    def wrapper(cls):

        from tinymodel.models.model import model
        # function registering itself, to mark the class as product via schema singledispatch
        model.register(cls, product)

        class Model(Product):

            # TODO : put that in a small "invisible" data strucrture
            schema: Schema
            # strategy: strats.SearchStrategy  # TODO ...
            value: cls  # TODO : refine

            def __init__(self, value: cls):  # static type check for user code.
                self.value = value
                sch = product_schema(cls, cps=schema)  # single dispatch based on value type to retrieve schema/field
                self.schema = sch()  # we instantiate the schema here

            # NOTE : do not overload __call__ here, we should keep it available for user customization for his own behavior...

        return Model

    return wrapper
