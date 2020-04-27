from typing import NamedTuple, NamedTupleMeta

import pandas as pd
import typing

from core.framablemeta import FramableMeta
from core.framablebase import FramableBase

# Here we need to reimplement the logic for __frame__ and __series__, to avoid metaclass conflict.
# However we will need to patch objects directly, since we cannot rely on inheritance for NamedTuple,
# due to an odd class design in typing.NamedTuple (twisting inheritance as dynamic type factory...)


def FramableTuple(typename, fields=None):
    """
    This is a factory to create NamedTuple types,
    and patch it to add __frame__ to the class and __series__ to the instances

    WARNING : we should not rely on the class structure of NamedTuple.
              It is quite hacky, using a class as a dynamic class factory... forbidding potential inheritance.

    :param typename:
    :param fields:
    :return:
    """
    ntt = NamedTuple(typename=typename, fields=fields)

    # defining a child class to extend the nametuple type created
    framable = FramableMeta(typename, (ntt, FramableBase), {
        # nothing added here, let inheritance so its thing.
    })

    return framable


if __name__ == '__main__':

    InlineTuple = FramableTuple("InlineTuple", [("att1", int), ("att2", int)])

    inlta = InlineTuple(att1=42, att2=51)
    inltb = InlineTuple(att1=47, att2=53)

    print(inlta.__series__)
    print(inltb.__series__)

    print(InlineTuple.__frame__)





