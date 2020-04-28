import functools
import inspect

import typing
import wrapt
import pandas as pd
from framable.core.framabletuple import FramableTuple


class FramableBoundFunctionWrapper(wrapt.BoundFunctionWrapper):

    def __init__(self, descriptor, instance,
                        _self_wrapper, _self_enabled,
                        _self_binding, _self_parent):
        super(FramableBoundFunctionWrapper, self).__init__(descriptor, instance,
                                                         _self_wrapper, _self_enabled,
                                                         _self_binding, _self_parent)
        self._self_signature = _self_parent._self_signature
        self._self_argtuple = _self_parent._self_argtuple

        # because bound function is not mutable we need to store the callframe on the instance instead
        if not hasattr(instance, "_methodframes"):
            setattr(instance, "_methodframes", dict())
        instance._methodframes.setdefault(descriptor.__name__, pd.DataFrame()) #self._self_signature, self._self_argtuple, instance=self._self_instance))
        # and indirectly refer to it here
        self._self_callframe = instance._methodframes[descriptor.__name__]
        self._self_descriptor = descriptor

    def __call__(self, *args, **kwargs):
        instance, args, kwargs, result = super(FramableBoundFunctionWrapper, self).__call__(*args, **kwargs)

        # we bind afterwards to retrieve the instance from wrapt
        bound_args = self._self_signature.bind(instance, *args, **kwargs)

        # building argtuple instance
        args = self._self_argtuple(**bound_args.arguments)

        # converting result...
        try:
            restuple = tuple(r for r in result)  # TODO : name this from annotations
        except TypeError as te:  # if not iterable
            restuple = (result,)

        #  we dont need to apply default here, it has already been done during the call
        instance._methodframes[self._self_descriptor.__name__] = self._self_callframe.append([args + restuple], ignore_index=True)
        # Note how we need to store the new dataframe in the methodframes mapping, or modification on method object will not work
        return result

    @property
    def __frame__(self):
        """ Accessing _self_callframe via property to prevent mutation """
        return self._self_callframe


class FramableFunctionWrapper(wrapt.FunctionWrapper):

    __bound_function_wrapper__ = FramableBoundFunctionWrapper

    def __init__(self, wrapped, wrapper, signature, argtuple):
        super(FramableFunctionWrapper, self).__init__(wrapped, wrapper)
        self._self_signature = signature
        self._self_argtuple = argtuple
        self._self_callframe = pd.DataFrame()  # empty dataframe before we have any data sample...

    def __call__(self, *args, **kwargs):
        instance, args, kwargs, result = super(FramableFunctionWrapper, self).__call__(*args, **kwargs)
        # we bind afterwards to retrieve the instance from wrapt
        if instance is None:   # tentative : TODO : thorough testing
            bound_args = self._self_signature.bind(*args, **kwargs)
        else:
            bound_args = self._self_signature.bind(instance, *args, **kwargs)

        # building argtuple instance
        args = self._self_argtuple(**bound_args.arguments)

        # converting result...
        try:
            restuple = tuple(r for r in result)  # TODO : name this from annotations
        except TypeError as te:  # if not iterable
            restuple = (result,)

        #  we don't need to apply default here, it has already been done during the call
        self._self_callframe = self._self_callframe.append([args + restuple], ignore_index=True)
        return result

    @property
    def __frame__(self):
        """ Accessing _self_callframe via property to prevent mutation """
        return self._self_callframe


# TODO : add a pure option declaration (to grab result from trace when possible)
def framed_function_wrapper(wrapper):
    @functools.wraps(wrapper)
    def _wrapper(wrapped):

        # otherwise a decorator grabbing argument calls and returning
        signature = inspect.signature(wrapped)
        # Note : no accumulation of calls here (see trace for that)

        # building namedtuple from signature
        with_hints = dict()
        with_defaults = dict()
        for p, h in signature.parameters.items():
            if h.kind is inspect.Parameter.VAR_KEYWORD:
                with_defaults[p] = dict() if h.default is inspect._empty else h.default
            elif h.kind is inspect.Parameter.VAR_POSITIONAL:
                with_defaults[p] = tuple() if h.default is inspect._empty else h.default

            with_hints[p] = typing.Any if h.annotation is inspect._empty else h.annotation
            if h.default and h.default is not inspect._empty:
                with_defaults[p] = h.default

        # Note: a namedtuple is the proper data structure to represent frozen bound args.
        # Immutable, iterable on values, indexed via keys.
        argtuple = FramableTuple(f"{wrapped.__name__}_arguments_tuple", field_names= signature.parameters.keys(),
                                 types=with_hints,
                                 defaults=with_defaults)

        return FramableFunctionWrapper(wrapped, wrapper, signature, argtuple)
    return _wrapper


# TODO : add a pure option declaration (to optimize and grab result from trace on call when possible)
def framed():

    @framed_function_wrapper
    def framed_decorator(wrapped, instance, args, kwargs):

        # TODO : BIND HERE INSTEAD ! for clarity...
        return instance, args, kwargs, wrapped(*args, **kwargs)

    return framed_decorator


if __name__ == '__main__':

    @framed()
    def myfun(a = 39):
        return a + 3

    assert myfun(48) == 51

    print (myfun.__frame__)
    assert len(myfun.__frame__) == 1
    # assert myfun.__frame__[48] == 51  # TODO : access trace result via mapping syntax (getitem)

    # tracing a method (careful with instances and call time !)

    class FrameTest:
        @framed()
        def myfun(self, a = 39):
            return a + 2

    tt = FrameTest()
    assert tt.myfun(48) == 50

    print(tt.myfun.__frame__)
    assert len(tt.myfun.__frame__) == 1
    # assert tt.myfun.__frame__[{'a': 48}] == 50

