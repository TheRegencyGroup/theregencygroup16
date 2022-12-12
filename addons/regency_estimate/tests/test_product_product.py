from datetime import timedelta

from odoo.fields import Datetime
from odoo.tests import tagged, TransactionCase, Form


@tagged('regency', 'regency_estimate')
class TestProductVariant(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_template = cls.env['product.template'].create({'name': 'Test Product'})
        cls.product_variant = cls.env['product.product'].create({'product_tmpl_id': cls.product_template.id, 'name': 'test variantйцуйу'})
        cls.vendor = cls.env['res.partner'].create({'name': 'Test Vendor', 'is_company': False})
        # cls.purchase_order1 = cls.env['purchase.order'].create({'product_id': cls.product_variant.id,
        #                                                        'partner_id': cls.vendor.id,
        #                                                         'state': 'purchase',
        #                                                         'invoice_status': 'invoiced',
        #                                                         'receipt_status': 'full',
        #                                                         'date_approve': Datetime.now() - timedelta(days=1)
        #                                                         })
        # cls.purchase_order2 = cls.env['purchase.order'].create({'product_id': cls.product_variant.id,
        #                                                         'partner_id': cls.vendor.id,
        #                                                         'state': 'purchase',
        #                                                         'date_approve': Datetime.now()
        #                                                         })

    def test_last_po_date(self):
        # purchase_order = self.purchase_order1
        product_variant = self.product_variant
        # self.assertEqual(product_variant.last_purchase_order_date, purchase_order.date_approve)
