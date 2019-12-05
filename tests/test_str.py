"""
Tests a String model
"""
import pytest
from hypothesis import infer, given

from tinymodel.models.atom import atom


@given(model=infer)
def test_str(model: str):

    M = atom(model)

    # asserts M is stored forever.
    # A second call recover the same value (type constructor is functional)
    N = atom(model)
    assert N == M

    # TODO : figure out what properties type constructors must fulfill...


if __name__ == '__main__':
    pytest.main(['-s', __file__])



