import dataclasses
import typing
from functools import singledispatch

from marshmallow import fields

from tinymodel.schemas.atom import atom
from tinymodel.schemas.product import product
from tinymodel.schemas.union import union


# Using mapping data structure to deal with types
schemas = {
    int: fields.Integer,
    str: fields.String,
}

# using function with singledispatch to deal with values of the type...
@singledispatch
def schema(model):
    raise NotImplementedError


@schema.register
def _(model_type: type):
    """
    Specialization to deal with types directly, based on mapping datastructure (deterministic & minimum computation)
    :param model_type:
    :return:
    """
    return schemas[model_type]


# FOLLOWING : values specialization based on the type (using single dispatch) #
# Note : there are two orthogonal "functional" relationship semantic here...
@schema.register
def _(model_atom: int):
    return atom(model_atom)


@schema.register
def _(model_atom: str):
    return atom(model_atom)