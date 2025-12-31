import os
import sys
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_agent_builder.agent_engine import AgentEngine, ExecutionStatus, API_KEY_ERROR_MESSAGE


class TestRefactoredHelpers(unittest.TestCase):
    """Test the refactored helper methods in AgentEngine."""

    def setUp(self):
        self.engine = AgentEngine(api_key="test_key")

    def test_check_api_key_with_key(self):
        """Test that _check_api_key returns None when API key is present."""
        result = self.engine._check_api_key(start_time=0.0)
        self.assertIsNone(result)

    def test_check_api_key_without_key(self):
        """Test that _check_api_key returns error when API key is missing."""
        engine = AgentEngine(api_key=None)
        with patch.dict(os.environ, {}, clear=True):
            result = engine._check_api_key(start_time=0.0)
            self.assertIsNotNone(result)
            self.assertEqual(result.status, ExecutionStatus.API_KEY_MISSING)
            self.assertEqual(result.error, API_KEY_ERROR_MESSAGE)

    def test_determine_source_type_path_object(self):
        """Test source type determination with Path object."""
        path = Path(__file__)
        result = self.engine._determine_source_type(path)
        self.assertTrue(result)

    def test_determine_source_type_code_string(self):
        """Test source type determination with code string."""
        code = "class Test:\n    pass"
        result = self.engine._determine_source_type(code)
        self.assertFalse(result)

    def test_determine_source_type_file_path_string(self):
        """Test source type determination with file path string."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            temp_path = f.name
        
        try:
            result = self.engine._determine_source_type(temp_path)
            self.assertTrue(result)
        finally:
            os.remove(temp_path)

    def test_determine_source_type_py_extension(self):
        """Test source type determination with .py extension."""
        result = self.engine._determine_source_type("nonexistent.py")
        self.assertTrue(result)

    def test_validate_agent_path_exists(self):
        """Test path validation with existing file."""
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            temp_path = f.name
        
        try:
            result = self.engine._validate_agent_path(temp_path, start_time=0.0)
            self.assertIsNone(result)
        finally:
            os.remove(temp_path)

    def test_validate_agent_path_not_exists(self):
        """Test path validation with non-existing file."""
        result = self.engine._validate_agent_path(
            "/nonexistent/path/to/agent.py", 
            start_time=0.0
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.status, ExecutionStatus.AGENT_NOT_FOUND)
        self.assertIn("Agent file not found", result.error)

    def test_api_key_error_message_constant(self):
        """Test that API_KEY_ERROR_MESSAGE constant is properly defined."""
        self.assertIsInstance(API_KEY_ERROR_MESSAGE, str)
        self.assertIn("GOOGLE_GEMINI_KEY", API_KEY_ERROR_MESSAGE)
        self.assertIn("HUGGINGFACEHUB_API_TOKEN", API_KEY_ERROR_MESSAGE)
        self.assertIn("GITHUB_COPILOT_TOKEN", API_KEY_ERROR_MESSAGE)


if __name__ == "__main__":
    unittest.main()
