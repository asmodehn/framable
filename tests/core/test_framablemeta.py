import unittest
import pandas as pd
from pandas.core import dtypes

from framable.core.framablemeta import FramableMeta


class TestFramableMeta(unittest.TestCase):
    def test_framableclass(self):
        class MyKls(metaclass=FramableMeta):
            att1: int = 0
            att2: int = 42

        assert isinstance(MyKls.__frame__, pd.DataFrame)
        assert MyKls.__frame__.empty
        assert len(MyKls.__frame__) == 0

        myobj = MyKls(att1=42, att2=51)

        assert myobj.att1 == 42
        assert myobj.att2 == 51

        # the class has a frame (from the metaclass)
        assert (MyKls.__frame__ == pd.DataFrame([vars(myobj)])).all().all()
        # or checking by column
        assert (MyKls.__frame__.columns == ["att1", "att2"]).all()
        # proper panda way to check datatype...
        assert pd.api.types.is_int64_dtype(MyKls.__frame__.dtypes["att1"])
        assert pd.api.types.is_int64_dtype(MyKls.__frame__.dtypes["att2"])
        # checking the first record is the instance we just created
        assert (MyKls.__frame__.iloc[0] == pd.Series(vars(myobj))).all()

        # but the obj instance doesnt have the attribute
        with self.assertRaises(AttributeError):
            myobj.__frame__
        # expected AttributeError, as the instance doesnt have a frame representation provided by the class

        # appending happens as expected
        myobj2 = MyKls(att1=47, att2=53)

        assert myobj2.att1 == 47
        assert myobj2.att2 == 53

        # checking the second record is the instance we just created
        assert (MyKls.__frame__.iloc[1] == pd.Series(vars(myobj2))).all()

        # Which is reflected in its series
        assert (myobj2.__series__ == pd.Series(vars(myobj2))).all()

        # Test with another class in an attempt to detect conflicts...
        class MyOtherKls(metaclass=FramableMeta):

            att1: str = "dflt"
            att2: int = 0

        assert isinstance(MyOtherKls.__frame__, pd.DataFrame)
        assert MyOtherKls.__frame__.empty

        myotherobj = MyOtherKls(att1="alice", att2=51)

        assert (MyOtherKls.__frame__ == pd.DataFrame([vars(myotherobj)])).all().all()
        assert (MyOtherKls.__frame__.columns == ["att1", "att2"]).all()
        # proper panda way to check datatype...
        assert pd.api.types.is_string_dtype(MyOtherKls.__frame__.dtypes["att1"])
        assert pd.api.types.is_int64_dtype(MyOtherKls.__frame__.dtypes["att2"])
        # checking the first record is the instance we just created
        assert (MyOtherKls.__frame__.iloc[0] == pd.Series(vars(myotherobj))).all()

    def test_framablecall(self):

        MyTpl = FramableMeta("MyTpl", (), {
            "att1": 0,
            "att2": 42,
            "__annotations__":{
                "att1": int, "att2": int
            }})

        myobj = MyTpl(att1=42, att2=51)

        assert (myobj.__series__ == pd.Series(myobj._asdict())).all()

        # the class has a frame (from the metaclass)
        assert (MyTpl.__frame__ == pd.DataFrame([myobj._asdict()])).all().all()
        # but the obj instance doesnt have the attribute
        with self.assertRaises(AttributeError):
            myobj.__frame__
        # expected AttributeError, as the instance doesnt have a frame representation provided by the class

        # appending happens as expected
        myobj2 = MyTpl(att1=47, att2=53)

        # checking the second record is the instance we just created
        assert (myobj2.__series__ == pd.Series(myobj2._asdict())).all()



if __name__ == "__main__":
    unittest.main()
