from __future__ import annotations

import ast
import functools
import inspect

import typing
import wrapt
import pandas as pd

from framable import FramableMeta


def signature_tuple(wrapped: typing.Callable):

    # See https://www.python.org/dev/peps/pep-0362/#id8
    signature = inspect.signature(wrapped)

    # building arg namedtuple from signature
    with_hints = dict()
    with_defaults = dict()
    for p, h in signature.parameters.items():
        with_hints[p] = typing.Any if h.annotation is inspect._empty else h.annotation
        if h.default and h.default is not inspect._empty:
            with_defaults[p] = h.default
        elif h.kind is inspect.Parameter.VAR_KEYWORD:
            with_defaults[p] = dict() if h.default is inspect._empty else h.default
        elif h.kind is inspect.Parameter.VAR_POSITIONAL:
            with_defaults[p] = tuple() if h.default is inspect._empty else h.default
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
    else:  # TODO : some special optimisation when we can iterate on the result -> namedtuple -> columns in frame ?
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
        # Note : this is called at every mention of the decorated function, in order to attempt grabbing the instance.
        # unexpected => TODO minimize code here
        super(FramableBoundFunctionWrapper, self).__init__(descriptor, instance,
                                                         _self_wrapper, _self_enabled,
                                                         _self_binding, _self_parent)

        self._self_descriptor = descriptor

        self._self_signature = self._self_parent._self_signature
        self._self_argtuple = self._self_parent._self_argtuple
        self._self_resulttuple = self._self_parent._self_resulttuple

        # using the properly initialized frames, storing the instance in columns somehow...
        self._self_callframe = self._self_parent._self_callframe
        self._self_returnframe = self._self_parent._self_returnframe
        # Note this is called again whenever needed and bounded object is reconstructed

        if self._self_instance:
            # This happens on bound functions only
            # It is the only case were we need partial binding of the signature
            # static method doesnt and classmethod "hides" the class argument from the signature
            sig, argt, rest = _self_parent._self_sigbind(self._self_instance)
            self._self_signature = sig
            self._self_argtuple = argt
            self._self_resulttuple = rest

    def __call__(self, *args, **kwargs):

        if self._self_instance:
            # we bind only if we have an instance retrieved by wrapt (bound function case)
            bound_args = self._self_signature.bind(self._self_instance, *args, **kwargs)
        else:
            bound_args = self._self_signature.bind(*args, **kwargs)

        # where is instance grabbed from ? cant we retrieve it before calling ?
        result = super(FramableBoundFunctionWrapper, self).__call__(*args, **kwargs)

        # note: Here instance can be the class (for class methods) or None (for static methods)

        # building argtuple instance
        # Note : instance of the method call must be in argtuple !
        args = self._self_argtuple(**bound_args.arguments)

        # converting result...
        restuple = self._self_resulttuple(result)

        # bound function gets recreated everytime we want to access it. we need to store the callframe in the parent.
        self._self_parent._self_callframe = self._self_parent._self_callframe.append([args._asdict()], ignore_index=True)
        self._self_parent._self_returnframe = self._self_parent._self_returnframe.append([restuple._asdict()], ignore_index=True)

        return result

    @property
    def __frame__(self):
        """ Accessing _self_callframe via property to prevent mutation """
        if self._self_instance:  # bound usecase (also in frame)
            firstparam = next(iter(self._self_signature.parameters))
            # taking only subframe for current instance
            boundframe = self._self_callframe.loc[self._self_callframe[firstparam] == self._self_instance].drop([firstparam], axis=1)
        else:
            # if called on the class (and not the instance)
            boundframe = self._self_callframe
        return boundframe.join(self._self_returnframe)


class FramableFunctionWrapper(wrapt.FunctionWrapper):

    __bound_function_wrapper__ = FramableBoundFunctionWrapper

    def __init__(self, wrapped, wrapper):
        super(FramableFunctionWrapper, self).__init__(wrapped, wrapper)
        sig, argt, rest, bind = signature_tuple(wrapped)
        self._self_signature = sig
        self._self_argtuple = argt
        self._self_resulttuple = rest
        self._self_sigbind = bind

        self._self_reset = True  # signal to the potential boundfunctionwrapper init call
        # that it is time to reset its data, that might be stored elsewhere...

        self._self_callframe = pd.DataFrame(columns=argt._fields)  # empty dataframe before we have any data sample...
        self._self_returnframe = pd.DataFrame(columns=rest._fields)  # empty dataframe before we have any data sample...

    def __call__(self, *args, **kwargs):

        # here we bind on the signature
        # mandatory first arguments - self, class - are not part of the signature see PEP 362)
        bound_args = self._self_signature.bind(*args, **kwargs)

        result = super(FramableFunctionWrapper, self).__call__(*args, **kwargs)

        # building argtuple instance
        args = self._self_argtuple(**bound_args.arguments)

        # converting result... careful this needs to match how the signature interpreted result as tuple...
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

        return wrapped(*args, **kwargs)

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

    # Note the __frame__ attrribute on class return calls for all instances
    print(FrameTest.myfun.__frame__)

