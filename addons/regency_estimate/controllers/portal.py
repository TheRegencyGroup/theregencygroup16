import binascii
import json
from functools import partial
from odoo.tools import formatLang

from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.sale_management.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager
from odoo.addons.portal.controllers.mail import _message_post_helper

from odoo import fields, http, SUPERUSER_ID, _, Command


class CustomerPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        PriceSheet = request.env['product.price.sheet']
        if 'price_sheets_count' in counters:
            values['price_sheets_count'] = PriceSheet.search_count(self._prepare_price_sheets_domain(partner)) \
                if PriceSheet.check_access_rights('read', raise_exception=False) else 0

        return values

    def _prepare_price_sheets_domain(self, partner):
        return [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
        ]

    def _get_price_sheets_searchbar_sortings(self):
        return {
            'date': {'label': _('Create Date'), 'order': 'create_date desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

    def _get_portal_price_sheet_details(self, order_sudo, order_line=False):
        currency = order_sudo.currency_id
        format_price = partial(formatLang, request.env, digits=currency.decimal_places)
        results = {
            'order_amount_total': format_price(order_sudo.amount_total),
            'order_amount_untaxed': format_price(order_sudo.amount_untaxed),
            'order_amount_tax': format_price(order_sudo.amount_tax),
            'order_amount_undiscounted': format_price(order_sudo.amount_total),
        }
        if order_line:
            results.update({
                'order_line_product_uom_qty': str(order_line.product_uom_qty),
                'order_line_price_total': format_price(order_line.price_total),
                'order_line_price_subtotal': format_price(order_line.price_subtotal)
            })
            try:
                results['order_totals_table'] = request.env['ir.ui.view']._render_template(
                    'regency_estimate.price_sheet_portal_content_totals_table', {'price_sheet': order_sudo})
            except ValueError:
                pass

        return results

    @http.route(['/my/price_sheets/<int:order_id>/update_line_dict'], type='json', auth="public", website=True)
    def update_price_sheet_line_dict(self, line_id, remove=False, unlink=False, order_id=None, access_token=None,
                         input_quantity=False, **kwargs):
        """
            Overridden method for adding custom logic
        """
        try:
            order_sudo = self._document_check_access('product.price.sheet', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if order_sudo.state not in ('draft', 'confirmed'):
            return False
        order_line = request.env['product.price.sheet.line'].sudo().browse(int(line_id))
        if order_line.price_sheet_id != order_sudo:
            return False

        if input_quantity is not False:
            quantity = input_quantity
        else:
            number = -1 if remove else 1
            quantity = order_line.product_uom_qty + number

        # START OF CUSTOM LOGIC
        if quantity < order_line.min_quantity and remove:
            quantity = 0
        else:
            quantity = min(max(quantity, order_line.min_quantity), order_line.max_quantity)
        # END OF CUSTOM LOGIC
        if unlink:  # or quantity <= 0:  # CUSTOM LOGIC
            order_line.unlink()
            results = self._get_portal_price_sheet_details(order_sudo)
            results.update({
                'unlink': True,
                'price_sheet_template': request.env['ir.ui.view']._render_template('regency_estimate.price_sheet_portal_content', {
                    'product_price_sheet': order_sudo,
                    'report_type': "html"
                }),
            })
            return results

        order_line.write({'product_uom_qty': quantity})
        results = self._get_portal_price_sheet_details(order_sudo, order_line)

        return results

    @http.route(['/my/price_sheets/<int:order_id>/update_line_type'], type='json', auth="public", website=True)
    def update_price_sheet_line_type(self, line_id, order_id=None, consumption_type=False, access_token=None, **kwargs):
        """
            Overridden method for adding custom logic
        """
        try:
            order_sudo = self._document_check_access('product.price.sheet', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if order_sudo.state not in ('draft', 'confirmed'):
            return False
        order_line = request.env['product.price.sheet.line'].sudo().browse(int(line_id))
        if order_line.price_sheet_id != order_sudo:
            return False

        if consumption_type is not False:
            order_line.write({'consumption_type': consumption_type})

        results = self._get_portal_price_sheet_details(order_sudo, order_line)

        return results

    @http.route(['/my/price_sheets', '/my/price_sheets/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_price_sheets(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        PriceSheets = request.env['product.price.sheet']

        domain = self._prepare_price_sheets_domain(partner)

        searchbar_sortings = self._get_price_sheets_searchbar_sortings()

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        price_sheets_count = PriceSheets.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/price_sheets",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=price_sheets_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        price_sheets = PriceSheets.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_price_sheets_history'] = price_sheets.ids[:100]

        values.update({
            'date': date_begin,
            'price_sheets': price_sheets.sudo(),
            'page_name': 'price_sheet',
            'pager': pager,
            'default_url': '/my/price_sheets',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("regency_estimate.portal_my_price_sheets", values)

    @http.route(['/my/price_sheets/<int:order_id>'], type='http', auth="public", website=True)
    def portal_price_sheet_page(self, order_id, report_type=None, access_token=None, message=False, download=False,
                                **kw):
        try:
            order_sudo = self._document_check_access('product.price.sheet', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # TODO: add report later

        # if report_type in ('html', 'pdf', 'text'):
        #     return self._show_report(model=order_sudo, report_type=report_type,
        #                              report_ref='sale.action_report_saleorder', download=download)

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        # Log only once a day
        if order_sudo:
            # store the date as a string in the session to allow serialization
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_price_sheet_%s' % order_sudo.id)
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_price_sheet_%s' % order_sudo.id] = now
                body = _('Price Sheet viewed by customer %s', order_sudo.partner_id.name)
                _message_post_helper(
                    "product.price.sheet",
                    order_sudo.id,
                    body,
                    token=order_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=order_sudo.user_id.sudo().partner_id.ids,
                )

        values = {
            'price_sheet': order_sudo,
            'message': message,
            'token': access_token,
            'landing_route': '/shop/payment/validate',
            'bootstrap_formatting': True,
            'partner_id': order_sudo.partner_id.id,
            'report_type': 'html',
            'action': order_sudo._get_portal_return_action(),
        }

        history = request.session.get('my_price_sheets_history', [])

        values.update(get_records_pager(history, order_sudo))

        return request.render('regency_estimate.price_sheet_portal_template', values)

    @http.route(['/my/price_sheets/<int:order_id>/accept'], type='json', auth="public", website=True)
    def portal_price_sheets_accept(self, order_id, access_token=None, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            order_sudo = self._document_check_access('product.price.sheet', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}

        # START OF CUSOM LOGIC
        # split quotation on CA and Sales Order
        consumption_lines = order_sudo.item_ids.filtered(lambda l: l.consumption_type == 'consumption')
        consumption = False
        if consumption_lines:
            consumption = request.env['consumption.agreement'].create({'partner_id': order_sudo.partner_id.id,
                                                                       'access_token': order_sudo.access_token,
                                                                       'line_ids': [Command.create({
                                                                           'product_id': l.product_id.id,
                                                                           'qty_allowed': l.product_uom_qty,
                                                                           'price_unit': l.price_unit
                                                                       }) for l in consumption_lines.sorted('sequence')]
                                                                       })
            consumption_lines.unlink()
        if not order_sudo.item_ids.filtered(lambda l: not l.display_type).exists() and consumption:
            order_sudo.action_cancel()
            order_sudo.unlink()
            order_sudo = consumption
        # END OF CUSTOM LOGIC

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
            # request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}

        if not order_sudo.has_to_be_paid():
            order_sudo.action_confirm()
            order_sudo._send_order_confirmation_mail()

        # START CUSTOM LOGIC
        if order_sudo._name == 'sale.order':
            pdf = \
            request.env.ref('sale.action_report_saleorder').with_user(SUPERUSER_ID)._render_qweb_pdf([order_sudo.id])[
                0]

            _message_post_helper(
                'sale.order', order_sudo.id, _('Order signed by %s') % (name,),
                attachments=[('%s.pdf' % order_sudo.name, pdf)],
                **({'token': access_token} if access_token else {}))
        else:
            # TODO: add consumption pdf
            _message_post_helper(
                'consumption.agreement', order_sudo.id, _('Order signed by %s') % (name,),
                # attachments = [('%s.pdf' % order_sudo.name, pdf)],
                **({'token': access_token} if access_token else {}))
        # END CUSTOM LOGIC

        query_string = '&message=sign_ok'
        # START CUSTOM LOGIC
        if consumption:
            url = consumption.get_portal_url()
            query_string += f'&new_consumption={consumption.name}&consumption_url={url}'
        # END CUSTOM LOGIC
        if order_sudo.has_to_be_paid(True):
            query_string += '#allow_payment=yes'
        return {
            'force_refresh': True,
            'redirect_url': order_sudo.get_portal_url(query_string=query_string),
        }

    @http.route(['/my/price_sheets/<int:order_id>/decline'], type='http', auth="public", methods=['POST'], website=True)
    def price_sheet_decline(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('product.price.sheet', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        message = post.get('decline_message')

        query_string = False
        if order_sudo.has_to_be_signed() and message:
            order_sudo.action_cancel()
            _message_post_helper('product.price.sheet', order_id, message,
                                 **{'token': access_token} if access_token else {})
        else:
            query_string = "&message=cant_reject"

        return request.redirect(order_sudo.get_portal_url(query_string=query_string))

    @http.route(['/my/price_sheets/<int:order_id>/create_sale_order'], type='json', auth="public", website=True)
    def create_sale_order_from_price_sheet(self, order_id, access_token=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            order_sudo = self._document_check_access('product.price.sheet', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}

        lines_to_order = order_sudo.item_ids.filtered(lambda l: l.product_uom_qty > 0 and
                                                          l.consumption_type == 'dropship')
        if not lines_to_order:
            return {'error': _('Select at least one line.')}

        sale_order = order_sudo.create_sale_order(lines_to_order)

        query_string = f'&comeback_url_caption={order_sudo.name}&comeback_url={order_sudo.get_portal_url()}'

        return {
            'force_refresh': True,
            'redirect_url': sale_order.get_portal_url(query_string=query_string)
        }

    @http.route(['/my/price_sheets/<int:order_id>/create_consumption_agreement'], type='json', auth="public", website=True)
    def create_consumption_from_price_sheet(self, order_id, access_token=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            order_sudo = self._document_check_access('product.price.sheet', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}

        lines_to_order = order_sudo.item_ids.filtered(lambda l: l.product_uom_qty > 0 and
                                                          l.consumption_type == 'consumption')
        if not lines_to_order:
            return {'error': _('Select at least one line.')}

        consumption = order_sudo.create_consumption_agreement(lines_to_order)

        query_string = f'&comeback_url_caption={order_sudo.name}&comeback_url={order_sudo.get_portal_url()}'

        return {
            'force_refresh': True,
            'redirect_url': consumption.get_portal_url(query_string=query_string)
        }

    @http.route('/requisition/get/<int:prl_id>', type='http', auth='public')
    def get_requisition_id(self, prl_id):
        purchase_requisition_line_id = request.env['purchase.requisition.line'].browse(prl_id)
        purchase_requisition_id = purchase_requisition_line_id.requisition_id.id
        return request.make_response(json.dumps({'pr_id': purchase_requisition_id}))
