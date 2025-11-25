#!/bin/bash

# Step 1: Stage all changes
git add .

# Step 2: Commit with a message (use argument or default)
commit_message=${1:-"changes"}
git commit -m "$commit_message"

# Step 3: Push to the current branch
git push
