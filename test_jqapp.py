import unittest
from unittest.mock import patch, MagicMock, ANY
from jq_processor_logic import JQProcessorLogic, JQProcessorError
import subprocess 

class TestJQProcessorLogic(unittest.TestCase):

    @patch('subprocess.Popen')
    def setUp(self, mock_popen_init):
        init_process_mock = MagicMock()
        init_process_mock.communicate.return_value = ('jq-1.6', '') 
        init_process_mock.returncode = 0
        mock_popen_init.return_value = init_process_mock
        
        self.logic = JQProcessorLogic()

    @patch('subprocess.Popen')
    def test_process_valid_json_and_expr(self, mock_popen):
        process_mock = MagicMock()
        process_mock.communicate.return_value = ('"data"', '') 
        process_mock.returncode = 0
        mock_popen.return_value = process_mock

        result = self.logic.process_json('{"test": "data"}', '.test')
        self.assertEqual(result, '"data"')
        mock_popen.assert_called_once_with(
            ['jq', '.test'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        process_mock.communicate.assert_called_once_with('{"test": "data"}', timeout=15)

    @patch('subprocess.Popen')
    def test_process_jq_error_stderr(self, mock_popen):
        process_mock = MagicMock()
        jq_error_output = "jq: error: test/0 is not defined at <top-level>, line 1:\n.test\njq: 1 compile error"
        process_mock.communicate.return_value = ('', jq_error_output)
        process_mock.returncode = 5 
        mock_popen.return_value = process_mock

        print(f"\n[DEBUG test_process_jq_error_stderr] mock_popen.return_value.returncode: {mock_popen.return_value.returncode}")
        print(f"[DEBUG test_process_jq_error_stderr] process_mock.returncode: {process_mock.returncode}")

        expected_regex = r"(?s)JQ processing error \(exit code 5\):.*jq: \d+ compile error"
        with self.assertRaisesRegex(JQProcessorError, expected_regex):
            self.logic.process_json('{"test": "data"}', '.test | invalid_func')

        
        mock_popen.assert_called_once()
        # Ensure communicate was called with the correct input
        process_mock.communicate.assert_called_once_with('{"test": "data"}', timeout=15)


    @patch('subprocess.Popen')
    def test_process_jq_error_exit_code_no_stderr(self, mock_popen):
        process_mock = MagicMock()
        process_mock.communicate.return_value = ('some output', '')
        process_mock.returncode = 3
        mock_popen.return_value = process_mock

        print(f"\n[DEBUG test_process_jq_error_exit_code_no_stderr] mock_popen.return_value.returncode: {mock_popen.return_value.returncode}")
        print(f"[DEBUG test_process_jq_error_exit_code_no_stderr] process_mock.returncode: {process_mock.returncode}")

        with self.assertRaisesRegex(JQProcessorError, r"JQ processing error \(exit code 3\).*\nOutput \(if any\):\nsome output"):
            self.logic.process_json('{"test": "data"}', '.foo')
        
        mock_popen.assert_called_once()
        process_mock.communicate.assert_called_once_with('{"test": "data"}', timeout=15)

    @patch('subprocess.Popen')
    def test_process_empty_json_input(self, mock_popen):        
        process_mock = MagicMock()
        process_mock.communicate.return_value = ('null', '')
        process_mock.returncode = 0
        mock_popen.return_value = process_mock

        result = self.logic.process_json('', 'empty')
        self.assertEqual(result, 'null')


    @patch('subprocess.Popen')
    def test_jq_not_found_at_processing(self, mock_popen):
        mock_popen.side_effect = FileNotFoundError("jq not found")
        
        with self.assertRaisesRegex(JQProcessorError, "jq command not found"):
            self.logic.process_json('{"a":1}', '.')

    @patch('subprocess.Popen')
    def test_jq_version_check_fails_filenotfound(self, mock_popen_init):
        mock_popen_init.side_effect = FileNotFoundError
        with self.assertRaisesRegex(JQProcessorError, "jq command not found"):
            JQProcessorLogic()

    @patch('subprocess.Popen')
    def test_jq_version_check_fails_returncode(self, mock_popen_init):
        init_process_mock = MagicMock()
        init_process_mock.communicate.return_value = ('', 'Some error from jq --version')
        init_process_mock.returncode = 1
        mock_popen_init.return_value = init_process_mock
        with self.assertRaisesRegex(JQProcessorError, "jq command error: Some error from jq --version"):
            JQProcessorLogic()

    @patch('subprocess.Popen')
    def test_jq_processing_timeout(self, mock_popen):
        process_mock = MagicMock()
        process_mock.communicate.side_effect = subprocess.TimeoutExpired(cmd="jq", timeout=0.1)
        mock_popen.return_value = process_mock

        with self.assertRaisesRegex(JQProcessorError, "JQ processing timed out for expression: ."):
            self.logic.process_json('{"test": "data"}', '.')


if __name__ == '__main__':
    unittest.main()