from __future__ import  annotations
from typing import ClassVar

import pandas as pd
from .framablemeta import FramableMeta


class FramableBase(metaclass=FramableMeta):
    """
    A base class to provide __series__ properties on its instances

    Note : because FramableMeta is used as a metaclass,
    all classes with a __series__ property on their instances also have a __frame__ property on the class itself

    Note : This is the "base" of our constructive type system.
    A type constructor has traditionally two behaviors, merged into one (to be implemented as a function):

     - on send/write to : encaspulate the data into an element of the type.
     - on recv/read from : return an element of the type.

    When interacting with a type, we can separate the two behaviors to extend its power:

     - on send/write to : verify the "data" sent belongs to the type (via type-aware equality)
       For advanced usage, this can be leveraged to convert between types (the usual python behavior !)

     - on recv/read from : pick an element of the type, here this is a default value, to match python call signature.
       For advanced usage, this can be leverage to probabilistically draw an element (hypothesis search strategy !)

    """

    __initial__: ClassVar[FramableBase]

    @property
    def __series__(self):
        if isinstance(self, dict):
            return pd.Series(self)
        elif isinstance(self, tuple) and hasattr(self, "_asdict"):
            return pd.Series(self._asdict())
        else:
            return pd.Series(vars(self))


if __name__ == "__main__":

    class MyKls(FramableBase):
        att: int

        def __init__(self, att, other):
            self.att = att
            self.other = other

    print(MyKls.__frame__)

    fobj = MyKls(42, 51)

    print(MyKls.__frame__)

    print(fobj.__series__)

    fobj = MyKls(47, 53)

    print(MyKls.__frame__)

    print(fobj.__series__)
