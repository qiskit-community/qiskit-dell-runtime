import unittest
from test_qruntime import FirstTest

def suite():
    suite = unittest.TestSuite()
    tests = [FirstTest]
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())