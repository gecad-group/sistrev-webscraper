from unittest import TestCase
from datacleaner import DataCleaner

class TestDataCleaner(TestCase):

    def setUp(self):
        self.cleaner = DataCleaner()
        self.cleaner.add_file("../testdata/testdata.ris")

    def test_count_in_entries(self):
        if self.cleaner.count_in_entries() != 5:
            self.fail()

    def test_count_out_entries(self):
        self.cleaner.out_entries = self.cleaner.in_entries
        if self.cleaner.count_out_entries() != 5:
            self.fail()

    def test_clean_entries(self):
        self.cleaner.out_entries = self.cleaner.in_entries
        self.cleaner.clean_entries()
        if len(self.cleaner.out_entries) != 1:
            self.fail()
