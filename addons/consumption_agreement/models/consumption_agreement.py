from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError
from odoo.tools import html_keep_url, is_html_empty, get_lang
from odoo.addons.regency_tools import SystemMessages


class ConsumptionAgreement(models.Model):
    _name = 'consumption.agreement'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(required=True, copy=False, index=True, default=lambda self: _('New'))
    signed_date = fields.Date()
    partner_id = fields.Many2one('res.partner', domain=[('contact_type', '=', 'customer')], string='Primary Customer')
    possible_partners = fields.One2many('res.partner', compute='_compute_possible_partners')
    allowed_partner_ids = fields.Many2many('res.partner', string="Allowed Customers")
    line_ids = fields.One2many('consumption.agreement.line', 'agreement_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    signature = fields.Image('Signature', help='Signature received through the portal.', copy=False, attachment=True,
                             max_width=1024, max_height=1024)
    signed_by = fields.Char('Signed By', help='Name of the person that signed the Consumption Agreement.', copy=False)
    signed_on = fields.Datetime('Signed On', help='Date of the signature.', copy=False)
    sale_order_ids = fields.One2many('sale.order', 'consumption_agreement_id')
    sale_order_count = fields.Integer(compute='_compute_order_count')
    purchase_order_ids = fields.One2many('purchase.order', 'consumption_agreement_id')
    purchase_order_count = fields.Integer(compute='_compute_order_count')
    note = fields.Html(string="Terms and conditions", compute='_compute_note', store=True, readonly=False,
                       precompute=True)
    company_id = fields.Many2one('res.company', required=True, index=True, default=lambda self: self.env.company)
    terms_type = fields.Selection(related='company_id.terms_type')
    legal_accepted = fields.Boolean(default=False)
    invoice_count = fields.Integer(string="Invoice Count", compute='_compute_invoice_stat')
    deposit_percent = fields.Float(string='Deposit %', compute='_compute_invoice_stat')
    deposit_percent_str = fields.Char(compute='_compute_invoice_stat')
    invoice_ids = fields.One2many('account.move', 'consumption_agreement_id', string="Invoices")
    tax_totals = fields.Binary(compute='_compute_tax_totals')

    @api.depends('line_ids.price_unit', 'line_ids.qty_allowed')
    def _compute_tax_totals(self):
        for order in self:
            order_lines = order.line_ids #.filtered(lambda x: not x.display_type)
            order.tax_totals = self.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in order_lines],
                order.currency_id,
            )

    @api.depends('invoice_ids', 'invoice_ids.amount_untaxed', 'line_ids.untaxed_amount')
    def _compute_invoice_stat(self):
        for rec in self:
            rec.invoice_count = len(rec.invoice_ids)
            ca_amount = sum(rec.line_ids.mapped("untaxed_amount"))
            downpayment_amount = sum(rec.invoice_ids.mapped('amount_untaxed'))
            rec.deposit_percent = round(downpayment_amount / ca_amount * 100, 2) if ca_amount > 0 else 0
            rec.deposit_percent_str = str(rec.deposit_percent) + '%'

    @api.model
    def _get_note_url(self):
        return self.env.company.get_base_url()

    def toggle_legal_accepted(self, checked):
        self.ensure_one()
        if self.state == 'draft':
            self.sudo().write({'legal_accepted': checked})
        return self.legal_accepted

    @api.depends('partner_id')
    def _compute_note(self):
        use_invoice_terms = self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms')
        if not use_invoice_terms:
            return
        for order in self:
            order = order.with_company(order.company_id)
            if order.terms_type == 'html' and self.env.company.invoice_terms_html:
                baseurl = html_keep_url(order._get_note_url() + '/terms')
                order.note = _('Terms & Conditions: %s', baseurl)
            elif not is_html_empty(self.env.company.invoice_terms):
                order.note = order.with_context(lang=order.partner_id.lang).env.company.invoice_terms

    @api.depends('sale_order_ids', 'purchase_order_ids')
    def _compute_order_count(self):
        for rec in self:
            rec.sale_order_count = len(rec.sale_order_ids)
            rec.purchase_order_count = len(rec.purchase_order_ids)

    def _compute_access_url(self):
        super(ConsumptionAgreement, self)._compute_access_url()
        for rec in self:
            rec.access_url = '/my/consumptions/%s' % (rec.id)

    @api.depends('partner_id')
    def _compute_possible_partners(self):
        for ca in self:
            association_type_ids = [self.env.ref('regency_contacts.hotel_group_to_management_group'),
                                    self.env.ref('regency_contacts.management_group_to_hotel')]
            ca.possible_partners = False  # Need to avoid compute error
            ca.possible_partners = ca.partner_id.association_ids.filtered(
                lambda f: f.association_type_id in association_type_ids).mapped('right_partner_id.id')

    def action_confirm(self):
        for rec in self:
            rec._check_is_vendor_set()
            rec.state = 'confirmed'
            if not rec.signed_date:
                rec.signed_date = fields.Date.today()
            rec.update_product_route_ids()

    def update_product_route_ids(self):
        products = self.line_ids.mapped('product_id')
        cross_docks = self.env['stock.warehouse'].search([]).mapped('crossdock_route_id')
        dropship_route = self.env.ref('stock_dropshipping.route_drop_shipping')
        mto = self.env.ref('stock.route_warehouse0_mto')
        routes_to_remove = cross_docks + dropship_route + mto
        mto_mts = self.env.ref('stock_mts_mto_rule.route_mto_mts')
        buy = self.env.ref('purchase_stock.route_warehouse0_buy')
        products.write({'route_ids': [Command.link(mto_mts.id)] + [Command.unlink(r.id) for r in routes_to_remove]})

    def open_sale_orders(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("sale.action_orders")
        action['context'] = {'default_consumption_agreement_id': self.id}
        action['domain'] = [('id', 'in', self.sale_order_ids.ids)]
        if len(self.sale_order_ids) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = self.sale_order_ids.id
        return action

    def open_purchase_orders(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("purchase.purchase_rfq")
        action['context'] = {'default_consumption_agreement_id': self.id}
        action['domain'] = [('id', 'in', self.purchase_order_ids.ids)]
        if len(self.purchase_order_ids) == 1:
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = self.purchase_order_ids.id
        return action

    def create_sale_order(self, selected_line_ids, qtys=False):
        if not qtys:
            qtys = {}
        self.ensure_one()
        order_count = self.sale_order_count
        order = self.env['sale.order'].create({'access_token': self.access_token,
                                       'partner_id': self.partner_id.id,
                                       'consumption_agreement_id': self.id,
                                       'order_line': [
                                            Command.create({
                                                'product_id': p.product_id.id,
                                                'product_uom_qty': qtys.get(p.id, p.qty_remaining),
                                                'price_unit': p.price_unit,
                                                'product_uom': p.product_id.uom_id.id,
                                                'consumption_agreement_line_id': p.id
                                            }) for p in self.line_ids.filtered(lambda l: l.id in selected_line_ids)]})
        order.message_subscribe([order.partner_id.id])
        return order, order_count

    def _check_is_vendor_set(self):
        self.ensure_one()
        products_without_vendor = []
        for line in self.line_ids:
            if line.product_id:
                seller = line.product_id._select_seller(quantity=line.qty_allowed)
                if not line.vendor_id and not seller:
                    products_without_vendor += line.product_id
        if products_without_vendor:
            raise UserError(_('Please set a vendor on product %s.') % ', '.join(
                [p.display_name for p in products_without_vendor]))

    def generate_purchase_order(self):
        self.ensure_one()
        self._check_is_vendor_set()
        order_count = self.purchase_order_count
        new_purchase_orders = self.env['purchase.order']
        for line in self.line_ids:
            seller = line.product_id._select_seller(quantity=line.qty_allowed)
            po = self.env['purchase.order'].create({
                'partner_id': line.vendor_id.id if line.vendor_id else seller.partner_id.id,
                'consumption_agreement_id': self.id,
                'order_line': [Command.create({
                    'product_id': line.product_id.id,
                    'product_qty': line.qty_allowed,
                    'price_unit': line.price_unit,
                    'customer_id': line.agreement_id.partner_id.id
                })]
            })
            new_purchase_orders += po
        if not order_count:
            action = self.env["ir.actions.act_window"]._for_xml_id("purchase.purchase_rfq")
            action['domain'] = [('id', 'in', [x.id for x in new_purchase_orders])]
            if len(new_purchase_orders) == 1:
                action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
                action['res_id'] = new_purchase_orders.id
            return action
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _(SystemMessages.get('M-009') % (
                ', '.join([o.name for o in new_purchase_orders]), 'are' if len(new_purchase_orders) > 1 else 'is')),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'}
            }
        }

    def generate_downpayment_invoice(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("sale.action_view_sale_advance_payment_inv")
        action['views'] = [(self.env.ref('consumption_agreement.view_consumption_advance_payment_inv').id, 'form')]
        action['context'] = {'default_advance_payment_method': 'percentage'}
        return action

    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env['ir.actions.actions']._for_xml_id('account.action_move_out_invoice_type')
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.partner_id.id,
                'default_partner_shipping_id': self.partner_id.id,
                'default_invoice_payment_term_id': self.partner_id.property_payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_invoice_origin': self.name,
            })
        action['context'] = context
        return action

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()

        return {
            'ref': '',
            'move_type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.currency_id and self.currency_id.id or self.env.company.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_shipping_id': self.partner_id.id,
            'fiscal_position_id': (self.env['account.fiscal.position']._get_fiscal_position(
                self.partner_id)).id,
            'invoice_payment_term_id': self.partner_id.property_payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
            'invoice_origin': self.name,
            'company_id': self.company_id.id,
            'invoice_line_ids': [],
            'consumption_agreement_id': self.id
        }

    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('consumption.agreement') or _('New')
        result = super(ConsumptionAgreement, self).create(vals)
        result._check_is_vendor_set()
        return result

    def write(self, values):
        for rec in self:
            rec._check_is_vendor_set()
        return super().write(values)

    def has_to_be_signed(self):
        return not self.signature

    def has_to_be_paid(self, draft=False):
        return False

    def _send_order_confirmation_mail(self):
        return False

    def _get_portal_return_action(self):
        """ Return the action used to display orders when returning from customer portal. """
        self.ensure_one()
        return self.env.ref('consumption_agreement.consumption_agreement_action')

    def preview_consumptions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }

    def action_create_so(self):
        so_wizard = self.env['sale.order.ca.wizard'].create(
            {
                'consumption_agreement_id': self.id,
                'ca_line_ids': [(0, 0, {'consumption_agreement_line_id': ca_line.id, 'selected_qty': ca_line.qty_remaining}) for ca_line in self.line_ids]
            })
        return {
            'name': _('Create SO'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(self.env.ref('consumption_agreement.create_so_wizard_form_view').id, 'form'),
                      (False, 'tree')],
            'res_model': 'sale.order.ca.wizard',
            'res_id': so_wizard.id,
            'target': 'new'
        }

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for ca in self:
            if ca.partner_id:
                ca.allowed_partner_ids = ca.partner_id + ca.possible_partners
            else:
                ca.allowed_partner_ids = False


