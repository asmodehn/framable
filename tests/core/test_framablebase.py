import unittest
import pandas as pd
from pandas.core import dtypes

from framable.framablebase import FramableBase


class TestFramableBase(unittest.TestCase):

    def test_framableclass(self):

        class MyKls(FramableBase):

            att1: int

            def __init__(self, att1, att2):
                self.att1 = att1
                self.att2 = att2  # unspecified in class, added on init

        myobj = MyKls(42, 51)

        assert (myobj.__series__ == pd.Series(vars(myobj))).all()

        # the class has a frame (from the metaclass)
        assert (MyKls.__frame__ == pd.DataFrame([vars(myobj)])).all().all()
        # but the obj instance doesnt have the attribute
        with self.assertRaises(AttributeError):
            myobj.__frame__
        # expected AttributeError, as the instance doesnt have a frame representation provided by the class

        # appending happens as expected
        myobj2 = MyKls(47, 53)

        # checking the second record is the instance we just created
        assert (myobj2.__series__ == pd.Series(vars(myobj2))).all()


if __name__ == '__main__':
    unittest.main()
