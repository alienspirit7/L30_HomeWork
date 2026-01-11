"""
File analyzer module for scanning Python repositories.
Finds and analyzes Python files according to configuration rules.
"""
import os
from pathlib import Path
from typing import List, Dict
from fnmatch import fnmatch

from src.line_counter import LineCounter


class FileAnalyzer:
    """Analyzes Python files in a repository."""

    def __init__(self, file_extensions: List[str],
                 exclude_patterns: List[str],
                 line_counter: LineCounter):
        self.file_extensions = file_extensions
        self.exclude_patterns = exclude_patterns
        self.line_counter = line_counter

    def analyze_repository(self, repository_path: str) -> List[Dict]:
        """
        Analyze all Python files in a repository.

        Args:
            repository_path: Path to the repository root

        Returns:
            List of file details dictionaries
        """
        if not os.path.exists(repository_path):
            raise ValueError(f"Repository path does not exist: {repository_path}")

        if not os.path.isdir(repository_path):
            raise ValueError(f"Repository path is not a directory: {repository_path}")

        python_files = self._find_python_files(repository_path)
        file_details = []

        for file_path in python_files:
            _, line_count = self.line_counter.count_lines(file_path)

            # Get relative path for better readability
            try:
                relative_path = os.path.relpath(file_path, repository_path)
            except ValueError:
                relative_path = file_path

            file_details.append({
                "filename": relative_path,
                "line_count": line_count,
                "above_threshold": False  # Will be set by grading calculator
            })

        return file_details

    def _find_python_files(self, repository_path: str) -> List[str]:
        """
        Find all Python files in repository excluding patterns.

        Args:
            repository_path: Path to the repository root

        Returns:
            List of absolute paths to Python files
        """
        python_files = []

        for root, dirs, files in os.walk(repository_path):
            # Filter out excluded directories to prevent walking into them
            dirs[:] = [d for d in dirs if not self._is_excluded(
                os.path.join(root, d), repository_path)]

            for file in files:
                file_path = os.path.join(root, file)

                # Check if file has Python extension
                if not any(file.endswith(ext) for ext in self.file_extensions):
                    continue

                # Check if file matches exclusion patterns
                if self._is_excluded(file_path, repository_path):
                    continue

                python_files.append(file_path)

        return python_files

    def _is_excluded(self, file_path: str, repository_path: str) -> bool:
        """
        Check if a file path matches any exclusion pattern.

        Args:
            file_path: Absolute path to check
            repository_path: Repository root path

        Returns:
            True if file should be excluded
        """
        try:
            relative_path = os.path.relpath(file_path, repository_path)
        except ValueError:
            return False

        # Normalize path separators for pattern matching
        normalized_path = relative_path.replace(os.sep, '/')

        for pattern in self.exclude_patterns:
            # Remove leading ** for fnmatch
            pattern_normalized = pattern.replace('**/', '').replace('**', '*')

            # Check if pattern matches
            if fnmatch(normalized_path, pattern_normalized):
                return True

            # Also check each path component
            path_parts = normalized_path.split('/')
            for i in range(len(path_parts)):
                partial_path = '/'.join(path_parts[i:])
                if fnmatch(partial_path, pattern_normalized):
                    return True

        return False
