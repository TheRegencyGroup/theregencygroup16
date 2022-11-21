from odoo.tests import tagged, TransactionCase
from odoo.exceptions import ValidationError, MissingError
from psycopg2.errors import ForeignKeyViolation


@tagged('all_run')
class TestOverlayTemplateArchivingDeletion(TransactionCase):

    def setUp(self):
        self.product = self.env['product.template'].create({'name': 'Test Product'})
        self.overlay_position = self.browse_ref('regency_shopsite.overlay_position_front')
        self.overlay_template = self.env['overlay.template'].create({
            'name': 'Test Overlay',
            'overlay_position_ids': [self.overlay_position.id],
            'product_template_id': self.product.id,
        })

    def test_01_1_success_deletion_if_has_not_product_template(self):
        self.overlay_template.unlink()
        with self.assertRaises(MissingError):
            self.overlay_template.mapped('name')

    def test_01_2_success_archiving_if_has_not_product_template(self):
        self.overlay_template.active = False
        self.assertFalse(self.overlay_template.active)

    def test_02_1_restrict_deletion_if_has_archived_product_template(self):
        self.overlay_product = self.env['overlay.product'].create({
            'overlay_template_id': self.overlay_template.id,
        })
        self.overlay_product.active = False
        with self.assertRaises(ForeignKeyViolation):
            self.overlay_template.unlink()

    def test_02_1_allow_archiving_if_has_archived_product_template(self):
        self.overlay_product = self.env['overlay.product'].create({
            'overlay_template_id': self.overlay_template.id,
        })
        self.overlay_product.active = False
        self.overlay_template.active = False
        self.assertFalse(self.overlay_template.active)

    def test_03_1_restrict_deletion_if_has_active_product_template(self):
        self.overlay_product = self.env['overlay.product'].create({
            'overlay_template_id': self.overlay_template.id,
        })
        with self.assertRaises(ValidationError):
            self.overlay_template.unlink()

    def test_03_2_restrict_archiving_if_has_active_product_template(self):
        self.overlay_product = self.env['overlay.product'].create({
            'overlay_template_id': self.overlay_template.id,
        })
        with self.assertRaises(ValidationError):
            self.overlay_template.active = False


