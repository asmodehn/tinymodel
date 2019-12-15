
"""

Inspired from marshmallow structure :

- Schema <-> Model
- Field <-> Data
- code <-> Behavior

This data module gather all basic python types, but given a "behavioral? "extrensic" meaning, as well as runtime consistency

"""
import datetime
import dis
import functools
import inspect
import pickle
import random
import types
import typing
from collections import OrderedDict
from pprint import pformat
from uuid import uuid4

import dill
import hypothesis
import hypothesis.strategies as st
import tinydb
from marshmallow import fields
from tinydb import TinyDB

runsig = uuid4()


class DataBase:

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


# def DynaMeta(impl: typing.Type[typing.Any], db: TinyDB, field: fields.Field):
# 
#     class DataMeta(type):
# 
#         def __init__(cls, name, bases, attributes):
#             cls.table = db.table(name)
#             cls.table_idx = db.table((name+"_idx"))
#             cls.field = field()  # instantiation of schema
#             # strategy: strats.SearchStrategy  # TODO ...
# 
#             bases += (DataBase, )
# 
#             # we replace the name (internal implementation here) with the user's implementation name
#             super(DataMeta, cls).__init__(impl.__name__, bases, attributes)
# 
#         @functools.lru_cache(maxsize=128)  # enforcing pure functionality, via lru_cache.
#         def __getitem__(self, item):
#             if not hasattr(self, 'idx'):
#                 self.idx = OrderedDict()  # cached index
# 
#             if item not in self.idx:  # search needed (based on previous storage structure...)
#                 # build a new instance of the model since it is not in cache.
# 
#                 q = TinyDB.Query()
#                 item_queried = self.table_idx.search(q.arg == item)
#                 assert isinstance(item_queried, list)
#                 assert len(item_queried) in (0, 1)
#                 if not item_queried:
#                     item_val = self(item)  #TODO : product...
#                     serialized = self.schema.dump(item_val.value)  # serialize it
#                     self.idx[item] = self.table.insert(serialized)  # and store it
#                     self.table_idx.insert({'arg': item, 'idx': self.idx[item]})
#                 else:
#                     item_idx = item_queried[0]  # get the first and only result
#                     self.idx[item] = item_idx.get('idx')
#                     serialized = self.table.get(doc_id=self.idx[item])
#                     item_val = self(**self.schema.load(serialized))  # just to get the model (via marshmallow postload)
# 
#             assert item in self.idx
# 
#             return item_val
# 
#         def __iter__(self):
#             return iter([e.get('name', 'UNKNOWN') for e in self.table])
# 
#         def __len__(self):
#             return len(self.table)
# 
#     return DataMeta



def DynaMeta(impl: typing.Type[typing.Any], db: TinyDB):

    class MetaData(type):

        def __init__(cls, name, bases, attributes):
            cls.table = db.table(impl.__name__)
            # cls.table_idx = db.table((name+"_idx"))
            # cls.field = field()  # instantiation of schema
            # strategy: strats.SearchStrategy  # TODO ...

            bases += (DataBase, )

            # we replace the name (internal implementation here) with the user's implementation name
            super(MetaData, cls).__init__(impl.__name__, bases, attributes)

        def __getitem__(self, item):
            
            if callable(self.value):
                name = self.value.__name__
                # retrieve stored cache for this callable
                q = TinyDB.Query()
                cache_queried = self.type_table.search(q.name == name)
                assert len(cache_queried) in (0, 1)
                if not cache_queried:  # No result, we must create it
                    # create new map as cache for callable
                    self.cache = {}
                    # store in type table
                    cache_id = self.type_table.insert({'name': name, 'cache': {}})
                    self.cache = self.type_table.get(cache_id).get('cache')
                else:  # TODO : compare all this with klepto...
                    self.cache = cache_queried[0].get('cache')  # get first and only result
            else:
                # table not needed, constant is embedded in code instead
                self.table = None
            
            
            if isinstance(self.value, int):
                return self.value
            elif len(inspect.getfullargspec(self.value).args) == 0:
                return self.value()  #ignoring arg if not present.
            else:
                if item not in self.cache:
                    return self.cache[item]
                else:  # TODO : progressive cache... only cache after n tries in some time interval...
                    self.cache[item] = self.value(item)
                    # store in cache
                    self.db.update({'name': self.value.__name__}, tinydb.Query().cache == self.cache)

                # TODO: async passive verification on non-cached version...
                return self.cache[item]




class BaseData:
    pass



