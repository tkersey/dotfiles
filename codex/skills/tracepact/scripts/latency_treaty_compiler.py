#!/usr/bin/env python3
"""Compatibility wrapper for TracePact.

Prefer: python scripts/tracepact.py ...
"""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("tracepact.py")), run_name="__main__")
