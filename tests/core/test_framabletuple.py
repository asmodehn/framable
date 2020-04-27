import unittest
import pandas as pd
from pandas.core import dtypes

from framable.core.framabletuple import FramableTuple


class TestFramableTuple(unittest.TestCase):
    def test_framabletuple(self):

        MyTpl = FramableTuple("MyTpl", [("att1", int), ("att2", int)])

        myobj = MyTpl(42, 51)

        assert (myobj.__series__ == pd.Series(myobj._asdict())).all()

        # the class has a frame (from the metaclass)
        assert (MyTpl.__frame__ == pd.DataFrame([myobj._asdict()])).all().all()
        # but the obj instance doesnt have the attribute
        with self.assertRaises(AttributeError):
            myobj.__frame__
        # expected AttributeError, as the instance doesnt have a frame representation provided by the class

        # appending happens as expected
        myobj2 = MyTpl(47, 53)

        # checking the second record is the instance we just created
        assert (myobj2.__series__ == pd.Series(myobj2._asdict())).all()


if __name__ == "__main__":
    unittest.main()
