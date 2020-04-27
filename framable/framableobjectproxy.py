import wrapt
import pandas as pd
from framable.framablebase import FramableBase


class FramableObjectProxy(wrapt.ObjectProxy):
    """ Extending wrapt.ObjectProxy with a __series__ property
    This provides the same functionality as FramableBase, however without using inheritance

    The main advantage being that we can build a proxy around an object defined elsewhere.
    """

    def __new__(cls, wrapped):
        wrapper = super(FramableObjectProxy, cls).__new__(cls, wrapped)
        return wrapper

    @property
    def __series__(self):
        return pd.Series(vars(self))


if __name__ == '__main__':

    class MyKls:
        att: int

        def __init__(self, att, other):
            self.att = att
            self.other = other

    fobj = MyKls(42, 51)
    fproxy = FramableObjectProxy(fobj)

    print(fproxy.__series__)

    fobj = MyKls(47, 53)
    fproxy = FramableObjectProxy(fobj)

    print(fproxy.__series__)
