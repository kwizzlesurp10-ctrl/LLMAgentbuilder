"""
Entry point wrapper for backward compatibility.

This file imports and delegates to the main entry point in llm_agent_builder.__main__
to maintain backward compatibility with direct execution of main.py.
"""
from llm_agent_builder.__main__ import main

if __name__ == "__main__":
    main()

