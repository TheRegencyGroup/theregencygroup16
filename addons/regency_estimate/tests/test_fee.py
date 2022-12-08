from odoo.addons.purchase_requisition.tests.common import TestPurchaseRequisitionCommon
from odoo.tests import TransactionCase


class TestFee(TestPurchaseRequisitionCommon):

    def setUp(self):
        self.psl = self.env['product.price.sheet.line'].create({
            'vendor_price': 33,
            'product_id': self.product_09.id,
            'min_quantity': 10,
            'unit_price': 50,
            'price': 75,
            'total': 75 * 10
        })
        self.ps = self.env['product.price.sheet'].create({
            'name': 'Test PS',
            'item_ids': self.psl,
        })
        self.fee_value_per_item = self.env['fee.value'].create({
            'fee_type_id': self.env.ref('regency_estimate.fee_type_die_plate').id,
            'per_item': True,
            'value': 1.5,
            'price_sheet_line_id': self.psl.id
        })
        self.fee_value_percent = self.env['fee.value'].create({
            'fee_type_id': self.env.ref('regency_estimate.fee_type_foil_plate').id,
            'per_item': False,
            'percent_value': 5,
            'value': self.psl.min_quantity * self.psl.price * 5 / 100,
            'price_sheet_line_id': self.psl.id
        })
        self.fee_value_abs = self.env['fee.value'].create({
            'fee_type_id': self.env.ref('regency_estimate.fee_type_freight').id,
            'per_item': False,
            'value': 7,
            'price_sheet_line_id': self.psl.id
        })

    # def test_compute_fee(self):
    #     self.assertEqual(self.fee_value_per_item.value, 1.5)  # 1.5
    #     self.assertEqual(self.fee_value_percent.value, 10 * 75 * 5 / 100)  # 37.5
    #     self.assertEqual(self.fee_value_abs.value, 7)  # 7
    #     self.assertEqual(self.psl.fee, (1.5 * 10) + (75 * 10 * 5 / 100) + 7)  # 59.5
    #     self.assertEqual(self.psl.total, 59.5 + 10 * 75)  # 809.5
    #     self.assertEqual(self.psl.price, 75)

    def test_change_price(self):
        self.assertEqual(self.fee_value_per_item.value, 1.5)  # 1.5
        self.assertEqual(self.fee_value_percent.value, 10 * 75 * 5 / 100)  # 37.5
        self.assertEqual(self.fee_value_abs.value, 7)  # 7

        self.psl.write({'price': 72})

        self.assertEqual(self.psl.fee, (1.5 * 10) + (72 * 10 * 5 / 100) + 7)  # 58
        self.assertEqual(self.psl.total, 58 + 10 * 72)

        self.psl.onchange_total()

        self.assertEqual(self.psl.price, 72)
        self.assertEqual(self.fee_value_per_item.value, 1.5)  # 1.5
        self.assertEqual(self.fee_value_percent.value, 10 * 72 * 5 / 100)  # 36
        self.assertEqual(self.fee_value_abs.value, 7)  # 7

    def test_change_qty(self):
        self.assertEqual(self.fee_value_per_item.value, 1.5)  # 1.5
        self.assertEqual(self.fee_value_percent.value, 10 * 75 * 5 / 100)  # 37.5
        self.assertEqual(self.fee_value_abs.value, 7)  # 7

        self.psl.write({'min_quantity': 20})

        self.assertEqual(self.psl.fee, (1.5 * 20) + (75 * 20 * 5 / 100) + 7)  # 112
        self.assertEqual(self.psl.total, 112 + 20 * 75)

        self.psl.onchange_total()

        self.assertEqual(self.psl.price, 75)
        self.assertEqual(self.fee_value_per_item.value, 1.5)  # 1.5
        self.assertEqual(self.fee_value_percent.value, 20 * 75 * 5 / 100)  # 75
        self.assertEqual(self.fee_value_abs.value, 7)  # 7




