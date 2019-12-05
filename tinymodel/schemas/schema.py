import typing
from functools import singledispatch

from tinymodel.schemas.atom import atom
from tinymodel.schemas.product import product
from tinymodel.schemas.union import union


@singledispatch
def schema(*args, **kwargs):
    if len(args) == 1:
        return product(args[0], product(**kwargs))
    else:
        return product(
            union(*args),
            product(**kwargs)
        )


@schema.register
def _(model_atom: typing.Union[int, bytes, str]):
    return atom(model_atom)
