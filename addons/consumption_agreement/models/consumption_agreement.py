from odoo import api, fields, models, _, Command


class ConsumptionAgreement(models.Model):
    _name = 'consumption.agreement'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(required=True, copy=False, index=True, default=lambda self: _('New'))
    signed_date = fields.Date()
    partner_id = fields.Many2one('res.partner', domain=[('contact_type', '=', 'customer')], string='Primary Customer')
    allowed_partner_ids = fields.Many2many('res.partner',  domain=[('contact_type', '=', 'customer')], string="Allowed Customers")
    line_ids = fields.One2many('consumption.agreement.line', 'agreement_id')
    currency_id = fields.Many2one('res.currency')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    signature = fields.Image('Signature', help='Signature received through the portal.', copy=False, attachment=True,
                             max_width=1024, max_height=1024)
    signed_by = fields.Char('Signed By', help='Name of the person that signed the Consumption Agreement.', copy=False)
    signed_on = fields.Datetime('Signed On', help='Date of the signature.', copy=False)

    def _compute_access_url(self):
        super(ConsumptionAgreement, self)._compute_access_url()
        for rec in self:
            rec.access_url = '/my/consumptions/%s' % (rec.id)

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'
            if not rec.signed_date:
                rec.signed_date = fields.Date.today()

    def create_sale_order(self, selected_line_ids):
        self.ensure_one()
        order = self.env['sale.order'].create({'access_token': self.access_token,
                                       'partner_id': self.partner_id.id,
                                       'order_line': [
                                            Command.create({
                                                'product_id': p.product_id.id,
                                                'product_uom_qty': 0,
                                                'price_unit': p.price_unit,
                                                'product_uom': p.product_id.uom_id.id,
                                                'consumption_agreement_line_id': p.id
                                            }) for p in self.line_ids.filtered(lambda l: l.id in selected_line_ids)]})
        return order

    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('consumption.agreement') or _('New')
        result = super(ConsumptionAgreement, self).create(vals)
        return result

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

    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    currency_id = fields.Many2one(related='agreement_id.currency_id', store=True)
    state = fields.Selection(related='agreement_id.state', store=True)
    sale_order_line_ids = fields.One2many('sale.order.line', 'consumption_agreement_line_id')
    partner_id = fields.Many2one(related='agreement_id.partner_id', domain=[('contact_type', '=', 'customer')], store=True)
    allowed_partner_ids = fields.Many2many('res.partner', domain=[('contact_type', '=', 'customer')], string="Allowed Customers")

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

