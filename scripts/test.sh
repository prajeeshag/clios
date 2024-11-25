#!/bin/bash

set -ex

pytest --cov --cov-report=term ${@}
