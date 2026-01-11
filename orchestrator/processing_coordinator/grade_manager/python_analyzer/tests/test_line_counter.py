"""Tests for line counter module."""
import unittest
import tempfile
import os
from src.line_counter import LineCounter


class TestLineCounter(unittest.TestCase):
    """Test cases for LineCounter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.counter = LineCounter(
            exclude_comments=True,
            exclude_blank_lines=True,
            exclude_docstrings=True
        )

    def test_count_simple_code(self):
        """Test counting simple code without comments or docstrings."""
        content = """x = 1
y = 2
z = x + y"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            total, counted = self.counter.count_lines(temp_path)
            self.assertEqual(counted, 3)
        finally:
            os.unlink(temp_path)

    def test_exclude_blank_lines(self):
        """Test that blank lines are excluded."""
        content = """x = 1

y = 2

z = x + y"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            total, counted = self.counter.count_lines(temp_path)
            self.assertEqual(counted, 3)
        finally:
            os.unlink(temp_path)

    def test_exclude_comments(self):
        """Test that comment lines are excluded."""
        content = """# This is a comment
x = 1
# Another comment
y = 2"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            total, counted = self.counter.count_lines(temp_path)
            self.assertEqual(counted, 2)
        finally:
            os.unlink(temp_path)

    def test_exclude_docstrings(self):
        """Test that docstrings are excluded."""
        content = '''"""
This is a module docstring.
It spans multiple lines.
"""
x = 1
"""Another docstring"""
y = 2'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            total, counted = self.counter.count_lines(temp_path)
            self.assertEqual(counted, 2)
        finally:
            os.unlink(temp_path)

    def test_single_line_docstring(self):
        """Test that single-line docstrings are excluded."""
        content = '''"""Single line docstring"""
x = 1
"""Another single line"""
y = 2'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            total, counted = self.counter.count_lines(temp_path)
            self.assertEqual(counted, 2)
        finally:
            os.unlink(temp_path)

    def test_mixed_content(self):
        """Test counting with mixed content."""
        content = '''"""Module docstring"""
# Import statement comment
import os

def function():
    """Function docstring"""
    x = 1  # Inline comment (should count)

    y = 2
    return x + y

# End of file comment'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            total, counted = self.counter.count_lines(temp_path)
            # Should count: import os, def function():, x = 1, y = 2, return x + y
            self.assertEqual(counted, 5)
        finally:
            os.unlink(temp_path)

    def test_nonexistent_file(self):
        """Test handling of nonexistent file."""
        total, counted = self.counter.count_lines('/nonexistent/file.py')
        self.assertEqual(total, 0)
        self.assertEqual(counted, 0)


if __name__ == '__main__':
    unittest.main()
