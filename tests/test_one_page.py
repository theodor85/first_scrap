import unittest
import tests


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase( tests.BSOnePageTest )
    suite = unittest.defaultTestLoader.loadTestsFromTestCase( tests.SeleniumOnePageTest )
    unittest.TextTestRunner().run(suite)