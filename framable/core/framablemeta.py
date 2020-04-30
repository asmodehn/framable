import collections
import sys

import pandas as pd


# TODO : record the object address or full name, for reference in "foreign keys" later...

# _prohibited = ['__new__',]


class FramableMeta(type):
    def __new__(mcls, name, bases, ns):

        # If called dynamically, some mandatory attributes might be missing:

        # __module__ (source inspired from collections.namedtuple)

        # For pickling to work, the __module__ variable needs to be set to the frame
        # where the named tuple is created.  Bypass this step in environments where
        # sys._getframe is not defined (Jython for example) or sys._getframe is not
        # defined for arguments greater than 0 (IronPython), or where the user has
        # specified a particular module.
        if ns.get('__module__') is None:
            try:
                module = sys._getframe(1).f_globals.get('__name__', '__main__')
            except (AttributeError, ValueError):
                pass
            ns.setdefault('__module__', module)

        #TODO: __qualname__

        # We have to build a subclass of the namedtuple
        # inspired from typing.NamedTupleMeta : https://github.com/python/cpython/blob/master/Lib/typing.py#L1731
        types = ns.get('__annotations__', {})
        default_names = []
        for field_name in types:
            if field_name in ns:
                default_names.append(field_name)
            elif hasattr(types[field_name], '__initial__'):  # assigning the initial element as default
                ns[field_name] = types[field_name].__initial__
                default_names.append(field_name)
            else:
                raise TypeError(f"Non-framable type {types[field_name]} of field {field_name} "
                                f"needs to specify a default value")

        # Note: a namedtuple is the proper data structure to represent frozen bound args.
        # Immutable, iterable on values, indexed via keys.
        # TODO : check nptyping...
        # Here we leverage our core framable implementation...
        Impl = collections.namedtuple(typename=f"{name}Impl", field_names=types.keys(),
                                      defaults=[ns[n] for n in default_names],
                                      module=ns['__module__'])
        Impl.__annotations__ = types

        return super(FramableMeta, mcls).__new__(mcls, name, bases + (Impl,), ns)

    def __init__(cls, name, bases, ns):
        # leveraging inheritance for implementation, for simplicity reasons
        super(FramableMeta, cls).__init__(name, bases, ns)

        # overriding __init__ for additional behavior (__new__ is reserved for namedtuple)
        def init(s, *args, **kwargs):
            super(cls, s).__init__()
            for f in s._fields:
                # replacing instance values with values from tuple (immutable) for consistency
                setattr(s, f, getattr(super(cls, s), f))

        cls.__init__ = init

        cls._classframe = pd.DataFrame()  # empty dataframe on class creation

        cls.__initial__ = cls()  # creating initial object on class creation

        # setting up property to represent instance as a series
        def series(self):
            if isinstance(self, dict):
                return pd.Series(self)
            elif isinstance(self, tuple) and hasattr(self, "_asdict"):
                return pd.Series(self._asdict())
            else:
                return pd.Series(vars(self))
        cls.__series__ = property(series)

    def __call__(cls, *args, **kwargs):
        if not args and not kwargs:
            if hasattr(cls, '__initial__'):
                return cls.__initial__  # return the initial object inside the type
            else:  # the first time for initial instance creation
                try:
                    return super(FramableMeta, cls).__call__(*args, **kwargs)
                except TypeError as e:
                    raise  # missing required position arguments -> TODO : encapsulate in lib exception

        inst = super(FramableMeta, cls).__call__(*args, **kwargs)

        # get instance and store it in classframe
        if isinstance(inst, dict):
            cls._classframe = cls._classframe.append([inst],)
        elif isinstance(inst, tuple) and hasattr(inst, "_asdict"):
            cls._classframe = cls._classframe.append([inst._asdict()],)
        else:
            cls._classframe = cls._classframe.append([vars(inst)],)
        # column and dtypes will be inferred...
        cls._classframe.convert_dtypes()

        return inst

    @property
    def __frame__(cls):
        """ Accessing classframe via property to prevent mutation """
        return cls._classframe

    # TODO : add for sum of types (and concatenation of namedtuple implementation)


if __name__ == "__main__":

    class MyKls(metaclass=FramableMeta):
        att1: int = 0
        att2: int = 42

    myobj = MyKls(att1=42, att2=51)

    print(MyKls.__frame__)

    try:
        print(myobj.__frame__)
    except AttributeError as te:
        print(
            "expected AttributeError, as the instance doesnt have a frame representation provided by the metaclass"
        )

    print(myobj.__series__)

    myobj2 = MyKls(att1=47, att2=53)

    print(MyKls.__frame__)

    print(myobj2.__series__)
