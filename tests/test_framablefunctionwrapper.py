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


class TestFramed(unittest.TestCase):

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
        # the trace should also have it
        # resa, reskwa = cf._self_trace[args][kwargs]
        # assert resa == args
        # assert reskwa == kwargs
        # Note : No future there, simply the call result.

    @given(args=st.tuples(st.integers()),
           kwargs=st.dictionaries(keys=st.text(max_size=5), values=st.integers()))
    def test_framable_boundfunction(self, args, kwargs):
        cf = framed()(function_test)
        assert isinstance(cf, wrapt.FunctionWrapper)
        cc = cf(*args, **kwargs)
        # usual result
        resa, reskwa = cc
        assert resa == args
        assert reskwa == kwargs
        # the trace should also have it
        # resa, reskwa = cf._self_trace[args][kwargs]
        # assert resa == args
        # assert reskwa == kwargs
        # Note : No future there, simply the call result.

    #
    # @given(args=st.integers(),
    #        kwargs=st.dictionaries(keys=st.text(max_size=5), values=st.integers()))
    # def test_traced_coroutine(self, *args, **kwargs):
    #     # testing a simple dict (minimum necessary interface to use the trace as a producer)
    #     self.trace = dict()
    #
    #     cf = framed()(coroutine_test)
    #     assert isinstance(cf, wrapt.FunctionWrapper)
    #     cc = cf(*args, **kwargs)
    #     assert inspect.iscoroutine(cc)
    #     # trace already has the future/task stored as the last element
    #     assert isinstance(self.trace[(args, kwargs)], Task)
    #     resa, reskwa = asyncio.run(cc)
    #     assert resa == args
    #     assert reskwa == kwargs
    #     assert self.trace[:-1].done()  # future is done()
    #     # and the result should be accessible
    #     resa, reskwa = self.trace[:-1]
    #     assert resa == args
    #     assert reskwa == kwargs

    #
    # @given(delay=st.floats(allow_nan=False, allow_infinity=False),
    #        args=st.integers(),
    #        kwargs=st.dictionaries(keys=st.text(max_size=5), values=st.integers()))
    # def test_delayed_generator(self, delay, *args, **kwargs):
    #     # obvious setup
    #     self.delayed = 0.0
    #     self.adelayed = 0.0
    #
    #     cf = delayed(delay=delay, sleeper=self.syncsleep)(generator_test)
    #     assert isinstance(cf, wrapt.FunctionWrapper)
    #     cc = cf(*args, **kwargs)
    #     assert self.delayed == delay  # already delayed here, before starting generator.
    #     assert self.adelayed == 0.0
    #     assert inspect.isgenerator(cc)
    #     # passing same args and kwargs to watcher for asserting
    #     resa, reskwa = generator_watcher(cc, *args, **kwargs)
    #     assert self.delayed == delay  # This was just a starting delay, not a throttle in generator loop.
    #     assert self.adelayed == 0.0
    #     assert resa == args
    #     assert reskwa == kwargs
    #
    # @given(delay=st.floats(allow_nan=False, allow_infinity=False),
    #        args=st.integers(),
    #        kwargs=st.dictionaries(keys=st.text(max_size=5), values=st.integers()))
    # def test_delayed_async_generator(self, delay, *args, **kwargs):
    #     # obvious setup
    #     self.delayed = 0.0
    #     self.adelayed = 0.0
    #
    #     cf = delayed(delay=delay, sleeper=self.asyncsleep)(async_generator_test)
    #     assert isinstance(cf, wrapt.FunctionWrapper)
    #     cc = cf(*args, **kwargs)
    #     assert self.delayed == 0.0
    #     assert self.adelayed == 0.0
    #     assert inspect.iscoroutine(cc)  # IS a coroutine ! wrapping an asyncgen !
    #     # passing same args and kwargs to watcher for asserting
    #     resa, reskwa = asyncio.run(awaitable_async_generator_watcher(cc, *args, **kwargs))
    #     assert self.delayed == 0.0
    #     assert self.adelayed == delay  # This was just a starting delay, not a throttle in generator loop
    #     assert resa == args
    #     assert reskwa == kwargs
    #
    # @given(delay=st.floats(allow_nan=False, allow_infinity=False),
    #        args=st.integers(), kwargs=st.dictionaries(keys=st.text(max_size=5), values=st.integers()))
    # def test_delayed_classmethod(self, delay, *args, **kwargs):
    #     # obvious setup
    #     self.delayed = 0.0
    #     self.adelayed = 0.0
    #
    #     # test decorating the method (doing it functionally for tests)
    #     ClassMethodTest.decmeth = delayed(delay=delay, sleeper=self.syncsleep)(ClassMethodTest.method)
    #     assert isinstance(ClassMethodTest.decmeth, wrapt.BoundFunctionWrapper)
    #
    #     # Instantiation of the class (must be in sync code !)
    #     ci = ClassMethodTest()
    #
    #     # calling it as usual as a method
    #     cc = ci.decmeth(*args, **kwargs)
    #     assert self.delayed == delay
    #     assert self.adelayed == 0.0
    #     resa, reskwa = cc
    #     assert resa == args
    #     assert reskwa == kwargs

    #TODO : decorating the class itself ? what semantics ? like decorating __init__ ? like a meta class, smthg else ? *typeclass* ?




if __name__ == "__main__":
    unittest.main()
