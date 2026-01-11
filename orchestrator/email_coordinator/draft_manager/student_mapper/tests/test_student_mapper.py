"""
Tests for Student Mapper Service
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from student_mapper import StudentMapper, lookup_student


class TestStudentMapper:
    """Test cases for StudentMapper class."""

    @pytest.fixture
    def mapper(self):
        """Create a StudentMapper instance for testing."""
        config_path = "./config.yaml"
        return StudentMapper(config_path)

    def test_initialization(self, mapper):
        """Test that the mapper initializes correctly."""
        assert mapper is not None
        assert len(mapper.mapping_cache) > 0
        assert mapper.config is not None
        assert mapper.logger is not None

    def test_load_mapping(self, mapper):
        """Test that mappings are loaded correctly."""
        assert len(mapper.mapping_cache) > 0
        # Check that sample data is loaded
        assert 'student1@example.com' in mapper.mapping_cache
        assert mapper.mapping_cache['student1@example.com'] == 'Alex Johnson'

    def test_map_existing_email_lowercase(self, mapper):
        """Test mapping an existing email (lowercase)."""
        result = mapper.map_email_to_name('student1@example.com')
        assert result['found'] is True
        assert result['name'] == 'Alex Johnson'

    def test_map_existing_email_uppercase(self, mapper):
        """Test case-insensitive email matching."""
        result = mapper.map_email_to_name('STUDENT1@EXAMPLE.COM')
        assert result['found'] is True
        assert result['name'] == 'Alex Johnson'

    def test_map_existing_email_mixed_case(self, mapper):
        """Test case-insensitive matching with mixed case."""
        result = mapper.map_email_to_name('Student2@Example.Com')
        assert result['found'] is True
        assert result['name'] == 'Maria Garcia'

    def test_map_nonexistent_email(self, mapper):
        """Test mapping a non-existent email."""
        result = mapper.map_email_to_name('unknown@example.com')
        assert result['found'] is False
        assert result['name'] == 'Student'  # fallback name from config

    def test_map_empty_email(self, mapper):
        """Test handling of empty email address."""
        result = mapper.map_email_to_name('')
        assert result['found'] is False
        assert result['name'] == 'Student'

    def test_map_none_email(self, mapper):
        """Test handling of None email address."""
        result = mapper.map_email_to_name(None)
        assert result['found'] is False
        assert result['name'] == 'Student'

    def test_map_email_with_whitespace(self, mapper):
        """Test that whitespace is properly trimmed."""
        result = mapper.map_email_to_name('  student1@example.com  ')
        assert result['found'] is True
        assert result['name'] == 'Alex Johnson'

    def test_multiple_lookups(self, mapper):
        """Test multiple lookups in sequence."""
        result1 = mapper.map_email_to_name('student1@example.com')
        result2 = mapper.map_email_to_name('student2@example.com')
        result3 = mapper.map_email_to_name('unknown@example.com')

        assert result1['found'] is True
        assert result1['name'] == 'Alex Johnson'

        assert result2['found'] is True
        assert result2['name'] == 'Maria Garcia'

        assert result3['found'] is False
        assert result3['name'] == 'Student'

    def test_get_stats(self, mapper):
        """Test statistics retrieval."""
        stats = mapper.get_stats()
        assert 'total_mappings' in stats
        assert stats['total_mappings'] > 0
        assert stats['service'] == 'student_mapper'
        assert stats['version'] == '1.0.0'

    def test_reload_mapping(self, mapper):
        """Test reloading the mapping."""
        original_count = len(mapper.mapping_cache)
        mapper.reload_mapping()
        assert len(mapper.mapping_cache) == original_count

    def test_all_sample_students(self, mapper):
        """Test all sample students from the data file."""
        expected_mappings = {
            'student1@example.com': 'Alex Johnson',
            'student2@example.com': 'Maria Garcia',
            'student3@example.com': 'James Smith',
            'student4@example.com': 'Sarah Williams',
            'student5@example.com': 'Michael Brown',
            'test@university.edu': 'Test Student',
            'john.doe@college.edu': 'John Doe',
            'jane.smith@university.edu': 'Jane Smith',
        }

        for email, expected_name in expected_mappings.items():
            result = mapper.map_email_to_name(email)
            assert result['found'] is True, f"Expected to find {email}"
            assert result['name'] == expected_name, \
                f"Expected {expected_name} for {email}, got {result['name']}"


class TestLookupStudentFunction:
    """Test the standalone lookup_student function."""

    def test_lookup_student_found(self):
        """Test lookup_student with an existing email."""
        result = lookup_student('student1@example.com')
        assert result['found'] is True
        assert result['name'] == 'Alex Johnson'

    def test_lookup_student_not_found(self):
        """Test lookup_student with a non-existent email."""
        result = lookup_student('unknown@example.com')
        assert result['found'] is False
        assert result['name'] == 'Student'

    def test_lookup_student_case_insensitive(self):
        """Test lookup_student with different casing."""
        result = lookup_student('STUDENT2@EXAMPLE.COM')
        assert result['found'] is True
        assert result['name'] == 'Maria Garcia'


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def mapper(self):
        """Create a StudentMapper instance for testing."""
        return StudentMapper("./config.yaml")

    def test_special_characters_in_email(self, mapper):
        """Test handling of special characters in email."""
        result = mapper.map_email_to_name('user+tag@example.com')
        assert result['found'] is False
        assert result['name'] == 'Student'

    def test_very_long_email(self, mapper):
        """Test handling of very long email addresses."""
        long_email = 'a' * 100 + '@example.com'
        result = mapper.map_email_to_name(long_email)
        assert result['found'] is False
        assert result['name'] == 'Student'

    def test_invalid_config_file(self):
        """Test handling of invalid config file."""
        with pytest.raises(FileNotFoundError):
            StudentMapper("./nonexistent_config.yaml")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
