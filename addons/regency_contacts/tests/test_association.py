from odoo.tests import tagged, TransactionCase, Form

from ..models.const import HOTEL_GROUP, MANAGEMENT_GROUP, HOTEL, CONTACT


@tagged('regency', 'regency_contacts')
class TestAssociation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.hotel_group = cls.env['res.partner'].create({
            'name': 'Test',
            'entity_type': HOTEL_GROUP,
        })
        cls.management_group = cls.env['res.partner'].create({
            'name': 'Test',
            'entity_type': MANAGEMENT_GROUP,
        })

    def test_inverse_partners(self):
        assoc_id = self.env['customer.association'].create({
            'left_partner_id': self.hotel_group.id,
            'right_partner_id': self.management_group.id,
            'association_type_id': self.env.ref('regency_contacts.hotel_group_to_management_group').id,
        })
        self.assertEqual(2, len(assoc_id.partner_ids.ids))
        self.assertEqual(self.management_group.id, assoc_id.right_partner_id.id)
        self.assertEqual(self.hotel_group.id, assoc_id.left_partner_id.id)

    def test_association_form(self):
        with Form(self.env['customer.association'].with_context(default_left_partner_id=self.hotel_group)) as form:
            form.association_type_id = self.env.ref('regency_contacts.hotel_group_to_management_group')
            form.right_partner_id = self.management_group
            assoc_id = form.save()
            self.assertEqual(2, len(assoc_id.partner_ids.ids))
            self.assertEqual(self.management_group.id, assoc_id.right_partner_id.id)
            self.assertEqual(self.hotel_group.id, assoc_id.left_partner_id.id)

    def test_hotel_ids_right(self):
        hotel = self.env['res.partner'].create({
            'name': 'Test',
            'entity_type': HOTEL,
        })
        self.env['customer.association'].create({
            'left_partner_id': self.management_group.id,
            'right_partner_id': hotel.id,
            'association_type_id': self.env.ref('regency_contacts.management_group_to_hotel').id,
        })
        self.assertEqual(1, len(self.management_group.hotel_ids.ids))
        self.assertEqual(hotel.id, self.management_group.hotel_ids[0].id)

    def test_hotel_ids_left(self):
        hotel = self.env['res.partner'].create({
            'name': 'Test',
            'entity_type': HOTEL,
        })
        contact = self.env['res.partner'].create({
            'name': 'Test',
            'entity_type': CONTACT,
        })
        self.env['customer.association'].create({
            'left_partner_id': hotel.id,
            'right_partner_id': contact.id,
            'association_type_id': self.env.ref('regency_contacts.hotel_to_contact').id,
        })
        self.assertEqual(1, len(contact.hotel_ids.ids))
        self.assertEqual(hotel.id, contact.hotel_ids[0].id)
