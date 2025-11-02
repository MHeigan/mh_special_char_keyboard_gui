#!/usr/bin/env bash
set -e
git init
git checkout -b main || git branch -M main
git add -A
git commit -m "Initial commit: mh_special_char_keyboard 1.0.0 (MIT)"
echo
echo "To add a remote and push:"
echo "  git remote add origin https://github.com/<youruser>/mh_special_char_keyboard.git"
echo "  git push -u origin main"
