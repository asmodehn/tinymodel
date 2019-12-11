import dataclasses
import functools
import typing
from functools import singledispatch
from pprint import pformat

from tinymodel.product import product

from collections import OrderedDict

from tinydb import Query, TinyDB
from marshmallow import Schema
"""
Provides a Mapping interface to access class instances, stored in tinydb.
This implies that class __init__() are, semantically, purely functional.

"""


class ModelBase:

    # Note : This is the unambiguous interface. Safe, use for "external"/deterministic/automated communication
    def __repr__(self):
        return str(self.value)

    # Note: This is the pretty interface. Safe, use for "external/biased/contextual/human communication
    def __str__(self):
        return pformat(self.value)

    # Note : this is the pickle interface. unsafe, use only for "internal"/"known" communication.
    def __setstate__(self, state):
        self.value = state

    def __getstate__(self):
        raise NotImplementedError


def DynaMeta(impl: typing.Type[typing.Any], db: TinyDB, schema: Schema):

    class ModelMeta(type):

        def __init__(cls, name, bases, attributes):
            cls.table = db.table(name)
            cls.table_idx = db.table((name+"_idx"))
            cls.schema = schema()  # instantiation of schema
            # strategy: strats.SearchStrategy  # TODO ...

            bases += (ModelBase, )

            # we replace the name (internal implementation here) with the user's implementation name
            super(ModelMeta, cls).__init__(impl.__name__, bases, attributes)

        @functools.lru_cache(maxsize=128)  # enforcing pure functionality, via lru_cache.
        def __getitem__(self, item):
            if not hasattr(self, 'idx'):
                self.idx = OrderedDict()  # cached index

            if item not in self.idx:  # search needed (based on previous storage structure...)
                # build a new instance of the model since it is not in cache.

                q = Query()
                item_queried = self.table_idx.search(q.arg == item)
                assert isinstance(item_queried, list)
                assert len(item_queried) in (0, 1)
                if not item_queried:
                    item_val = self(item)  #TODO : product...
                    serialized = self.schema.dump(item_val.value)  # serialize it
                    self.idx[item] = self.table.insert(serialized)  # and store it
                    self.table_idx.insert({'arg': item, 'idx': self.idx[item]})
                else:
                    item_idx = item_queried[0]  # get the first and only result
                    self.idx[item] = item_idx.get('idx')
                    serialized = self.table.get(doc_id=self.idx[item])
                    item_val = self(**self.schema.load(serialized))  # just to get the model (via marshmallow postload)

            assert item in self.idx

            return item_val

        def __iter__(self):
            return iter([e.get('name', 'UNKNOWN') for e in self.table])

        def __len__(self):
            return len(self.table)

    return ModelMeta


# using function with singledispatch, mostly to deal with values of the type...
@singledispatch
def model_dispatcher(model):
    # TODO : we probably need to deal with unions here...
    raise NotImplementedError

# late imports
from .atom import AtomInt, AtomStr
# Using mapping data structure to deal with types
models = {
    int: AtomInt,
    str: AtomStr,
}


@model_dispatcher.register
def _(model_type: type, db: TinyDB):
    """
    Specialization to deal with types directly, based on mapping datastructure (deterministic & minimum computation)
    :param model_type:
    :return:
    """
    if dataclasses.is_dataclass(model_type):
        return product(db=db)(model_type)
    return models[model_type]

# Maybe useless ??
@model_dispatcher.register
def _(model_atom: int, db: TinyDB):
    return AtomInt(model_atom)


@model_dispatcher.register
def _(model_atom: str, db: TinyDB):
    return AtomStr(model_atom)


def model(permadb: TinyDB):

    def decorator(cls):
        return model_dispatcher(cls, db=permadb)

    return decorator