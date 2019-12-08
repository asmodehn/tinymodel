import unittest
from hypothesis import given, infer
from marshmallow import fields

from ..models.atom import AtomInt, AtomStr


class TestInt(unittest.TestCase):

    @given(pyvalue=infer)
    def test_atom_int(self, pyvalue: int):
        a = AtomInt(pyvalue)

        # verifies properties of the atom
        assert isinstance(a.field,fields.Int)
        assert a.value == pyvalue


class TestStr(unittest.TestCase):
    @given(pyvalue=infer)
    def test_atom_str(self, pyvalue: str):
        a = AtomStr(pyvalue)

        # verifies properties of the atom
        assert isinstance(a.field, fields.String)
        assert a.value == pyvalue

#TODO : TestBytes
