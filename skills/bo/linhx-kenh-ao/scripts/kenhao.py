#!/usr/bin/env python3
"""Điểm vào CLI: python scripts/kenhao.py --home <thư mục kênh> <lệnh> ..."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kenhao.cli import main  # noqa: E402

main()
