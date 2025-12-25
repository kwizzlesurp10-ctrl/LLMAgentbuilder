import os
import sys
import unittest
from unittest.mock import patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_agent_builder.agent_engine import AgentEngine, ExecutionStatus


class TestAgentEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AgentEngine(api_key="dummy_key")

    def test_load_agent_from_code(self):
        code = """
class TestAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def run(self, task):
        return f"Executed: {task}"
"""
        agent_class = self.engine._load_agent_from_code(code)
        self.assertIsNotNone(agent_class)
        agent = agent_class(api_key="key")
        self.assertEqual(agent.run("test"), "Executed: test")

    def test_execute_success(self):
        code = """
class TestAgent:
    def __init__(self, api_key=None):
        pass

    def run(self, task):
        return f"Echo: {task}"
"""
        result = self.engine.execute(code, "hello")
        self.assertEqual(result.status, ExecutionStatus.SUCCESS)
        self.assertEqual(result.output, "Echo: hello")

    def test_execute_with_timeout_subprocess(self):
        # This test requires the code to be runnable in a subprocess
        # We need to ensure the subprocess can import the agent
        # Since we are passing code string, AgentEngine creates a temp file

        code = """
import time
import sys
import argparse

class TestAgent:
    def __init__(self, api_key=None):
        pass

    def run(self, task):
        return f"Subprocess: {task}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    args = parser.parse_args()

    agent = TestAgent()
    print(agent.run(args.task))
"""
        result = self.engine.execute_with_timeout(code, "world")
        self.assertEqual(result.status, ExecutionStatus.SUCCESS)
        self.assertIn("Subprocess: world", result.output)

    def test_execute_timeout_failure(self):
        code = """
import time
import argparse

if __name__ == "__main__":
    time.sleep(2)
"""
        # Set short timeout
        engine = AgentEngine(api_key="dummy", timeout=1)
        result = engine.execute_with_timeout(code, "task")
        self.assertEqual(result.status, ExecutionStatus.TIMEOUT)

    def test_api_key_missing(self):
        engine = AgentEngine(api_key=None)
        # Mock env vars to be empty
        with patch.dict(os.environ, {}, clear=True):
            result = engine.execute("code", "task")
            self.assertEqual(result.status, ExecutionStatus.API_KEY_MISSING)


if __name__ == "__main__":
    unittest.main()
