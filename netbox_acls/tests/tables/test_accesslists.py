from utilities.testing import TableTestCases

from ...tables import AccessListTable


class AccessListTableTestCase(TableTestCases.StandardTableTestCase):
    table = AccessListTable
