"""Demos of ixdat, grouped like ixdat itself into readers, calculators and techniques.

Each demo module has loader functions which return the demo's ixdat objects, an
``EXAMPLES`` dictionary of these loaders, and a ``main()`` which plots the results.
Most demos read data from the folder given by :func:`get_demo_data_dir`.
"""

from .demo_tools import get_demo_data_dir, get_test_data_dir, view_tables  # noqa
