"""
Test course_fetcher module

python -m unittest test_course_fetcher
"""
import unittest
import src.course_fetcher as crs_fchr


class TestCourseFetcher(unittest.TestCase):
    # basic test
    def test(self):
        self.assertTrue(True)

    # test course name generator
    def test_get_course_name(self):
        crs_name_val = "CSC:501 - 2198"
        val = crs_fchr.get_course_name("CSC", "501", "2198")
        self.assertEqual(val, crs_name_val, "Course Name")

    # read json utility
    def test_read_json(self):
        prop_val = "Data item 1"
        arr_val = "Array item 1"
        dict_val = "Dict Property"

        test_file_path = "./test_json.json"
        data = crs_fchr.read_json(test_file_path)

        self.assertEqual(data['prop'], prop_val, "Reading json property")
        self.assertEqual(data['arr'][0], arr_val, "Reading json array")
        self.assertEqual(data['dict']['dictProp'], dict_val, "Reading json dict")


if __name__ == '__main__':
    unittest.main()
