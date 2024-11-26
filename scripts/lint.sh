#!/usr/bin/env bash

set -ex

uv run mypy clios
uv run ruff check clios tests examples
uv run ruff format --check clios tests examples
