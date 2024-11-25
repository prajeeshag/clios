#!/bin/bash

set -ex

mypy clios
ruff check clios tests examples
ruff format --check clios tests examples
