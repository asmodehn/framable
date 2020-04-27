import pandas as pd
from core.framablemeta import FramableMeta


class FramableBase(metaclass=FramableMeta):
    """
    A base class to provide __series__ properties on its instances

    Note : because FramableMeta is used as a metaclass,
    all classes with a __series__ property on their instances also have a __frame__ property on the class itself
    """

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
