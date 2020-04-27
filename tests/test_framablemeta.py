import unittest
import pandas as pd
from pandas.core import dtypes

from framable.framablemeta import FramableMeta


class TestFramableMeta(unittest.TestCase):

    def test_simpleclass(self):

        class MyKls(metaclass=FramableMeta):

            att1: int

            def __init__(self, att1, att2):
                self.att1 = att1
                self.att2 = att2  # unspecified in class, added on init

        assert isinstance(MyKls.__frame__, pd.DataFrame)
        assert MyKls.__frame__.empty

        # assert len(MyKls.__frame__) == 0

        myobj = MyKls(42, 51)

        assert len(MyKls.__frame__) == 1
        assert (MyKls.__frame__.columns == ['att1', 'att2']).all()
        # proper panda way to check datatype...
        assert pd.api.types.is_int64_dtype(MyKls.__frame__.dtypes['att1'])
        assert pd.api.types.is_int64_dtype(MyKls.__frame__.dtypes['att2'])
        # checking the first record is the instance we just created
        assert (MyKls.__frame__.iloc[0] == pd.Series(vars(myobj))).all()

        # TODO : fix this, it should break the test...
        # with self.assertRaises(TypeError):
        #     myobj.__frame__
        # # expected type error, as the instance doesnt have a frame representation provided by the class

        # appending happens as expected
        myobj2 = MyKls(47, 53)

        # checking the second record is the instance we just created
        assert (MyKls.__frame__.iloc[1] == pd.Series(vars(myobj2))).all()


if __name__ == '__main__':
    unittest.main()
