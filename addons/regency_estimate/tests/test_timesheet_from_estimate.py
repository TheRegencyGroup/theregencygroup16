from odoo.addons.crm.tests import common as crm_common


class TimesheetFromEstimate(crm_common.TestCrmCommon):
    @classmethod
    def setUpClass(cls):
        super(TimesheetFromEstimate, cls).setUpClass()
        cls.stage_gen_won.generate_estimate = True
        cls.lead_1.partner_id = cls.contact_2

        cls.product_variant_1 = cls.env['product.product'].create({
            'name': 'ProductVariant1',
        })
        cls.product_variant_2 = cls.env['product.product'].create({
            'name': 'ProductVariant2',
        })
        cls.product_variant_3 = cls.env['product.product'].create({
            'name': 'ProductVariant3',
        })
        cls.product_variant_4 = cls.env['product.product'].create({
            'name': 'ProductVariant4',
        })
        cls.product_variant_5 = cls.env['product.product'].create({
            'name': 'ProductVariant5',
        })

    def test_01(self):
        self.lead_1.action_set_won()
        estimate = self.lead_1.estimate_ids
        estimate_line1 = self.env['sale.estimate.line'].create({
            'estimate_id': estimate.ids[0],
            'product_id': self.product_variant_1.id,
            'product_uom_qty': 10.0,
            'name': 'test'
        })
        estimate_line2 = self.env['sale.estimate.line'].create({
            'estimate_id': estimate.ids[0],
            'product_id': self.product_variant_2.id,
            'product_uom_qty': 10.0,
            'name': 'test'
        })
        purchase_requisition = self.env['purchase.requisition'].create({'estimate_id': estimate.id})
        estimate.product_lines.write({'selected': True})
        estimate.action_new_price_sheet()
        price_sheet = estimate.price_sheet_ids
        self.assertEqual(len(price_sheet), 1)
        self.assertEqual(len(price_sheet.item_ids), 2)
        self.assertEqual(len(estimate_line1.price_sheet_line_ids), 1)
        self.assertEqual(len(estimate_line2.price_sheet_line_ids), 1)

        purchase_requisition.write({'line_ids': [(0, 0, {
                                                    'product_id': self.product_variant_3.id,
                                                    'product_qty': 10.0,
                                                    'state': 'done',
                                                    'partner_id': self.contact_2.id,
                                                    'price_unit': 1.0}),
                                                 (0, 0, {
                                                     'product_id': self.product_variant_1.id,
                                                     'product_qty': 10.0,
                                                     'state': 'done',
                                                     'partner_id': self.contact_2.id,
                                                     'price_unit': 1.0})
                                                 ]})
        estimate.product_lines.write({'selected': True})
        estimate.action_new_price_sheet()
        self.assertEqual(len(price_sheet), 1)
        self.assertEqual(len(price_sheet.item_ids), 4)
        self.assertEqual(len(estimate.product_lines), 2)
        self.assertEqual(len(estimate_line1.price_sheet_line_ids), 2)
        self.assertEqual(len(estimate_line2.price_sheet_line_ids), 1)

        purchase_requisition.line_ids[0].write({'product_qty': 25.0})
        pr_new_line = self.env['purchase.requisition.line'].create({
            'requisition_id': purchase_requisition.id,
            'product_id': self.product_variant_5.id,
            'product_qty': 10.0,
            'state': 'done',
            'partner_id': self.contact_2.id,
            'price_unit': 1.0
        })
        estimate.product_lines.write({'selected': True})
        estimate.action_new_price_sheet()
        self.assertEqual(len(price_sheet), 1)
        self.assertEqual(len(price_sheet.item_ids), 6)
        self.assertEqual(len(estimate.product_lines), 2)
        self.assertEqual(len(purchase_requisition.line_ids), 3)

