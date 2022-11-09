from odoo.tests import tagged, TransactionCase
from odoo.exceptions import ValidationError, MissingError
from odoo import Command
from psycopg2.errors import ForeignKeyViolation


@tagged('all_run')
class TestOverlayProductArchivingDeletion(TransactionCase):

    def setUp(self):
        self.product = self.env['product.template'].create({'name': 'Test Product'})
        self.overlay_position = self.browse_ref('regency_shopsite.overlay_position_front')
        self.overlay_template = self.env['overlay.template'].create({
            'name': 'Test Overlay',
            'overlay_position_ids': [self.overlay_position.id],
            'product_template_id': self.product.id,
        })
        self.overlay_product = self.env['overlay.product'].create({
            'overlay_template_id': self.overlay_template.id,
        })
        self.partner = self.env.ref('base.partner_admin')

    def create_sale_order(self):
        sale_line = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [Command.create({
                'product_uom_qty': 1,
                'product_id': self.product.product_variant_ids[0].id,
            })]
        })
        return sale_line

    def test_01_1_success_deletion_if_has_no_sales(self):
        self.overlay_product.unlink()
        with self.assertRaises(MissingError):
            self.overlay_product.mapped('name')

    def test_01_2_success_archiving_if_has_no_sales(self):
        self.overlay_product.active = False
        self.assertFalse(self.overlay_product.active)

    def test_02_1_restrict_deletion_if_has_sales(self):
        self.create_sale_order()
        with self.assertRaises(ValidationError):
            self.overlay_product.unlink()

    def test_02_2_success_archiving_if_has_sales(self):
        self.create_sale_order()
        self.overlay_product.active = False
        self.assertFalse(self.overlay_product.active)
