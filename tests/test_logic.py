import sys,os,datetime,unittest
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util import fixcity,daysleft,expclass,tier,toint
class Cities(unittest.TestCase):
    def test_match_ok(self):
        self.assertEqual(fixcity("ranchi"),"Ranchi")
        self.assertEqual(fixcity(" Bhopal "),"Bhopal")
    def test_match_none(self):
        self.assertIsNone(fixcity("Atlantis"))
        self.assertIsNone(fixcity(""))
        self.assertIsNone(fixcity(None))
class Expiry(unittest.TestCase):
    def test_days_string(self):
        d=(datetime.date.today()+datetime.timedelta(days=10)).isoformat()
        self.assertEqual(daysleft(d),10)
    def test_days_bad(self):
        self.assertEqual(daysleft("not-a-date"),-1)
    def test_class_thresholds(self):
        today=datetime.date.today()
        self.assertEqual(expclass((today+datetime.timedelta(days=200)).isoformat()),"ok")
        self.assertEqual(expclass((today+datetime.timedelta(days=100)).isoformat()),"soon")
        self.assertEqual(expclass((today+datetime.timedelta(days=10)).isoformat()),"critical")
class Tier(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(tier(0),"New")
        self.assertEqual(tier(3),"Bronze")
        self.assertEqual(tier(6),"Silver")
        self.assertEqual(tier(11),"Gold")
        self.assertEqual(tier(25),"Platinum")
class ToInt(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(toint("42"),42)
        self.assertEqual(toint(" 7 "),7)
    def test_invalid(self):
        self.assertEqual(toint("abc"),0)
        self.assertEqual(toint(None),0)
if(__name__=="__main__"):
    unittest.main()
