from odoo.addons.purchase_requisition.tests.common import TestPurchaseRequisitionCommon


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

    def test_compute_fee(self):
        self.assertEqual(1.5, self.fee_value_per_item.value)  # 1.5
        self.assertEqual(10 * 75 * 5 / 100, self.fee_value_percent.value)  # 37.5
        self.assertEqual(7, self.fee_value_abs.value)  # 7
        self.assertEqual(1.5 * 10 + 75 * 10 * 5 / 100 + 7, self.psl.fee)  # 59.5
        self.assertEqual(59.5 + 10 * 75, self.psl.total)  # 809.5
        self.assertEqual(75, self.psl.price)

    def test_change_fee(self):
        self.fee_value_percent.write({'percent_value': 6})
        self.fee_value_abs.write({'value': 8})
        self.fee_value_per_item.write({'value': 2})

        self.assertEqual(2 * 10 + 75 * 10 * 6 / 100 + 8, self.psl.fee)  # 73
        self.assertEqual(73 + 10 * 75, self.psl.total)  # 823

    def test_change_price(self):
        self.assertEqual(1.5, self.fee_value_per_item.value)  # 1.5
        self.assertEqual(10 * 75 * 5 / 100, self.fee_value_percent.value)  # 37.5
        self.assertEqual(7, self.fee_value_abs.value)  # 7

        self.psl.write({'price': 72})

        self.assertEqual(1.5 * 10 + 72 * 10 * 5 / 100 + 7, self.psl.fee)  # 58
        self.assertEqual(58 + 10 * 72, self.psl.total)

        self.psl.onchange_total()

        self.assertEqual(72, self.psl.price)
        self.assertEqual(1.5, self.fee_value_per_item.value)  # 1.5
        self.assertEqual(10 * 72 * 5 / 100, self.fee_value_percent.value)  # 36
        self.assertEqual(7, self.fee_value_abs.value)  # 7

    def test_change_qty(self):
        self.assertEqual(1.5, self.fee_value_per_item.value)  # 1.5
        self.assertEqual(10 * 75 * 5 / 100, self.fee_value_percent.value)  # 37.5
        self.assertEqual(7, self.fee_value_abs.value)  # 7

        self.psl.write({'min_quantity': 20})

        self.assertEqual(1.5 * 20 + 75 * 20 * 5 / 100 + 7, self.psl.fee)  # 112
        self.assertEqual(112 + 20 * 75, self.psl.total)

        self.psl.onchange_total()

        self.assertEqual(75, self.psl.price)
        self.assertEqual(1.5, self.fee_value_per_item.value)  # 1.5
        self.assertEqual(20 * 75 * 5 / 100, self.fee_value_percent.value)  # 75
        self.assertEqual(7, self.fee_value_abs.value)  # 7
