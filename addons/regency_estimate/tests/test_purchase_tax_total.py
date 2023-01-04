# -*- coding: utf-8 -*-
from odoo.addons.account.tests.test_invoice_tax_totals import TestTaxTotals
from odoo.tests import tagged

PRODUCT_QTY = 2
PRICE_UNIT = 10
FEE_VALUE = 7
TAX_AMOUNT = 21


@tagged('all_run')
class PurchaseTestTaxTotals(TestTaxTotals):

    def setUp(self):
        super(PurchaseTestTaxTotals, self).setUp()
        self.po_product = self.env['product.product'].create({
            'name': 'Bag',
            'type': 'product',
        })

        self.percent_tax_1 = self.env['account.tax'].create({
            'name': '21%',
            'amount_type': 'percent',
            'amount': TAX_AMOUNT,
            'sequence': 10,
        })

        self.fee_value_abs_vals = {
            'fee_type_id': self.env.ref('regency_estimate.fee_type_freight').id,
            'per_item': False,
            'value': FEE_VALUE,
        }

        self.pol_vals = {
                'name': 'test Bag',
                'product_id': self.po_product.id,
                'product_qty': PRODUCT_QTY,
                'price_unit': PRICE_UNIT,
                'taxes_id': [(6, 0, self.percent_tax_1.ids)],
            }

    # TODO tests for taxes in case of discount should be added
    def test_01_taxes_on_purchase_order_creation(self):
        self.pol_vals.update({'fee_value_ids': [(0, 0, self.fee_value_abs_vals)]})
        purchase_order_1 = self.env['purchase.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [(0, 0, self.pol_vals)],
        })
        self.assertEqual(FEE_VALUE, purchase_order_1.order_line.fee)
        self.assertEqual(PRODUCT_QTY * PRICE_UNIT + FEE_VALUE, purchase_order_1.order_line.price_subtotal)
        pol_price_total_tax_included = (PRODUCT_QTY * PRICE_UNIT + FEE_VALUE) * (1 + TAX_AMOUNT/100)
        self.assertEqual(pol_price_total_tax_included, purchase_order_1.order_line.price_total)
        self.assertEqual(pol_price_total_tax_included, purchase_order_1.amount_total)

    def test_02_taxes_when_fee_add_after_creation(self):
        purchase_order_1 = self.env['purchase.order'].create({
            'partner_id': self.partner_a.id,
            'order_line': [(0, 0, self.pol_vals)],
        })
        purchase_order_1.order_line.write({'fee_value_ids': [(0, 0, self.fee_value_abs_vals)]})
        self.assertEqual(FEE_VALUE, purchase_order_1.order_line.fee)
        self.assertEqual(PRODUCT_QTY * PRICE_UNIT + FEE_VALUE, purchase_order_1.order_line.price_subtotal)
        pol_price_total_tax_included = (PRODUCT_QTY * PRICE_UNIT + FEE_VALUE) * (1 + TAX_AMOUNT/100)
        self.assertEqual(pol_price_total_tax_included, purchase_order_1.order_line.price_total)
        self.assertEqual(pol_price_total_tax_included, purchase_order_1.amount_total)


