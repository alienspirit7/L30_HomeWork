"""
Line counter module for Python files.
Counts lines excluding blanks, comments, and docstrings.
"""
import re
from typing import Tuple


class LineCounter:
    """Counts effective lines of code in Python files."""

    def __init__(self, exclude_comments: bool = True,
                 exclude_blank_lines: bool = True,
                 exclude_docstrings: bool = True):
        self.exclude_comments = exclude_comments
        self.exclude_blank_lines = exclude_blank_lines
        self.exclude_docstrings = exclude_docstrings

    def count_lines(self, file_path: str) -> Tuple[int, int]:
        """
        Count lines in a Python file.

        Args:
            file_path: Path to the Python file

        Returns:
            Tuple of (total_raw_lines, counted_lines)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (IOError, UnicodeDecodeError) as e:
            return 0, 0

        lines = content.split('\n')
        total_raw_lines = len(lines)

        counted_lines = self._count_effective_lines(content)

        return total_raw_lines, counted_lines

    def _count_effective_lines(self, content: str) -> int:
        """
        Count effective lines excluding blanks, comments, and docstrings.

        Args:
            content: File content as string

        Returns:
            Number of counted lines
        """
        lines = content.split('\n')
        counted = 0
        in_docstring = False
        docstring_delimiter = None

        for line in lines:
            stripped = line.strip()

            # Check for blank lines
            if self.exclude_blank_lines and not stripped:
                continue

            # Check for docstring delimiters
            if self.exclude_docstrings:
                # Check for triple quotes
                triple_double = '"""'
                triple_single = "'''"

                if not in_docstring:
                    # Check if line starts a docstring
                    if triple_double in stripped:
                        docstring_delimiter = triple_double
                        # Check if it's a single-line docstring
                        if stripped.count(triple_double) >= 2:
                            continue
                        else:
                            in_docstring = True
                            continue
                    elif triple_single in stripped:
                        docstring_delimiter = triple_single
                        # Check if it's a single-line docstring
                        if stripped.count(triple_single) >= 2:
                            continue
                        else:
                            in_docstring = True
                            continue
                else:
                    # We're in a docstring, check if this line ends it
                    if docstring_delimiter in stripped:
                        in_docstring = False
                        docstring_delimiter = None
                    continue

            # If we're in a docstring, skip
            if in_docstring:
                continue

            # Check for comment lines
            if self.exclude_comments and stripped.startswith('#'):
                continue

            # This is a counted line
            counted += 1

        return counted
