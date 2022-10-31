import json

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
        hotel_id = self.env.user._active_hotel_id()
        data = {
            'activeHotel': hotel_id.id if hotel_id else False,
            'hotels': self.env.user.hotel_ids.mapped(
                lambda h: {field: h[field] for field in ['id', 'name', 'logo_url']}
            ),
        }
        return data

    def get_active_hotel_background_url(self):
        self.env.user._active_hotel_id()

    @api.model
    def _header_preloaded(self):
        website = request and request.website_routing
        if website:
            data = self.env['website'].browse(website)._header_preloaded_data()
        else:
            data = False
        return Markup(json.dumps(data))

    @api.model
    def _get_cart_data(self, preloaded=False):
        if self.env.user._is_public():
            return None

        order = request.website.sale_get_order()
        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()

        cart_data = {
            'lineList': order.website_order_line.read(['id'])
        }

        if preloaded:
            return Markup(json.dumps(cart_data))

        return cart_data
