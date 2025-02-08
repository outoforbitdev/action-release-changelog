#!/usr/bin/env sh

python --version | head -n 1 | grep 3.12.9
if [ -e create_release.py ]; then
    echo "create_release.py exists"
else
    exit 1
fi
python -m pip list | grep PyGithub