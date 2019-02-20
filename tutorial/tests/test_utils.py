
__package__ = "tutorial"


import unittest
from .utils import filter_qparams


class UtilsTest(unittest.TestCase):
    def test_remove(self):
        url = 'https://www.wlw.de/de/firma/hfs-verpackungen-gmbh-1713082?q=Tiefdruck&category_id=95529#about_us/image/3'
        to_be = 'https://www.wlw.de/de/firma/hfs-verpackungen-gmbh-1713082?category_id=95529'
        result = filter_qparams(['q'], 'remove', url)
        self.assertEqual(result, to_be)

    def test_retain(self):
        url = 'https://www.wlw.de/de/firma/hfs-verpackungen-gmbh-1713082?q=Tiefdruck&category_id=95529#about_us'
        to_be = 'https://www.wlw.de/de/firma/hfs-verpackungen-gmbh-1713082?category_id=95529'
        result = filter_qparams(['category_id'], 'retain', url)
        self.assertEqual(result, to_be)
