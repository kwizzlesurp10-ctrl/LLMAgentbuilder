#!/bin/bash
# Test script using mock API key for testing purposes

# Set mock API key for testing
export ANTHROPIC_API_KEY="sk-ant-test-mock-key-for-testing-purposes-1234567890abcdef"

echo "Using mock API key for testing: $ANTHROPIC_API_KEY"
echo "Running main.py with mock key..."
echo ""

# Run the main script
python main.py

echo ""
echo "Note: This mock key is for testing code structure only."
echo "It will not work for actual Anthropic API calls."
echo "Replace with your real API key for production use."

