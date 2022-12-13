from odoo.tests import TransactionCase


class TestCreateUser(TransactionCase):
    def test_create_portal_user(self):
        """
        After creating a new Portal User its Partner Entity Type by default should be Contact
        """
        user = self.env['res.users'].create({
            'name': 'New Portal User',
            'login': 'new@portal.user',
            'groups_id': self.env.ref('base.group_portal')
        })
        self.assertEqual(user.partner_id.entity_type, 'contact')
        self.assertFalse(user.partner_id.is_company)
