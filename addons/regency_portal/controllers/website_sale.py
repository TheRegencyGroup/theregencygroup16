from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import pager as portal_pager


class RegencyCustomerPortal(CustomerPortal):

    def _prepare_all_orders_domain(self, partner):
        return [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sent', 'sale', 'done'])
        ]

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        SaleOrder = request.env['sale.order']
        if 'all_orders_count' in counters:
            values['all_orders_count'] = SaleOrder.search_count(self._prepare_all_orders_domain(partner)) \
                if SaleOrder.check_access_rights('read', raise_exception=False) else 0

        return values

    def _prepare_sale_portal_rendering_values_all_orders(self, page=1, date_begin=None, date_end=None, sortby=None,
                                                         **kwargs):
        SaleOrder = request.env['sale.order']

        url = '/my/all_orders'

        if not sortby:
            sortby = 'date'

        partner = request.env.user.partner_id
        values = self._prepare_portal_layout_values()

        domain = self._prepare_all_orders_domain(partner)

        searchbar_sortings = self._get_sale_searchbar_sortings()

        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        pager_values = portal_pager(
            url=url,
            total=SaleOrder.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
        )
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager_values['offset'])

        values.update({
            'date': date_begin,
            'orders': orders.sudo(),
            'page_name': 'all_orders',
            'pager': pager_values,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return values

    @http.route(['/my/all_orders', '/my/all_orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_all_orders(self, **kwargs):
        values = self._prepare_sale_portal_rendering_values_all_orders(**kwargs)
        return request.render("regency_portal.portal_my_all_orders", values)

