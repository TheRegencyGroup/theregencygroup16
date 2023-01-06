from odoo import fields, models, api, Command, _


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    opportunity_id = fields.Many2one('crm.lead')
    estimate_id = fields.Many2one('sale.estimate')
    estimate_line_ids = fields.Many2many('sale.estimate.line', 'sale_estimate_line_purchase_agreements_rel',
                                     'purchase_agreement_id', 'estimate_line_id')
    color = fields.Integer('Color Index', compute='_compute_color')
    customer_id = fields.Many2one(related='estimate_id.partner_id')
    product_ids = fields.One2many('product.product', compute='_compute_product_ids')

    def _compute_product_ids(self):
        for rec in self:
            rec.product_ids = self.env['product.product'].browse(set([line.product_id.id for line in rec.line_ids]))

    def _compute_color(self):
        for rec in self:
            if rec.state == 'in_progress':
                rec.color = 7
            elif rec.state == 'open':
                rec.color = 3
            elif rec.state == 'done':
                rec.color = 10
            else:
                rec.color = 0

    @api.depends('price_sheet_ids')
    def _compute_price_sheet_data(self):
        for lead in self:
            lead.price_sheet_count = len(lead.price_sheet_ids)

    def action_done(self):
        """
        Generate all purchase order based on selected lines, should only be called on one agreement at a time
        """
        # TODO: do we need this?
        for requisition in self:
            for requisition_line in requisition.line_ids:
                requisition_line.supplier_info_ids.unlink()
        self.write({'state': 'done'})

    @api.depends('name', 'user_id')
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.user_id:
                name = record.user_id.name + ' ' + (name if name != 'New' else '#' + str(record.id))
            res.append((record.id, name))
        return res

    @api.model
    def create(self, vals):
        res = super(PurchaseRequisition, self).create(vals)
        for rec in res:
            user_id = rec.user_id
            if user_id:
                rec.send_notification(user_id)
        return res

    def write(self, values):
        res = super(PurchaseRequisition, self).write(values)
        user_id = values.get('user_id')
        if user_id:
            for rec in self:
                rec.send_notification(self.env['res.users'].browse(user_id))
        return res

    def action_cancel(self):
        # try to set all associated quotations to cancel state
        for requisition in self:
            for requisition_line in requisition.line_ids:
                requisition_line.supplier_info_ids.unlink()
            if requisition.purchase_ids:
                requisition.purchase_ids.cancel_order_with_requisition_cancellation('purchase requisition has been canceled')
            for po in requisition.purchase_ids:
                po.message_post(body=_('Cancelled by the agreement associated to this quotation.'))
        self.write({'state': 'cancel'})

    def send_notification(self, user_id, message=False):
        if not message:
            message = f'Purchase Requisition #' \
                      f'<a href="/web#id={self.id}&amp;model={self._name}&amp;view_type=form">{self.name}</a>' \
                      f' is assigned to you'
        ch_obj = self.env['mail.channel']
        ch_obj.send_notification(user_id, message=message)

    def action_in_progress(self):
        super(PurchaseRequisition, self).action_in_progress()
        self.send_notification(self.create_uid,
                               message=f'User has confirmed Purchase Requisition #<a href="/web#id={self.id}&amp;'
                                       f'model={self._name}&amp;view_type=form">{self.name}</a>')


class PurchaseRequisitionLine(models.Model):
    _name = 'purchase.requisition.line'
    _inherit = [ 'purchase.requisition.line', 'multi.currency.mixin']

    partner_id = fields.Many2one('res.partner', 'Vendor')
    produced_overseas = fields.Boolean('Produced Overseas')
    display_name = fields.Char(compute='_compute_display_name')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ], compute='_compute_state', store=True)
    color = fields.Integer('Color Index', compute='_compute_color')
    fee = fields.Float(readonly=True, compute='_compute_fee')
    fee_value_ids = fields.One2many('fee.value', 'purchase_requisition_line_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id)

    @api.depends('fee_value_ids', 'fee_value_ids.value', 'fee_value_ids.per_item', 'product_qty', 'price_unit')
    def _compute_fee(self):
        for rec in self:
            rec.fee = rec.fee_value_ids.get_fee_sum(rec.product_qty, rec.price_unit)

    @api.onchange('partner_id')
    def _onchange_partner(self):
        self.produced_overseas = self.partner_id.is_company\
                                 and self.partner_id.is_vendor and self.partner_id.vendor_type == 'overseas'

    def _compute_display_name(self):
        for prl in self:
            prl.display_name = '%s %s' % (prl.requisition_id.user_id.name, prl.requisition_id.name)

    @api.depends('requisition_id', 'partner_id', 'requisition_id.state', 'price_unit')
    def _compute_state(self):
        for prl in self:
            if prl.partner_id and prl.price_unit > 0:
                prl.state = 'done'
                continue
            elif prl.requisition_id.state == 'draft':
                prl.state = 'draft'
                continue
            else:
                prl.state = 'in_progress'

    def _compute_color(self):
        for rec in self:
            if rec.state == 'in_progress':
                rec.color = 3  # Yellow
            elif rec.state == 'done':
                rec.color = 10  # Green
            else:
                rec.color = 0  # White

    def action_edit_fee_value(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("regency_estimate.action_fee_value")
        action['domain'] = [('purchase_requisition_line_id', '=', self.id)]
        action['context'] = {'default_purchase_requisition_line_id': self.id}
        return action
