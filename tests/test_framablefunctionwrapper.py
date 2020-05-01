import asyncio
import inspect
import unittest
from asyncio import Task

import wrapt
from hypothesis import given
import hypothesis.strategies as st

from framable.framablefunctionwrapper import framed


def function_test(*args, **kwargs):
    return args, kwargs


class TestFramableFunctionWrapper(unittest.TestCase):

    @classmethod
    def class_boundfunction_test(cls, *args, **kwargs):
        return args, kwargs

    @staticmethod
    def static_boundfunction_test(*args, **kwargs):
        return args, kwargs

    def boundfunction_test(self, *args, **kwargs):
        return args, kwargs

    @given(args=st.tuples(st.integers()),
           kwargs=st.dictionaries(keys=st.text(max_size=5), values=st.integers()))
    def test_framable_function(self, args, kwargs):
        cf = framed()(function_test)
        assert isinstance(cf, wrapt.FunctionWrapper)
        cc = cf(*args, **kwargs)

        # usual result
        resa, reskwa = cc
        assert resa == args
        assert reskwa == kwargs
        # callframe should have arguments
        a, kwa = cf._self_callframe.loc[0]
        assert resa == a
        assert reskwa == kwa
        # returnframe should have result
        resa, reskwa = cf._self_returnframe.loc[0].result
        assert resa == args
        assert reskwa == kwargs

    @given(args=st.tuples(st.integers()),
           kwargs=st.dictionaries(keys=st.text(max_size=5), values=st.integers()))
    def test_framable_static_boundfunction(self, args, kwargs):
        TestFramableFunctionWrapper.dsf = framed()(TestFramableFunctionWrapper.static_boundfunction_test)
        assert isinstance(TestFramableFunctionWrapper.dsf, wrapt.BoundFunctionWrapper)
        cc = TestFramableFunctionWrapper.dsf(*args, **kwargs)

        # usual result
        resa, reskwa = cc
        assert resa == args
        assert reskwa == kwargs
        # callframe should have arguments
        a, kwa = TestFramableFunctionWrapper.dsf._self_callframe.loc[0]
        assert resa == a
        assert reskwa == kwa
        # returnframe should have result
        resa, reskwa = TestFramableFunctionWrapper.dsf._self_returnframe.loc[0].result
        assert resa == args
        assert reskwa == kwargs

    @given(args=st.tuples(st.integers()),
           kwargs=st.dictionaries(keys=st.text(max_size=5), values=st.integers()))
    def test_framable_class_boundfunction(self, args, kwargs):
        TestFramableFunctionWrapper.dcf = framed()(TestFramableFunctionWrapper.class_boundfunction_test)
        assert isinstance(TestFramableFunctionWrapper.dcf, wrapt.BoundFunctionWrapper)
        cc = TestFramableFunctionWrapper.dcf(*args, **kwargs)

        # usual result
        resa, reskwa = cc
        assert resa == args
        assert reskwa == kwargs
        # callframe should have arguments
        a, kwa = TestFramableFunctionWrapper.dcf._self_callframe.loc[0]
        assert resa == a
        assert reskwa == kwa
        # returnframe should have result
        resa, reskwa = TestFramableFunctionWrapper.dcf._self_returnframe.loc[0].result
        assert resa == args
        assert reskwa == kwargs

    @given(args=st.tuples(st.integers()),
           kwargs=st.dictionaries(keys=st.text(max_size=5), values=st.integers()))
    def test_framable_boundfunction_early(self, args, kwargs):
        # simulating deacorating (with early decoration)
        TestFramableFunctionWrapper.bfe = framed()(TestFramableFunctionWrapper.boundfunction_test)
        # this will trigger __init__ of boundfunctionwrapper (with None as instance)
        assert isinstance(self.bfe, wrapt.BoundFunctionWrapper)
        bfe = self.bfe(*args, **kwargs)

        # usual result
        resa, reskwa = bfe
        assert resa == args
        assert reskwa == kwargs
        # callframe should have arguments, AND self, since it was NOT obvious when we framed it
        # Which also means all other instances WILL have the frame.
        s, a, kwa = self.bfe._self_callframe.loc[0]
        assert self == s
        assert resa == a
        assert reskwa == kwa
        # returnframe should have result
        resa, reskwa = self.bfe._self_returnframe.loc[0].result
        assert resa == args
        assert reskwa == kwargs

    @given(args=st.tuples(st.integers()),
           kwargs=st.dictionaries(keys=st.text(max_size=5), values=st.integers()))
    def test_framable_boundfunction_late(self, args, kwargs):
        # simulating decorating (with late decoration - equivalent to a function call of a partial method with self)
        self.bfl = framed()(self.boundfunction_test)
        assert isinstance(self.bfl, wrapt.FunctionWrapper)
        cc = self.bfl(*args, **kwargs)

        # usual result
        resa, reskwa = cc
        assert resa == args
        assert reskwa == kwargs
        # callframe should have arguments, but NOT self, since it was obvious when we framed it
        # Which also means other instances WONT have the frame.
        a, kwa = self.bfl._self_callframe.loc[0]
        assert resa == a
        assert reskwa == kwa
        # returnframe should have result
        resa, reskwa = self.bfl._self_returnframe.loc[0].result
        assert resa == args
        assert reskwa == kwargs


if __name__ == "__main__":
    unittest.main()
