import typing
from functools import singledispatch

from tinymodel.models.atom import atom
from tinymodel.models.product import product
from tinymodel.models.union import union


@singledispatch
def model(*args, **kwargs):
    if len(args) == 1:
        return product(args[0], product(**kwargs))
    else:
        return product(
            union(*args),
            product(**kwargs)
        )


@model.register
def _(model_atom: typing.Union[int, bytes, str]):
    return atom(model_atom)
