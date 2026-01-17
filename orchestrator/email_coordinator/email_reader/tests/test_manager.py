"""
Tests for Email Reader Manager
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import yaml

from manager import EmailReaderManager


class TestEmailReaderManagerInitialization:
    """Test manager initialization and configuration."""

    def test_manager_creation_with_valid_config(self, test_config):
        """Test creating manager with valid configuration."""
        manager = EmailReaderManager(config_path=test_config)

        assert manager is not None
        assert manager.config is not None
        assert manager.logger is not None
        assert 'manager' in manager.config
        assert manager.config['manager']['name'] == 'email_reader'

    def test_manager_creation_with_missing_config(self, temp_dir):
        """Test creating manager with missing configuration file."""
        missing_config = temp_dir / 'missing.yaml'

        with pytest.raises(FileNotFoundError):
            EmailReaderManager(config_path=str(missing_config))

    def test_manager_creation_with_invalid_yaml(self, invalid_config):
        """Test creating manager with invalid YAML."""
        with pytest.raises(ValueError):
            EmailReaderManager(config_path=invalid_config)

    def test_config_loading(self, test_config):
        """Test configuration is loaded correctly."""
        manager = EmailReaderManager(config_path=test_config)

        assert 'children' in manager.config
        assert 'gmail_reader' in manager.config['children']
        assert 'email_parser' in manager.config['children']
        assert 'output' in manager.config
        assert 'modes' in manager.config

    def test_logging_setup(self, test_config, temp_dir):
        """Test logging is set up correctly."""
        manager = EmailReaderManager(config_path=test_config)

        assert manager.logger is not None
        assert manager.logger.name == 'email_reader'

        # Check log directory was created
        log_dir = temp_dir / 'logs'
        assert log_dir.exists()


class TestEmailReaderManagerConfiguration:
    """Test configuration handling."""

    def test_modes_configuration(self, test_config):
        """Test processing modes are configured."""
        manager = EmailReaderManager(config_path=test_config)

        modes = manager.config.get('modes', {})
        assert 'test' in modes
        assert 'batch' in modes
        assert 'full' in modes
        assert modes['test']['batch_size'] == 5
        assert modes['batch']['batch_size'] == 50
        assert modes['full']['batch_size'] == 1000

    def test_gmail_search_configuration(self, test_config):
        """Test Gmail search query is configured."""
        manager = EmailReaderManager(config_path=test_config)

        gmail_search = manager.config.get('gmail_search', {})
        assert 'query' in gmail_search
        assert 'homework' in gmail_search['query'].lower()

    def test_output_configuration(self, test_config):
        """Test output settings are configured."""
        manager = EmailReaderManager(config_path=test_config)

        output = manager.config.get('output', {})
        assert 'file_path' in output
        assert 'file_1_2.xlsx' in output['file_path']


class TestEmailReaderManagerProcessing:
    """Test email processing workflow."""

    @patch('manager.GmailReaderService')
    @patch('manager.EmailParser')
    def test_process_with_test_mode(self, mock_parser_class, mock_gmail_class,
                                   test_config, sample_raw_emails, sample_parsed_emails):
        """Test processing emails in test mode."""
        # Setup mocks
        mock_gmail = Mock()
        mock_gmail.process.return_value = {
            'emails': sample_raw_emails,
            'count': len(sample_raw_emails),
            'status': 'success'
        }
        mock_gmail_class.return_value = mock_gmail

        mock_parser = Mock()
        mock_parser.parse.side_effect = sample_parsed_emails
        mock_parser_class.return_value = mock_parser

        # Create manager and process
        manager = EmailReaderManager(config_path=test_config)
        manager.gmail_reader = mock_gmail
        manager.email_parser = mock_parser

        input_data = {'mode': 'test'}
        result = manager.process(input_data)

        # Assertions
        assert result is not None
        assert result['processed_count'] == 3
        assert result['ready_count'] == 2
        assert result['failed_count'] == 1
        assert len(result['emails']) == 3

    @patch('manager.GmailReaderService')
    @patch('manager.EmailParser')
    def test_process_with_batch_mode(self, mock_parser_class, mock_gmail_class,
                                     test_config):
        """Test processing emails in batch mode."""
        # Setup mocks
        mock_gmail = Mock()
        mock_gmail.process.return_value = {
            'emails': [],
            'count': 0,
            'status': 'success'
        }
        mock_gmail_class.return_value = mock_gmail

        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        # Create manager and process
        manager = EmailReaderManager(config_path=test_config)
        manager.gmail_reader = mock_gmail
        manager.email_parser = mock_parser

        input_data = {'mode': 'batch'}
        result = manager.process(input_data)

        # Check that batch_size from config was used
        assert mock_gmail.process.called
        call_args = mock_gmail.process.call_args[0][0]
        assert call_args['max_results'] == 50

    @patch('manager.GmailReaderService')
    @patch('manager.EmailParser')
    def test_process_with_custom_batch_size(self, mock_parser_class, mock_gmail_class,
                                           test_config):
        """Test processing with custom batch size override."""
        # Setup mocks
        mock_gmail = Mock()
        mock_gmail.process.return_value = {
            'emails': [],
            'count': 0,
            'status': 'success'
        }
        mock_gmail_class.return_value = mock_gmail

        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        # Create manager and process
        manager = EmailReaderManager(config_path=test_config)
        manager.gmail_reader = mock_gmail
        manager.email_parser = mock_parser

        input_data = {'mode': 'test', 'batch_size': 10}
        result = manager.process(input_data)

        # Check that custom batch_size was used
        call_args = mock_gmail.process.call_args[0][0]
        assert call_args['max_results'] == 10

    @patch('manager.GmailReaderService')
    @patch('manager.EmailParser')
    def test_process_with_gmail_failure(self, mock_parser_class, mock_gmail_class,
                                       test_config):
        """Test handling Gmail Reader failure."""
        # Setup mocks
        mock_gmail = Mock()
        mock_gmail.process.return_value = {
            'emails': [],
            'count': 0,
            'status': 'failed'
        }
        mock_gmail_class.return_value = mock_gmail

        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        # Create manager and process
        manager = EmailReaderManager(config_path=test_config)
        manager.gmail_reader = mock_gmail
        manager.email_parser = mock_parser

        input_data = {'mode': 'test'}
        result = manager.process(input_data)

        # Assertions
        assert result['processed_count'] == 0
        assert result['ready_count'] == 0
        assert result['failed_count'] == 0
        assert result['output_file'] is None

    @patch('manager.GmailReaderService')
    @patch('manager.EmailParser')
    def test_process_with_parser_exception(self, mock_parser_class, mock_gmail_class,
                                          test_config, sample_raw_emails):
        """Test handling Email Parser exceptions."""
        # Setup mocks
        mock_gmail = Mock()
        mock_gmail.process.return_value = {
            'emails': sample_raw_emails[:1],  # Just one email
            'count': 1,
            'status': 'success'
        }
        mock_gmail_class.return_value = mock_gmail

        mock_parser = Mock()
        mock_parser.parse.side_effect = Exception("Parser error")
        mock_parser_class.return_value = mock_parser

        # Create manager and process
        manager = EmailReaderManager(config_path=test_config)
        manager.gmail_reader = mock_gmail
        manager.email_parser = mock_parser

        input_data = {'mode': 'test'}
        result = manager.process(input_data)

        # Should handle exception gracefully
        assert result['processed_count'] == 0
        assert result['failed_count'] == 1

    def test_process_without_gmail_reader(self, test_config):
        """Test processing without Gmail Reader initialized."""
        manager = EmailReaderManager(config_path=test_config)
        manager.gmail_reader = None

        input_data = {'mode': 'test'}

        with pytest.raises(RuntimeError, match="Gmail Reader service not initialized"):
            manager.process(input_data)

    @patch('manager.GmailReaderService')
    def test_process_without_email_parser(self, mock_gmail_class,
                                         test_config, sample_raw_emails):
        """Test processing without Email Parser initialized."""
        # Setup mock
        mock_gmail = Mock()
        mock_gmail.process.return_value = {
            'emails': sample_raw_emails,
            'count': len(sample_raw_emails),
            'status': 'success'
        }
        mock_gmail_class.return_value = mock_gmail

        manager = EmailReaderManager(config_path=test_config)
        manager.gmail_reader = mock_gmail
        manager.email_parser = None

        input_data = {'mode': 'test'}

        with pytest.raises(RuntimeError, match="Email Parser service not initialized"):
            manager.process(input_data)


class TestExcelOutput:
    """Test Excel file generation."""

    @patch('manager.GmailReaderService')
    @patch('manager.EmailParser')
    @patch('manager.Workbook')
    def test_excel_output_created(self, mock_workbook_class, mock_parser_class,
                                  mock_gmail_class, test_config, sample_raw_emails,
                                  sample_parsed_emails):
        """Test that Excel file is created with correct data."""
        # Setup mocks
        mock_gmail = Mock()
        mock_gmail.process.return_value = {
            'emails': sample_raw_emails,
            'count': len(sample_raw_emails),
            'status': 'success'
        }
        mock_gmail_class.return_value = mock_gmail

        mock_parser = Mock()
        mock_parser.parse.side_effect = sample_parsed_emails
        mock_parser_class.return_value = mock_parser

        mock_wb = MagicMock()
        mock_ws = MagicMock()
        mock_wb.active = mock_ws
        mock_workbook_class.return_value = mock_wb

        # Create manager and process
        manager = EmailReaderManager(config_path=test_config)
        manager.gmail_reader = mock_gmail
        manager.email_parser = mock_parser

        input_data = {'mode': 'test'}
        result = manager.process(input_data)

        # Check Excel file was created
        assert mock_workbook_class.called
        assert mock_wb.save.called
        assert result['output_file'] is not None

    @patch('manager.GmailReaderService')
    @patch('manager.EmailParser')
    def test_excel_output_path(self, mock_parser_class, mock_gmail_class,
                               test_config, temp_dir):
        """Test that Excel file is saved to correct path."""
        # Setup mocks
        mock_gmail = Mock()
        mock_gmail.process.return_value = {
            'emails': [],
            'count': 0,
            'status': 'success'
        }
        mock_gmail_class.return_value = mock_gmail

        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        # Create manager and process
        manager = EmailReaderManager(config_path=test_config)
        manager.gmail_reader = mock_gmail
        manager.email_parser = mock_parser

        input_data = {'mode': 'test'}
        result = manager.process(input_data)

        # Check output path
        expected_path = str(temp_dir / 'output' / 'file_1_2.xlsx')
        assert result['output_file'] == expected_path

    @patch('manager.GmailReaderService')
    @patch('manager.EmailParser')
    @patch('manager.Workbook', None)
    def test_excel_output_without_openpyxl(self, mock_parser_class, mock_gmail_class,
                                           test_config, sample_raw_emails,
                                           sample_parsed_emails):
        """Test handling when openpyxl is not installed."""
        # Setup mocks
        mock_gmail = Mock()
        mock_gmail.process.return_value = {
            'emails': sample_raw_emails,
            'count': len(sample_raw_emails),
            'status': 'success'
        }
        mock_gmail_class.return_value = mock_gmail

        mock_parser = Mock()
        mock_parser.parse.side_effect = sample_parsed_emails
        mock_parser_class.return_value = mock_parser

        # Create manager and process
        manager = EmailReaderManager(config_path=test_config)
        manager.gmail_reader = mock_gmail
        manager.email_parser = mock_parser

        input_data = {'mode': 'test'}
        result = manager.process(input_data)

        # Should handle gracefully
        assert result['output_file'] is None
        assert result['processed_count'] == 3


class TestEmailReaderManagerEdgeCases:
    """Test edge cases and error handling."""

    @patch('manager.GmailReaderService')
    @patch('manager.EmailParser')
    def test_process_empty_email_list(self, mock_parser_class, mock_gmail_class,
                                      test_config):
        """Test processing when no emails are fetched."""
        # Setup mocks
        mock_gmail = Mock()
        mock_gmail.process.return_value = {
            'emails': [],
            'count': 0,
            'status': 'success'
        }
        mock_gmail_class.return_value = mock_gmail

        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser

        # Create manager and process
        manager = EmailReaderManager(config_path=test_config)
        manager.gmail_reader = mock_gmail
        manager.email_parser = mock_parser

        input_data = {'mode': 'test'}
        result = manager.process(input_data)

        # Assertions
        assert result['processed_count'] == 0
        assert result['ready_count'] == 0
        assert result['failed_count'] == 0
        assert len(result['emails']) == 0

    @patch('manager.GmailReaderService')
    @patch('manager.EmailParser')
    def test_process_all_emails_ready(self, mock_parser_class, mock_gmail_class,
                                      test_config, sample_raw_emails):
        """Test processing when all emails are ready."""
        # Setup mocks
        mock_gmail = Mock()
        mock_gmail.process.return_value = {
            'emails': sample_raw_emails[:2],  # Only ready emails
            'count': 2,
            'status': 'success'
        }
        mock_gmail_class.return_value = mock_gmail

        mock_parser = Mock()
        mock_parser.parse.side_effect = [
            {'status': 'Ready'},
            {'status': 'Ready'}
        ]
        mock_parser_class.return_value = mock_parser

        # Create manager and process
        manager = EmailReaderManager(config_path=test_config)
        manager.gmail_reader = mock_gmail
        manager.email_parser = mock_parser

        input_data = {'mode': 'test'}
        result = manager.process(input_data)

        # Assertions
        assert result['processed_count'] == 2
        assert result['ready_count'] == 2
        assert result['failed_count'] == 0

    @patch('manager.GmailReaderService')
    @patch('manager.EmailParser')
    def test_process_all_emails_failed(self, mock_parser_class, mock_gmail_class,
                                       test_config, sample_raw_emails):
        """Test processing when all emails have missing fields."""
        # Setup mocks
        mock_gmail = Mock()
        mock_gmail.process.return_value = {
            'emails': sample_raw_emails,
            'count': len(sample_raw_emails),
            'status': 'success'
        }
        mock_gmail_class.return_value = mock_gmail

        mock_parser = Mock()
        mock_parser.parse.side_effect = [
            {'status': 'Missing: repo_url'},
            {'status': 'Missing: repo_url'},
            {'status': 'Missing: repo_url'}
        ]
        mock_parser_class.return_value = mock_parser

        # Create manager and process
        manager = EmailReaderManager(config_path=test_config)
        manager.gmail_reader = mock_gmail
        manager.email_parser = mock_parser

        input_data = {'mode': 'test'}
        result = manager.process(input_data)

        # Assertions
        assert result['processed_count'] == 3
        assert result['ready_count'] == 0
        assert result['failed_count'] == 3
