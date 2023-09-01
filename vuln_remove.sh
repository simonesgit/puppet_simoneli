#!/bin/bash

FILES="/path/file1" 
FILES+="/path/file2 "
FILES+="/path/file3"

for f in $FILES; do
  if [ -f "$f" ]; then
    echo "Removing $f"
    rm -f "$f" 
  fi
done

for f in $FILES; do
  if [ -f "$f" ]; then
    echo "WARNING: Unable to clean up vulnerable file $f. Please remove manually."
  fi
done

echo "Verification complete."
