from odoo import fields, models, api, _, tools


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    contacted = fields.Boolean(compute="_compute_contacted", store=True)
    representative_name = fields.Many2one('res.partner')
    email_from = fields.Char()
    no_open_actions = fields.Integer(string='No. Open Actions')
    no_spend_issues = fields.Boolean(string="No. Spend Issues")
    management_group = fields.Char(string="Management Group")
    avendra_id = fields.Char(string="Avendra ID")
    account_number = fields.Char(string="Account Number")
    customer_supplier_status = fields.Char(string="Customer Supplier Status")
    customer_status = fields.Char(string="Customer Status")
    market_segment = fields.Char(string="Market Segment")
    brand = fields.Char(string="Brand")
    date_acknowledged = fields.Date(string="Date Acknowledged No Longer a Customer")
    date_de_enrollment = fields.Date(string="De-Enrollment Date")
    avendra_account_name = fields.Char(string="Account Name")
    avendra_account_address1 = fields.Char(string="Account Address 1")
    avendra_account_address2 = fields.Char(string="Account Address 2")
    avendra_account_date_setup = fields.Date(string="Account Setup Date")
    avendra_account_punchout_user_name = fields.Char(string="Account Punchout User Name")
    number_of_keys = fields.Integer()
    is_existing_customer = fields.Boolean(compute='_compute_is_existing_customer', store=True)
    partner_id = fields.Many2one(
        domain="[('is_company', '=', True), ('contact_type', '=', 'customer')]")
    partner_contact_ids = fields.One2many(related='partner_id.child_ids')
    partner_contact_id = fields.Many2one('res.partner', domain="[('id', 'in', partner_contact_ids)]")

    @api.onchange('partner_contact_id')
    def _onchange_partner_contact_id(self):
        if self.partner_contact_id:
            self.email_from = self.partner_contact_id.email
            self.function = self.partner_contact_id.function
            self.phone = self.partner_contact_id.phone
            self.mobile = self.partner_contact_id.mobile

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id != self.partner_contact_id.parent_id:
            self.partner_contact_id = False
            self.email_from = False
            self.function = False
            self.phone = False
            self.mobile = False

    @api.depends('account_number', 'avendra_account_address1', 'avendra_account_address2', 'street', 'street2')
    def _compute_is_existing_customer(self):
        for rec in self:
            rec.is_existing_customer = rec.account_number\
                                       and rec.street == rec.avendra_account_address1\
                                       and rec.street2 == rec.avendra_account_address2

    @api.depends('message_ids')
    def _compute_contacted(self):
        for rec in self:
            rec.contacted = rec.message_ids.filtered(lambda l: l.body)

    @api.depends('representative_name.email')
    def _compute_email_from(self):
        """
        Overridden to propagate email from representative_name instead of partner_id
        """
        for lead in self:
            if lead.representative_name.email and lead._get_partner_email_update():
                lead.email_from = lead.representative_name.email

    def _inverse_email_from(self):
        """
        Overridden to propagate email from representative_name instead of partner_id
        """
        for lead in self:
            if lead._get_partner_email_update():
                lead.representative_name.email = lead.email_from

    def _get_partner_email_update(self):
        """
        Overridden to propagate email from representative_name instead of partner_id
        """
        """
        Calculate if we should write the email on the related representative. When
        the email of the lead / representative is an empty string, we force it to False
        to not propagate a False on an empty string.
        Done in a separate method so it can be used in both ribbon and inverse
        and compute of email update methods.
        """
        self.ensure_one()
        if self.representative_name and self.email_from != self.representative_name.email:
            lead_email_normalized = tools.email_normalize(self.email_from) or self.email_from or False
            partner_email_normalized = tools.email_normalize(self.representative_name.email) or self.representative_name.email or False
            return lead_email_normalized != partner_email_normalized
        return False

    @api.depends('email_from', 'representative_name')
    def _compute_partner_email_update(self):
        """
        Overridden to propagate email from representative_name instead of partner_id
        """
        for lead in self:
            lead.partner_email_update = lead._get_partner_email_update()

    @api.depends('phone', 'representative_name')
    def _compute_partner_phone_update(self):
        """
        Overridden to propagate phone from representative_name instead of partner_id
        """
        for lead in self:
            lead.partner_phone_update = lead._get_partner_phone_update()

    @api.depends('representative_name.phone')
    def _compute_phone(self):
        """
        Overridden to propagate phone from representative_name instead of partner_id
        """
        for lead in self:
            if lead.representative_name.phone and lead._get_partner_phone_update():
                lead.phone = lead.representative_name.phone

    @api.depends_context('uid')
    @api.depends('partner_id', 'type')
    def _compute_is_partner_visible(self):
        """Overridden to ALWAYS show field customer_id"""
        is_debug_mode = True
        for lead in self:
            lead.is_partner_visible = bool(lead.type == 'opportunity' or lead.partner_id or is_debug_mode)

    def _inverse_phone(self):
        """
        Overridden to propagate phone from representative_name instead of partner_id
        """
        for lead in self:
            if lead._get_partner_phone_update():
                lead.representative_name.phone = lead.phone

    def _get_partner_phone_update(self):
        """
        Overridden to propagate phone from representative_name instead of partner_id
        """
        """Calculate if we should write the phone on the related representative. When
        the phone of the lead / representative is an empty string, we force it to False
        to not propagate a False on an empty string.
        Done in a separate method so it can be used in both ribbon and inverse
        and compute of phone update methods.
        """
        self.ensure_one()
        if self.representative_name and self.phone != self.representative_name.phone:
            lead_phone_formatted = self.phone_get_sanitized_number(number_fname='phone') or self.phone or False
            partner_phone_formatted = self.representative_name.phone_get_sanitized_number(number_fname='phone') or self.representative_name.phone or False
            return lead_phone_formatted != partner_phone_formatted
        return False

    def _message_post_after_hook(self, message, msg_vals):
        res = super(CRMLead, self)._message_post_after_hook(message, msg_vals)
        self._compute_contacted()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for rec in res:
            rec.representative_name.parent_id = rec.partner_id
        return res

    def action_show_customer(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("base.action_partner_customer_form")
        action['views'] = [(self.env.ref('base.view_partner_form').id, 'form')]
        action['res_id'] = self.partner_id.id
        return action