class ConsumptionAggreementLine(models.Model):
    _name = 'consumption.agreement.line'

    agreement_id = fields.Many2one('consumption.agreement', 'Consumption Agreement')
    signed_date = fields.Date(related='agreement_id.signed_date', store=True)
    product_id = fields.Many2one('product.product')
    qty_allowed = fields.Integer('Agreement Qty')
    qty_allowed_confirmed = fields.Integer('Confirmed Agreement Qty', store=True, compute="_compute_report_values")
    qty_consumed = fields.Integer('Ordered Qty', compute="_compute_qty_consumed", store=True)
    qty_consumed_confirmed = fields.Integer('Confirmed Ordered Qty', compute="_compute_qty_consumed", store=True)
    qty_remaining = fields.Integer('Remaining Qty', compute="_compute_qty_consumed", store=True)
    qty_available = fields.Float('Product On Hand Quantity', related='product_id.qty_available')

    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    currency_id = fields.Many2one(related='agreement_id.currency_id', store=True)
    state = fields.Selection(related='agreement_id.state', store=True)
    sale_order_line_ids = fields.One2many('sale.order.line', 'consumption_agreement_line_id')
    partner_id = fields.Many2one(related='agreement_id.partner_id', domain=[('contact_type', '=', 'customer')],
                                 store=True)
    allowed_partner_ids = fields.Many2many('res.partner', string="Allowed Customers")
    vendor_id = fields.Many2one('res.partner', required=True)
    untaxed_amount = fields.Monetary(compute='_compute_untaxed_amount', store=True)
    name = fields.Text(string='Description')
    product_custom_attribute_value_ids = fields.One2many('product.attribute.custom.value', 'ca_product_line_id',
                                                         string="Custom Values", copy=True)
    # M2M holding the values of product.attribute with create_variant field set to 'no_variant'
    # It allows keeping track of the extra_price associated to those attribute values and add them to the SO line description
    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value', string="Extra Values",
                                                              ondelete='restrict')
    product_template_attribute_value_ids = fields.Many2many(related='product_id.product_template_attribute_value_ids',
                                                            readonly=True)

    @api.depends('qty_allowed', 'state', 'sale_order_line_ids', 'sale_order_line_ids.product_uom_qty')
    def _compute_qty_consumed(self):
        for rec in self:
            rec.qty_consumed_confirmed = sum(rec.sale_order_line_ids.filtered(lambda l: l.order_id.state == 'sale').
                mapped('product_uom_qty'))
            rec.qty_consumed = sum(rec.sale_order_line_ids.filtered(lambda l: l.order_id.state in ('draft', 'sale')).
                                             mapped('product_uom_qty'))
            rec.qty_remaining = rec.qty_allowed - rec.qty_consumed

    @api.depends('qty_allowed', 'state')
    def _compute_report_values(self):
        for rec in self:
            rec.qty_allowed_confirmed = rec.qty_allowed if rec.state == 'confirmed' else 0

    def name_get(self):
        result = []
        for rec in self.sudo():
            name = '%s - %s' % (rec.agreement_id.name, rec.product_id.name)
            result.append((rec.id, name))
        return result

    @api.depends('price_unit', 'qty_allowed')
    def _compute_untaxed_amount(self):
        for line in self:
            line.untaxed_amount = line.price_unit * line.qty_allowed

    @api.onchange('product_id')
    def product_id_change(self):
        self._update_description()

    def _update_description(self):
        if not self.product_id:
            return
        valid_values = self.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.custom_product_template_attribute_value_id not in valid_values:
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav._origin not in valid_values:
                self.product_no_variant_attribute_value_ids -= ptav

        product = self.product_id.with_context(
            lang=get_lang(self.env, self.agreement_id.partner_id.lang).code,
        )

        self.update({'name': self.get_multiline_description_sale(product, self.product_template_attribute_value_ids)})

    def get_multiline_description_sale(self, product, picked_attrs):
        """ Compute a default multiline description for this product line.

        In most cases the product description is enough but sometimes we need to append information that only
        exists on the sale order line itself.
        e.g:
        - custom attributes and attributes that don't create variants, both introduced by the "product configurator"
        - in event_sale we need to know specifically the sales order line as well as the product to generate the name:
          the product is not sufficient because we also need to know the event_id and the event_ticket_id (both which belong to the sale order line).
        """
        # display the is_custom values
        attrs_name = ''
        for pacv in picked_attrs:
            attrs_name += "\n" + pacv.with_context(lang=self.agreement_id.partner_id.lang).display_name
        return product.get_product_multiline_description_sale() + attrs_name + self._get_multiline_description_variants()

    def _get_multiline_description_variants(self):
        """When using no_variant attributes or is_custom values, the product
        itself is not sufficient to create the description: we need to add
        information about those special attributes and values.

        :return: the description related to special variant attributes/values
        :rtype: string
        """
        if not self.product_custom_attribute_value_ids and not self.product_no_variant_attribute_value_ids:
            return ""

        name = "\n"

        custom_ptavs = self.product_custom_attribute_value_ids.custom_product_template_attribute_value_id
        no_variant_ptavs = self.product_no_variant_attribute_value_ids._origin

        # display the no_variant attributes, except those that are also
        # displayed by a custom (avoid duplicate description)
        for ptav in (no_variant_ptavs - custom_ptavs):
            name += "\n" + ptav.with_context(lang=self.agreement_id.partner_id.lang).display_name

        # Sort the values according to _order settings, because it doesn't work for virtual records in onchange
        custom_values = sorted(self.product_custom_attribute_value_ids,
                               key=lambda r: (r.custom_product_template_attribute_value_id.id, r.id))
        # display the is_custom values
        for pacv in custom_values:
            name += "\n" + pacv.with_context(lang=self.agreement_id.partner_id.lang).display_name

        return name

    def _convert_to_tax_base_line_dict(self):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.

        :return: A python dictionary.
        """
        self.ensure_one()
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=self.agreement_id.partner_id,
            currency=self.currency_id,
            product=self.product_id,
            #taxes=self.tax_id,
            price_unit=self.price_unit,
            quantity=self.qty_allowed,
           # discount=self.discount,
            price_subtotal=self.untaxed_amount,
        )
