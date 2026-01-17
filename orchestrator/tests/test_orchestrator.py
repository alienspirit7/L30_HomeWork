"""
Tests for Orchestrator
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestOrchestrator:
    """Tests for Orchestrator class."""
    
    @pytest.fixture
    def mock_config(self, tmp_path):
        """Create a mock config file."""
        config_content = """
orchestrator:
  name: homework_grading_orchestrator
  version: "1.0.0"
modes:
  test:
    batch_size: 1
  batch:
    max_batch_size: 100
    default_batch_size: 10
  full:
    process_all: true
children:
  email_coordinator: "./email_coordinator"
  processing_coordinator: "./processing_coordinator"
logging:
  level: DEBUG
  file: "./logs/test.log"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        return str(config_file)
    
    def test_initialization(self, mock_config):
        """Test orchestrator initializes without errors."""
        with patch('main.EmailCoordinator', None):
            with patch('main.ProcessingCoordinator', None):
                from main import Orchestrator
                orchestrator = Orchestrator(config_path=mock_config)
                assert orchestrator is not None
    
    def test_set_mode_test(self, mock_config):
        """Test set_mode configures test mode correctly."""
        with patch('main.EmailCoordinator', None):
            with patch('main.ProcessingCoordinator', None):
                from main import Orchestrator
                orchestrator = Orchestrator(config_path=mock_config)
                
                orchestrator.set_mode('test')
                
                assert orchestrator.current_mode == 'test'
                assert orchestrator.batch_size == 1
    
    def test_set_mode_batch(self, mock_config):
        """Test set_mode configures batch mode correctly."""
        with patch('main.EmailCoordinator', None):
            with patch('main.ProcessingCoordinator', None):
                from main import Orchestrator
                orchestrator = Orchestrator(config_path=mock_config)
                
                orchestrator.set_mode('batch', 25)
                
                assert orchestrator.current_mode == 'batch'
                assert orchestrator.batch_size == 25
    
    def test_set_mode_full(self, mock_config):
        """Test set_mode configures full mode correctly."""
        with patch('main.EmailCoordinator', None):
            with patch('main.ProcessingCoordinator', None):
                from main import Orchestrator
                orchestrator = Orchestrator(config_path=mock_config)
                
                orchestrator.set_mode('full')
                
                assert orchestrator.current_mode == 'full'
                assert orchestrator.batch_size == 1000
    
    def test_health_check(self, mock_config):
        """Test health check returns correct structure."""
        with patch('main.EmailCoordinator', None):
            with patch('main.ProcessingCoordinator', None):
                from main import Orchestrator
                orchestrator = Orchestrator(config_path=mock_config)
                
                health = orchestrator.health_check()
                
                assert 'orchestrator' in health
                assert 'status' in health
                assert 'children' in health
                assert health['status'] == 'healthy'
    
    def test_reset(self, mock_config):
        """Test reset clears all cached data."""
        with patch('main.EmailCoordinator', None):
            with patch('main.ProcessingCoordinator', None):
                from main import Orchestrator
                orchestrator = Orchestrator(config_path=mock_config)
                
                # Add some data
                orchestrator.email_records = [{'test': 'data'}]
                orchestrator.grade_records = [{'test': 'data'}]
                orchestrator.feedback_records = [{'test': 'data'}]
                
                orchestrator.reset()
                
                assert orchestrator.email_records == []
                assert orchestrator.grade_records == []
                assert orchestrator.feedback_records == []
    
    def test_step1_without_coordinator(self, mock_config):
        """Test step1 handles missing coordinator gracefully."""
        with patch('main.EmailCoordinator', None):
            with patch('main.ProcessingCoordinator', None):
                from main import Orchestrator
                orchestrator = Orchestrator(config_path=mock_config)
                
                result = orchestrator.step1_search_emails()
                
                assert result['status'] == 'failed'
                assert 'not available' in result['error']
    
    def test_step2_without_records(self, mock_config):
        """Test step2 handles missing email records."""
        with patch('main.EmailCoordinator', None):
            with patch('main.ProcessingCoordinator', None):
                from main import Orchestrator
                orchestrator = Orchestrator(config_path=mock_config)
                # Mock processing_coordinator exists but email_records empty
                orchestrator.processing_coordinator = Mock()
                
                result = orchestrator.step2_clone_and_grade()
                
                assert result['status'] == 'failed'
                assert 'No email records' in result['error']
