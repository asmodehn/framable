import wrapt
import pandas as pd


class FramableClassProxy(wrapt.ObjectProxy):
    """ Extending wrapt.ObjectProxy with a __frame__. Meaningful for classes.
    This provide the same functionality as FramableMeta, however using a proxy pattern (instead of a metaclass).

    The main advantage being that we can build a proxy around a class defined elsewhere.
    """

    def __new__(cls, wrapped):
        wrapper = super(FramableClassProxy, cls).__new__(cls, wrapped)
        return wrapper

    def __init__(self, wrapped):
        super(FramableClassProxy, self).__init__(wrapped)
        self._classframe = pd.DataFrame()  # empty dataframe on class initialization

    def __call__(self, *args, **kwargs):
        inst = self.__wrapped__(*args, **kwargs)

        # get instance and store it in classframe
        self._classframe = self._classframe.append([vars(inst)], )
        # column and dtypes will be inferred...
        self._classframe.convert_dtypes()

        return inst

    @property
    def __frame__(self):
        """ Accessing classframe via property to prevent mutation """
        return self._classframe


if __name__ == '__main__':

    class MyKls:
        att: int

        def __init__(self, att, other):
            self.att = att
            self.other = other

    KlassProxy = FramableClassProxy(MyKls)

    myobj = KlassProxy(42, 51)

    print(KlassProxy.__frame__)

    try:
        print(myobj.__frame__)
    except AttributeError as ae:
        print("expected AttributeError, as the instance doesnt have a frame representation provided by the class proxy")

    try:
        print(MyKls.__frame__)
    except AttributeError as ae:
        print("expected AttributeError, as the class doesnt have a frame representation provided by the proxy")

    myobj2 = KlassProxy(47, 53)

    print(KlassProxy.__frame__)
