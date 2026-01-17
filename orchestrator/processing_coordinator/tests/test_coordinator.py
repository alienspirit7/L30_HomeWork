"""
Tests for Processing Coordinator
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestProcessingCoordinator:
    """Tests for ProcessingCoordinator class."""
    
    @pytest.fixture
    def mock_config(self, tmp_path):
        """Create a mock config file."""
        config_content = """
coordinator:
  name: processing_coordinator
  version: "1.0.0"
children:
  grade_manager: "./grade_manager"
  feedback_manager: "./feedback_manager"
logging:
  level: DEBUG
  file: "./logs/test.log"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        return str(config_file)
    
    def test_initialization(self, mock_config):
        """Test coordinator initializes without errors."""
        with patch('processing_coordinator.coordinator.GradeManagerService', None):
            with patch('processing_coordinator.coordinator.FeedbackManager', None):
                from processing_coordinator.coordinator import ProcessingCoordinator
                coordinator = ProcessingCoordinator(config_path=mock_config)
                assert coordinator is not None
    
    def test_health_check(self, mock_config):
        """Test health check returns correct structure."""
        with patch('processing_coordinator.coordinator.GradeManagerService', None):
            with patch('processing_coordinator.coordinator.FeedbackManager', None):
                from processing_coordinator.coordinator import ProcessingCoordinator
                coordinator = ProcessingCoordinator(config_path=mock_config)
                
                health = coordinator.health_check()
                
                assert 'coordinator' in health
                assert 'status' in health
                assert 'children' in health
                assert health['coordinator'] == 'processing_coordinator'
    
    def test_grade_without_manager(self, mock_config):
        """Test grade handles missing manager gracefully."""
        with patch('processing_coordinator.coordinator.GradeManagerService', None):
            with patch('processing_coordinator.coordinator.FeedbackManager', None):
                from processing_coordinator.coordinator import ProcessingCoordinator
                coordinator = ProcessingCoordinator(config_path=mock_config)
                
                result = coordinator.grade([])
                
                assert result['status'] == 'failed'
                assert 'error' in result
    
    def test_generate_feedback_without_manager(self, mock_config):
        """Test generate_feedback handles missing manager gracefully."""
        with patch('processing_coordinator.coordinator.GradeManagerService', None):
            with patch('processing_coordinator.coordinator.FeedbackManager', None):
                from processing_coordinator.coordinator import ProcessingCoordinator
                coordinator = ProcessingCoordinator(config_path=mock_config)
                
                result = coordinator.generate_feedback([])
                
                assert result['status'] == 'failed'
                assert 'error' in result
    
    def test_process_grade_action(self, mock_config):
        """Test process method with grade action."""
        with patch('processing_coordinator.coordinator.GradeManagerService', None):
            with patch('processing_coordinator.coordinator.FeedbackManager', None):
                from processing_coordinator.coordinator import ProcessingCoordinator
                coordinator = ProcessingCoordinator(config_path=mock_config)
                
                result = coordinator.process({
                    'action': 'grade',
                    'email_records': []
                })
                
                assert 'status' in result
    
    def test_process_unknown_action(self, mock_config):
        """Test process method with unknown action."""
        with patch('processing_coordinator.coordinator.GradeManagerService', None):
            with patch('processing_coordinator.coordinator.FeedbackManager', None):
                from processing_coordinator.coordinator import ProcessingCoordinator
                coordinator = ProcessingCoordinator(config_path=mock_config)
                
                result = coordinator.process({'action': 'unknown_action'})
                
                assert result['status'] == 'failed'
                assert 'Unknown action' in result['error']
