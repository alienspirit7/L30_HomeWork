"""Tests for file analyzer module."""
import unittest
import tempfile
import os
from pathlib import Path
from src.file_analyzer import FileAnalyzer
from src.line_counter import LineCounter


class TestFileAnalyzer(unittest.TestCase):
    """Test cases for FileAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.line_counter = LineCounter(
            exclude_comments=True,
            exclude_blank_lines=True,
            exclude_docstrings=True
        )
        self.analyzer = FileAnalyzer(
            file_extensions=['.py'],
            exclude_patterns=[
                '**/venv/**',
                '**/__pycache__/**',
                '**/test_*.py',
                '**/*_test.py',
                '**/setup.py',
                '**/conftest.py'
            ],
            line_counter=self.line_counter
        )

    def test_analyze_empty_directory(self):
        """Test analyzing an empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.analyzer.analyze_repository(tmpdir)
            self.assertEqual(len(result), 0)

    def test_analyze_single_file(self):
        """Test analyzing a directory with a single Python file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, 'test.py')
            with open(file_path, 'w') as f:
                f.write('x = 1\ny = 2\nz = 3\n')

            result = self.analyzer.analyze_repository(tmpdir)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['filename'], 'test.py')
            self.assertEqual(result[0]['line_count'], 3)

    def test_exclude_test_files(self):
        """Test that test files are excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create regular file
            with open(os.path.join(tmpdir, 'module.py'), 'w') as f:
                f.write('x = 1\n')

            # Create test files that should be excluded
            with open(os.path.join(tmpdir, 'test_module.py'), 'w') as f:
                f.write('x = 1\n')

            with open(os.path.join(tmpdir, 'module_test.py'), 'w') as f:
                f.write('x = 1\n')

            result = self.analyzer.analyze_repository(tmpdir)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['filename'], 'module.py')

    def test_exclude_pycache(self):
        """Test that __pycache__ files are excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create regular file
            with open(os.path.join(tmpdir, 'module.py'), 'w') as f:
                f.write('x = 1\n')

            # Create __pycache__ directory
            pycache_dir = os.path.join(tmpdir, '__pycache__')
            os.makedirs(pycache_dir)
            with open(os.path.join(pycache_dir, 'module.cpython-39.pyc'), 'w') as f:
                f.write('binary content\n')

            result = self.analyzer.analyze_repository(tmpdir)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['filename'], 'module.py')

    def test_exclude_venv(self):
        """Test that venv files are excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create regular file
            with open(os.path.join(tmpdir, 'module.py'), 'w') as f:
                f.write('x = 1\n')

            # Create venv directory
            venv_dir = os.path.join(tmpdir, 'venv', 'lib')
            os.makedirs(venv_dir)
            with open(os.path.join(venv_dir, 'site.py'), 'w') as f:
                f.write('x = 1\n')

            result = self.analyzer.analyze_repository(tmpdir)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['filename'], 'module.py')

    def test_exclude_setup_py(self):
        """Test that setup.py is excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create regular file
            with open(os.path.join(tmpdir, 'module.py'), 'w') as f:
                f.write('x = 1\n')

            # Create setup.py
            with open(os.path.join(tmpdir, 'setup.py'), 'w') as f:
                f.write('from setuptools import setup\n')

            result = self.analyzer.analyze_repository(tmpdir)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['filename'], 'module.py')

    def test_nested_directories(self):
        """Test analyzing nested directory structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested structure
            subdir1 = os.path.join(tmpdir, 'src')
            subdir2 = os.path.join(subdir1, 'utils')
            os.makedirs(subdir2)

            with open(os.path.join(tmpdir, 'main.py'), 'w') as f:
                f.write('x = 1\n')

            with open(os.path.join(subdir1, 'module1.py'), 'w') as f:
                f.write('y = 2\n')

            with open(os.path.join(subdir2, 'module2.py'), 'w') as f:
                f.write('z = 3\n')

            result = self.analyzer.analyze_repository(tmpdir)
            self.assertEqual(len(result), 3)
            filenames = sorted([f['filename'] for f in result])
            self.assertIn('main.py', filenames)
            self.assertIn(os.path.join('src', 'module1.py'), filenames)
            self.assertIn(os.path.join('src', 'utils', 'module2.py'), filenames)

    def test_nonexistent_repository(self):
        """Test handling of nonexistent repository path."""
        with self.assertRaises(ValueError):
            self.analyzer.analyze_repository('/nonexistent/path')

    def test_file_path_instead_of_directory(self):
        """Test handling when a file path is provided instead of directory."""
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            f.write(b'x = 1\n')
            temp_path = f.name

        try:
            with self.assertRaises(ValueError):
                self.analyzer.analyze_repository(temp_path)
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
