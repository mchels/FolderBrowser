import sys
sys.path.append('..')
import unittest
from datahandler import data_handler_factory
from sweep import Sweep


class DataHandlerTestCase(unittest.TestCase):
    def setUp(self):
        path = 'C:/Dropbox/PhD/sandbox_phd/FolderBrowser/data/2016-09-19#015'
        self.sweep = Sweep(path)
        data = self.sweep.data
        x = data['mL']
        y = data['mR']
        self.data_h = data_handler_factory(x, y)

    def test_data_validity(self):
        self.assertTrue(self.data_h.data_is_valid)

    def test_imshow_eligible(self):
        self.assertTrue(self.data_h.imshow_eligible)

    def test_data_is_linear(self):
        self.assertTrue(self.data_h.data_is_linear[0])
        self.assertTrue(self.data_h.data_is_linear[1])

    def test_data_is_linear_on_axis(self):
        self.assertEqual(self.data_h.lin_axis_for_data[1], 0)
        self.assertEqual(self.data_h.lin_axis_for_data[0], 1)

    def test_not_reversed(self):
        for i in (0,1):
            elems_are_equal = self.data_h.data[i] == self.data_h.tdata[i]
            self.assertTrue(elems_are_equal.all())


if __name__=='__main__':
    unittest.main()
