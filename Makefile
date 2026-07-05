# Verification contract — see code/VERIFY.md G5.
# T0-only stub: no test suite exists yet. Syntax-check is the honest floor —
# promote to real pytest coverage incrementally, don't leave this as the ceiling.
PY := /mnt/workspace/.venv/bin/python3

verify-fast:
	$(PY) -m compileall -q .

verify-full:
	$(PY) -m compileall -q .

.PHONY: verify-fast verify-full
