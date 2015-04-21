import unittest

from gluon.globals import Request

execfile("applications/iapt2group1/controllers/project.py",globals())

class Test(unittest.TestCase):
    def setUp(self):
        pass

    def test(self):
        self.assertEqual(1,1)


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(Test))
unittest.TextTestRunner(verbosity=2).run(suite)