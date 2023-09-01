#!/bin/bash

FILES="/path/file1"
FILES+="/path/file2"  
FILES+="/path/file3"

for f in $FILES; do
  if [ -f "$f" ]; then
    echo "Removing $f"
    rm -f "$f"
  fi
done

remaining=()
for f in $FILES; do
  if [ -f "$f" ]; then
    remaining+=("$f")
  fi
done

if [ ${#remaining[@]} -gt 0 ]; then
  echo "WARNING: Unable to clean up vulnerable files: ${remaining[@]}. Please remove manually."
fi

echo "Verification complete."
