from odoo.tests import tagged, TransactionCase


@tagged('all_run')
class TestRun(TransactionCase):

    def test_01(self):
        self.assertEqual(1, 2)
