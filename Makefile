# Verification contract — see code/VERIFY.md G5.
# T0-only stub: no test suite exists yet. Syntax-check is the honest floor —
# promote to real pytest coverage incrementally, don't leave this as the ceiling.
# NOTE (postproc-tests Loop 4a): test/ now has a pytest suite, but it is
# deliberately red until Loop 4b lands src/cli/sheet_qc.py (TDD). Wiring
# pytest into verify-fast/verify-full is T6's job, done once the suite is
# green — see .loop/postproc-tests/.
PY := /mnt/workspace/.venv/bin/python3

verify-fast:
	$(PY) -m compileall -q .

verify-full:
	$(PY) -m compileall -q .

.PHONY: verify-fast verify-full
