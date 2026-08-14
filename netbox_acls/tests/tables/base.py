"""
Shim for NetBox's table test base, which arrived in NetBox 4.5.8.

The plugin's floor is 4.5.0, so it cannot be imported unconditionally. Import this
module and subclass ``base.StandardTableTestCase``. Importing the name into a test
module instead makes the runner collect the base as a test case of its own, where its
setUpClass errors for want of a table.
"""

try:
    from utilities.testing import TableTestCases

    StandardTableTestCase = TableTestCases.StandardTableTestCase
except ImportError:  # NetBox < 4.5.8 ships no table test base
    from django.test import SimpleTestCase as StandardTableTestCase  # noqa: F401
