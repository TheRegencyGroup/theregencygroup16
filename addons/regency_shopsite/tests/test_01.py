from odoo.tests import tagged, TransactionCase
from odoo import Command, fields


@tagged('all_run')
class TestPricelistItems(TransactionCase):

    def setUp(self):
        self.product = self.env['product.template'].create({'name': 'Test Product'})
        self.overlay_position = self.env.ref('regency_shopsite.overlay_position_front')
        self.overlay_template = self.env['overlay.template'].create({
            'name': 'Test Overlay',
            'overlay_position_ids': [self.overlay_position.id],
            'product_template_id': self.product.id,
        })
        self.overlay_product = self.env['overlay.product'].create({
            'overlay_template_id': self.overlay_template.id,
        })
        self.pricelist = self.env['product.pricelist'].create({
            'name': 'Test Pricelist',
            'currency_id': self.env.company.currency_id.id
        })
        self.partner = self.env.ref('base.partner_admin')
        self.partner.write({
            'property_product_pricelist': self.pricelist.id
        })

    def test_create_price_rule_from_overlay_template(self):
        """
        Creating price rules from the Overlay template [OT] (covering: Link on OT exists, new price rule object link)
        """
        self.overlay_template.price_item_ids.create({
            'pricelist_id': self.pricelist.id,
            'applied_on': '4_overlay_template',
            'overlay_tmpl_id': self.overlay_template.id,
            'min_quantity': 4,
            'fixed_price': 5.5,
        })
        self.assertEqual(len(self.pricelist.item_ids), 1)
        self.assertEqual(self.pricelist.item_ids.overlay_tmpl_id, self.overlay_template)
        self.assertEqual(len(self.overlay_template.price_item_ids), 1)
        self.assertEqual(self.overlay_template.price_item_ids.pricelist_id, self.pricelist)
        self.assertEqual(self.pricelist.item_ids.name,
                         'Shopsite Item Template: '
                         '' + self.overlay_template.product_template_id.name + ' ' + self.overlay_template.name)

    def test_create_so_use_price_rule(self):
        """
        Create SO with relevant Overlay template use Price rule for Overlay template
        """
        self.overlay_template.price_item_ids.create({
            'pricelist_id': self.pricelist.id,
            'applied_on': '4_overlay_template',
            'overlay_tmpl_id': self.overlay_template.id,
            'min_quantity': 1,
            'fixed_price': 5.5,
        })
        self.overlay_template.price_item_ids.create({
            'pricelist_id': self.pricelist.id,
            'applied_on': '4_overlay_template',
            'overlay_tmpl_id': self.overlay_template.id,
            'min_quantity': 5,
            'fixed_price': 5.2,
        })
        so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [Command.create({
                'product_uom_qty': 2,
                'product_id': self.product.product_variant_ids[0].id,
            })]
        })
        so2 = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [Command.create({
                'product_uom_qty': 6,
                'product_id': self.product.product_variant_ids[0].id,
            })]
        })
        self.assertEqual(so.order_line.price_unit, 5.5)
        self.assertEqual(so2.order_line.price_unit, 5.2)


