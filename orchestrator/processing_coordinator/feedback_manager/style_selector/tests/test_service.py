"""
Test suite for Style Selector Service
Tests all grade ranges and edge cases
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from service import StyleSelector


class TestStyleSelector:
    """Test cases for StyleSelector service."""

    @pytest.fixture
    def service(self):
        """Create a StyleSelector instance for testing."""
        return StyleSelector(config_path="config.yaml")

    def test_initialization(self, service):
        """Test that service initializes correctly."""
        assert service is not None
        assert len(service.styles) == 4
        assert service.config['service']['name'] == 'style_selector'

    # Test Trump style (90-100)
    def test_select_style_trump_perfect_score(self, service):
        """Test trump style for perfect score."""
        result = service.select_style(100)
        assert result['style_name'] == 'trump'
        assert 'tremendous' in result['style_description'].lower() or 'enthusiastic' in result['style_description'].lower()
        assert '100' in result['prompt_template']

    def test_select_style_trump_boundary(self, service):
        """Test trump style at lower boundary."""
        result = service.select_style(90)
        assert result['style_name'] == 'trump'

    def test_select_style_trump_mid_range(self, service):
        """Test trump style in mid-range."""
        result = service.select_style(95.5)
        assert result['style_name'] == 'trump'

    # Test Hason style (70-89)
    def test_select_style_hason_upper_boundary(self, service):
        """Test hason style at upper boundary."""
        result = service.select_style(89)
        assert result['style_name'] == 'hason'

    def test_select_style_hason_lower_boundary(self, service):
        """Test hason style at lower boundary."""
        result = service.select_style(70)
        assert result['style_name'] == 'hason'

    def test_select_style_hason_mid_range(self, service):
        """Test hason style in mid-range."""
        result = service.select_style(80)
        assert result['style_name'] == 'hason'
        assert 'witty' in result['style_description'].lower() or 'humor' in result['style_description'].lower()

    # Test Constructive style (55-69)
    def test_select_style_constructive_upper_boundary(self, service):
        """Test constructive style at upper boundary."""
        result = service.select_style(69)
        assert result['style_name'] == 'constructive'

    def test_select_style_constructive_lower_boundary(self, service):
        """Test constructive style at lower boundary."""
        result = service.select_style(55)
        assert result['style_name'] == 'constructive'

    def test_select_style_constructive_mid_range(self, service):
        """Test constructive style in mid-range."""
        result = service.select_style(62)
        assert result['style_name'] == 'constructive'
        assert 'helpful' in result['style_description'].lower() or 'encouraging' in result['style_description'].lower()

    # Test Amsalem style (0-54)
    def test_select_style_amsalem_upper_boundary(self, service):
        """Test amsalem style at upper boundary."""
        result = service.select_style(54)
        assert result['style_name'] == 'amsalem'

    def test_select_style_amsalem_zero(self, service):
        """Test amsalem style at zero."""
        result = service.select_style(0)
        assert result['style_name'] == 'amsalem'

    def test_select_style_amsalem_mid_range(self, service):
        """Test amsalem style in mid-range."""
        result = service.select_style(30)
        assert result['style_name'] == 'amsalem'
        assert 'brash' in result['style_description'].lower() or 'confrontational' in result['style_description'].lower()

    # Test boundary transitions
    def test_boundary_89_to_90(self, service):
        """Test transition from hason to trump."""
        result_89 = service.select_style(89)
        result_90 = service.select_style(90)
        assert result_89['style_name'] == 'hason'
        assert result_90['style_name'] == 'trump'

    def test_boundary_69_to_70(self, service):
        """Test transition from constructive to hason."""
        result_69 = service.select_style(69)
        result_70 = service.select_style(70)
        assert result_69['style_name'] == 'constructive'
        assert result_70['style_name'] == 'hason'

    def test_boundary_54_to_55(self, service):
        """Test transition from amsalem to constructive."""
        result_54 = service.select_style(54)
        result_55 = service.select_style(55)
        assert result_54['style_name'] == 'amsalem'
        assert result_55['style_name'] == 'constructive'

    # Test output format
    def test_output_format(self, service):
        """Test that output contains all required fields."""
        result = service.select_style(85)
        assert 'style_name' in result
        assert 'style_description' in result
        assert 'prompt_template' in result
        assert isinstance(result['style_name'], str)
        assert isinstance(result['style_description'], str)
        assert isinstance(result['prompt_template'], str)

    def test_prompt_contains_grade(self, service):
        """Test that prompt template contains the grade value."""
        grade = 75
        result = service.select_style(grade)
        assert str(grade) in result['prompt_template']

    # Test process method (main interface)
    def test_process_method(self, service):
        """Test the process method with input dictionary."""
        input_data = {"grade": 85}
        result = service.process(input_data)
        assert result['style_name'] == 'hason'

    def test_process_method_missing_grade(self, service):
        """Test process method with missing grade field."""
        with pytest.raises(ValueError, match="must contain 'grade'"):
            service.process({})

    # Test error handling
    def test_invalid_grade_negative(self, service):
        """Test that negative grades raise ValueError."""
        with pytest.raises(ValueError, match="between 0 and 100"):
            service.select_style(-1)

    def test_invalid_grade_above_100(self, service):
        """Test that grades above 100 raise ValueError."""
        with pytest.raises(ValueError, match="between 0 and 100"):
            service.select_style(101)

    def test_invalid_grade_type_string(self, service):
        """Test that string grades raise ValueError."""
        with pytest.raises(ValueError, match="must be a number"):
            service.select_style("85")

    def test_invalid_grade_type_none(self, service):
        """Test that None grade raises ValueError."""
        with pytest.raises(ValueError, match="must be a number"):
            service.select_style(None)

    # Test floating point grades
    def test_floating_point_grade(self, service):
        """Test that floating point grades work correctly."""
        result = service.select_style(89.9)
        assert result['style_name'] == 'hason'

    def test_floating_point_grade_boundary(self, service):
        """Test floating point at exact boundary."""
        result = service.select_style(90.0)
        assert result['style_name'] == 'trump'

    # Test all styles are loaded
    def test_all_styles_loaded(self, service):
        """Test that all four styles are loaded."""
        style_names = [style['name'] for style in service.styles]
        assert 'trump' in style_names
        assert 'hason' in style_names
        assert 'constructive' in style_names
        assert 'amsalem' in style_names

    def test_styles_have_required_fields(self, service):
        """Test that all styles have required fields."""
        for style in service.styles:
            assert 'name' in style
            assert 'grade_range' in style
            assert 'description' in style
            assert 'prompt' in style
            assert len(style['grade_range']) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
