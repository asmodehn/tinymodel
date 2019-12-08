import dataclasses
import typing
from functools import singledispatch

from tinymodel.models.atom import AtomInt, AtomStr
from tinymodel.models.product import product
from tinymodel.models.union import union

# Using mapping data structure to deal with types
models = {
    int: AtomInt,
    str: AtomStr,
}

# using function with singledispatch to deal with values of the type...
@singledispatch
def model(model):
    raise NotImplementedError


@model.register
def _(model_type: type):
    """
    Specialization to deal with types directly, based on mapping datastructure (deterministic & minimum computation)
    :param model_type:
    :return:
    """
    return models[model_type]


@model.register
def _(model_atom: int):
    return AtomInt(model_atom)


@model.register
def _(model_atom: str):
    return AtomStr(model_atom)
