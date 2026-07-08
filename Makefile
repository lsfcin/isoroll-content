# Verification contract — see code/VERIFY.md G5.
# postproc-tests Loop 4b: sheet_qc.py landed, full pytest suite is green —
# pytest is now wired into both gates below (T6).
PY := /mnt/workspace/.venv/bin/python3

verify-fast:
	$(PY) -m compileall -q .
	$(PY) -m pytest test/ -q

verify-full:
	$(PY) -m compileall -q .
	$(PY) -m pytest test/ -q

.PHONY: verify-fast verify-full
