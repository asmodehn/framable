import unittest
import pandas as pd
from pandas.core import dtypes

from framable.framablemeta import FramableMeta


class TestFramableMeta(unittest.TestCase):

    def test_framableclass(self):

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

        with self.assertRaises(AttributeError):
            myobj.__frame__
        # expected AttributeError, as the instance doesnt have a frame representation provided by the class

        # appending happens as expected
        myobj2 = MyKls(47, 53)

        # checking the second record is the instance we just created
        assert (MyKls.__frame__.iloc[1] == pd.Series(vars(myobj2))).all()

        # Test with another class in an attempt to detect conflicts...
        class MyOtherKls(metaclass=FramableMeta):

            att1: str

            def __init__(self, att1, att2):
                self.att1 = att1
                self.att2 = att2  # unspecified in class, added on init

        assert isinstance(MyOtherKls.__frame__, pd.DataFrame)
        assert MyOtherKls.__frame__.empty

        myotherobj = MyOtherKls("alice", 51)

        assert len(MyOtherKls.__frame__) == 1
        assert (MyOtherKls.__frame__.columns == ['att1', 'att2']).all()
        # proper panda way to check datatype...
        assert pd.api.types.is_string_dtype(MyOtherKls.__frame__.dtypes['att1'])
        assert pd.api.types.is_int64_dtype(MyOtherKls.__frame__.dtypes['att2'])
        # checking the first record is the instance we just created
        assert (MyOtherKls.__frame__.iloc[0] == pd.Series(vars(myotherobj))).all()


if __name__ == '__main__':
    unittest.main()
