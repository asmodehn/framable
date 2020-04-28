from collections import namedtuple

from typing import Union, Iterable, Optional, Any, Type, Mapping

if not __package__:
    __package__ = "framable.core"
from .framablemeta import FramableMeta
from .framablebase import FramableBase

# Here we need to reimplement the logic for __frame__ and __series__, to avoid metaclass conflict.
# However we will need to patch objects directly, since we cannot rely on inheritance for NamedTuple,
# due to an odd class design in typing.NamedTuple (twisting inheritance as dynamic type factory...)


def FramableTuple(typename, field_names: Union[str, Iterable[str]],
                  types: Optional[Mapping[str,Type]],
                  defaults: Optional[Mapping[str,Any]],
                  module: Optional[str] = "__main__") -> Type[FramableMeta]:
    """
    This is a factory to create NamedTuple FramableTypes.

    WARNING : We should not rely on the class structure of typing.NamedTuple,
              it is still changing between different versions of python...

    However we keep an interface close to collection.namedtuple()
    to be able to quickly adjust to various python versions.

    :param typename:
    :param fields:
    :return:
    """
    ntt = namedtuple(typename, field_names=field_names, defaults=defaults, module=module)
    ntt.__annotations__ = ntt.__new__.__annotations__ = types

    # defining a child class to extend the nametuple type created
    framable = FramableMeta(
        typename,
        (ntt, FramableBase),
        {
            # nothing added here, let inheritance do its thing.
            # TODO : wrap __new__ to take late defaults into account... => use it into framablefunctionwrapper
            # '__new__': lambda cls, **kwa:
            # TODO : python 3.8 careful with multiple inheritance...
        },
    )

    return framable


if __name__ == "__main__":

    InlineTuple = FramableTuple("InlineTuple", field_names=["att1", "att2"],
                                types={"att1": int, "att2": int},
                                defaults={"att1": 0, "att2": 0})

    inlta = InlineTuple(att1=42, att2=51)
    inltb = InlineTuple(att1=47, att2=53)

    print(inlta.__series__)
    print(inltb.__series__)

    print(InlineTuple.__frame__)
