#!/bin/bash

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: ./git-commit.sh \"commit message\"" >&2
  exit 1
fi

COMMIT_MESSAGE="$1"

git add .
git commit -m "$COMMIT_MESSAGE"
./git-push-current.sh
