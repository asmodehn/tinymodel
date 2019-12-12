import dataclasses
import functools
import inspect
import typing
from functools import singledispatch

import marshmallow
from marshmallow import fields, Schema
from marshmallow_union import Union

# Using mapping data structure to deal with types
fields_cache = {
    int: fields.Integer,
    str: fields.String,
}

# using function with singledispatch to deal with values of the type...
@singledispatch
def field(value: typing.Any):
    """
    Dealing here with typehints (usual types should be dealt in dispatcher specialization)
    Others values are not handled.
    :param model:
    :return:
    """
    # Trying to get info from special form type hints
    try:
        if value.__origin__ == typing.Union:
            # partial call here is temporary see https://github.com/adamboche/python-marshmallow-union/issues/26
            return functools.partial(Union, fields=[field(a)() for a in value.__args__])  # Note : dont forget to initialize the fields here!
        # TODO : handle classvar and others for cleaner model types ??
    except Exception as e:
        raise e


@field.register
def _(model_type: type):
    """
    Specialization to deal with python types directly (not type hints !)
    Used when dealing with user data (classes) based on mapping datastructure (deterministic & minimum computation)
    :param model_type:
    :return:
    """

    if model_type not in fields_cache:
        def construct(self, data, **kwargs):
            return model_type(**data)

        if dataclasses.is_dataclass(model_type):
            from tinymodel.schema import schema
            fields_cache[model_type] = fields.Nested(schema(model_type))
        else:
            raise NotImplementedError  #TODO : more usecases...
    return fields_cache[model_type]


# FOLLOWING : values specialization based on the type of an instance (using single dispatch) #
# Note : there are two orthogonal "functional" relationship semantic here.
# These are only useful for building field, after an instance have been retrieved...
@field.register
def _(model_atom: int):
    return fields.Integer


@field.register
def _(model_atom: str):
    return fields.String


if __name__ == '__main__':

    assert field(int) == fields.Integer
    assert field(str) == fields.String

    s = field(typing.Union[int, str])
    # This cannot be asserted... currently a partial call.
    # assert schema(typing.Union[int, str]) == Union

    assert isinstance(s()._candidate_fields[0], fields.Integer), s()._candidate_fields[0]
    assert isinstance(s()._candidate_fields[1], fields.String), s()._candidate_fields[1]

    b = 42
    bf = field(b)
    assert bf == field(type(b))  # maybe unnecessary ?

    bfi = bf()
    ser = bfi.serialize('v', {'v': b})
    assert ser == 42, ser
    des = bfi.deserialize(ser)
    assert des == b, des
