import dataclasses
import functools
import inspect
import typing
from functools import singledispatch

import marshmallow
from marshmallow import fields, Schema
from marshmallow_union import Union

# Using mapping data structure to deal with types
schemas_cache = {}

# using function with singledispatch to deal with values of the type...
@singledispatch
def schema(model):
    """
    Dealing here with typehints (usual types should be dealt in dispatcher specialization)
    Others values are not handled.
    :param model:
    :return:
    """
    # Trying to get info from special form type hints
    try:
        pass
        # This is handled by fields now...
        # if model.__origin__ == typing.Union:
        #     # partial call here is temporary see https://github.com/adamboche/python-marshmallow-union/issues/26
        #     return functools.partial(Union, fields=[schema(a) for a in model.__args__])
        # TODO : handle classvar and others for cleaner model types ??
    except Exception as e:
        raise e


@schema.register
def _(model_type: type):  # single dispathc needed on top of cache ??
    """
    Specialization to deal with python types directly (not type hints !)
    Used when dealing with user data (classes) based on mapping datastructure (deterministic & minimum computation)
    :param model_type:
    :return:
    """

    if model_type not in schemas_cache:

        def construct(self, data, **kwargs):
            return model_type(**data)

        if dataclasses.is_dataclass(model_type):
            from tinymodel.field import field
            schema_fields = {
                # Note : we instantiate the marshmallow fields here
                f.name: field(f.type)() for f in dataclasses.fields(model_type)
            }
            # schema_fields.update({
            #     'construct': marshmallow.post_load()(construct)
            # })

            schm = marshmallow.Schema.from_dict(schema_fields)
            # TODO : solve recursivity problem... (field of its own type...)
            schemas_cache[model_type] = schm
        # TODO :
        # elif inspect.isclass(model_type):
        #     schema_fields = {
        #         # Note : we instantiate the marshmallow fields here
        #         f.name: schema(f.type)() for f in vars(model_type) if not f.startswith('__')
        #     }
        #     # schema_fields.update({
        #     #     'construct': marshmallow.post_load()(construct)
        #     # })
        #
        #     schm = marshmallow.Schema.from_dict(schema_fields)
        #     # TODO : solve recursivity problem... (field of its own type...)
        #     schemas[model_type] = schm
        else:
            raise NotImplementedError

    return schemas_cache[model_type]


# FOLLOWING : values specialization based on the type (using single dispatch) #
# Note : there are two orthogonal "functional" relationship semantic here...
@schema.register
def _(model_atom: int):
    return fields.Integer


@schema.register
def _(model_atom: str):
    return fields.String


if __name__ == '__main__':
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

    b = Bob(42, "bobby")
    bs = BobS()
    dumped = bs.dump(b)
    assert dumped == {'f2': 'bobby', 'f1': 42}, dumped
    loaded = Bob(**bs.load(dumped))
    assert loaded == b, loaded
