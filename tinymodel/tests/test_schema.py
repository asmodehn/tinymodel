import dataclasses
import typing
import unittest
from dataclasses import dataclass

from hypothesis import given, infer
from marshmallow import Schema, fields

from tinymodel.schema import schema


class TestAtomSchema(unittest.TestCase):

    @given(v=infer)
    def test_atom_str(self, v: str):

        s = schema(str)
        assert isinstance(s._declared_fields.get('value'), fields.String)

        si = s()
        dumped = si.dump(v)
        assert dumped == v, dumped
        loaded = si.load(dumped)
        assert loaded == v, loaded

    @given(v=infer)
    def test_atom_int(self, v: int):

        s = schema(int)
        assert isinstance(s._declared_fields.get('value'), fields.Integer)

        si = s()
        dumped = si.dump(v)
        assert dumped == v, dumped
        loaded = si.load(dumped)
        assert loaded == v, loaded


class TestUnionSchema(unittest.TestCase):
    def test_union(self, v: typing.Union[int, str]):

        s = schema(typing.Union[int, str])
        # This cannot be asserted... currently a partial call.
        # assert schema(typing.Union[int, str]) == Union

        si = s()
        assert si._candidate_fields == [fields.Integer, fields.String]

        dumped = si.dump(v)
        assert dumped == v, dumped
        loaded = si.load(dumped)
        assert loaded == v, loaded


class TestProductSchema(unittest.TestCase):
    def test_product_tuple(self, v: typing.Tuple[int, str]):
        raise NotImplementedError

    def test_product_dataclass(self, f1: int, f2: str):

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

        b = Bob(f1=f1, f2=f2)
        bs = BobS()
        dumped = bs.dump(b)
        assert dumped == {'f2': f2, 'f1': f1}, dumped
        loaded = Bob(**bs.load(dumped))
        assert loaded == b, loaded

