import unittest
from dataclasses import dataclass

from hypothesis import given, infer
from marshmallow import fields, Schema

from tinymodel.models.model import model
from tinymodel.models.product import product, Product

class TestFrozenDataclass(unittest.TestCase):

    @given(field1=infer, field2=infer)
    def test_product_init(self, field1: str, field2: int):

        # the user data model
        @dataclass(frozen=True)
        class TwoFields:
            f1: type(field1)
            f2: type(field2)

        i = TwoFields(f1=field1, f2=field2)

        # explicit usage, but this is a 'class decorator'.
        TP = product()(TwoFields)

        tp = TP(i)

        # what tiny model does with it...

        # verifying properties of the value itself
        assert tp.value == i

        # verifies properties of the model
        assert isinstance(tp, Product)

        # verifies reversibility properties of the schema load/dump methods
        assert isinstance(tp.schema, Schema)
        dumped = tp.schema.dump(i)
        loaded = tp.schema.load(dumped)
        assert loaded == i, print(f"{loaded} != {i}")
        redumped = tp.schema.dump(loaded)
        assert redumped == dumped, print(f"{redumped} != {dumped}")



