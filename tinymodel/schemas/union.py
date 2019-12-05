"""
Module to handle translation for categorical product of usable domain model language/concepts.
Should at least handle :
- <What is a union in python code ??? maybe just duck typing ??>
"""
import marshmallow


def union(*model):
    schema = type("", (marshmallow.Schema,), {
        type(m).__name__: m for m in model
    })
    return schema