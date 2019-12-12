import dataclasses
import typing
import unittest
from dataclasses import dataclass

from hypothesis import given, infer
from marshmallow import Schema, fields

from tinymodel.field import field


class TestField(unittest.TestCase):

    @given(v=infer)
    def test_str(self, v: str):

        f = field(str)
        assert f == fields.String

        fi = f()
        ser = fi.serialize('v', {'v': v})
        assert ser == v, ser  # TODO :: double check if string is same once dumped ??
        des = fi.deserialize(ser)
        assert des == v, des

    @given(v=infer)
    def test_int(self, v: int):

        f = field(int)
        assert f == fields.Integer

        fi = f()
        ser = fi.serialize('v', {'v': v})
        assert ser == v, ser  # TODO :: double check if int is same once dumped ??
        des = fi.deserialize(ser)
        assert des == v, des

    @given(v=infer)
    def test_union(self, v: typing.Union[int, str]):

        f = field(typing.Union[int, str])
        # This cannot be asserted... currently a partial call.
        # assert schema(typing.Union[int, str]) == Union

        fi = f()
        assert isinstance(fi._candidate_fields[0], fields.Integer), fi._candidate_fields[0]
        assert isinstance(fi._candidate_fields[1], fields.String), fi._candidate_fields[1]

        ser = fi.serialize('v', {'v': v})
        assert ser == v, ser  # TODO :: double check if int is same once dumped ??
        des = fi.deserialize(ser)
        assert des == v, des



