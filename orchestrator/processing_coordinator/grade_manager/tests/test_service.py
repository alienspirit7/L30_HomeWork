"""
Tests for Grade Manager Service
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestGradeManagerService:
    """Tests for GradeManagerService class."""
    
    @pytest.fixture
    def mock_config(self, tmp_path):
        """Create a mock config file."""
        config_content = """
manager:
  name: grade_manager
  version: "1.0.0"
children:
  github_cloner: "./github_cloner"
  python_analyzer: "./python_analyzer"
output:
  file_path: "./data/output/file_2_3.xlsx"
parallelism:
  max_workers: 2
cleanup:
  delete_repos_after_grading: true
logging:
  level: DEBUG
  file: "./logs/test.log"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        return str(config_file)
    
    def test_initialization(self, mock_config):
        """Test service initializes without errors."""
        with patch('service.GitHubClonerService', None):
            with patch('service.PythonAnalyzerService', None):
                from service import GradeManagerService
                service = GradeManagerService(config_path=mock_config)
                assert service is not None
    
    def test_health_check(self, mock_config):
        """Test health check returns correct structure."""
        with patch('service.GitHubClonerService', None):
            with patch('service.PythonAnalyzerService', None):
                from service import GradeManagerService
                service = GradeManagerService(config_path=mock_config)
                
                health = service.health_check()
                
                assert 'manager' in health
                assert 'status' in health
                assert 'children' in health
                assert health['manager'] == 'grade_manager'
    
    def test_grade_single_repository_missing_url(self, mock_config):
        """Test grade_single_repository handles missing URL."""
        with patch('service.GitHubClonerService', None):
            with patch('service.PythonAnalyzerService', None):
                from service import GradeManagerService
                service = GradeManagerService(config_path=mock_config)
                
                result = service.grade_single_repository({
                    'email_id': 'test123',
                    'repo_url': ''
                })
                
                assert result['status'] == 'Failed'
                assert 'Missing repo_url' in result['error']
    
    def test_grade_single_repository_no_cloner(self, mock_config):
        """Test grade_single_repository handles missing cloner service."""
        with patch('service.GitHubClonerService', None):
            with patch('service.PythonAnalyzerService', None):
                from service import GradeManagerService
                service = GradeManagerService(config_path=mock_config)
                
                result = service.grade_single_repository({
                    'email_id': 'test123',
                    'repo_url': 'https://github.com/user/repo.git'
                })
                
                assert result['status'] == 'Failed'
                assert 'not available' in result['error']
    
    def test_process_empty_records(self, mock_config):
        """Test process handles empty email records."""
        with patch('service.GitHubClonerService', None):
            with patch('service.PythonAnalyzerService', None):
                from service import GradeManagerService
                service = GradeManagerService(config_path=mock_config)
                
                result = service.process({'email_records': []})
                
                assert result['grades'] == []
                assert result['graded_count'] == 0
                assert result['failed_count'] == 0
    
    def test_process_filters_ready_records(self, mock_config):
        """Test process filters to only Ready records."""
        with patch('service.GitHubClonerService', None):
            with patch('service.PythonAnalyzerService', None):
                from service import GradeManagerService
                service = GradeManagerService(config_path=mock_config)
                
                records = [
                    {'email_id': '1', 'repo_url': 'url1', 'status': 'Ready'},
                    {'email_id': '2', 'repo_url': '', 'status': 'Missing: repo_url'},
                    {'email_id': '3', 'repo_url': 'url3', 'status': 'Ready'},
                ]
                
                result = service.process({'email_records': records})
                
                # Only 2 Ready records should be processed
                assert len(result['grades']) == 2
