"""Tests for grading calculator module."""
import unittest
from src.grading_calculator import GradingCalculator


class TestGradingCalculator(unittest.TestCase):
    """Test cases for GradingCalculator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.calculator = GradingCalculator(line_threshold=150)

    def test_empty_file_list(self):
        """Test calculation with no files."""
        result = self.calculator.calculate_grade([])
        self.assertEqual(result['total_files'], 0)
        self.assertEqual(result['total_lines'], 0)
        self.assertEqual(result['lines_above_150'], 0)
        self.assertEqual(result['grade'], 0.0)
        self.assertEqual(result['status'], 'Success')

    def test_all_files_below_threshold(self):
        """Test when all files are below threshold."""
        file_details = [
            {"filename": "file1.py", "line_count": 50},
            {"filename": "file2.py", "line_count": 100},
            {"filename": "file3.py", "line_count": 75}
        ]

        result = self.calculator.calculate_grade(file_details)
        self.assertEqual(result['total_files'], 3)
        self.assertEqual(result['total_lines'], 225)
        self.assertEqual(result['lines_above_150'], 0)
        self.assertEqual(result['grade'], 0.0)
        self.assertFalse(result['file_details'][0]['above_threshold'])
        self.assertFalse(result['file_details'][1]['above_threshold'])
        self.assertFalse(result['file_details'][2]['above_threshold'])

    def test_all_files_above_threshold(self):
        """Test when all files are above threshold."""
        file_details = [
            {"filename": "file1.py", "line_count": 200},
            {"filename": "file2.py", "line_count": 300},
            {"filename": "file3.py", "line_count": 250}
        ]

        result = self.calculator.calculate_grade(file_details)
        self.assertEqual(result['total_files'], 3)
        self.assertEqual(result['total_lines'], 750)
        self.assertEqual(result['lines_above_150'], 750)
        self.assertEqual(result['grade'], 100.0)
        self.assertTrue(result['file_details'][0]['above_threshold'])
        self.assertTrue(result['file_details'][1]['above_threshold'])
        self.assertTrue(result['file_details'][2]['above_threshold'])

    def test_mixed_files(self):
        """Test with mix of files above and below threshold."""
        file_details = [
            {"filename": "file1.py", "line_count": 50},
            {"filename": "file2.py", "line_count": 200},
            {"filename": "file3.py", "line_count": 100},
            {"filename": "file4.py", "line_count": 300}
        ]

        result = self.calculator.calculate_grade(file_details)
        self.assertEqual(result['total_files'], 4)
        self.assertEqual(result['total_lines'], 650)
        self.assertEqual(result['lines_above_150'], 500)
        # Grade should be (500 / 650) * 100 = 76.92
        self.assertAlmostEqual(result['grade'], 76.92, places=2)
        self.assertFalse(result['file_details'][0]['above_threshold'])
        self.assertTrue(result['file_details'][1]['above_threshold'])
        self.assertFalse(result['file_details'][2]['above_threshold'])
        self.assertTrue(result['file_details'][3]['above_threshold'])

    def test_file_exactly_at_threshold(self):
        """Test file with exactly 150 lines (should be False)."""
        file_details = [
            {"filename": "file1.py", "line_count": 150}
        ]

        result = self.calculator.calculate_grade(file_details)
        self.assertFalse(result['file_details'][0]['above_threshold'])
        self.assertEqual(result['lines_above_150'], 0)
        self.assertEqual(result['grade'], 0.0)

    def test_file_just_above_threshold(self):
        """Test file with 151 lines (should be True)."""
        file_details = [
            {"filename": "file1.py", "line_count": 151}
        ]

        result = self.calculator.calculate_grade(file_details)
        self.assertTrue(result['file_details'][0]['above_threshold'])
        self.assertEqual(result['lines_above_150'], 151)
        self.assertEqual(result['grade'], 100.0)


if __name__ == '__main__':
    unittest.main()
