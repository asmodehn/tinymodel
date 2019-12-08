"""
Module to handle translation for categorical product of usable domain model language/concepts.
Should at least handle :
- tuples
- dicts
- classes (inc. slots)
- dataclasses


Note : These are mostly handled by the developer, traditionally
"""
import dataclasses
from functools import singledispatch

from dataclasses import dataclass

import marshmallow
from marshmallow import fields


def product(model, cps=None):

    # delayed import
    from tinymodel.schemas.schema import schema, schemas
    cps = schema if cps is None else cps

    # function registering itself, to mark the class as product via schema singledispatch
    schema.register(model, product)

    def construct(self, data, **kwargs):
        return model(**data)

    if dataclasses.is_dataclass(model):

        schema_fields = {
            # Note : we instantiate the marshmallow fields here
            f.name: cps(f.type)() for f in dataclasses.fields(model)
        }
        schema_fields.update({
            'construct': marshmallow.post_load()(construct)
        })

        schm = marshmallow.Schema.from_dict(schema_fields)
        # TODO : solve recursivity problem... (field of its own type...)
        schemas[model] = schm

    else:
        raise NotImplementedError  # TODO : more cases

    return schemas[model]


