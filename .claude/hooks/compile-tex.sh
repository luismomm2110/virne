#!/bin/bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ "$FILE_PATH" == *.tex ]]; then
  DIR=$(dirname "$FILE_PATH")
  cd "$DIR" || exit 0
  pdflatex -interaction=nonstopmode "$(basename "$FILE_PATH")" > /dev/null 2>&1
fi

exit 0