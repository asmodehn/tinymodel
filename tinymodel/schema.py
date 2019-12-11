import dataclasses
import functools
import typing
from functools import singledispatch

import marshmallow
from marshmallow import fields, Schema
from marshmallow_union import Union

# Using mapping data structure to deal with types
schemas = {
    int: fields.Integer,
    str: fields.String,
}

# using function with singledispatch to deal with values of the type...
@singledispatch
def schema(model):
    # Trying to get info from special form type hints
    try:
        if model.__origin__ == typing.Union:
            # partial call here is temporary see https://github.com/adamboche/python-marshmallow-union/issues/26
            return functools.partial(Union, fields=[schema(a) for a in model.__args__])
        # TODO : handle classvar and other for cleaner model types ??
    except Exception as e:
        raise e


@schema.register
def _(model_type: type):
    """
    Specialization to deal with python types directly (not type hints !)
    Used when dealing with user data (classes) based on mapping datastructure (deterministic & minimum computation)
    :param model_type:
    :return:
    """

    if model_type not in schemas:

        def construct(self, data, **kwargs):
            return model_type(**data)

        if dataclasses.is_dataclass(model_type):
            schema_fields = {
                # Note : we instantiate the marshmallow fields here
                f.name: schema(f.type)() for f in dataclasses.fields(model_type)
            }
            schema_fields.update({
                'construct': marshmallow.post_load()(construct)
            })

            schm = marshmallow.Schema.from_dict(schema_fields)
            # TODO : solve recursivity problem... (field of its own type...)
            schemas[model_type] = schm
        else:
            raise NotImplementedError

    return schemas[model_type]


# FOLLOWING : values specialization based on the type (using single dispatch) #
# Note : there are two orthogonal "functional" relationship semantic here...
@schema.register
def _(model_atom: int):
    return fields.Integer


@schema.register
def _(model_atom: str):
    return fields.String


if __name__ == '__main__':
    # TODO : proper docs and tests
    assert schema(int) == fields.Integer
    assert schema(str) == fields.String

    s = schema(typing.Union[int, str])
    # This cannot be asserted... currently a partial call.
    # assert schema(typing.Union[int, str]) == Union

    assert s()._candidate_fields == [fields.Integer, fields.String]


    @dataclasses.dataclass()
    class Bob:
        f1: int
        f2: str

    BobS = schema(Bob)

    # Cannot be asserted with the way marshmallow currently works
    # This is a generated schema
    # assert isinstance(BobS, Schema)

    # careful the fields are instantiated in the class itself...
    assert isinstance(BobS._declared_fields.get('f1'), fields.Integer)
    assert isinstance(BobS._declared_fields.get('f2'), fields.String)

