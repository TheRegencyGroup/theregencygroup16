from json import dumps

from markupsafe import Markup
from odoo import api, models
from odoo.http import request
from odoo.osv import expression


class Website(models.Model):
    _inherit = 'website'

    def sale_product_domain(self):
        domain = super().sale_product_domain()
        return expression.AND([domain, [('is_fit_for_overlay', '=', 'True')]])

    def _header_preloaded_data(self):
        self.ensure_one()
        user_id = self.env['res.users'].browse(self.env.uid)
        hotel_id = user_id._active_hotel_id()
        data = {
            'active_hotel_id': hotel_id.id if hotel_id else False,
            'hotel_ids': user_id.hotel_ids.read(['id', 'name']),
        }
        return data

    @api.model
    def _header_preloaded(self):
        website = request and request.website_routing
        if website:
            data = self.env['website'].browse(website)._header_preloaded_data()
        else:
            data = False
        return Markup(dumps(data))
