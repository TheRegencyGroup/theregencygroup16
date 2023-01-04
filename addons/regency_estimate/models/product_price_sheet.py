import json
from odoo import fields, models, api, Command, _
from odoo.tools.misc import formatLang
from odoo.exceptions import AccessError
MAX_QUANTITY = 999999999999
from odoo.tools import html_keep_url
from odoo.addons.regency_tools import SystemMessages


class ProductPriceSheet(models.Model):
    _name = 'product.price.sheet'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    def _get_default_name(self):
        return self.env['ir.sequence'].next_by_code('product.price.sheet')

    def _get_default_currency_id(self):
        return self.env.company.currency_id.id

    @api.model
    def _default_note_url(self):
        return self.env.company.get_base_url()

    @api.model
    def _default_note(self):
        use_invoice_terms = self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms')
        if use_invoice_terms and self.env.company.terms_type == "html":
            baseurl = html_keep_url(self._default_note_url() + '/terms')
            return _('Terms & Conditions: %s', baseurl)
        return use_invoice_terms and self.env.company.invoice_terms or ''

    name = fields.Char('Pricesheet Name', required=True, translate=True, default=_get_default_name, readonly=True,
                       states={'draft': [('readonly', False)]})
    item_ids = fields.One2many(
        'product.price.sheet.line', 'price_sheet_id', 'Price sheet lines',
        copy=True)
    has_produced_overseas_items = fields.Boolean(compute='_compute_has_produced_overseas_items')
    currency_id = fields.Many2one('res.currency', 'Currency', default=_get_default_currency_id, required=True,
                                  readonly=True, states={'draft': [('readonly', False)]})
    opportunity_id = fields.Many2one(related='estimate_id.opportunity_id')
    estimate_id = fields.Many2one('sale.estimate', readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one(related='estimate_id.partner_id')
    quotation_count = fields.Integer(compute='_compute_sale_order_data',
                                     string="Number of Quotations")
    sale_order_ids = fields.One2many('sale.order', 'price_sheet_id', string='Quotations')
    state = fields.Selection([('draft', 'Draft'),
                              ('request_approval', 'Request Approval'),
                              ('confirmed', 'Confirmed'),
                              ('approved', 'Approved'),
                              ('closed', 'Close')], default='draft')
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, compute='_amount_all', tracking=5)
    tax_totals_json = fields.Char(compute='_compute_tax_totals_json')
    amount_tax = fields.Monetary(string='Taxes', store=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, compute='_amount_all', tracking=4)
    note = fields.Html('Terms and conditions', default=_default_note)
    terms_type = fields.Selection(related='company_id.terms_type')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms', check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    can_edit = fields.Boolean(compute="_compute_can_edit")

    def _compute_can_edit(self):
        for rec in self:
            rec.can_edit = rec.state == 'draft' or \
                           rec.state in ['request_approval', 'confirmed'] and self.env.user.has_group('regency_estimate.group_estimate_manager') or \
                           rec.state in ['approved'] and self.env.user.has_group('regency_estimate.group_estimate_administrator')

    @api.depends('sale_order_ids')
    def _compute_sale_order_data(self):
        for lead in self:
            lead.quotation_count = len(lead.sale_order_ids)

    @api.depends('item_ids.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.item_ids:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.depends('item_ids.produced_overseas')
    def _compute_has_produced_overseas_items(self):
        for ps in self:
            ps.has_produced_overseas_items = any(ps.mapped('item_ids.produced_overseas'))

    def _compute_access_url(self):
        # super(ProductPriceSheet, self)._compute_access_url()
        for rec in self:
            rec.access_url = '/my/price_sheets/%s' % (rec.id)

    def action_new_quotation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale_crm.sale_action_quotations_new")
        selected_lines = self.item_ids
        action['context'] = {
            'search_default_price_sheet_id': self.id,
            'default_price_sheet_id': self.id,
            'search_default_opportunity_id': self.opportunity_id.id,
            'default_opportunity_id': self.opportunity_id.id,
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_campaign_id': self.opportunity_id.campaign_id.id,
            'default_medium_id': self.opportunity_id.medium_id.id,
            'default_origin': self.opportunity_id.name,
            'default_source_id': self.opportunity_id.source_id.id,
            'default_company_id': self.opportunity_id.company_id.id or self.env.company.id,
            'default_tag_ids': [(6, 0, self.opportunity_id.tag_ids.ids)],
            'default_order_line': [
                Command.create({
                    'name': p.name,
                    'sequence': p.sequence,
                    'product_id': p.product_id.id,
                    'product_uom_qty': 0,
                    'min_quantity': p.min_quantity,
                    'max_quantity': p.max_quantity,
                    'display_type': p.display_type,
                    'price_unit': p.price,
                    'product_uom': p.product_id.uom_id.id,
                    'shipping_options': p.shipping_options,
                    'allow_consumption_agreement': p.allow_consumption_agreement
                }) for p in selected_lines.sorted('sequence')]
        }
        if self.opportunity_id.team_id:
            action['context']['default_team_id'] = self.opportunity_id.team_id.id,
        if self.opportunity_id.user_id:
            action['context']['default_user_id'] = self.opportunity_id.user_id.id
        self.action_confirm()
        return action

    def action_view_sale_quotation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action['context'] = {
            'search_default_draft': 1,
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_opportunity_id': self.opportunity_id.id,
            'default_price_sheet_id': self.id
        }
        action['domain'] = [('price_sheet_id', '=', self.id)]
        quotations = self.mapped('sale_order_ids')
        if len(quotations) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = quotations.id
        return action

    def _prepare_supplier_info(self, partner, line, price, currency):
        # Prepare supplierinfo data when adding a product
        return {
            'partner_id': partner.id,
            'sequence': max(line.product_id.seller_ids.mapped('sequence')) + 1 if line.product_id.seller_ids else 1,
            'min_qty': line.min_quantity,
            'price': price,
            'currency_id': currency.id,
           # 'delay': line.ETA,
        }

    def action_request_approval(self):
        for rec in self:
            rec.write({'state': 'request_approval'})
            if rec.estimate_id.estimate_manager_id:
                message = SystemMessages['M-013'] % rec.name
                self.env['mail.channel'].send_notification(message=message, user_id=rec.estimate_id.estimate_manager_id)

    def action_confirm(self):
        for line in self.mapped('item_ids'):
            # Do not add a contact as a supplier
            partner = line.partner_id
            if line.product_id and partner and partner not in line.product_id.seller_ids.mapped('partner_id') and len(
                    line.product_id.seller_ids) <= 10:
                # Convert the price in the right currency.
                currency = partner.property_purchase_currency_id or self.env.company.currency_id
                price = line.vendor_price

                supplierinfo = self._prepare_supplier_info(partner, line, price, currency)

                vals = {
                    'seller_ids': [(0, 0, supplierinfo)],
                }
                try:
                    line.product_id.write(vals)
                except AccessError:  # no write access rights -> just ignore
                    break
        self.write({'state': 'confirmed'})
        est_admin = self._get_estimate_administrator()
        if est_admin:
            for rec in self:
                message = SystemMessages['M-013'] % rec.name
                self.env['mail.channel'].send_notification(message=message, user_id=est_admin)

    def action_approve(self):
        self.ensure_one()
        self.write({'state': 'approved'})
        if self.estimate_id.user_id:
            url = f'{self.get_base_url()}{self.get_portal_url()}'
            message = SystemMessages['M-005'] % (
                f'<a href="/web#id={self.id}&amp;model={self._name}&amp;view_type=form">{self.name}</a>',
                f'<a href={url}>{url}</a>')
            self.env['mail.channel'].send_notification(message=message, user_id=self.estimate_id.user_id)

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_close(self):
        self.write({'state': 'closed'})

    def action_get_portal_link(self):
        base_url = self.get_base_url()
        wiz = self.env['portal.link.wizard'].create({'name': f'{base_url}{self.get_portal_url()}'})
        return {
            'name': 'Portal Link',
            'view_mode': 'form',
            'res_model': 'portal.link.wizard',
            'res_id': wiz.id,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def _get_estimate_administrator(self):
        return self.env['res.users'].search([('groups_id', 'in', self.env.ref('regency_estimate.group_estimate_administrator').ids)])

    def has_to_be_signed(self):
        return False

    def has_to_be_paid(self, draft=False):
        return False

    def _get_portal_return_action(self):
        """ Return the action used to display orders when returning from customer portal. """
        self.ensure_one()
        return self.env.ref('regency_estimate.action_product_price_sheet')

    def preview_price_sheets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }

    @api.depends('item_ids.price', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json(self):
        for order in self:
            totals =  {
                'amount_total': order.amount_total,
                'amount_untaxed': order.amount_untaxed,
                'formatted_amount_total': formatLang(self.env, order.amount_total, currency_obj=order.currency_id),
                'formatted_amount_untaxed': formatLang(self.env, order.amount_untaxed, currency_obj=order.currency_id),
                'groups_by_subtotal': [],
                'subtotals': [],
                'allow_tax_edition': False,
            }
            order.tax_totals_json = json.dumps(totals)

    def create_sale_order(self, lines_to_order):
        self.ensure_one()

        order = self.env['sale.order'].create({'access_token': self.access_token,
                                       'partner_id': self.partner_id.id,
                                       'estimate_id': lines_to_order.price_sheet_id.estimate_id.id,
                                       'price_sheet_id': self.id,
                                       'order_line': [
                                            Command.create({
                                                'product_id': p.product_id.id,
                                                'product_uom_qty': p.product_uom_qty,
                                                'price_unit': p.price,
                                                'product_uom': p.product_id.uom_id.id,
                                                'pricesheet_line_id': p.id,
                                                'name': p.name,
                                            }) for p in lines_to_order]})
        if order.partner_id.country_id:
            order.currency_id = order.partner_id.country_id.currency_id
        order.message_subscribe([order.partner_id.id])
        sequence = 10
        for line in order.order_line:
            sequence += 1
            line.sequence = sequence
            fee_value_ids = line.pricesheet_line_id.fee_value_ids
            if fee_value_ids:
                sequence += 1
                line.create({'display_type': 'line_note',
                             'name': f'Additional Fees for {line.product_id.name}:',
                             'order_id': line.order_id.id,
                             'pricesheet_line_id': line.pricesheet_line_id.id,
                             'sequence': sequence})
                for fee in fee_value_ids:
                    sequence += 1
                    line.create({'product_id': fee.fee_type_id.product_id.id,
                                 'price_unit': fee.portal_value,
                                 'order_id': line.order_id.id,
                                 'pricesheet_line_id': line.pricesheet_line_id.id,
                                 'sequence': sequence})
        lines_to_order.write({'product_uom_qty': 0})
        return order

    def create_consumption_agreement(self, lines_to_order):
        self.ensure_one()
        order = self.env['consumption.agreement'].create({'access_token': self.access_token,
                                                          'partner_id': self.partner_id.id,
                                                          'from_pricesheet_id': self.id,
                                                          'line_ids': [
                                                              Command.create({
                                                                  'product_id': p.product_id.id,
                                                                  'qty_allowed': p.product_uom_qty,
                                                                  'price_unit': p.price,
                                                                  'vendor_id': p.partner_id.id,
                                                                  'name': p.name
                                                              }) for p in lines_to_order],
                                                          'currency_id': self.currency_id.id})
        lines_to_order.write({'product_uom_qty': 0})
        return order

    def update_lines(self, sheet_lines):
        for rec in self:
            existing_product_lines = self.item_ids.mapped(lambda x: (x.product_id.id, x.partner_id.id, x.min_quantity))
            for line in sheet_lines:
                if (line.product_id.id, line.partner_id.id, line.min_quantity) not in existing_product_lines:
                    rec.write({'item_ids': [(4, line.id)]})


class ProductPriceSheetLine(models.Model):
    _name = 'product.price.sheet.line'
    _order = 'product_id ASC, min_quantity ASC'

    price_sheet_id = fields.Many2one('product.price.sheet')
    name = fields.Text('Description')
    sequence = fields.Integer("Sequence", default=10)
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain="[('sale_ok', '=', True)]",
        change_default=True, ondelete='restrict', check_company=True)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    min_quantity = fields.Float(string='Min Qty', digits='Product Unit of Measure', default=0.0)
    max_quantity = fields.Float(string='Max Qty', digits='Product Unit of Measure', compute="_compute_max_quantity")
    product_uom_qty = fields.Float(string='Qty', digits='Product Unit of Measure', default=0.0)
    margin = fields.Float(string='Margin %', compute='_compute_margin')
    vendor_price = fields.Float(required=True, default=0.0, digits='Product Price')
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        readonly=True, related='price_sheet_id.currency_id', store=True)
    price = fields.Float(string='Customer Price', digits='Product Price', store=True)
    sale_estimate_line_ids = fields.Many2many('sale.estimate.line', 'product_price_sheet_line_sale_estimate_line_relation',
                                         'price_sheet_line_id', 'sale_estimate_line_id')
    total = fields.Float()
    shipping_options = fields.Char()
    partner_id = fields.Many2one('res.partner', 'Vendor')
    duty = fields.Float(digits='Product Price')
    freight = fields.Float(digits='Product Price')
    unit_price = fields.Float(string='Unit Price', digits='Product Price', store=True, compute='_compute_unit_price')
    production_lead_time = fields.Char()
    shipping_lead_time = fields.Char()
    allow_consumption_agreement = fields.Boolean(default=True)
    consumption_type = fields.Selection([('consumption', 'Consumption Agreement'),
                                         ('dropship', 'Dropship')], default='dropship')  # TODO: delete?
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    qty_range_str = fields.Char(compute='_compute_qty_range_str')
    insection_rownumber = fields.Integer(compute="_compute_insection_rownumber")
    insection_total_rows = fields.Integer(compute="_compute_insection_rownumber")
    attachment_id = fields.Binary('File', attachment=True)
    attachment_name = fields.Char()
    produced_overseas = fields.Boolean('Produced Overseas')
    display_name = fields.Char(compute='_compute_display_name')
    color = fields.Integer('Color Index', compute='_compute_color')
    fee = fields.Float(readonly=True, compute='_compute_fee', store=True)
    fee_value_ids = fields.One2many('fee.value', 'price_sheet_line_id')
    portal_fee = fields.Float(compute='_compute_fee', store=True)

    @api.depends('fee_value_ids', 'fee_value_ids.value', 'fee_value_ids.portal_value', 'fee_value_ids.per_item',
                 'min_quantity', 'price')
    def _compute_fee(self):
        for rec in self:
            rec.fee = rec.fee_value_ids.get_fee_sum(rec.min_quantity, rec.price)
            rec.portal_fee = sum(rec.fee_value_ids.mapped('portal_value'))
            rec.onchange_price()

    def _compute_display_name(self):
        for psl in self:
            psl.display_name = '%s %s' % (psl.price_sheet_id.name, psl.name)

    def _compute_color(self):
        for rec in self:
            if rec.price_sheet_id.state == 'draft':
                rec.color = 0  # White
            elif rec.price_sheet_id.state in ['approved', 'closed']:
                rec.color = 10  # Green
            else:
                rec.color = 3  # Yellow

    @api.depends('vendor_price', 'duty', 'freight')
    def _compute_unit_price(self):
        for rec in self:
            rec.unit_price = rec.vendor_price + rec.duty + rec.freight

    @api.depends('min_quantity', 'max_quantity', 'sequence')
    def _compute_qty_range_str(self):
        for rec in self:
            if rec.min_quantity and rec.max_quantity == MAX_QUANTITY:
                qstr = '> ' + str(int(rec.min_quantity))
            elif rec.min_quantity > 0 and rec.max_quantity < MAX_QUANTITY:
                qstr = str(int(rec.min_quantity)) + ' - ' + str(int(rec.max_quantity))
            elif rec.min_quantity == 0 and rec.max_quantity < MAX_QUANTITY:
                qstr = '< ' + str(int(rec.max_quantity))
            else:
                qstr = ''
            rec.qty_range_str = qstr

    def _compute_insection_rownumber(self):
        prev_rec = False
        first_rec = False
        for rec in self.sorted('sequence'):
            rec.insection_rownumber = 1
            rec.insection_total_rows = 1
            if prev_rec and prev_rec.product_id == rec.product_id:
                rec.insection_rownumber = prev_rec.insection_rownumber + 1
                if not first_rec:
                    first_rec = prev_rec
                first_rec.insection_total_rows = rec.insection_rownumber
            else:
                first_rec = False
            prev_rec = rec

    @api.depends('price', 'unit_price')
    def _compute_margin(self):
        for rec in self:
            rec.margin = 100 * (rec.price - rec.unit_price) / rec.price if rec.price else 0

    @api.onchange('total')
    def onchange_total(self):
        for rec in self:
            rec.price = (rec.total - rec.fee) / rec.min_quantity if rec.min_quantity else 0

    @api.onchange('price')
    def onchange_price(self):
        for rec in self:
            rec.total = rec.price * rec.min_quantity + rec.fee

    def _compute_max_quantity(self):
        for rec in self.sorted('sequence'):
            same_product_and_vendor_recs = self.filtered(
                lambda f: f.product_id == rec.product_id and f.partner_id == rec.partner_id).sorted('min_quantity')
            prev_rec = False
            for item in same_product_and_vendor_recs:
                item.max_quantity = MAX_QUANTITY
                if prev_rec:
                    prev_rec.max_quantity = item.min_quantity
                prev_rec = item

    @api.depends('product_uom_qty', 'price')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price  # * (1 - (line.discount or 0.0) / 100.0)  #TODO: add if discount will be needed
            taxes = self.env['account.tax'].compute_all(price, line.price_sheet_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.price_sheet_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_subtotal': taxes['total_excluded'] + line.portal_fee,
            })

    def action_check_prices(self):
        customer = self.price_sheet_id.partner_id
        if customer:
            related_so_lines = self.env['sale.order.line'].search([('order_id.state', '=', 'sale'),
                                                                   ('order_id.partner_id', '=', customer.id),
                                                                   ('product_id', '=', self.product_id.id),
                                                                   ('qty_invoiced', '>', 0),
                                                                   ('qty_delivered', '>', 0)])
            price_lines = self.env['previous.price.line.wizard']
            for r_line in related_so_lines:
                if r_line.product_id:
                    p_line = r_line.get_purchase_order_lines().filtered(lambda x: x.state != 'cancel')
                    p_line = p_line[0] if p_line else False
                    new_price_line = self.env['previous.price.line.wizard'].create(
                        {'product_id': r_line.product_id.id, 'price': r_line.price_unit,
                         'date_order': r_line.order_id.date_order, 'qty': r_line.product_uom_qty,
                         'cost_price': r_line.purchase_price, 'margin_percent': r_line.margin_percent,
                         'ca_price': r_line.consumption_agreement_line_id.price_unit if r_line.consumption_agreement_line_id else 0,
                         'ca_qty': r_line.consumption_agreement_line_id.qty_allowed if r_line.consumption_agreement_line_id else 0,
                         'ca_date_order': r_line.consumption_agreement_line_id.signed_date if r_line.consumption_agreement_line_id else False,
                         'po_price': p_line.price_unit if p_line else 0,
                         'po_qty': p_line.product_uom_qty if p_line else 0
                         })
                    price_lines += new_price_line
            wizard_id = self.env['previous.prices.wizard'].create({'name': 'Prices'})
            price_lines.write({'price_wizard_id': wizard_id.id})
            res = {
                'name': 'Previous prices',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'previous.prices.wizard',
                'res_id': wizard_id.id,
                'target': 'new'
            }
            return res

    def action_edit_fee_value(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("regency_estimate.action_fee_value")
        action['domain'] = [('price_sheet_line_id', '=', self.id)]
        action['context'] = {'default_price_sheet_line_id': self.id}
        return action
