from unittest import TestCase
from datacleaner import DataCleaner
import os

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

    def test_export(self):
        self.cleaner.export_data("/tmp")
        # Check if the file was created
        if not os.path.exists("/tmp/out.ris"):
            self.fail()
        # Delete file
        os.remove("/tmp/out.ris")

    def test_export_invalid(self):
        try:
            self.cleaner.export_data("/tmp/invalid.ris")
        except ValueError as e:
            self.assertEqual(str(e), "The path is a file, not a directory!")
        else:
            self.fail()

    def test_export_to_file(self):
        self.cleaner.export_data_tofile("/tmp/test.ris")
        # Check if the file was created
        if not os.path.exists("/tmp/test.ris"):
            self.fail()
        # Delete file
        os.remove("/tmp/test.ris")

    def test_export_to_file_dir(self):
        try:
            self.cleaner.export_data_tofile("/tmp")
        except ValueError as e:
            self.assertEqual(str(e), "The path is a directory, not a file!")
        else:
            self.fail()

    def test_export_to_file_invalid(self):
        try:
            self.cleaner.export_data_tofile("/tmp/invalid.txt")
        except Exception as e:
            self.assertEqual(str(e), "The file is not a RIS file!")
        else:
            self.fail()