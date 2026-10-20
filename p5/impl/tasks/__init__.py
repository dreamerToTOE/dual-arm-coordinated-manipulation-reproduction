"""Task modules, one per plan task.  Each exposes ``run(rec)``.

They are importable as ``tasks.tNN_*`` because ``p5/impl`` is on ``sys.path``
(see ``run_all.py``); the package is deliberately namespace-only so that a
missing task shows up as ``NOT_IMPLEMENTED`` in the ledger instead of an import
error at collection time.
"""
