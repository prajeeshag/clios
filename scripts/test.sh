#!/usr/bin/env bash

set -ex

uv run pytest --cov --cov-report=term ${@}
