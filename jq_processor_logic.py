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
        if not jq_expr:
            raise JQProcessorError("JQ expression cannot be empty.")

        process: Optional[subprocess.Popen] = None 
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
                    error_message += f".\nOutput (if any):\n{stdout.strip()}"
                raise JQProcessorError(error_message)
            
            return stdout.strip()

        except FileNotFoundError:
            raise JQProcessorError("jq command not found. Please ensure jq is installed and in your PATH.")
        except subprocess.TimeoutExpired:
            err_msg = f"JQ processing timed out for expression: {jq_expr}"
            if process and process.stderr:
                 err_msg += f"\nstderr from process: {process.stderr.read() if hasattr(process.stderr, 'read') else 'N/A'}"
            raise JQProcessorError(err_msg)
        except JQProcessorError:
            raise
        except Exception as e:
            raise JQProcessorError(f"An unexpected system or subprocess error occurred: {type(e).__name__}: {e}")