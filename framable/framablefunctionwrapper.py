from __future__ import annotations

import ast
import functools
import inspect

import typing
import wrapt
import pandas as pd

from framable import FramableMeta


def signature_tuple(wrapped: typing.Callable):

    signature = inspect.signature(wrapped)

    # building arg namedtuple from signature
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
        else:
            with_defaults[p] = None  # default value for any type in python...

    argtuple = FramableMeta(f"{wrapped.__name__}_arguments_tuple", bases=(), ns={
        # **signature.parameters,  # not needed ??
        **with_defaults,
        '__annotations__': with_hints
    })

    # TODO : maybe default to id() to return initial object seems sensible ??
    if signature.return_annotation is inspect._empty:
        result_default = None  # default return value in python
        result_hint = typing.Any  # default return type in python
    else:
        result_hint = type(signature.return_annotation)
        result_default = result_hint.__initial__ if hasattr(result_hint, '__initial__') else None

    result_tuple = FramableMeta(f"{wrapped.__name__}_result_tuple", bases=(), ns={
        'result': result_default,  # default return value in python
        '__annotations__': {'result': result_hint}
        # note 'return' is a special key : https://docs.python.org/3/library/inspect.html#types-and-members
        # BUT nametuple keys cannot be keywords...
    })

    def bind(instance):
        """ refining signature of the method after binding for proper typing."""
        nonlocal argtuple, result_default, result_hint

        # specializing first bound argument type annotation
        argtuple.__annotations__[next(iter(signature.parameters))] = type(instance)
        # note default doesn't change
        # we need one for framable semantics, and we want stuff to break if somehow python doesnt pass self...

        # make bound methods return self-type instances by default, if not specified otherwise in type hints
        if signature.return_annotation is inspect._empty:
            result_hint = type(instance)  # default return type in python

        # make result default to instance value (providing chainable call interface by default)
        if isinstance(instance, result_hint):
            result_default = instance

        #refine the result tuple
        result_tuple = FramableMeta(f"{wrapped.__name__}_result_tuple", bases=(), ns={
            'result': result_default,
            '__annotations__': {'result': result_hint}
        })
        # otherwise keep it the same (same semantics as unbound)

        # signature for python doesnt change (?)

        return signature, argtuple, result_tuple

    return signature, argtuple, result_tuple, bind


class FramableBoundFunctionWrapper(wrapt.BoundFunctionWrapper):

    def __init__(self, descriptor, instance,
                        _self_wrapper, _self_enabled,
                        _self_binding, _self_parent):
        super(FramableBoundFunctionWrapper, self).__init__(descriptor, instance,
                                                         _self_wrapper, _self_enabled,
                                                         _self_binding, _self_parent)
        # Note this is called on method call, not on decoration, to be able to known about python late binding
        sig, argt, rest = _self_parent._self_sigbind(instance)
        self._self_signature = sig
        self._self_argtuple = argt
        self._self_resulttuple = rest

        # because bound function is not mutable we need to store the callframe on the instance instead
        if not hasattr(instance, "_method_callframes"):
            setattr(instance, "_method_callframes", dict())
        instance._method_callframes.setdefault(descriptor.__name__, pd.DataFrame(columns=argt._fields))
        if not hasattr(instance, "_method_returnframes"):
            setattr(instance, "_method_returnframes", dict())
        instance._method_returnframes.setdefault(descriptor.__name__, pd.DataFrame(columns=rest._fields))
        # and indirectly refer to it here
        self._self_callframe = instance._method_callframes[descriptor.__name__]
        self._self_returnframe = instance._method_returnframes[descriptor.__name__]
        self._self_descriptor = descriptor

    def __call__(self, *args, **kwargs):
        instance, args, kwargs, result = super(FramableBoundFunctionWrapper, self).__call__(*args, **kwargs)

        # we bind afterwards to retrieve the instance from wrapt
        bound_args = self._self_signature.bind(instance, *args, **kwargs)

        # building argtuple instance
        args = self._self_argtuple(**bound_args.arguments)

        # converting result...
        try:
            restuple = self._self_resulttuple(*result)
        except TypeError as te:  # if not iterable
            restuple = self._self_resulttuple(result)

        #  we dont need to apply default here, it has already been done during the call
        instance._method_callframes[self._self_descriptor.__name__] = self._self_callframe.append([args._asdict()], ignore_index=True)
        instance._method_returnframes[self._self_descriptor.__name__] = self._self_returnframe.append([restuple._asdict()], ignore_index=True)
        # Note how we need to store the new dataframe in the methodframes mapping, or modification on method object will not work
        return result

    @property
    def __frame__(self):
        """ Accessing _self_callframe via property to prevent mutation """
        return self._self_callframe.join(self._self_returnframe)


class FramableFunctionWrapper(wrapt.FunctionWrapper):

    __bound_function_wrapper__ = FramableBoundFunctionWrapper

    def __init__(self, wrapped, wrapper):
        super(FramableFunctionWrapper, self).__init__(wrapped, wrapper)
        sig, argt, rest, bind = signature_tuple(wrapped)
        self._self_signature = sig
        self._self_argtuple = argt
        self._self_resulttuple = rest
        self._self_sigbind = bind

        self._self_callframe = pd.DataFrame(columns=argt._fields)  # empty dataframe before we have any data sample...
        self._self_returnframe = pd.DataFrame(columns=rest._fields)  # empty dataframe before we have any data sample...

    def __call__(self, *args, **kwargs):
        instance, args, kwargs, result = super(FramableFunctionWrapper, self).__call__(*args, **kwargs)
        # we bind afterwards to retrieve the instance from wrapt
        if instance is None:   # tentative : TODO : thorough testing
            bound_args = self._self_signature.bind(*args, **kwargs)
        else:
            bound_args = self._self_signature.bind(instance, *args, **kwargs) # TODO : which case is this one, if not bound ?

        # building argtuple instance
        args = self._self_argtuple(**bound_args.arguments)

        # converting result...
        try:
            restuple =  self._self_resulttuple(*result)
        except TypeError as te:  # if not iterable
            restuple =  self._self_resulttuple(result)

        #  we don't need to apply default here, it has already been done during the call
        self._self_callframe = self._self_callframe.append([args._asdict()], ignore_index=True)
        self._self_returnframe = self._self_returnframe.append([restuple._asdict()], ignore_index=True)
        return result

    @property
    def __frame__(self):
        """ Accessing _self_callframe and _self_resultframe via property to prevent mutation """
        return self._self_callframe.join(self._self_returnframe)


# TODO : add a pure option declaration (to grab result from trace when possible)
def framed_function_wrapper(wrapper):
    @functools.wraps(wrapper)
    def _wrapper(wrapped):
        return FramableFunctionWrapper(wrapped, wrapper)
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
    def myfun(a: int = 39) -> int:
        return a + 3

    assert myfun(48) == 51

    print (myfun.__frame__)
    assert len(myfun.__frame__) == 1
    # assert myfun.__frame__[48] == 51  # TODO : access trace result via mapping syntax (getitem)

    # tracing a method (careful with instances and call time !)

    class FrameTest:
        @framed()
        def myfun(self: FrameTest, a: int = 39):
            return a + 2

    tt = FrameTest()
    assert tt.myfun(48) == 50

    print(tt.myfun.__frame__)
    assert len(tt.myfun.__frame__) == 1
    # assert tt.myfun.__frame__[{'a': 48}] == 50

