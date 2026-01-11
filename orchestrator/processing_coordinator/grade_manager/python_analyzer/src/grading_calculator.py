"""
Grading calculator module.
Calculates grades based on line count metrics.
"""
from typing import List, Dict


class GradingCalculator:
    """Calculates grades for Python repositories."""

    def __init__(self, line_threshold: int):
        self.line_threshold = line_threshold

    def calculate_grade(self, file_details: List[Dict]) -> Dict:
        """
        Calculate grade based on file line counts.

        Args:
            file_details: List of file detail dictionaries

        Returns:
            Dictionary with grading results
        """
        if not file_details:
            return {
                "total_files": 0,
                "total_lines": 0,
                "lines_above_150": 0,
                "grade": 0.0,
                "file_details": [],
                "status": "Success"
            }

        total_files = len(file_details)
        total_lines = 0
        lines_above_threshold = 0

        # Process each file
        for file_detail in file_details:
            line_count = file_detail["line_count"]
            total_lines += line_count

            # Check if file is above threshold
            if line_count > self.line_threshold:
                file_detail["above_threshold"] = True
                lines_above_threshold += line_count
            else:
                file_detail["above_threshold"] = False

        # Calculate grade
        if total_lines > 0:
            grade = (lines_above_threshold / total_lines) * 100
        else:
            grade = 0.0

        return {
            "total_files": total_files,
            "total_lines": total_lines,
            "lines_above_150": lines_above_threshold,
            "grade": round(grade, 2),
            "file_details": file_details,
            "status": "Success"
        }
