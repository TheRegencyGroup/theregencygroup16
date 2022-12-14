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
                lambda h: {field: h[field] for field in ['id', 'name', 'logo_url', 'background_url']}
            ),
        }
        return data

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

    def _default_salesteam_id(self):
        team = self.env.ref('regency_shopsite.team_shopsite_department', False)
        if team and team.active:
            return team.id
        else:
            return None
            
    @api.model
    def _get_country_state_full_list_data(self):
        countries_data = [{'id': country.id,
                           'name': country.name,
                           'isStateRequired': country.state_required,
                           'hasProvince': bool(country.state_ids),
                           } for country in self.env['res.country'].search([])]
        states_data = [{'id': state.id,
                        'name': state.name,
                        'code': state.code,
                        'countryId': state.country_id.id,
                        } for state in self.env['res.country.state'].search([])]
        default_country = self.env.ref('base.us')
        return Markup(json.dumps({
            'countryList': countries_data,
            'provinceList': states_data,
            'defaultCountryId': default_country.id,
            'defaultCountryHasProvince': bool(default_country.state_ids)
        }))

    def _prepare_sale_order_values(self, partner_sudo):
        res = super()._prepare_sale_order_values(partner_sudo)
        partner_id, partner_invoice_id, partner_shipping_id = self.env.user._get_so_partners()
        res.update({
            'partner_id': partner_id.id,
            'partner_invoice_id': partner_invoice_id.id,
            'partner_shipping_id': partner_shipping_id.id
        })
        return res