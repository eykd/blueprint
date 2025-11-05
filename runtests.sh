#!/bin/sh
set -e
set -x

## Automatically reformat code, but ignore breakpoint() and commented code:
uv run ruff check --fix --unsafe-fixes --ignore T100  --ignore ERA001
uv run ruff format
uv run mypy src tests
uv run  \
   pytest \
   -vv \
   --new-first \
   --exitfirst \
   --disable-warnings \
   --capture=no \
   -m "not slow" \
   "$@"
