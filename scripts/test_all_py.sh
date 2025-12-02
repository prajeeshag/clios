#!/bin/bash

set -ex

for py in 3.12 3.13; do
    echo "Testing Python $py"
    uv run --python=python$py -m pytest
done
