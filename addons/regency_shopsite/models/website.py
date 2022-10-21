import json

from markupsafe import Markup
from odoo import api, fields, models
from odoo.http import request
from odoo.osv import expression


class Website(models.Model):
    _inherit = 'website'

    def sale_product_domain(self):
        domain = super(Website, self).sale_product_domain()
        only_item_domain = expression.AND([domain, [('is_fit_for_overlay', '=', 'True')]])
        return only_item_domain

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
