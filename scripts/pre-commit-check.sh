#!/bin/bash
# Pre-commit hook to check for exposed API keys

# Keywords to search for
KEYWORDS="sk-ant- hf_"

# Check staged files
FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$FILES" ]; then
    exit 0
fi

FOUND_KEYS=0

for FILE in $FILES; do
    # Skip check for specific files and directories
    if [[ "$FILE" == ".env.example" || 
          "$FILE" == "scripts/pre-commit-check.sh" || 
          "$FILE" == "GEMINI.md" || 
          "$FILE" == "README.md" || 
          "$FILE" == "scripts/test_with_mock_key.sh" ||
          "$FILE" == "scripts/setup_hf_space.py" ||
          "$FILE" == generated_agents/* ]]; then
        continue
    fi

    # Check for potential keys (longer sequences)
    # sk-ant-: starts with sk-ant- followed by characters
    # hf_: starts with hf_ followed by characters
    # We use -E for extended regex
    if grep -q -E "sk-ant-[a-zA-Z0-9]{10,}|hf_[a-zA-Z0-9]{10,}" "$FILE"; then
        echo "ERROR: Found potential API key in '$FILE'."
        FOUND_KEYS=1
    fi
done

if [ $FOUND_KEYS -eq 1 ]; then
    echo "Commit rejected. Please remove sensitive information before committing."
    exit 1
fi

exit 0
