from odoo.tests import tagged, TransactionCase, Form

from ..models.const import HOTEL_GROUP, MANAGEMENT_GROUP


@tagged('regency', 'regency_contacts')
class TestAssociation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_left = cls.env['res.partner'].create({
            'name': 'Test',
            'entity_type': HOTEL_GROUP,
        })
        cls.partner_right = cls.env['res.partner'].create({
            'name': 'Test',
            'entity_type': MANAGEMENT_GROUP,
        })

    def test_inverse_partners(self):
        assoc_id = self.env['customer.association'].create({
            'left_partner_id': self.partner_left.id,
            'right_partner_id': self.partner_right.id,
            'association_type_id': self.env.ref('regency_contacts.hotel_group_to_management_group').id,
        })
        self.assertEqual(2, len(assoc_id.partner_ids.ids))
        self.assertEqual(self.partner_right.id, assoc_id.right_partner_id.id)
        self.assertEqual(self.partner_left.id, assoc_id.left_partner_id.id)

    def test_association_form(self):
        with Form(self.env['customer.association'].with_context(default_left_partner_id=self.partner_left)) as form:
            form.association_type_id = self.env.ref('regency_contacts.hotel_group_to_management_group')
            form.right_partner_id = self.partner_right
            assoc_id = form.save()
            self.assertEqual(2, len(assoc_id.partner_ids.ids))
            self.assertEqual(self.partner_right.id, assoc_id.right_partner_id.id)
            self.assertEqual(self.partner_left.id, assoc_id.left_partner_id.id)
