import pandas as pd


class FramableMeta(type):

    def __new__(mcls, name, bases, ns):

        cls = super(FramableMeta, mcls).__new__(mcls, name, bases, ns)
        return cls

    def __init__(cls, name, bases, ns):

        super(FramableMeta, cls).__init__(name, bases, ns)
        cls._classframe = pd.DataFrame()  # empty dataframe on class creation

    def __call__(cls, *args, **kwargs):

        inst = super(FramableMeta, cls).__call__(*args, **kwargs)

        # get instance and store it in classframe
        if isinstance(inst, dict):
            cls._classframe = cls._classframe.append([inst], )
        elif isinstance(inst, tuple) and hasattr(inst, '_asdict'):
            cls._classframe = cls._classframe.append([inst._asdict()], )
        else:
            cls._classframe = cls._classframe.append([vars(inst)], )
        # column and dtypes will be inferred...
        cls._classframe.convert_dtypes()

        return inst

    @property
    def __frame__(cls):
        """ Accessing classframe via property to prevent mutation """
        return cls._classframe


if __name__ == '__main__':

    class MyKls(metaclass=FramableMeta):

        att1: int

        def __init__(self, att1, att2):
            self.att1 = att1
            self.att2 = att2  # unspecified in class, added on init

    myobj = MyKls(42, 51)

    print(MyKls.__frame__)

    try:
        print(myobj.__frame__)
    except AttributeError as te:
        print("expected AttributeError, as the instance doesnt have a frame representation provided by the metaclass")

    myobj2 = MyKls(47, 53)

    print(MyKls.__frame__)


