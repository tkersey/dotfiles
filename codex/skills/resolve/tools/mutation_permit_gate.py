#!/usr/bin/env python3
"""Compatibility wrapper for old RGR mutation permits."""
from __future__ import annotations
import subprocess, sys
from pathlib import Path

tool = Path(__file__).with_name("compiled_delivery_permit_gate.py")
raise SystemExit(subprocess.call(["python3", str(tool), *sys.argv[1:]]))
