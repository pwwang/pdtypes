"""Monkey-patch data frame formatter to
1. add dtypes next to column names when printing
2. collapse data frames when they are elements of a parent data frame.
"""
from .patching import patch, unpatch

__version__ = "0.3.0"

patch()