def observably_similar(a, b, dist=None):
    """
    Returns similarity under a distribution of arguments
    :param a:
    :param b:
    :param dist:
    :return:
    """

    strat = None

    # picking a strategy based on a and exploring
    if hasattr(a, 'index_domain'):
        if a.index_domain == int:
            if strat is None:
                strat = hypothesis.strategies.integers()
            adist = strat.map(a)
        else:
            raise NotImplementedError(f"Unknown index Domain: {a.index_domain}")
    else:  # assumed constant
        adist = None  # TODO: generate a dist of A

    if hasattr(b, 'index_domain'):
        if b.index_domain == int:
            if strat is None:
                strat = hypothesis.strategies.integers()
            bdist = strat.map(a)
        else:
            raise NotImplementedError(f"Unknown index Domain: {b.index_domain}")
    else:  # assumed constant
        bdist = None  # TODO : generate a dist of B

    if adist is not None and bdist is None:
        bdist = strat.map(b)
    if bdist is not None and adist is None:
        adist = strat.map(a)

    # TODO : A simpler way to check search strategy equality
    # sampled = [draw(adist)]

    return adist == bdist  # TODO : generate a composite strategy instead...


def int_class(permadb: TinyDB):

    class Int:
        # classvar is cleaner than playing with metaclasses
        db: typing.ClassVar[TinyDB] = permadb
        table: typing.ClassVar[typing.Any] = db.table("Int")  # TODO : type table properly ?
        
        def __init__(self, fun: typing.Union[int, typing.Callable[[typing.Hashable], int]]):

            # assert not fun.__closure__  # make sure it is not a closure -> no side effect in code => can be cached
            # how about constant values in closure ? but they can change without being rflected in the bytecode...

            self.value = fun if callable(fun) else lambda _: fun  # make it a callable to treat everything the same.
            # Having special cases for a constant is an optimization.

            funspec = inspect.getfullargspec(self.value)
            self.index_domain = funspec.annotations.get(funspec.args[0])
            # TODO : validate index_domain ?

            self.name = self.value.__qualname__ + ("_[" + "_".join(str(cv.cell_contents) for cv in self.value.__closure__) + "]_") if self.value.__closure__ else ""
            # retrieve stored cache for this callable
            q = tinydb.Query()
            assert self.table.count(q.name == self.name) in (0, 1)  # TODO otherwise delete it ???
            self.cache_doc = self.table.get(q.name == self.name)

            if self.cache_doc is None:
                # store in type table
                # TODO : refine runsig... maybe with versioning ? or datetime ?
                cache_id = self.table.insert({'run': runsig.hex, 'name': self.name, 'bytecode': [str(i) for i in dis.get_instructions(self.value)], 'cache': {}})
                self.cache_doc = self.table.get(doc_id=cache_id)

            else:  # retrieving old callable cache...
                # name is same as per the query
                assert self.cache_doc['name'] == self.name

                # compare bytecode:
                current_bytecode = [str(i) for i in dis.get_instructions(self.value)]

                if runsig.hex == self.cache_doc['run'] and current_bytecode != self.cache_doc['bytecode']:  # this run !
                    # TODO : Need improvement, what about higher order functions + imperative closures ??!!
                    # => related with functional implicitely guaranteed by cache ??
                    raise RuntimeError(" Two functions with same name have been identified ! Caches will be mixed !")  # TODO : improve
                elif self.cache_doc['bytecode'] != current_bytecode:  # we assume named function has been erased and replaced
                    self.cache_doc['bytecode'] = current_bytecode
                    self.cache_doc['cache'] = {}  # erasing cache
                    self.table.write_back([self.cache_doc])

            self.cache = self.cache_doc['cache']  # reference !

        def __eq__(self, other):
            if not isinstance(other, Int):
                return False  # different types, NO implicit cast/coerce
            else:
                # TODO : maybe better to do this by leveraging getitem [] for simplicity ??
                if self.cache.keys() <= other.cache.keys():
                    # check equality on existing values
                    eq = all(v == other.cache[s] for s, v in self.cache.items())
                    if not eq:
                        return False  # early exit
                    # add required values to finish comparison
                    for s in other.cache.keys() - self.cache.keys():
                        eq = eq and other[s] == self[s]
                elif other.cache.keys() <= self.cache.keys():
                    # check equality on existing values
                    eq = all(v == self.cache[o] for o, v in other.cache.items())
                    if not eq:
                        return False  # early exit
                    # add required values to finish comparison
                    for s in self.cache.keys() - other.cache.keys():
                        eq = eq and self[s] == other[s]
                else:
                    return False  # cannot be equal

        def __getitem__(self, item: typing.Hashable):
            if isinstance(self.value, int):  # TODO : remove if we use lambda instead of constant
                return self.value  # TODO : or self ?? what about equality ??
            elif len(inspect.getfullargspec(self.value).args) == 0:
                return self.value()  #ignoring arg if not present.
            else:
                if item in self.cache:
                    return self.cache[item]
                else:  # TODO : progressive cache... only cache after n tries in some time interval...
                    self.cache[item] = self.value(item)
                    try:
                        # store cache in DB
                        self.table.write_back([self.cache_doc])
                    except TypeError:
                        raise
                # TODO: async passive verification on non-cached version...
                return self.cache[item]

            # TODO : compared with stored DB value...

        # TODO : iter and len, repr, str, ...

        # Note : this is the pickle interface. unsafe, use only for "internal"/"known environment" communication.
        def __getstate__(self):
            return self.value

        def __setstate__(self, state):
            self.value = state

        # delegating everything else to the internal value for transparent usage
        def __getattr__(self, item):
            return getattr(self.value, item)

    return Int

