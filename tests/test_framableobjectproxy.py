import unittest
import pandas as pd
from pandas.core import dtypes

from framable.framableobjectproxy import FramableObjectProxy


class TestFramableObjectProxy(unittest.TestCase):

    def test_framableobjectproxy(self):

        class MyKls:

            att1: int

            def __init__(self, att1, att2):
                self.att1 = att1
                self.att2 = att2  # unspecified in class, added on init

        myobj = MyKls(42, 51)

        myobjproxy = FramableObjectProxy(myobj)
        assert (myobjproxy.__series__ == pd.Series(vars(myobjproxy))).all()

        # the class does NOT have a frame (it wasn't wrapped in a proxy, it would be too unexpected)
        with self.assertRaises(AttributeError):
            MyKls.__frame__

        # but the obj instance doesnt have the attribute
        with self.assertRaises(AttributeError):
            myobjproxy.__frame__
        # expected AttributeError, as the instance doesnt have a frame representation provided by the class

        # appending happens as expected
        myobj2 = MyKls(47, 53)
        myobj2proxy = FramableObjectProxy(myobj2)

        # checking the second record is the instance we just created
        assert (myobj2proxy.__series__ == pd.Series(vars(myobj2proxy))).all()


if __name__ == '__main__':
    unittest.main()
