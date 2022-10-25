from odoo import models, fields
from odoo.http import request


class ResUsers(models.Model):
    _inherit = 'res.users'

    hotel_ids = fields.Many2many(related='partner_id.hotel_ids')

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
