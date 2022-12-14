import binascii

from odoo import fields, http, SUPERUSER_ID, _
from odoo.http import request

from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.addons.portal.controllers.mail import _message_post_helper


class CustomerPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        Consumption = request.env['consumption.agreement']
        if 'consumptions_count' in counters:
            values['consumptions_count'] = Consumption.search_count(self._prepare_consumptions_domain(partner)) \
                if Consumption.check_access_rights('read', raise_exception=False) else 0

        return values


    def _prepare_consumptions_domain(self, partner):
        return [
            '|', ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
        ]

    def _get_consumption_searchbar_sortings(self):
        return {
            'date': {'label': _('Signed Date'), 'order': 'signed_date desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

    @http.route(['/my/consumptions', '/my/consumptions/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_consumptions(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        Consumption = request.env['consumption.agreement']

        domain = self._prepare_consumptions_domain(partner)

        searchbar_sortings = self._get_consumption_searchbar_sortings()

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        consumptions_count = Consumption.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/consumptions",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=consumptions_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        consumptions = Consumption.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_consumptions_history'] = consumptions.ids[:100]

        values.update({
            'date': date_begin,
            'consumptions': consumptions.sudo(),
            'page_name': 'consumption',
            'pager': pager,
            'default_url': '/my/consumptions',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("consumption_agreement.portal_my_consumptions", values)

    @http.route(['/my/consumptions/<int:order_id>'], type='http', auth="public", website=True)
    def portal_consumption_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access('consumption.agreement', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        #TODO: add report later

        # if report_type in ('html', 'pdf', 'text'):
        #     return self._show_report(model=order_sudo, report_type=report_type,
        #                              report_ref='sale.action_report_saleorder', download=download)

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        # Log only once a day
        if order_sudo:
            # store the date as a string in the session to allow serialization
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_consumption_%s' % order_sudo.id)
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_consumption_%s' % order_sudo.id] = now
                body = _('Consumption viewed by customer %s', order_sudo.partner_id.name)
                _message_post_helper(
                    "consumption.agreement",
                    order_sudo.id,
                    body,
                    token=order_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=order_sudo.sudo().partner_id.ids,
                )

        values = {
            'consumption': order_sudo,
            'message': message,
            'token': access_token,
            'landing_route': '/shop/payment/validate',
            'bootstrap_formatting': True,
            'partner_id': order_sudo.partner_id.id,
            'report_type': 'html',
            'action': order_sudo._get_portal_return_action(),
        }

        history = request.session.get('my_consumptions_history', [])

        values.update(get_records_pager(history, order_sudo))

        return request.render('consumption_agreement.consumption_portal_template', values)

    @http.route(['/my/consumptions/<int:order_id>/accept'], type='json', auth="public", website=True)
    def portal_consumption_accept(self, order_id, access_token=None, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            order_sudo = self._document_check_access('consumption.agreement', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}

        if not order_sudo.has_to_be_signed():
            return {'error': _('The order is not in a state requiring customer signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            order_sudo.write({
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
                'signature': signature,
            })
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}

        order_sudo.action_confirm()

        #TODO: add report

        # pdf = request.env.ref('consumption_agreement.action_report_consumption').with_user(SUPERUSER_ID)._render_qweb_pdf([order_sudo.id])[
        #     0]

        _message_post_helper(
            'consumption.agreement', order_sudo.id, _('Order signed by %s') % (name,),
            #attachments=[('%s.pdf' % order_sudo.name, pdf)],
            **({'token': access_token} if access_token else {}))

        query_string = '&message=sign_ok'
        return {
            'force_refresh': True,
            'redirect_url': order_sudo.get_portal_url(query_string=query_string),
        }

    @http.route(['/my/consumptions/<int:order_id>/decline'], type='http', auth="public", methods=['POST'], website=True)
    def decline(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('consumption.agreement', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        message = post.get('decline_message')

        query_string = False
        if order_sudo.has_to_be_signed() and message:
            order_sudo.action_cancel()
            _message_post_helper('consumption.agreement', order_id, message, **{'token': access_token} if access_token else {})
        else:
            query_string = "&message=cant_reject"

        return request.redirect(order_sudo.get_portal_url(query_string=query_string))

    @http.route(['/my/consumptions/<int:order_id>/create_sale_order'], type='json', auth="public", website=True)
    def create_sale_order(self, order_id, access_token=None, selected_line_ids=[]):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            order_sudo = self._document_check_access('consumption.agreement', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}

        if not selected_line_ids:
            return {'error': _('Select at least one line.')}

        sale_order, count = order_sudo.create_sale_order([int(str_id) for str_id in selected_line_ids])
        # to make quotation visible on Portal set it Sent
        sale_order.state = 'sent'

        query_string = f'&comeback_url_caption={order_sudo.name}&comeback_url={order_sudo.get_portal_url()}'

        return {
            'force_refresh': True,
            'redirect_url': sale_order.get_portal_url(query_string=query_string)
        }
