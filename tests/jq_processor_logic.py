import subprocess

class JQProcessorLogic:
    def process_json(self, json_input, jq_expr):
        process = subprocess.Popen(['jq', jq_expr],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)
        stdout, stderr = process.communicate(json_input)
        if stderr:
            raise Exception(stderr)
        return stdout
