from odoo import models, fields
from odoo.http import request


class ResUsers(models.Model):
    _inherit = 'res.users'

    hotel_ids = fields.Many2many('res.partner', related='partner_id.hotel_ids')

    def _active_hotel_id(self) -> object:
        self.ensure_one()
        try:
            hotel = int(request.session.get('selected_hotel'))
        except (ValueError, TypeError):
            hotel = None
        if hotel not in self.hotel_ids.ids:
            hotel = None
        if hotel:
            hotel_id = self.env['res.partner'].browse(hotel)
        elif self.hotel_ids:
            hotel_id = self.hotel_ids[0]
        else:
            hotel_id = self.env['res.partner']
        return hotel_id

    def _active_hotel_background_url(self) -> str:
        return self._active_hotel_id().background_url

    def _get_so_partners(self):
        """
        Docs:
        https://theregencygroup.atlassian.net/wiki/spaces/RAINDROP/pages/72843268/Customer+BDD
        https://app.diagrams.net/#G1H27FaUZSqMAaTDnubIw0TwnfyvU-TkTi
        """
        partner_id = self.partner_id
        parent_company_id = self.partner_id.parent_id
        if parent_company_id:
            return partner_id, parent_company_id, parent_company_id

        possible_associations = self.env.ref('regency_contacts.hotel_group_to_management_group') + self.env.ref(
            'regency_contacts.management_group_to_hotel')
        association_partner_id = self.partner_id.association_ids.filtered(
            lambda f: f.association_type_id in possible_associations)
        if len(association_partner_id) == 1:  # Correct case
            partner_invoice_id = association_partner_id
            partner_shipping_id = association_partner_id
            return partner_id, partner_invoice_id, partner_shipping_id
        else:
            # Other cases, invalid
            # For correct work return all expected vars
            return partner_id, partner_id, partner_id
