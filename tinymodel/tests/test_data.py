import typing
import unittest

from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from ..data import data

from hypothesis import given, infer
import hypothesis.strategies as st


class TestIntData(unittest.TestCase):

    def setUp(self) -> None:
        # Setup temporary TinyDB
        self.testdb = TinyDB("test_data.json")

    @given(value=infer)
    def test_int(self, value: int):
        i = data(permadb=self.testdb)(value)

        assert i[42] == value

        # TODO : proper observable equality based on a set of calls

        # assert dist_equal(value, i),  f"{value} != {i}"  # equality of instances/values
        # assert dist_equal(i[42], i), f"{i[42]} != {i}"  # index is ignored

    @given(retval=infer)
    def test_callint(self, retval: int):
        def clbl(arg: int) -> int:
            return retval

        i = data(permadb=self.testdb)(clbl)

        assert i[42] == i[42]

        # TODO : proper observable equality based on a set of calls

        # assert dist_equal(retval, i), f"{retval} != {i}"  # equality of instances/values
        # assert dist_equal(i[42], i), f"{i[42]} != {i}"  # index is ignored

    #TODO : lambda

class TestStrData(unittest.TestCase):

    pass