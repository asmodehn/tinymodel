"""
Module to represent atomic components of usable domain model language/concepts in python.
# Should at least handle :
# - bytes
# - decimal (int and float are optimisations - careful with that)
# - str
# Goal : all basic python/json datastructures/types (list, tuples, array, etc)
"""
import decimal
import enum
import typing

import hypothesis
import hypothesis.strategies as strats
import marshmallow
import marshmallow.fields as fields


class Atom:
    """
    >>> answer = Atom(42)
    42
    >>> repr(answer)
    42
    >>> str(answer)
    '42'
    """
    type: typing.Type[typing.Any]  #TODO : refine
    field: fields.Field
    #strategy: strats.SearchStrategy  # TODO ...
    value: typing.Any  # TODO : refine

    def __init__(self, value: typing.Union[bytes, int, str]):  # static type check for user code.
        self.type = type(value)
        self.value = value
        from ..schemas.atom import atom
        self.field = atom(value)  # single dispatch based on value type to retrieve schema/field

    # NOTE : do not overload __call__ here, we should keep it available for user customization for his own behavior...

    # Note : This is the unambiguous interface. Safe, use for "external"/deterministic/automated communication
    def __repr__(self):
        pass

    # Note: This is the pretty interface. Safe, use for "external/biased/contextual/human communication
    def __str__(self):
        pass

    # Note : this is the pickle interface. unsafe, use only for "internal"/"known" communication.
    # Maybe for storage of tinymodel itself ???
    def __setstate__(self, state):
        pass

    def __getstate__(self):
        pass