# class Str:
#     def __init__(self, fun: typing.Union[str, typing.Callable[[typing.Hashable], str]]):
#         self.value = fun
#
#     @functools.lru_cache(maxsize=128)  # enforcing pure functionality, via lru_cache.
#     def __getitem__(self, item: typing.Hashable):
#         if isinstance(self.value, str):
#             return self.value
#         elif len(inspect.getfullargspec(self.value).args) == 0:
#             return self.value()  #ignoring arg if not present.
#         else:
#             return self.value(item)
#
#     # TODO : iter and len, repr, str, ...
#
#     # TODO : check dill and klepto for this ?
#     def __getstate__(self):
#         return self.value
#
#     def __setstate__(self, state):
#         self.value = state

#
# class CoInt:
#     def __init__(self, fun: typing.Callable[[int], typing.Any]):
#         self.fun = functools.lru_cache(maxsize=128)(fun)
#
#     def __getitem__(self, item: int):
#         return self.fun(item)
#
#
# class CoStr:
#     def __init__(self, fun: typing.Callable[[str], typing.Any]):
#         self.fun = functools.lru_cache(maxsize=128)(fun)
#
#     def __getitem__(self, item: str):
#         return self.fun(item)


@functools.singledispatch
def data_dispatcher(pydat, db: TinyDB):
    raise NotImplementedError(type(pydat))


@data_dispatcher.register
def _(pydat: type, db:TinyDB):

    if pydat == typing.Callable[[typing.Hashable], int]:
        return int_class(permadb=db)(pydat)
    # elif pydat == typing.Callable[[typing.Hashable], str]:
    #     return Str
    # elif pydat == typing.Callable[[int], typing.Any]:
    #     return CoInt
    # elif pydat == typing.Callable[[str], typing.Any]:
    #     return CoStr
    else:
        raise NotImplementedError(pydat)


# to directly lift functions and values
@data_dispatcher.register
def _(pydat: types.FunctionType, db:TinyDB):
    spc = inspect.getfullargspec(pydat)

    if spc.annotations.get('return') == int:
        return int_class(permadb=db)(pydat)
    # elif spc.annotations.get('return') == str:
    #     return Str(pydat)

    # elif spc.annotations.get('return') ==:
    #     return CoInt
    # elif pydat == typing.Callable[[str], typing.Any]:
    #     return CoStr
    else:
        raise NotImplementedError(pydat)


@data_dispatcher.register
def _(pydat: int, db: TinyDB):
    return int_class(permadb=db)(pydat)


# @data_dispatcher.register
# def _(pydat: str):
#     return Str(pydat)


def data(permadb: TinyDB):

    def decorator(pd):

        return data_dispatcher(pd, db=permadb)

    return decorator


if __name__ == '__main__':

    @data(permadb=TinyDB("data_test.json"))
    def fun(v:int) -> int:
        return v+3

    v = fun[39]

    w = fun[39]

    # These are the same
    assert v == w

    # And they can be used as usual class instance
    internal = pickle.dumps(v)
    assert internal == b'\x80\x03K*.', internal


    @data(permadb=TinyDB("data_test.json"))
    def funbis() -> int:
        return 3

    v = fun[39]

    w = fun[39]

    # These are the same
    assert v == w

    # And they can be used as usual class instance
    assert v == 42

    dv = data(permadb=TinyDB("data_test.json"))(42)

    assert dv[1] == dv[89] == dv  # argument is ignore, this is a constant
