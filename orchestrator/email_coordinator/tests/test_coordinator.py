"""
Tests for Email Coordinator
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestEmailCoordinator:
    """Tests for EmailCoordinator class."""
    
    @pytest.fixture
    def mock_config(self, tmp_path):
        """Create a mock config file."""
        config_content = """
coordinator:
  name: email_coordinator
  version: "1.0.0"
children:
  email_reader: "./email_reader"
  draft_manager: "./draft_manager"
logging:
  level: DEBUG
  file: "./logs/test.log"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        return str(config_file)
    
    def test_initialization(self, mock_config):
        """Test coordinator initializes without errors."""
        with patch('email_coordinator.coordinator.EmailReaderManager', None):
            with patch('email_coordinator.coordinator.DraftManager', None):
                from email_coordinator.coordinator import EmailCoordinator
                coordinator = EmailCoordinator(config_path=mock_config)
                assert coordinator is not None
    
    def test_health_check(self, mock_config):
        """Test health check returns correct structure."""
        with patch('email_coordinator.coordinator.EmailReaderManager', None):
            with patch('email_coordinator.coordinator.DraftManager', None):
                from email_coordinator.coordinator import EmailCoordinator
                coordinator = EmailCoordinator(config_path=mock_config)
                
                health = coordinator.health_check()
                
                assert 'coordinator' in health
                assert 'status' in health
                assert 'children' in health
                assert health['coordinator'] == 'email_coordinator'
    
    def test_read_emails_without_reader(self, mock_config):
        """Test read_emails handles missing reader gracefully."""
        with patch('email_coordinator.coordinator.EmailReaderManager', None):
            with patch('email_coordinator.coordinator.DraftManager', None):
                from email_coordinator.coordinator import EmailCoordinator
                coordinator = EmailCoordinator(config_path=mock_config)
                
                result = coordinator.read_emails(mode="test", batch_size=1)
                
                assert result['status'] == 'failed'
                assert 'error' in result
    
    def test_create_drafts_without_manager(self, mock_config):
        """Test create_drafts handles missing manager gracefully."""
        with patch('email_coordinator.coordinator.EmailReaderManager', None):
            with patch('email_coordinator.coordinator.DraftManager', None):
                from email_coordinator.coordinator import EmailCoordinator
                coordinator = EmailCoordinator(config_path=mock_config)
                
                result = coordinator.create_drafts([], [])
                
                assert result['status'] == 'failed'
                assert 'error' in result
    
    def test_process_read_emails_action(self, mock_config):
        """Test process method with read_emails action."""
        with patch('email_coordinator.coordinator.EmailReaderManager', None):
            with patch('email_coordinator.coordinator.DraftManager', None):
                from email_coordinator.coordinator import EmailCoordinator
                coordinator = EmailCoordinator(config_path=mock_config)
                
                result = coordinator.process({
                    'action': 'read_emails',
                    'mode': 'test',
                    'batch_size': 1
                })
                
                assert 'status' in result
    
    def test_process_unknown_action(self, mock_config):
        """Test process method with unknown action."""
        with patch('email_coordinator.coordinator.EmailReaderManager', None):
            with patch('email_coordinator.coordinator.DraftManager', None):
                from email_coordinator.coordinator import EmailCoordinator
                coordinator = EmailCoordinator(config_path=mock_config)
                
                result = coordinator.process({'action': 'unknown_action'})
                
                assert result['status'] == 'failed'
                assert 'Unknown action' in result['error']
