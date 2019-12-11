"""
Module to represent categorical product of usable domain model language/concepts in python.
# Should at least handle :
# - classes
# - dataclasses
# All composed python/json datastructure/types (dicts? schemas?)
"""

from __future__ import annotations

from tinydb import TinyDB

from tinymodel.schema import schema


def product(db):

    def wrapper(cls):

        from tinymodel.model import model_dispatcher, models, DynaMeta
        # function registering itself, to mark the class as product via schema singledispatch
        model_dispatcher.register(cls, product)

        metacls = DynaMeta(cls, db, schema(cls))

        class Product(metaclass=metacls):
            # strategy: strats.SearchStrategy  # TODO ...
            value: cls

            def __init__(self, *data):
                # an initialization from user data is always expected
                self.value = cls(*data)

                # we we are supposed to get the same exact model, the cache should be used...
                # if the cache is not used (full or smthg), then the equality check falls onto the value user's implementation...

            # NOTE : do not overload __call__ here, we should keep it available for user customization for his own behavior...

            # delegate everything else to user implementation
            def __getattr__(self, item):
                return getattr(self.value, item)

        models[cls] = Product

        return models[cls]

    return wrapper


if __name__ == '__main__':

    from dataclasses import dataclass
    @product(db=TinyDB("product_test.json"))
    @dataclass()
    class SomeTest:
        f1: int
        f2: str

        # TODO : careful defining the schema based on optional fields...
        def __init__(self, f1: int, f2: str = 'something constant'):
            self.f1 = f1
            self.f2 = 'something constant'

    v = SomeTest[42]

    w = SomeTest[42]

    # These are the same
    assert v == w  # TODO FIXME

    # And they can be used as usual class instance
    assert v.f1 == 42
    assert w.f2 == 'something constant'

