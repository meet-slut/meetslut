from datetime import datetime
import unittest

from meetslut.config import GET_CFG
from meetslut.download import amend_suffix
from meetslut.webparser import ParserFactory
from meetslut.download import download


class Tester(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        print(f'Test start @: {datetime.now().strftime("%Y-%m-%d, %H:%M:%S")}')
    @classmethod
    def tearDownClass(cls) -> None:
        print(f'\nTest end   @: {datetime.now().strftime("%Y-%m-%d, %H:%M:%S")}')
    def setUp(self) -> None:
        pass
    def tearDown(self) -> None:
        pass

    def test_amend_suffix(self):
        self.assertEqual(amend_suffix('.gif'), '.gif', 'error')
        self.assertEqual(amend_suffix('.jiff'), '.jpg', 'error')

    def test_factory(self):
        for url in [
            'https://caitlin.top/home',
            'https://www.99zipai.com/selfies',
            'https://motherless.com/'
        ]:
            p = ParserFactory.create(url)
            self.assertTrue(p)

    @unittest.skipIf(GET_CFG['proxies'] is None, "Skiped: the proxy is necessary.")
    def test_bool_value(self):
        self.assertTrue(self.test_class.is_string("hello world!"))

if __name__ == '__main__':
    # build test
    suite = unittest.TestSuite()
    suite.addTest(Tester('test_amend_suffix'))
    suite.addTest(Tester('test_factory'))

    # execute test
    runner = unittest.TextTestRunner()
    runner.run(suite)