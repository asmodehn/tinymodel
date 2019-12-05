import unittest
from hypothesis import given, infer
from marshmallow import fields

from ..models.atom import Atom


class TestInt(unittest.TestCase):

    @given(pyvalue=infer)
    def test_atom_init(self, pyvalue: int):
        a = Atom(pyvalue)

        # verifies properties of the atom
        assert isinstance(a, Atom)
        assert a.type == int
        assert a.field == fields.Int
        assert a.value == pyvalue


class TestStr(unittest.TestCase):
    @given(pyvalue=infer)
    def test_atom_str(self, pyvalue: str):
        a = Atom(pyvalue)

        # verifies properties of the atom
        assert isinstance(a, Atom)
        assert a.type == str
        assert a.field == fields.Str
        assert a.value == pyvalue