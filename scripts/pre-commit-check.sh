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
    # Skip check for .env.example, pre-commit-check.sh, and generated_agents directory
    if [[ "$FILE" == ".env.example" || "$FILE" == "scripts/pre-commit-check.sh" || "$FILE" == generated_agents/* ]]; then
        continue
    fi

    for KEYWORD in $KEYWORDS; do
        if grep -q "$KEYWORD" "$FILE"; then
            echo "ERROR: Found potential API key or sensitive keyword '$KEYWORD' in '$FILE'."
            FOUND_KEYS=1
        fi
    done
done

if [ $FOUND_KEYS -eq 1 ]; then
    echo "Commit rejected. Please remove sensitive information before committing."
    exit 1
fi

exit 0
