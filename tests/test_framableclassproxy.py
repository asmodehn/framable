import unittest
import pandas as pd
from pandas.core import dtypes

from framable.framableclassproxy import FramableClassProxy


class TestFramableClassProxy(unittest.TestCase):

    def test_framableclass(self):

        class MyKls:

            att1: int

            def __init__(self, att1, att2):
                self.att1 = att1
                self.att2 = att2  # unspecified in class, added on init

        MyKlsProxy = FramableClassProxy(MyKls)

        assert isinstance(MyKlsProxy.__frame__, pd.DataFrame)
        assert MyKlsProxy.__frame__.empty
        assert len(MyKlsProxy.__frame__) == 0

        myobj = MyKlsProxy(42, 51)

        assert len(MyKlsProxy.__frame__) == 1
        assert (MyKlsProxy.__frame__.columns == ['att1', 'att2']).all()
        # proper panda way to check datatype...
        assert pd.api.types.is_int64_dtype(MyKlsProxy.__frame__.dtypes['att1'])
        assert pd.api.types.is_int64_dtype(MyKlsProxy.__frame__.dtypes['att2'])
        # checking the first record is the instance we just created
        assert (MyKlsProxy.__frame__.iloc[0] == pd.Series(vars(myobj))).all()

        with self.assertRaises(AttributeError):
            myobj.__frame__
        # expected AttributeError, as the instance doesnt have a frame representation provided by the class

        # appending happens as expected
        myobj2 = MyKlsProxy(47, 53)

        # checking the second record is the instance we just created
        assert (MyKlsProxy.__frame__.iloc[1] == pd.Series(vars(myobj2))).all()

        # Test with another class in an attempt to detect conflicts...
        class MyOtherKls:

            att1: str

            def __init__(self, att1, att2):
                self.att1 = att1
                self.att2 = att2  # unspecified in class, added on init

        MyOtherKlsProxy = FramableClassProxy(MyOtherKls)

        assert isinstance(MyOtherKlsProxy.__frame__, pd.DataFrame)
        assert MyOtherKlsProxy.__frame__.empty

        myotherobj = MyOtherKlsProxy("alice", 51)

        assert len(MyOtherKlsProxy.__frame__) == 1
        assert (MyOtherKlsProxy.__frame__.columns == ['att1', 'att2']).all()
        # proper panda way to check datatype...
        assert pd.api.types.is_string_dtype(MyOtherKlsProxy.__frame__.dtypes['att1'])
        assert pd.api.types.is_int64_dtype(MyOtherKlsProxy.__frame__.dtypes['att2'])
        # checking the first record is the instance we just created
        assert (MyOtherKlsProxy.__frame__.iloc[0] == pd.Series(vars(myotherobj))).all()


if __name__ == '__main__':
    unittest.main()
