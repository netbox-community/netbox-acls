from ...tables import AccessListTable

try:
    from utilities.testing import TableTestCases
except ImportError:  # NetBox < ~4.5.8 (aci's shim cites 4.5.10) ships no table-test base
    TableTestCases = None


if TableTestCases is not None:

    class AccessListTableTestCase(TableTestCases.StandardTableTestCase):
        table = AccessListTable
