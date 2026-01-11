"""Tests for main service module."""
import unittest
import tempfile
import os
import yaml
from src.service import PythonAnalyzerService


class TestPythonAnalyzerService(unittest.TestCase):
    """Test cases for PythonAnalyzerService class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file
        self.config_data = {
            'service': {
                'name': 'python_analyzer',
                'version': '1.0.0'
            },
            'analysis': {
                'file_extensions': ['.py'],
                'exclude_patterns': [
                    '**/venv/**',
                    '**/__pycache__/**',
                    '**/test_*.py',
                    '**/*_test.py',
                    '**/setup.py',
                    '**/conftest.py'
                ]
            },
            'grading': {
                'line_threshold': 150,
                'exclude_comments': True,
                'exclude_blank_lines': True,
                'exclude_docstrings': True
            },
            'logging': {
                'level': 'INFO',
                'file': './logs/test_python_analyzer.log'
            }
        }

        self.temp_config = tempfile.NamedTemporaryFile(
            mode='w', suffix='.yaml', delete=False
        )
        yaml.dump(self.config_data, self.temp_config)
        self.temp_config.close()

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)

    def test_service_initialization(self):
        """Test that service initializes correctly."""
        service = PythonAnalyzerService(config_path=self.temp_config.name)
        self.assertIsNotNone(service.line_counter)
        self.assertIsNotNone(service.file_analyzer)
        self.assertIsNotNone(service.grading_calculator)

    def test_analyze_simple_repository(self):
        """Test analyzing a simple repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple Python file
            with open(os.path.join(tmpdir, 'module.py'), 'w') as f:
                f.write('x = 1\ny = 2\nz = 3\n')

            service = PythonAnalyzerService(config_path=self.temp_config.name)
            result = service.analyze(tmpdir)

            self.assertEqual(result['status'], 'Success')
            self.assertEqual(result['total_files'], 1)
            self.assertEqual(result['total_lines'], 3)
            self.assertEqual(result['lines_above_150'], 0)
            self.assertEqual(result['grade'], 0.0)

    def test_analyze_repository_with_large_file(self):
        """Test analyzing repository with file above threshold."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file with 200 lines
            with open(os.path.join(tmpdir, 'large.py'), 'w') as f:
                for i in range(200):
                    f.write(f'x{i} = {i}\n')

            service = PythonAnalyzerService(config_path=self.temp_config.name)
            result = service.analyze(tmpdir)

            self.assertEqual(result['status'], 'Success')
            self.assertEqual(result['total_files'], 1)
            self.assertEqual(result['total_lines'], 200)
            self.assertEqual(result['lines_above_150'], 200)
            self.assertEqual(result['grade'], 100.0)
            self.assertTrue(result['file_details'][0]['above_threshold'])

    def test_analyze_mixed_repository(self):
        """Test analyzing repository with mixed file sizes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Small file
            with open(os.path.join(tmpdir, 'small.py'), 'w') as f:
                for i in range(50):
                    f.write(f'x{i} = {i}\n')

            # Large file
            with open(os.path.join(tmpdir, 'large.py'), 'w') as f:
                for i in range(200):
                    f.write(f'y{i} = {i}\n')

            service = PythonAnalyzerService(config_path=self.temp_config.name)
            result = service.analyze(tmpdir)

            self.assertEqual(result['status'], 'Success')
            self.assertEqual(result['total_files'], 2)
            self.assertEqual(result['total_lines'], 250)
            self.assertEqual(result['lines_above_150'], 200)
            # Grade should be (200 / 250) * 100 = 80.0
            self.assertEqual(result['grade'], 80.0)

    def test_analyze_with_exclusions(self):
        """Test that excluded files are not analyzed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Regular file
            with open(os.path.join(tmpdir, 'module.py'), 'w') as f:
                f.write('x = 1\n')

            # Test file (should be excluded)
            with open(os.path.join(tmpdir, 'test_module.py'), 'w') as f:
                f.write('y = 2\n')

            # Setup file (should be excluded)
            with open(os.path.join(tmpdir, 'setup.py'), 'w') as f:
                f.write('z = 3\n')

            service = PythonAnalyzerService(config_path=self.temp_config.name)
            result = service.analyze(tmpdir)

            self.assertEqual(result['status'], 'Success')
            self.assertEqual(result['total_files'], 1)
            self.assertEqual(result['file_details'][0]['filename'], 'module.py')

    def test_analyze_nonexistent_repository(self):
        """Test analyzing a nonexistent repository."""
        service = PythonAnalyzerService(config_path=self.temp_config.name)
        result = service.analyze('/nonexistent/path')

        self.assertEqual(result['status'], 'Failed')
        self.assertIn('error', result)

    def test_analyze_empty_repository(self):
        """Test analyzing an empty repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = PythonAnalyzerService(config_path=self.temp_config.name)
            result = service.analyze(tmpdir)

            self.assertEqual(result['status'], 'Success')
            self.assertEqual(result['total_files'], 0)
            self.assertEqual(result['total_lines'], 0)
            self.assertEqual(result['grade'], 0.0)


if __name__ == '__main__':
    unittest.main()
