import unittest
import sys

if __name__ == '__main__':
    # Run the tests
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.discover('.'))
    if result.wasSuccessful():
        print("Verification passed!")
        sys.exit(0)
    else:
        print("Verification failed!")
        sys.exit(1)
