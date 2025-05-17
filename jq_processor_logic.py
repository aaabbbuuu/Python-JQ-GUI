import subprocess
from typing import Tuple, Optional

class JQProcessorError(Exception):
    """Custom exception for JQ processing errors."""
    pass

class JQProcessorLogic:
    def __init__(self):
        self._check_jq_installed()

    def _check_jq_installed(self) -> None:
        """Checks if jq is installed and executable."""
        try:
            process = subprocess.Popen(['jq', '--version'],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       text=True)
            _, stderr = process.communicate(timeout=5) # Add timeout
            if process.returncode != 0:
                raise JQProcessorError(f"jq command error: {stderr.strip()}")
        except FileNotFoundError:
            raise JQProcessorError("jq command not found. Please ensure jq is installed and in your PATH.")
        except subprocess.TimeoutExpired:
            raise JQProcessorError("Timeout while checking jq version.")
        except Exception as e:
            raise JQProcessorError(f"An unexpected error occurred while checking for jq: {e}")

    def process_json(self, json_input: str, jq_expr: str) -> str:
        """
        Processes the given JSON input string with the JQ expression.

        Args:
            json_input: The JSON string to process.
            jq_expr: The JQ expression to apply.

        Returns:
            The processed output string from JQ.

        Raises:
            JQProcessorError: If JQ processing fails or JQ is not found.
        """
        if not jq_expr:
            raise JQProcessorError("JQ expression cannot be empty.")
        if not json_input:
            # JQ can handle empty input with certain filters           
            raise JQProcessorError("JSON input cannot be empty.")
            pass


        try:
            process = subprocess.Popen(['jq', jq_expr],
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       text=True,
                                       encoding='utf-8')
            stdout, stderr = process.communicate(json_input, timeout=15)

            if process.returncode != 0:
                error_message = f"JQ processing error (exit code {process.returncode})"
                if stderr:
                    error_message += f":\n{stderr.strip()}"
                else: 
                    # Try to get some output from stdout if any
                    error_message += f".\nOutput (if any):\n{stdout.strip()}"
                raise JQProcessorError(error_message)
            return stdout.strip()

        except FileNotFoundError:
            # Ideally caught by _check_jq_installed, but as a fallback:
            raise JQProcessorError("jq command not found. Please ensure jq is installed and in your PATH.")
        except subprocess.TimeoutExpired:
            raise JQProcessorError(f"JQ processing timed out for expression: {jq_expr}")
        except Exception as e:
            raise JQProcessorError(f"An unexpected error occurred during JQ processing: {e}")